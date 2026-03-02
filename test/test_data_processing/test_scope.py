'''
scope_tests.py

tests for the Scope utility class used by the parser
'''

import unittest

from gap_profiler.data_processing.scope import Scope
from gap_profiler.data_types.exceptions import InvalidExitFunction, InvalidEndCallStack


class ScopeTests(unittest.TestCase):
    def setUp(self) -> None:
        self.scope = Scope()

    def tearDown(self) -> None:
        del self.scope

    def test_enter_scope(self):
        '''simple valid case of calling Scope.enter_scope'''
        self.scope.enter_scope(10, 'testfunc', 5, 10)
        self.assertEqual(1, self.scope._function_calls['testfunc'])
        self.assertEqual(5, self.scope.curr_line())
        self.assertEqual('testfunc', self.scope.curr_func())
        self.assertEqual(10, self.scope.curr_file())

    def test_enter_scope_twice(self):
        '''tests calling the same function 2 times in a row'''
        self.scope.enter_scope(10, 'testfunc', 5, 10)
        self.assertEqual(1, self.scope._function_calls['testfunc'])
        self.scope.enter_scope(10, 'testfunc', 5, 10)
        self.assertEqual(2, self.scope._function_calls['testfunc'])

    def test_line_executed_simple(self):
        '''tests that when line executed is called and the line is in scope of the
        current function, the current line is incremented and the time is added
        '''
        self.scope.enter_scope(10, 'testfunc', 5, 10)
        self.assertEqual(5, self.scope.curr_line())
        self.scope.line_executed(6, 2)
        self.assertEqual(6, self.scope.curr_line())
        self.assertEqual('testfunc', self.scope.curr_func())
        self.assertEqual(2, self.scope._scope_stack[-1][Scope.TOTAL_TIME])
        self.assertEqual(2, self.scope._scope_stack[-1][Scope.LINES][1])

    def test_line_zero_executed(self):
        '''tests that when the line number given is 0, the scope assumes it was just
        the next line in the file which was executed
        '''
        self.scope.enter_scope(10, 'testfunc', 5, 10)
        self.assertEqual(5, self.scope.curr_line())
        self.scope.line_executed(0, 2)
        self.assertEqual(6, self.scope.curr_line())
        self.assertEqual('testfunc', self.scope.curr_func())
        self.assertEqual(2, self.scope._scope_stack[-1][Scope.TOTAL_TIME])
        self.assertEqual(2, self.scope._scope_stack[-1][Scope.LINES][1])

    def test_line_executed_bad_args(self):
        '''calls line executed with negative arguments'''
        self.scope.enter_scope(10, 'testfunc', 5, 10)
        self.assertEqual(5, self.scope.curr_line())
        self.assertRaises(ValueError, self.scope.line_executed, -1, 2)
        self.assertRaises(ValueError, self.scope.line_executed, 1, -1)

    def test_unscoped_line_executed(self):
        '''executes an unscoped line to test that the scope behaves as expected'''
        self.scope.line_executed(1, 2)
        self.assertEqual(1, self.scope.curr_line())
        self.assertEqual(Scope.TOP_LEVEL_FUNC, self.scope.curr_func())
        self.assertEqual(2, self.scope._scope_stack[-1][Scope.TOTAL_TIME])
        self.assertEqual(2, self.scope._scope_stack[-1][Scope.LINES][0])

    def test_unscoped_line_zero_executed(self):
        '''executes an unscoped line with line 0 as the line number'''
        self.scope.line_executed(0, 2)
        self.assertEqual(1, self.scope.curr_line())
        self.assertEqual(Scope.TOP_LEVEL_FUNC, self.scope.curr_func())
        self.assertEqual(2, self.scope._scope_stack[-1][Scope.TOTAL_TIME])
        self.assertEqual(2, self.scope._scope_stack[-1][Scope.LINES][0])

    def test_exit_scope_simple(self):
        '''tests base use case of exit_scope'''
        self.scope.line_executed(1, 1)
        self.scope.enter_scope(10, 'testfunc', 5, 10)
        self.assertEqual(5, self.scope.curr_line())
        self.scope.line_executed(6, 2)
        self.assertEqual(6, self.scope.curr_line())
        self.assertEqual('testfunc', self.scope.curr_func())
        self.assertEqual(2, self.scope._scope_stack[-1][Scope.TOTAL_TIME])
        self.assertEqual(2, self.scope._scope_stack[-1][Scope.LINES][1])

        # exits scope and tests that the function call which is returned is valid
        fc = self.scope.exit_scope()
        self.assertEqual(10, fc.file)
        self.assertEqual('testfunc', fc.function)
        self.assertEqual(5, fc.start)
        self.assertEqual(10, fc.end)
        self.assertEqual(2, fc.total_time)
        self.assertEqual(1, fc.called_from)
        self.assertEqual([0, 2, 0, 0, 0, 0], fc.lines)
        self.assertEqual('testfunc-1', fc.function_id)
        self.assertEqual(Scope.TOP_LEVEL_FUNC, fc.caller_id)
    
    def test_exit_scope_top_level(self):
        '''tests illegal exit scope (i.e. when the current function
        is the top level of the script
        '''
        self.assertRaises(InvalidExitFunction, self.scope.exit_scope)

    def test_end_call_stack_simple(self):
        '''tests that the end_call_stack function works properly'''
        self.scope.line_executed(1, 1)
        self.scope.set_curr_file(10) # ordinarily called in the parser
        self.scope.enter_scope(10, 'testfunc', 5, 10)
        self.assertEqual(5, self.scope.curr_line())
        self.scope.line_executed(6, 2)
        self.assertEqual(6, self.scope.curr_line())
        self.assertEqual('testfunc', self.scope.curr_func())
        self.assertEqual(2, self.scope._scope_stack[-1][Scope.TOTAL_TIME])
        self.assertEqual(2, self.scope._scope_stack[-1][Scope.LINES][1])
        self.scope.exit_scope()

        # ends the call stack and tests the characteristics of the unscoped function
        fc = self.scope.end_call_stack()
        self.assertEqual(10, fc.file)
        self.assertEqual(1, fc.start)
        self.assertEqual(1, fc.end)
        self.assertEqual(3, fc.total_time) # 1 tick here 2 from child func
        self.assertEqual(1, sum(fc.lines))
        self.assertEqual([1], fc.lines)
        self.assertEqual(Scope.TOP_LEVEL_FUNC, fc.function)
        self.assertEqual(Scope.TOP_LEVEL_FUNC, fc.function_id)
        self.assertIsNone(fc.called_from)
        self.assertIsNone(fc.caller_id)

    def test_illegal_end_call_stack(self):
        '''calls end_call_stack when not in the top level of the script'''
        self.scope.line_executed(1, 1)
        self.scope.set_curr_file(10) # ordinarily called in the parser
        self.scope.enter_scope(10, 'testfunc', 5, 10)
        self.assertEqual(5, self.scope.curr_line())
        self.scope.line_executed(6, 2)
        self.assertEqual(6, self.scope.curr_line())
        self.assertEqual('testfunc', self.scope.curr_func())
        self.assertEqual(2, self.scope._scope_stack[-1][Scope.TOTAL_TIME])
        self.assertEqual(2, self.scope._scope_stack[-1][Scope.LINES][1])
        self.assertRaises(InvalidEndCallStack, self.scope.end_call_stack)


if __name__=='__main__':
    unittest.main()