'''
scope.py

this file contains the definition of a data type to contain information about a given
scope (i.e. a function or similar)
'''

from gap_profiler.data_types.exceptions import InvalidExitFunction, InvalidEndCallStack, InvalidTopLevelFunction


class FunctionCall:
    '''class representing a fully realized function call
    
    utility class for cleaning up what is returned when a given scope is exited
    
    Attributes:
        file (int) : the unique file id
        function (str) : the name of the function
        start (int) : start line of the function in the given file
        end (int) : the end line of the function in the given file
        total_time (int) : the total time taken by the function including those called
        called_from (int) : line the function is called from
        lines (list) : a list of how long each line takes in the function call
        function_id (str) : the unique function name and call number used as a key in the call graph
        caller_id (str) : the unique function name and call number used as a key in the call graph
    '''
    def __init__(self, file_id: int, function: str, start: int, end: int, total_time: int, lines: list,
        called_from: int=None, call_num: int=None, caller: str=None, caller_num: int=None):
        self.file = file_id
        self.function = function
        self.start = start
        self.end = end
        self.total_time = total_time
        self.called_from = called_from
        self.lines = lines

        # formats unique function id (if unscoped always just called "unscoped")
        self.function_id = function
        if function != Scope.TOP_LEVEL_FUNC:
            self.function_id = f'{self.function_id}-{call_num}'
        elif function == Scope.TOP_LEVEL_FUNC and \
            (caller or called_from or call_num or caller_num):
            raise InvalidTopLevelFunction(Scope.TOP_LEVEL_FUNC)

        # formats unique caller id
        self.caller_id = caller
        if caller is None:
            self.caller_id = None
        elif caller != Scope.TOP_LEVEL_FUNC:
            self.caller_id = f'{self.caller_id}-{caller_num}'

class Scope:
    '''data type to contain information about the call stack
    
    Attributes:
        _function_calls (dict) : a dictionary storing how many times a function has been called
            for unique identification of each function call
        _scope_stack (list) : a 2-D list which stores rows of data for each function call (indices
            of each row stored in class attributes below)
    '''
    # stand-in name for the lines run outside of any function
    TOP_LEVEL_FUNC = 'unscoped'

    # index constants for array of values
    FILE = 0
    FUNCTION = 1
    START_LINE = 2
    END_LINE = 3
    CURR_LINE = 4
    LINES = 5
    CALL_NUM = 6
    TOTAL_TIME = 7 # time the function takes to run including children runtime

    def __init__(self):
        self._function_calls = {} # dict mapping each function to the number of times it has been called thus far
        self._scope_stack = [] # list to contain the call stack
        self._scope_stack.append([-1, Scope.TOP_LEVEL_FUNC, -1, -1, 0, [], 0, 0]) # initializes bottom of stack

    def enter_scope(self, file_id: int, function: str, start_line: int, end_line: int) -> None:
        '''appends a new entry to the call stack

        Args:
            file_id (int) : id of the new file where the called function is
            function (str) : name of the called function
            start_line (int) : the line the function starts on
            end_line (int) : the end line of the function
        '''
        self._function_calls[function] = self._function_calls.get(function, 0) + 1
        self._scope_stack.append([file_id, function, start_line, end_line,
            start_line, [0]*(1 + end_line - start_line), self._function_calls[function], 0])

    def line_executed(self, line_num: int, time: int) -> None:
        '''called on each line of the profile

        Args:
            line_num (int) : the line which is being executed
            time (int) : the time which the line took

        Raises:
            ValueError: if the line number or time given is < 0
        '''
        # error cases
        if line_num < 0:
            raise ValueError('line number cannot be < 0')
        elif time < 0:
            raise ValueError('execution time for a line cannot be < 0')
        # for unscoped lines
        if self._scope_stack[-1][Scope.FUNCTION] == Scope.TOP_LEVEL_FUNC:
            # if this is the first unscoped line executed
            if self._scope_stack[-1][Scope.START_LINE] == -1:
                self._scope_stack[-1][Scope.START_LINE] = line_num
            # if the line number executed is 0, assume the next line is being executed
            if line_num == 0:
                line_num = self._scope_stack[-1][Scope.CURR_LINE] + 1
            # adds 0 times for lines which were skipped
            for _ in range(line_num - self._scope_stack[-1][Scope.CURR_LINE] - 1):
                self._scope_stack[-1][Scope.LINES].append(0)
            self._scope_stack[-1][Scope.LINES].append(time)
            self._scope_stack[-1][Scope.CURR_LINE] = line_num 

        # if line number is 0, the profiler does not know what line this was -> assume it is the current line + 1
        elif line_num == 0:
            self._scope_stack[-1][Scope.LINES][self._scope_stack[-1][Scope.CURR_LINE] + 1 
                - self._scope_stack[-1][Scope.START_LINE]] += time
            self._scope_stack[-1][Scope.CURR_LINE] += 1

        # if we are in a function
        else:
            self._scope_stack[-1][Scope.LINES][line_num - self._scope_stack[-1][Scope.START_LINE]] += time
            self._scope_stack[-1][Scope.CURR_LINE] = line_num 
        self._scope_stack[-1][Scope.TOTAL_TIME] += time # adds the time of this line to the total

    def exit_scope(self) -> FunctionCall:
        '''called when a given function is exited

        Returns:
            (FunctionCall) : an instance of the function call data type

        Raises:
            InvalidExitFunction: if this method is called from the top of a call stack
                (i.e. unscoped lines in the script)
        '''
        if self.curr_func() == Scope.TOP_LEVEL_FUNC:
            raise InvalidExitFunction()
        entry = self._scope_stack.pop()
        self._scope_stack[-1][Scope.TOTAL_TIME] += entry[Scope.TOTAL_TIME]

        return FunctionCall(entry[Scope.FILE], entry[Scope.FUNCTION],
            entry[Scope.START_LINE], entry[Scope.END_LINE], entry[Scope.TOTAL_TIME],
            entry[Scope.LINES], self._scope_stack[-1][Scope.CURR_LINE],
            entry[Scope.CALL_NUM], self._scope_stack[-1][Scope.FUNCTION],
            self._scope_stack[-1][Scope.CALL_NUM])

    def end_call_stack(self) -> FunctionCall:
        '''called when the parse is finished to return data on the unscoped lines
        
        Returns
            (FunctionCall) : an instance of the function call data type

        Raises:
            InvalidEndCallStack: if this method is called while inside a function
        '''
        if self.curr_func() != Scope.TOP_LEVEL_FUNC:
            raise InvalidEndCallStack()
        entry = self._scope_stack.pop()

        return FunctionCall(entry[Scope.FILE], entry[Scope.FUNCTION],
            entry[Scope.START_LINE], entry[Scope.CURR_LINE],
            entry[Scope.TOTAL_TIME] , entry[Scope.LINES])

    def in_scope(self, line: int) -> bool:
        '''returns true if the given line number is contained in the current scope

        Args:
            line (int) : the line number in question

        Returns:
            (bool) : indicating if the line number is in range
        '''
        if (line >= self._scope_stack[-1][Scope.START_LINE]
            and line <= self._scope_stack[-1][Scope.END_LINE]):
            return True
        # if unscoped we cannot say for sure if the line is in scope so return True
        elif (self.curr_func() == Scope.TOP_LEVEL_FUNC):
            return True
        else:
            return False

    def curr_line(self) -> str:
        '''accessor to return the line of the current function which is being executed'''
        return self._scope_stack[-1][Scope.CURR_LINE]

    def curr_func(self) -> str:
        '''accessor to return the name of the current function as a string'''
        return self._scope_stack[-1][Scope.FUNCTION]

    def curr_file(self) -> int:
        '''accessor to return the id of the current file'''
        return self._scope_stack[-1][Scope.FILE]

    def set_curr_file(self, file: int) -> None:
        '''sets the id of the current scope's file. Should only be called for cases wherein the file
        id of the current function is not set yet (i.e. running unscoped lines in a script)
        '''
        self._scope_stack[-1][Scope.FILE] = file
