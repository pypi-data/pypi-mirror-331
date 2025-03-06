# coding: utf-8
from typing import Union, Type, TypeVar

ViewT = TypeVar('ViewT', bound=object)
ControllerT = TypeVar('ControllerT', bound=object)

def create_mvc_instance(
    class_name: str,
    view: Type[ViewT],
    controller: Type[ControllerT],
    *args, **kwargs
) -> Union[ViewT, ControllerT]: 
    def __init__(self, *args, **kwargs):
        view.__init__(self)
        controller.__init__(self, self, *args, **kwargs)
    
    bases = (view, controller)
    DynamicClass = type(class_name, bases, {'__init__': __init__})
    return DynamicClass(*args, **kwargs)