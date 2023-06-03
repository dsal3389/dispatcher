# dispatcher
this dispatcher module provide easy to use
events trigger for classes and functions, without creating a proxy class between the caller and the class.

## example 

```py
from dispatch import DispatchEventInfo, DispatchEvent, dispatch


def event_handler(event: DispatchEventInfo) -> None:
    print(event)


@dispatch((
    DispatchEvent.FIELD_GET |
    DispatchEvent.FIELD_SET
), handlers=(event_handler,))
class Person:
    def __init__(self, name: str) -> None:
        self.name = name  # `self.name = name` trigger event DispatchEvent.FIELD_SET

    def say(self, message: str) -> None:
        print(self.name + ":", message)  # self.name trigger event DispatchEvent.FIELD_GET


bob = Person("bob")
bob.say("Hello world")  # bob.say trigger event DispatchEvent.FIELD_GET


# output:
# DispatchEventInfo(event=<DispatchEvent.FIELD_SET: 2>, object=<__main__.Person object at 0x...>, function=<slot wrapper '__setattr__' of 'object' objects>, function_trigger=<function Person.__init__ at 0x...>, args=('name', 'bob'), kwargs={})
# DispatchEventInfo(event=<DispatchEvent.FIELD_GET: 1>, object=<__main__.Person object at 0x...>, function=<slot wrapper '__getattribute__' of 'object' objects>, function_trigger='<module>', args=('say',), kwargs={})
# DispatchEventInfo(event=<DispatchEvent.FIELD_GET: 1>, object=<__main__.Person object at 0x...>, function=<slot wrapper '__getattribute__' of 'object' objects>, function_trigger=<function Person.say at 0x...>, args=('name',), kwargs={})
# bob: Hello world
```


### advance example
```py
from dispatch import (
    DispatchEventInfo, 
    DispatchEvent, 
    DispatchBehaviour, 
    dispatch
)


def person_event_handler(event: DispatchEventInfo) -> None:
    print(event)


@dispatch(
    events=(
        DispatchEvent.FIELD_GET |
        DispatchEvent.FIELD_SET |
        DispatchEvent.ON_METHOD_CALLS
    ), 
    behaviour=(DispatchBehaviour.INCLUDE_INHERITANCE),  # call dispatch even for classes that inherit from current class
    handlers=(person_event_handler,)
)
class Person:
    def __init__(self, name: str, age: int) -> None:
        self.name = name  # `self.name = name` trigger event DispatchEvent.FIELD_SET
        self.age = age  # `self.age = age` trigger event DispatchEvent.FIELD_SET


class Adult(Person):
    def say(self, message: str) -> None:
        print(self.name.upper() + ":", message)  # `self.name`` trigger event DispatchEvent.FIELD_GET


class Kid(Person):
    def say(self, message: str) -> None:
        print(self.name.lower() + ":", message) # `self.name`` trigger event DispatchEvent.FIELD_GET



bob = Adult("bob", 23)
boby = Kid("boby", 6)

bob.say("Hello " + boby.name)  # `bob.say`` trigger event DispatchEvent.FIELD_GET, and `bob.say(...)` trigger DispatchEvent.ON_METHOD_CALLS
boby.say("Hey " + bob.name)  # `boby.say`` trigger event DispatchEvent.FIELD_GET, and `boby.say(...)` trigger DispatchEvent.ON_METHOD_CALLS

# output 
# qDispatchEventInfo(event=<DispatchEvent.FIELD_SET: 2>, object=<__main__.Adult object at 0x7f7a6450ca10>, function=<slot wrapper '__setattr__' of 'object' objects>, function_trigger=<function Person.__init__ at 0x7f7a64506d40>, args=('name', 'bob'), kwargs={})
# DispatchEventInfo(event=<DispatchEvent.FIELD_SET: 2>, object=<__main__.Adult object at 0x7f7a6450ca10>, function=<slot wrapper '__setattr__' of 'object' objects>, function_trigger=<function Person.__init__ at 0x7f7a64506d40>, args=('age', 23), kwargs={})
# DispatchEventInfo(event=<DispatchEvent.FIELD_SET: 2>, object=<__main__.Kid object at 0x7f7a6450df10>, function=<slot wrapper '__setattr__' of 'object' objects>, function_trigger=<function Person.__init__ at 0x7f7a64506d40>, args=('name', 'boby'), kwargs={})
# DispatchEventInfo(event=<DispatchEvent.FIELD_SET: 2>, object=<__main__.Kid object at 0x7f7a6450df10>, function=<slot wrapper '__setattr__' of 'object' objects>, function_trigger=<function Person.__init__ at 0x7f7a64506d40>, args=('age', 6), kwargs={})
# DispatchEventInfo(event=<DispatchEvent.FIELD_GET: 1>, object=<__main__.Adult object at 0x7f7a6450ca10>, function=<slot wrapper '__getattribute__' of 'object' objects>, function_trigger='<module>', args=('say',), kwargs={})
# DispatchEventInfo(event=<DispatchEvent.FIELD_GET: 1>, object=<__main__.Kid object at 0x7f7a6450df10>, function=<slot wrapper '__getattribute__' of 'object' objects>, function_trigger='<module>', args=('name',), kwargs={})
# DispatchEventInfo(event=<DispatchEvent.FIELD_GET: 1>, object=<__main__.Adult object at 0x7f7a6450ca10>, function=<slot wrapper '__getattribute__' of 'object' objects>, function_trigger='say', args=('name',), kwargs={})
# BOB: Hello boby
# DispatchEventInfo(event=<DispatchEvent.FIELD_GET: 1>, object=<__main__.Kid object at 0x7f7a6450df10>, function=<slot wrapper '__getattribute__' of 'object' objects>, function_trigger='<module>', args=('say',), kwargs={})
# DispatchEventInfo(event=<DispatchEvent.FIELD_GET: 1>, object=<__main__.Adult object at 0x7f7a6450ca10>, function=<slot wrapper '__getattribute__' of 'object' objects>, function_trigger='<module>', args=('name',), kwargs={})
# DispatchEventInfo(event=<DispatchEvent.FIELD_GET: 1>, object=<__main__.Kid object at 0x7f7a6450df10>, function=<slot wrapper '__getattribute__' of 'object' objects>, function_trigger='say', args=('name',), kwargs={})
# boby: Hey bob
```
