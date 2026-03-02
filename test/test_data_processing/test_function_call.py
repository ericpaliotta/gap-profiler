'''
function_call_tests.py

This file contains unit tests for the FunctionCall class. This class
is essentially a data type so the tests should be short
'''

import unittest

from gap_profiler.data_types.exceptions import InvalidTopLevelFunction
from gap_profiler.data_processing.scope import FunctionCall, Scope


class FunctionCallTests(unittest.TestCase):
    def test_top_level_func_call(self):
        '''simple functioning top level function call instantiation'''
        FunctionCall(10, Scope.TOP_LEVEL_FUNC, 1, 3, 3, [1,1,1])

    def test_invalid_top_level_func_call(self):
        '''tests that top level lines of code cannot be called (i.e. Scope.TOP_LEVEL_FUNC
        is a reserved function name)
        '''
        self.assertRaises(InvalidTopLevelFunction, FunctionCall,
            10, Scope.TOP_LEVEL_FUNC, 1, 3, 3, [1,1,1], called_from=4)
        self.assertRaises(InvalidTopLevelFunction, FunctionCall,
            10, Scope.TOP_LEVEL_FUNC, 1, 3, 3, [1,1,1], call_num=4)
        self.assertRaises(InvalidTopLevelFunction, FunctionCall,
            10, Scope.TOP_LEVEL_FUNC, 1, 3, 3, [1,1,1], caller='func')
        self.assertRaises(InvalidTopLevelFunction, FunctionCall,
            10, Scope.TOP_LEVEL_FUNC, 1, 3, 3, [1,1,1], caller_num=4)


if __name__=='__main__':
    unittest.main()