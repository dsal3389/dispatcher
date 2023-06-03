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
```

### run example
```
DispatchEventInfo(event=<DispatchEvent.FIELD_SET: 2>, object=<__main__.Person object at 0x...>, function=<slot wrapper '__setattr__' of 'object' objects>, function_trigger=<function Person.__init__ at 0x...>, args=('name', 'bob'), kwargs={})
DispatchEventInfo(event=<DispatchEvent.FIELD_GET: 1>, object=<__main__.Person object at 0x...>, function=<slot wrapper '__getattribute__' of 'object' objects>, function_trigger='<module>', args=('say',), kwargs={})
DispatchEventInfo(event=<DispatchEvent.FIELD_GET: 1>, object=<__main__.Person object at 0x...>, function=<slot wrapper '__getattribute__' of 'object' objects>, function_trigger=<function Person.say at 0x...>, args=('name',), kwargs={})
bob: Hello world
```
