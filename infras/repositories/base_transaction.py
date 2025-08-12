import inspect
import logging
from abc import ABC, abstractmethod
from functools import wraps
from inspect import iscoroutinefunction
from typing import Callable, Type, Union, get_origin, TypeVar

from repositories import T, P


class BaseTransactionManager(ABC):
    """Base class for transaction managers with common session injection logic."""

    def __init__(self, session_type: Type):
        self._session_type = session_type
        self.logger = logging.getLogger(self.__class__.__name__)

    def _create_transactional_decorator(self, read_only: bool = False, is_async: bool = False):
        """
        Create a transactional decorator with session injection.
        
        Args:
            read_only: Whether to use session (True) or transaction (False)
            is_async: Whether this is for async functions
            
        Returns:
            A decorator function
        """

        def decorator(func: Callable[P, T]) -> Callable[P, T]:
            # Check function type
            if is_async:
                if not iscoroutinefunction(func):
                    raise TypeError("transactional decorator can only be applied to async functions")
            else:
                if iscoroutinefunction(func):
                    raise TypeError("transactional decorator can only be applied to sync functions")

            sig = inspect.signature(func)

            @wraps(func)
            def sync_wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
                def operation(session):
                    return self._inject_session_and_call(func, sig, args, kwargs, session)

                if read_only:
                    return self.execute_with_session(operation)
                else:
                    return self.execute_with_transaction(operation)

            @wraps(func)
            async def async_wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
                async def operation(session):
                    return await self._inject_session_and_call_async(func, sig, args, kwargs, session)

                if read_only:
                    return await self.execute_with_session(operation)
                else:
                    return await self.execute_with_transaction(operation)

            return async_wrapper if is_async else sync_wrapper

        return decorator

    def _inject_session_and_call(self, func: Callable, sig: inspect.Signature,
                                 args: tuple, kwargs: dict, session) -> T:
        """Inject session parameter and call the function."""
        # First, find which parameter should be the session parameter
        session_param_name = None
        non_session_params = []
        
        for name, param in sig.parameters.items():
            param_type = param.annotation
            if param_type is inspect.Parameter.empty:
                non_session_params.append(name)
                continue
                
            if self._is_compatible_session_type(param_type):
                session_param_name = name
            else:
                non_session_params.append(name)
        
        if not session_param_name:
            raise TypeError(
                f"Function {func.__name__} does not accept a {self._session_type.__name__} parameter"
            )
        
        # Create a new kwargs dict with session injected
        new_kwargs = kwargs.copy()
        new_kwargs[session_param_name] = session
        
        # Bind arguments, excluding the session parameter from positional binding
        try:
            # Try to bind without the session parameter
            bound = sig.bind_partial(*args, **new_kwargs)
        except TypeError:
            # If that fails, we need to handle positional arguments more carefully
            # Create a signature without the session parameter for binding
            new_params = [p for name, p in sig.parameters.items() if name != session_param_name]
            new_sig = inspect.Signature(new_params, return_annotation=sig.return_annotation)
            
            # Bind to the new signature
            bound = new_sig.bind_partial(*args, **kwargs)
            
            # Create the final bound arguments
            final_args = {}
            for name, value in bound.arguments.items():
                final_args[name] = value
            final_args[session_param_name] = session
            
            # Call the function with the correct arguments
            return func(**final_args)
        
        # Apply defaults and call
        bound.apply_defaults()
        return func(*bound.args, **bound.kwargs)

    def _is_compatible_session_type(self, param_type) -> bool:
        """Check if parameter type is compatible with session type."""
        # Subclass or direct match
        try:
            if inspect.isclass(param_type) and issubclass(param_type, self._session_type):
                return True
        except TypeError:
            pass
        if param_type == self._session_type:
            return True

        # Check by name
        if hasattr(param_type, '__name__') and param_type.__name__ == self._session_type.__name__:
            return True

        # Check by string representation
        if str(param_type).endswith(self._session_type.__name__):
            return True

        # Check for TypeVar (like TSession)
        if isinstance(param_type, TypeVar):
            bound = getattr(param_type, "__bound__", None)
            if bound is not None:
                return self._is_compatible_session_type(bound)

        # Check for Union types (e.g., TSession = Union[AsyncSession, SyncSession])
        try:
            origin = get_origin(param_type)
            if origin is Union or (hasattr(origin, '__name__') and origin.__name__ == 'UnionType'):
                args = getattr(param_type, '__args__', [])
                for arg in args:
                    if self._is_compatible_session_type(arg):
                        return True
                    # Also check if our session type is a subclass of the union arg
                    try:
                        if inspect.isclass(self._session_type) and issubclass(self._session_type, arg):
                            return True
                    except TypeError:
                        pass
        except (TypeError, AttributeError):
            pass

        return False

    async def _inject_session_and_call_async(self, func: Callable, sig: inspect.Signature,
                                             args: tuple, kwargs: dict, session) -> T:
        """Inject session parameter and call the async function."""
        # First, find which parameter should be the session parameter
        session_param_name = None
        non_session_params = []
        
        for name, param in sig.parameters.items():
            param_type = param.annotation
            if param_type is inspect.Parameter.empty:
                non_session_params.append(name)
                continue
                
            if self._is_compatible_session_type(param_type):
                session_param_name = name
            else:
                non_session_params.append(name)
        
        if not session_param_name:
            raise TypeError(
                f"Function {func.__name__} does not accept a {self._session_type.__name__} parameter"
            )
        
        # Create a new kwargs dict with session injected
        new_kwargs = kwargs.copy()
        new_kwargs[session_param_name] = session
        
        # Bind arguments, excluding the session parameter from positional binding
        try:
            # Try to bind without the session parameter
            bound = sig.bind_partial(*args, **new_kwargs)
        except TypeError:
            # If that fails, we need to handle positional arguments more carefully
            # Create a signature without the session parameter for binding
            new_params = [p for name, p in sig.parameters.items() if name != session_param_name]
            new_sig = inspect.Signature(new_params, return_annotation=sig.return_annotation)
            
            # Bind to the new signature
            bound = new_sig.bind_partial(*args, **kwargs)
            
            # Create the final bound arguments
            final_args = {}
            for name, value in bound.arguments.items():
                final_args[name] = value
            final_args[session_param_name] = session
            
            # Call the function with the correct arguments
            return await func(**final_args)
        
        # Apply defaults and call
        bound.apply_defaults()
        return await func(*bound.args, **bound.kwargs)

    @abstractmethod
    def execute_with_session(self, operation) -> T:
        """Execute operation with session."""
        pass

    @abstractmethod
    def execute_with_transaction(self, operation) -> T:
        """Execute operation with transaction."""
        pass
