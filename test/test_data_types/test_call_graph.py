'''
call_graph_tests.py

Tests for the data_types/call_graph.py data structure
'''

import unittest

from gap_profiler.data_types.call_graph import CallGraph
from gap_profiler.data_processing.scope import FunctionCall, Scope

class CallGraphTests(unittest.TestCase):
    '''
    tests for the CallGraph data structure
    '''
    def setUp(self) -> None:
        self.call_graph = CallGraph()

    def tearDown(self) -> None:
        del self.call_graph

    def test_add_node_simple(self):
        '''tests adding a simple valid node to the call graph and linking
        it with the top level function
        '''
        fc = FunctionCall(12, 'testfunc', 5, 10, 12, [2,2,2,2,2,2],
            called_from=10, call_num=1, caller=Scope.TOP_LEVEL_FUNC)
        unscoped = FunctionCall(12, Scope.TOP_LEVEL_FUNC, 1, 3, 3, [1, 1, 1])
        self.call_graph.add_node(fc)
        self.call_graph.add_node(unscoped)

        # tests to make sure the call graph is in the correct form
        self.assertEqual(1, len(self.call_graph._edges))
        self.assertEqual(2, len(self.call_graph._nodes))
        self.assertIn('testfunc-1', self.call_graph._nodes.keys())
        self.assertIn(Scope.TOP_LEVEL_FUNC, self.call_graph._nodes.keys())
        self.assertEqual(self.call_graph._edges[0], [Scope.TOP_LEVEL_FUNC, 'testfunc-1', 10])

    def test_get_graph_no_pool(self):
        '''tests getting the graph from the call graph class without the pooled nodes'''
        fc = FunctionCall(12, 'testfunc', 5, 10, 12, [2,2,2,2,2,2],
            called_from=10, call_num=1, caller=Scope.TOP_LEVEL_FUNC)
        unscoped = FunctionCall(12, Scope.TOP_LEVEL_FUNC, 1, 3, 3, [1, 1, 1])
        self.call_graph.add_node(fc)
        self.call_graph.add_node(unscoped)

        # gets the call graph and tests that it is in the correct form
        nodes, edges = self.call_graph.get_graph(include_pool=False)
        self.assertEqual(1, len(edges))
        self.assertEqual(2, len(nodes))
        self.assertIn('testfunc-1', nodes.keys())
        self.assertIn(Scope.TOP_LEVEL_FUNC, nodes.keys())
        self.assertEqual(edges[0], [Scope.TOP_LEVEL_FUNC, 'testfunc-1', 10])

    def test_get_graph_include_pool(self):
        '''tests getting the graph from the call graph class with the pooled nodes'''
        fc_call_time = 12
        fc1 = FunctionCall(12, 'testfunc', 5, 10, 12, [2,2,2,2,2,2],
            called_from=10, call_num=1, caller=Scope.TOP_LEVEL_FUNC)
        fc2 = FunctionCall(12, 'testfunc', 5, 10, 12, [2,2,2,2,2,2],
            called_from=10, call_num=2, caller=Scope.TOP_LEVEL_FUNC)
        unscoped = FunctionCall(12, Scope.TOP_LEVEL_FUNC, 1, 3, 3, [1, 1, 1])
        self.call_graph.add_node(fc1)
        self.call_graph.add_node(fc2)
        self.call_graph.add_node(unscoped)

        # gets the call graph and tests that it is in the correct form
        nodes, edges, pooled = self.call_graph.get_graph(include_pool=True)
        self.assertEqual(2, len(edges))
        self.assertEqual(3, len(nodes))
        self.assertEqual(2, len(pooled))
        self.assertIn('testfunc-1', nodes.keys())
        self.assertIn('testfunc-2', nodes.keys())
        self.assertIn(Scope.TOP_LEVEL_FUNC, nodes.keys())
        # tests pooled nodes
        pooled_key = f'{fc1.function}-{fc1.file}'
        self.assertEqual(2*fc_call_time, pooled[pooled_key][CallGraph.TOTAL_TIME_KEY])
        self.assertIn('testfunc-1', pooled[pooled_key][CallGraph.CHILDREN_KEY])
        self.assertIn('testfunc-2', pooled[pooled_key][CallGraph.CHILDREN_KEY])

    def test_get_graph_pool_duplicate_funcname(self):
        '''tests getting the graph from the call graph class with the pooled nodes
        if there are duplicate function names in different files in the graph
        '''
        fc1 = FunctionCall(11, 'testfunc', 5, 10, 12, [2,2,2,2,2,2],
            called_from=10, call_num=1, caller=Scope.TOP_LEVEL_FUNC)
        fc2 = FunctionCall(12, 'testfunc', 5, 10, 12, [2,2,2,2,2,2],
            called_from=10, call_num=2, caller=Scope.TOP_LEVEL_FUNC)
        unscoped = FunctionCall(12, Scope.TOP_LEVEL_FUNC, 1, 3, 3, [1, 1, 1])
        self.call_graph.add_node(fc1)
        self.call_graph.add_node(fc2)
        self.call_graph.add_node(unscoped)

        # gets the call graph and tests that it is in the correct form
        nodes, edges, pooled = self.call_graph.get_graph(include_pool=True)
        self.assertEqual(2, len(edges))
        self.assertEqual(3, len(nodes))
        self.assertEqual(3, len(pooled))
        self.assertIn('testfunc-1', nodes.keys())
        self.assertIn('testfunc-2', nodes.keys())
        self.assertIn(Scope.TOP_LEVEL_FUNC, nodes.keys())
        # tests pooled nodes
        pooled_key_1 = f'{fc1.function}-{fc1.file}'
        pooled_key_2 = f'{fc2.function}-{fc2.file}'
        self.assertNotEqual(pooled_key_1, pooled_key_2)
        self.assertIn('testfunc-1', pooled[pooled_key_1][CallGraph.CHILDREN_KEY])
        self.assertNotIn('testfunc-2', pooled[pooled_key_1][CallGraph.CHILDREN_KEY])
        self.assertNotIn('testfunc-1', pooled[pooled_key_2][CallGraph.CHILDREN_KEY])
        self.assertIn('testfunc-2', pooled[pooled_key_2][CallGraph.CHILDREN_KEY])


if __name__=='__main__':
    unittest.main()