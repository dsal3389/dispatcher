import enum
import inspect
from functools import wraps
from dataclasses import dataclass
from typing import Callable, Iterable, Any


DISPATCH_HANDLERS_ATTR = '__dispatch_handlers__'


class DispatchHandlerNotFound(Exception):
    def __init__(self, cls: type, handler_name: str) -> None:
        super().__init__(
            f"dispatch handler with the name {handler_name} for {cls.__name__} not found"
        )


class DispatchEvent(enum.Flag):
    # can be used only on classes
    FIELD_GET = enum.auto()
    FIELD_SET = enum.auto()
    FIELD_CHANGE = enum.auto()
    ON_METHOD_CALLS = enum.auto()

    # can be use both on classes and functions
    ON_CALL = enum.auto()


class DispatchBehaviour(enum.Flag):
    INCLUDE_INHERITANCE = enum.auto()


@dataclass(slots=True, frozen=True)
class DispatchEventInfo:
    event: DispatchHandlerNotFound
    object: type | None
    function: Callable
    function_trigger: Callable | str
    args: Iterable
    kwargs: dict


def dispatchers(cls: type) -> list[Callable]:
    if hasattr(cls, DISPATCH_HANDLERS_ATTR):
        return getattr(cls, DISPATCH_HANDLERS_ATTR)
    return []


def _call_dispatch_handlers(handlers: list[Callable], event_info: DispatchEventInfo) -> None:
    for handler in handlers:
        handler(event_info)
    

def _dispatch_builtin_dunder(
    cls: type,
    name: str,
    event: DispatchEvent,
    behaviour: DispatchBehaviour,
    handlers: list[Callable]
) -> Callable:
    original_dunder_mathod = getattr(cls, name, None)

    @wraps(original_dunder_mathod)
    def __dunder_overwrite__(self, *args, **kwargs) -> Any:
        if type(self) is cls or DispatchBehaviour.INCLUDE_INHERITANCE in behaviour:
            # the last stack frame is `__dunder_overwrite__`, so we take who ever
            # called this dunder method, this is the one who triggered it
            trigger_function_name = inspect.stack()[1].function

            # if we can't retrive the function reference from the object
            # then at least give the dispatch event info the name of the function
            function_trigger = getattr(cls, trigger_function_name, trigger_function_name)

            _call_dispatch_handlers(
                handlers,
                DispatchEventInfo(
                    object=self,
                    event=event,
                    function=original_dunder_mathod,
                    function_trigger=function_trigger,
                    args=args,
                    kwargs=kwargs
                )
            )

        if original_dunder_mathod is not None:
            try:
                return original_dunder_mathod(self, *args, **kwargs)
            except Exception as e:
                raise e.__class__(
                    f"{cls.__name__}.{name}(self, {', '.join(map(str, args))}, {', '.join(f'{name}={value}' for name, value in kwargs.items())}): {str(e)}"
                )
    return __dunder_overwrite__


def _dispatch_function(
    func: Callable,
    events: DispatchEvent, 
    behaviour: DispatchBehaviour,
    handlers: Iterable[Callable]
) -> Callable:
    if DispatchEvent.ON_CALL in events:
        @wraps(func)
        def wrapper(*args, **kwargs):
            _call_dispatch_handlers(
                handlers,
                DispatchEventInfo(
                    event=DispatchEvent.ON_CALL,
                    object=None,
                    function=func,
                    function_trigger=func,
                    args=args,
                    kwargs=kwargs)
            )
            return func(*args, **kwargs)
        return wrapper
    return func


def _dispatch_class(
    cls: type,
    events: DispatchEvent, 
    behaviour: DispatchBehaviour,
    handlers: Iterable[Callable]
) -> type:
    builtin_event_dunder = {
        DispatchEvent.ON_CALL: ('__call__',),
        DispatchEvent.FIELD_GET: ('__getattribute__', '__getattr__', '__get__'),
        DispatchEvent.FIELD_SET: ('__setattr__', '__set__',),
    }

    # go over each builtin dunder method
    # that we can use for event dispatcher
    for event, dunder_func_names in builtin_event_dunder.items():
        if event not in events:
            continue

        for func_name in dunder_func_names:
            setattr(cls, func_name, _dispatch_builtin_dunder(
                cls, func_name, (event), (behaviour), handlers
            ))

    if DispatchEvent.ON_METHOD_CALLS in events:
        for member, func in inspect.getmembers(cls, predicate=inspect.isfunction):
            # skip dunder functions
            # we don't want to listen to them, because we use most of them
            if member.startswith('__') and member.endswith('__'):
                continue
            setattr(cls, member, _dispatch_function(
                func=func,
                events=(DispatchEvent.ON_CALL),
                behaviour=behaviour,
                handlers=handlers
            ))
    return cls 


def dispatch(
    events: DispatchEvent,
    behaviour: DispatchBehaviour,
    handlers: Iterable[Callable | str]
) -> None:
    def _(cls_or_func: type | Callable, /) -> type:
        dispatch_handlers = []

        # resolve handlers provided as string
        for handler in handlers:
            if isinstance(handler, str):
                if not hasattr(cls_or_func, handler):
                    raise DispatchHandlerNotFound(cls_or_func, handler)
                handler = getattr(cls_or_func, handler)
            dispatch_handlers.append(handler)

        setattr(cls_or_func, DISPATCH_HANDLERS_ATTR, dispatch_handlers)

        if inspect.isfunction(cls_or_func):
            return _dispatch_function(cls_or_func, events, behaviour, dispatch_handlers)
        return _dispatch_class(cls_or_func, events, behaviour, dispatch_handlers)
    return _

    
    
