"""Base Node Module helper classes."""

import inspect
import threading
import time
import traceback
from pathlib import Path
from typing import Any, Callable, ClassVar, Optional, Union, get_type_hints

from madsci.client.event_client import (
    EventClient,
    default_logger,
)
from madsci.common.exceptions import (
    ActionNotImplementedError,
)
from madsci.common.types.action_types import (
    ActionArgumentDefinition,
    ActionDefinition,
    ActionFileDefinition,
    ActionRequest,
    ActionResult,
    ActionStatus,
)
from madsci.common.types.admin_command_types import AdminCommandResponse
from madsci.common.types.auth_types import OwnershipInfo
from madsci.common.types.base_types import Error
from madsci.common.types.event_types import Event, EventClientConfig, EventType
from madsci.common.types.node_types import (
    AdminCommands,
    NodeConfig,
    NodeDefinition,
    NodeInfo,
    NodeSetConfigResponse,
    NodeStatus,
)
from madsci.common.utils import pretty_type_repr, threaded_daemon, threaded_task
from pydantic import ValidationError
from semver import Version


def action(
    func: Callable,
    name: Optional[str] = None,
    description: Optional[str] = None,
    blocking: bool = False,
) -> Callable:
    """Decorator to mark a method as an action handler."""
    func.__is_madsci_action__ = True

    # *Use provided action_name or function name
    if name is None:
        name = func.__name__
    # * Use provided description or function docstring
    if description is None:
        description = func.__doc__
    func.__madsci_action_name__ = name
    func.__madsci_action_description__ = description
    func.__madsci_action_blocking__ = blocking
    return func


class AbstractNode:
    """
    Base Node implementation, protocol agnostic, all node class definitions should inherit from or be based on this.

    Note that this class is abstract: it is intended to be inherited from, not used directly.
    """

    node_definition: ClassVar[NodeDefinition] = None
    """The node definition."""
    node_status: ClassVar[NodeStatus] = NodeStatus(
        initializing=True,
    )
    """The status of the node."""
    node_state: ClassVar[dict[str, Any]] = {}
    """The state of the node."""
    action_handlers: ClassVar[dict[str, callable]] = {}
    """The handlers for the actions that the node supports."""
    action_history: ClassVar[dict[str, ActionResult]] = {}
    """The history of the actions that the node has performed."""
    status_update_interval: ClassVar[float] = 5.0
    """The interval at which the status handler is called. Overridable by config."""
    state_update_interval: ClassVar[float] = 5.0
    """The interval at which the state handler is called. Overridable by config."""
    node_info_path: ClassVar[Optional[Path]] = None
    """The path to the node info file. If unset, defaults to '<node_definition_path>.info.yaml'"""
    logger: ClassVar[EventClient] = EventClient()
    """The event logger for this node"""
    module_version: ClassVar[str] = "0.0.1"
    """The version of the module. Should match the version in the node definition."""

    def __init__(
        self,
        node_definition: Optional[NodeDefinition] = None,
        node_config: Optional[NodeConfig] = None,
    ) -> "AbstractNode":
        """Initialize the node class."""

        # * Load the node definition
        if node_definition is not None:
            self.node_definition = NodeDefinition.load_model(require_unique=True)
        if self.node_definition is None:
            raise ValueError("Node definition not found, aborting node initialization")

        # * Load the node config
        self._initialize_node_config(node_config)

        self._configure_events()

        # * Check Node Version
        if (
            Version.parse(self.module_version).compare(
                self.node_definition.module_version
            )
            < 0
        ):
            self.logger.log_warning(
                "The module version in the Node Module's source code does not match the version specified in your Module Definition. Your module may have been updated. We recommend checking to ensure compatibility, and then updating the version in your node definition to match."
            )

        # * Synthesize the node info
        self.node_info = NodeInfo.from_node_def_and_config(
            self.node_definition,
            self.config,
        )

        # * Add the admin commands to the node info
        self.node_info.capabilities.admin_commands = set.union(
            self.node_info.capabilities.admin_commands,
            {
                admin_command.value
                for admin_command in AdminCommands
                if hasattr(self, admin_command.value)
                and callable(self.__getattribute__(admin_command.value))
            },
        )
        # * Add the action decorators to the node
        for action_callable in self.__class__.__dict__.values():
            if hasattr(action_callable, "__is_madsci_action__"):
                self._add_action(
                    func=action_callable,
                    action_name=action_callable.__madsci_action_name__,
                    description=action_callable.__madsci_action_description__,
                    blocking=action_callable.__madsci_action_blocking__,
                )

        # * Save the node info
        if self.node_info_path:
            self.node_info.to_yaml(self.node_info_path)
        elif self.node_definition._definition_path:
            self.node_info_path = Path(
                self.node_definition._definition_path,
            ).with_suffix(".info.yaml")
            self.node_info.to_yaml(self.node_info_path, exclude={"config_values"})

        if self.node_definition._definition_path:
            self.node_definition.to_yaml(self.node_definition._definition_path)
        else:
            self.logger.log_warning(
                "No definition path set for node, skipping node definition update"
            )

        # * Add a lock for thread safety with blocking actions
        self._action_lock = threading.Lock()

    """------------------------------------------------------------------------------------------------"""
    """Node Lifecycle and Public Methods"""
    """------------------------------------------------------------------------------------------------"""

    def start_node(self) -> None:
        """Called once to start the node."""

        # * Update EventClient with logging parameters
        self._configure_events()

        # * Log startup info
        self.logger.log_info(f"{self.node_definition=}")

    def status_handler(self) -> None:
        """Called periodically to update the node status. Should set `self.node_status`"""

    def state_handler(self) -> None:
        """Called periodically to update the node state. Should set `self.node_state`"""

    def startup_handler(self) -> None:
        """Called to (re)initialize the node. Should be used to open connections to devices or initialize any other resources."""

    def shutdown_handler(self) -> None:
        """Called to shut down the node. Should be used to clean up any resources."""

    """------------------------------------------------------------------------------------------------"""
    """Interface Methods"""
    """------------------------------------------------------------------------------------------------"""

    def get_action_history(self) -> list[str]:
        """Get the action history of the node."""
        return list(self.action_history.keys())

    def run_action(self, action_request: ActionRequest) -> ActionResult:
        """Run an action on the node."""
        self.node_status.running_actions.add(action_request.action_id)
        action_response = None
        arg_dict = {}
        try:
            arg_dict = self._parse_action_args(action_request)
            self._check_required_args(action_request)
        except Exception as e:
            self._exception_handler(e, set_node_error=False)
            action_response = action_request.failed(errors=Error.from_exception(e))
        try:
            action_response = self._run_action(action_request, arg_dict)
        except Exception as e:
            self._exception_handler(e)
            action_response = action_request.failed(errors=Error.from_exception(e))
        else:
            if action_response is None:
                # * Assume success if no return value and no exception
                action_response = action_request.succeeded()
            elif not isinstance(action_response, ActionResult):
                try:
                    action_response = ActionResult.model_validate(action_response)
                except ValidationError as e:
                    action_response = action_request.failed(
                        errors=Error.from_exception(e),
                    )
        finally:
            self.node_status.running_actions.discard(action_request.action_id)
            self.action_history[action_request.action_id] = action_response
        return action_response

    def get_action_result(self, action_id: str) -> ActionResult:
        """Get the status of an action on the node."""
        if action_id in self.action_history:
            return self.action_history[action_id]
        return ActionResult(
            status=ActionStatus.FAILED,
            errors=Error(
                message=f"Action with id '{action_id}' not found",
                error_type="ActionNotFound",
            ),
        )

    def get_status(self) -> NodeStatus:
        """Get the status of the node."""
        return self.node_status

    def set_config(self, new_config: dict[str, Any]) -> NodeSetConfigResponse:
        """Set configuration values of the node."""
        errors = []

        try:
            self.config = self.config.model_copy(update=new_config)
        except ValidationError as e:
            errors.append(Error.from_exception(e))

        if not errors:
            # * Reset after a short delay to allow the response to be returned
            @threaded_task
            def schedule_reset() -> None:
                time.sleep(2)
                self.reset()

            schedule_reset()
        return NodeSetConfigResponse(
            success=len(errors) == 0,
            errors=errors,
        )

    def run_admin_command(self, admin_command: AdminCommands) -> AdminCommandResponse:
        """Run the specified administrative command on the node."""
        if self.hasattr(admin_command) and callable(
            self.__getattribute__(admin_command),
        ):
            try:
                response = self.__getattribute__(admin_command)()
                if response is None:
                    # * Assume success if no return value
                    response = True
                    return AdminCommandResponse(
                        success=True,
                        errors=[],
                    )
                if isinstance(response, bool):
                    return AdminCommandResponse(
                        success=response,
                        errors=[],
                    )
                if isinstance(response, AdminCommandResponse):
                    return response
                raise ValueError(
                    f"Admin command {admin_command} returned an unexpected value: {response}",
                )
            except Exception as e:
                self._exception_handler(e)
                return AdminCommandResponse(
                    success=False,
                    errors=[Error.from_exception(e)],
                )
        else:
            return AdminCommandResponse(
                success=False,
                errors=[
                    Error(
                        message=f"Admin command {admin_command} not implemented by this node",
                        error_type="AdminCommandNotImplemented",
                    ),
                ],
            )

    def get_info(self) -> NodeInfo:
        """Get information about the node."""
        return self.node_info

    def get_state(self) -> dict[str, Any]:
        """Get the state of the node."""
        return self.node_state

    def get_log(self) -> list[Event]:
        """Return the log of the node"""
        return self.logger.get_log()

    """------------------------------------------------------------------------------------------------"""
    """Internal and Private Methods"""
    """------------------------------------------------------------------------------------------------"""

    def _initialize_node_config(self, node_config: Optional[NodeConfig] = None) -> None:
        if node_config is not None:
            self.config = node_config
        else:
            # * Load the config from the command line
            if getattr(self, "config_model", None) is not None:
                config_model = self.config_model
            elif getattr(self, "config", None) is not None:
                config_model = self.config.__class__
            else:
                config_model = NodeConfig
            self.config = config_model.set_fields_from_cli(
                model_instance=self.config if self.config else None,
                override_defaults=self.node_definition.config_defaults,
            )

        # * Set general node config
        state_update_interval = getattr(
            self.config,
            "state_update_interval",
            self.state_update_interval,
        )
        self.state_update_interval = (
            state_update_interval
            if state_update_interval is not None
            else self.state_update_interval
        )
        status_update_interval = getattr(
            self.config,
            "status_update_interval",
            self.status_update_interval,
        )
        self.status_update_interval = (
            status_update_interval
            if status_update_interval is not None
            else self.status_update_interval
        )

    def _configure_events(self) -> None:
        """Configure the event logger."""
        event_client_config = EventClientConfig(
            name=f"node.{self.node_definition.node_name}",
            source=OwnershipInfo(node_id=self.node_definition.node_id),
        )
        self.logger = EventClient(
            config=event_client_config,
        )
        if (
            event_client_config := getattr(self.config, "event_client_config", None)
        ) is not None:
            try:
                event_client_config = EventClientConfig(**event_client_config)
                self.logger = EventClient(
                    config=event_client_config,
                )
            except ValidationError:
                self.logger.log_warning(
                    "Invalid event client config, using default values",
                )

    def _add_action(
        self,
        func: Callable,
        action_name: str,
        description: str,
        blocking: bool = False,
    ) -> None:
        """Add an action to the node module.

        Args:
            func: The function to add as an action handler
            action_name: The name of the action
            description: The description of the action
            blocking: Whether this action blocks other actions while running
        """
        # *Register the action handler
        self.action_handlers[action_name] = func

        action_def = ActionDefinition(
            name=action_name,
            description=description,
            blocking=blocking,
            args=[],
            files=[],
        )
        # *Create basic action definition from function signature
        signature = inspect.signature(func)
        if signature.parameters:
            for parameter_name, parameter_type in get_type_hints(
                func,
                include_extras=True,
            ).items():
                if parameter_name == "return":
                    continue
                if (
                    parameter_name not in action_def.args
                    and parameter_name not in [file.name for file in action_def.files]
                    and parameter_name != "action"
                ):
                    type_hint = parameter_type
                    description = ""
                    annotated_as_file = False
                    annotated_as_arg = False
                    # * If the type hint is an Annotated type, extract the type and description
                    # * Description here means the first string metadata in the Annotated type
                    if type_hint.__name__ == "Annotated":
                        type_hint = get_type_hints(func, include_extras=False)[
                            parameter_name
                        ]
                        description = next(
                            (
                                metadata
                                for metadata in parameter_type.__metadata__
                                if isinstance(metadata, str)
                            ),
                            "",
                        )
                        annotated_as_file = any(
                            isinstance(metadata, ActionFileDefinition)
                            for metadata in parameter_type.__metadata__
                        )
                        annotated_as_arg = not any(
                            isinstance(metadata, ActionArgumentDefinition)
                            for metadata in parameter_type.__metadata__
                        )
                        if annotated_as_file and annotated_as_arg:
                            raise ValueError(
                                f"Parameter '{parameter_name}' is annotated as both a file and an argument. This is not allowed.",
                            )
                    if annotated_as_file or (
                        type_hint.__name__
                        in ["Path", "PurePath", "PosixPath", "WindowsPath"]
                        and not annotated_as_arg
                    ):
                        # * Add a file parameter to the action
                        action_def.files[parameter_name] = ActionFileDefinition(
                            name=parameter_name,
                            required=True,
                            description=description,
                        )
                    else:
                        parameter_info = signature.parameters[parameter_name]
                        # * Add an arg to the action
                        default = (
                            None
                            if parameter_info.default == inspect.Parameter.empty
                            else parameter_info.default
                        )

                        action_def.args[parameter_name] = ActionArgumentDefinition(
                            name=parameter_name,
                            type=pretty_type_repr(type_hint),
                            default=default,
                            required=default is None,
                            description=description,
                        )
        self.node_info.actions[action_name] = action_def

    def _parse_action_args(
        self,
        action_request: ActionRequest,
    ) -> Union[ActionResult, tuple[callable, dict[str, Any]]]:
        """Parse the arguments for an action request."""
        action_callable = self.action_handlers.get(action_request.action_name, None)
        if action_callable is None:
            raise ActionNotImplementedError(
                f"Action {action_request.action_name} not implemented by this node",
            )
        # * Prepare arguments for the action function.
        # * If the action function has a 'state' or 'action' parameter
        # * we'll pass in our state and action objects.
        arg_dict = {}
        parameters = inspect.signature(action_callable).parameters
        if parameters.__contains__("action"):
            arg_dict["action"] = action_request
        if parameters.__contains__("self"):
            arg_dict["self"] = self
        if list(parameters.values())[-1].kind == inspect.Parameter.VAR_KEYWORD:
            # * Function has **kwargs, so we can pass all action args and files
            arg_dict = {**arg_dict, **action_request.args}
            arg_dict = {
                **arg_dict,
                **{file.filename: file.file for file in action_request.files},
            }
        else:
            # * Pass only explicit arguments, dropping extras
            for arg_name, arg_value in action_request.args.items():
                if arg_name in parameters:
                    arg_dict[arg_name] = arg_value
                else:
                    default_logger.log_warning(
                        f"Ignoring unexpected argument {arg_name}"
                    )
            for file in action_request.files:
                if file in parameters:
                    arg_dict[file] = action_request.files[file]
                else:
                    default_logger.log_warning(f"Ignoring unexpected file {file}")
        return arg_dict

    def _run_action(
        self,
        action_request: ActionRequest,
        arg_dict: dict[str, Any],
    ) -> ActionResult:
        action_callable = self.action_handlers.get(action_request.action_name, None)
        # * Perform the action here and return result
        if not self.node_status.ready:
            return action_request.not_ready(
                error=Error(
                    message=f"Node is not ready: {self.node_status.description}",
                    error_type="NodeNotReady",
                ),
            )
        self._action_lock.acquire()
        try:
            # * If the action is marked as blocking, set the node status to not ready for the duration of the action, otherwise release the lock immediately
            if self.node_info.actions[action_request.action_name].blocking:
                self.node_status.busy = True
                try:
                    result = action_callable(**arg_dict)
                except Exception as e:
                    self._exception_handler(e)
                    result = action_request.failed(errors=Error.from_exception(e))
                finally:
                    self.node_status.busy = False
            else:
                if self._action_lock.locked():
                    self._action_lock.release()
                try:
                    result = action_callable(**arg_dict)
                except Exception as e:
                    self._exception_handler(e)
                    result = action_request.failed(errors=Error.from_exception(e))
        finally:
            if self._action_lock.locked():
                self._action_lock.release()
        if isinstance(result, ActionResult):
            # * Make sure the action ID is set correctly on the result
            result.action_id = action_request.action_id
            return result
        if result is None:
            # *Assume success if no return value and no exception
            return action_request.succeeded()
        # * Return a failure if the action returns something unexpected
        return action_request.failed(
            errors=Error(
                message=f"Action '{action_request.action_name}' returned an unexpected value: {result}",
            ),
        )

    def _exception_handler(self, e: Exception, set_node_error: bool = True) -> None:
        """Handle an exception."""
        self.node_status.errored = set_node_error
        madsci_error = Error.from_exception(e)
        self.node_status.errors.append(madsci_error)
        self.logger.log_error(
            Event(event_type=EventType.NODE_ERROR, event_data=madsci_error)
        )
        self.logger.log_error(traceback.format_exc())

    @threaded_daemon
    def _loop_handler(self) -> None:
        """Handles calling periodic handlers, like the status and state handlers"""
        last_status_update = 0.0
        last_state_update = 0.0
        while True:
            try:
                if time.time() - last_status_update > self.status_update_interval:
                    last_status_update = time.time()
                    self.status_handler()
                if time.time() - last_state_update > self.state_update_interval:
                    last_state_update = time.time()
                    self.state_handler()
                time.sleep(0.1)
            except Exception as e:
                self._exception_handler(e)
                time.sleep(0.1)
