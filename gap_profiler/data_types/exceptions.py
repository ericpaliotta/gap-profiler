'''
exceptions.py

this file contains all custom exception types for the profiler
'''

# from gap_profiler.data_processing.scope import Scop

# -- parser specific exceptions -- 
class IllegalProfiletype(Exception):
    def __init__(self, type: str):
        super().__init__(f'Profile type: {type} is not supported')

class UnrecognizedTimeType(Exception):
    def __init__(self, type: str):
        super().__init__(f'Time type: {type} is not supported')

class UnrecognizedLineType(Exception): 
    def __init__(self, line_type: str, line: str):
        super().__init__(f'type: {line_type} is not recognized for line: {line}')

# -- scope specific exceptions --
class InvalidExitFunction(Exception):
    def __init__(self):
        super().__init__('cannot exit top level scope')

class InvalidEndCallStack(Exception):
    def __init__(self):
        super().__init__('there are still functions on the call stack which need to be exited')

# -- data type exceptions --
class InvalidTopLevelFunction(Exception):
    def __init__(self, func_name: str):
        super().__init__(f'{func_name} cannot be called, and hence cannot have a caller in call graph\
            if a user-defined function is called {func_name} consider changing the value of this field in Scope')

# -- widget exceptions --
class UnrecognizedWidgetType(Exception):
    def __init__(self):
        super().__init__('unrecognized widget type passed to item delegate')

class UnrecognizedItemOrder(Exception):
    def __init__(self, order: str):
        super().__init__(f'unrecognized order type "{order}"". Order must be a valid attribute of the OrderBy class')
