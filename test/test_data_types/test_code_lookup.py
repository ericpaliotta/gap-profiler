'''
code_lookup_tests.py

this file contains unit tests for the CodeLookup class
'''

import unittest

from gap_profiler.data_types.code_lookup import CodeLookup
from gap_profiler.data_processing.scope import FunctionCall, Scope


class CodeLookupTests(unittest.TestCase):
    def setUp(self) -> None:
        self.code_lookup = CodeLookup()

    def tearDown(self) -> None:
        del self.code_lookup

    def test_add_file(self):
        '''tests adding a simple, valid file to the code lookup'''
        self.code_lookup.add_file(10, '/some/madeup/file.g')
        self.assertIn(10, self.code_lookup._files.keys())
        self.assertEqual(1, len(self.code_lookup._files))
        self.assertIn('/some/madeup/file.g', self.code_lookup._files.values())
    
    def test_add_func(self):
        '''tests adding a simple, valid function to the code lookup'''
        fc = FunctionCall(10, 'testfunc', 5, 10, 12, [2,2,2,2,2,2],
            called_from=10, call_num=1, caller=Scope.TOP_LEVEL_FUNC)
        self.code_lookup.add_file(10, '/some/madeup/file.g')
        self.assertIn(10, self.code_lookup._files.keys())
        self.code_lookup.add_function(fc)
        self.assertIn((fc.file, fc.start, fc.end), self.code_lookup._functions.values())

    def test_add_func_twice(self):
        '''tests adding a simple, valid function to the code lookup twice does not create a new entity'''
        fc1 = FunctionCall(10, 'testfunc', 5, 10, 12, [2,2,2,2,2,2],
            called_from=10, call_num=1, caller=Scope.TOP_LEVEL_FUNC)
        fc2 = FunctionCall(10, 'testfunc', 5, 10, 6, [1,1,1,1,1,1],
            called_from=10, call_num=1, caller=Scope.TOP_LEVEL_FUNC)
        self.code_lookup.add_file(10, '/some/madeup/file.g')
        self.assertIn(10, self.code_lookup._files.keys())
        self.code_lookup.add_function(fc1)
        self.code_lookup.add_function(fc2)
        
        # tests that the second function has not altered the data structure
        key = self.code_lookup._gen_func_id('testfunc', 10)
        self.assertIn(key, self.code_lookup._functions.keys())
        self.assertEqual(1, len(self.code_lookup._functions.keys()))

    def test_add_func_nonexistant_file(self):
        '''adds a function without the file being added first'''
        fc = FunctionCall(10, 'testfunc', 5, 10, 12, [2,2,2,2,2,2],
            called_from=10, call_num=1, caller=Scope.TOP_LEVEL_FUNC)
        self.assertRaises(ValueError,
            self.code_lookup.add_function, fc)

    def test_add_func_duplicate_name(self):
        '''tests that adding a 2 functions with the same name in different files creates distinct entities'''
        fc1 = FunctionCall(10, 'testfunc', 5, 10, 12, [2,2,2,2,2,2],
            called_from=10, call_num=1, caller=Scope.TOP_LEVEL_FUNC)
        fc2 = FunctionCall(11, 'testfunc', 5, 10, 12, [2,2,2,2,2,2],
            called_from=10, call_num=1, caller=Scope.TOP_LEVEL_FUNC)
        self.code_lookup.add_file(10, '/some/madeup/file1.g')
        self.code_lookup.add_file(11, '/some/madeup/file2.g')
        self.assertIn(10, self.code_lookup._files.keys())
        self.assertIn(11, self.code_lookup._files.keys())
        self.code_lookup.add_function(fc1)
        self.code_lookup.add_function(fc2)

        # tests the functions have been added properly
        key1 = self.code_lookup._gen_func_id('testfunc', 10)
        key2 = self.code_lookup._gen_func_id('testfunc', 11)
        self.assertIn(key1, self.code_lookup._functions.keys())
        self.assertIn(key2, self.code_lookup._functions.keys())
        self.assertEqual(2, len(self.code_lookup._functions.keys()))

    def test_file_search_regex(self):
        '''tests that regex searching of files works as intended'''
        exp = 'filename'
        self.assertEqual(0, len(self.code_lookup.search_files_regex(exp)))
        self.code_lookup.add_file(10, '/filename.g')
        self.code_lookup.add_file(11, '/filename/testfile.g')
        self.code_lookup.add_file(12, '/nomatch.g')
        self.code_lookup.add_file(13, '/nomatch/file_name/test.g')
        
        matches = self.code_lookup.search_files_regex(exp)
        self.assertEqual(2, len(matches))
        self.assertIn(10, matches)
        self.assertIn(11, matches)

    def test_get_filesystem(self):
        '''tests a valid case for returning the tree representation of the code lookup's filesystem'''
        self.code_lookup.add_file(1, '/root/file1.g')
        self.code_lookup.add_file(2, '/root/file2.g')
        self.code_lookup.add_file(3, '/root/dir1/file1.g')
        self.code_lookup.add_file(4, '/root/dir1/file2.g')
        self.code_lookup.add_file(5, '/root/dir2/file1.g')
        self.code_lookup.add_file(6, '/root/dir2/file2.g')

        filesystem = self.code_lookup.get_filesystem()
        self.assertEqual(2, len(filesystem['root']['files']))
        self.assertEqual(2, len(filesystem['root']['dir1']['files']))
        self.assertEqual(2, len(filesystem['root']['dir2']['files']))
        self.assertIn((1, 'file1.g'), filesystem['root']['files'])
        self.assertIn((2, 'file2.g'), filesystem['root']['files'])
        self.assertIn((3, 'file1.g'), filesystem['root']['dir1']['files'])
        self.assertIn((4, 'file2.g'), filesystem['root']['dir1']['files'])
        self.assertIn((5, 'file1.g'), filesystem['root']['dir2']['files'])
        self.assertIn((6, 'file2.g'), filesystem['root']['dir2']['files'])


if __name__=='__main__':
    unittest.main()
