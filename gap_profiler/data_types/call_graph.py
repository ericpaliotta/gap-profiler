'''
call_graph.py

this file contains a data structure to store the call graph
'''

import json
from zipfile import ZipFile

from gap_profiler.data_processing.scope import FunctionCall, Scope

class CallGraph:
    '''this class stores a graph representation of which functions call one another (i.e. a call tree)

    Attributes:
        total_time (int) : total time taken by the program
        time_type (str) : the type of time as a string given in the parser.TimeType class
        _nodes (dict) : a dictionary of the node id's mapped to the metadata of each node
        _edges (list) : a list of lists of the form [caller, callee, line called from in caller]
            where the types are [str, str, int]
    '''
    FILE_NAME = 'call_graph.json' # name of the file as stored in any generated zip file for a profile
    TIME_TYPE_KEY = 'time_type' # the units of time recorded for each line (i.e. ticks or wall time)
    NODES_KEY = 'nodes'
    EDGES_KEY = 'edges'
    RUNTIME_KEY = 'total_runtime' # total runtime for the whole profile
    TOP_LEVEL_FUNC = 'unscoped' # name of the top level node (i.e. not in a function) in the call graph

    # -- keys for the nodes dict --
    FUNCTION_TIME_KEY = 'function_time' # total time taken by the function EXCLUDING child calls
    TOTAL_TIME_KEY = 'total_time' # total time taken by the function INCLUDING child calls
    LINES_KEY = 'lines'
    FUNCTION_KEY = 'function'
    FILE_ID_KEY = 'file_id'
    CHILDREN_KEY = 'children' # only for pooled node dict

    def __init__(self, path: str=None):
        '''
        Args:
            path (str) : a path to the zip file containing the profiling output from the parser
        '''
        # if a path is passed into the function, reload from the zip archive
        if path:
            with ZipFile(path, 'r') as zip:
                content = json.loads(zip.read(CallGraph.FILE_NAME))
            self.total_time = content[CallGraph.RUNTIME_KEY]
            self.time_type = content[CallGraph.TIME_TYPE_KEY]
            self._nodes = content[CallGraph.NODES_KEY]
            self._edges = content[CallGraph.EDGES_KEY]
        else:
            self.total_time = 0
            self.time_type = None
            self._nodes = {
                Scope.TOP_LEVEL_FUNC: 
                    {
                        CallGraph.TOTAL_TIME_KEY: 0,
                        CallGraph.FUNCTION_TIME_KEY: 0,
                        CallGraph.LINES_KEY: [],
                        CallGraph.FUNCTION_KEY: Scope.TOP_LEVEL_FUNC,
                    }
                }
            self._edges = []

    def add_node(self, fc: FunctionCall) -> None:
        '''adds a specific function call to the graph with an edge to connect it to the caller

        Args:
            fc (FunctionCall) : a FunctionCall object storing information about the node to be added
        '''
        self.total_time += sum(fc.lines)
        self._nodes[fc.function_id] = { 
            CallGraph.LINES_KEY: fc.lines,
            CallGraph.FUNCTION_KEY: fc.function,
            CallGraph.FUNCTION_TIME_KEY: sum(fc.lines),
            CallGraph.TOTAL_TIME_KEY: fc.total_time,
            CallGraph.FILE_ID_KEY: fc.file
        }
        # if there was a caller function, create an edge
        if fc.caller_id:
            self._edges.append([fc.caller_id, fc.function_id, fc.called_from])

    def get_graph(self, include_pool: bool=False) -> tuple:
        '''returns node and edge dicts in form (node dict, edge list)
        
        Args:
            include_pool (bool) : whether to include node objects which are a pooled representation
                of all calls of each function across the run of the program (i.e. if a function is called
                twice, each with 1ms total time, the pooled node has 2ms total time). Default is False

        Returns:
            tuple: a tuple of the form (node dict, edge list, pooled_nodes dict) where the pooled nodes
                are only included if include_pool=True
        '''
        if include_pool:
            pooled_nodes = {}
            for k, v in self._nodes.items():
                key = f'{v[CallGraph.FUNCTION_KEY]}-{v[CallGraph.FILE_ID_KEY]}'
                if pooled_nodes.get(key, None) is None:
                    pooled_nodes[key] = {
                        CallGraph.FUNCTION_KEY: v[CallGraph.FUNCTION_KEY],
                        CallGraph.FUNCTION_TIME_KEY: v[CallGraph.FUNCTION_TIME_KEY],
                        CallGraph.TOTAL_TIME_KEY: v[CallGraph.FUNCTION_TIME_KEY],
                        CallGraph.FILE_ID_KEY: v[CallGraph.FILE_ID_KEY],
                        CallGraph.CHILDREN_KEY: [k]
                    }
                else:
                    pooled_nodes[key][CallGraph.FUNCTION_TIME_KEY] += v[CallGraph.FUNCTION_TIME_KEY]
                    pooled_nodes[key][CallGraph.TOTAL_TIME_KEY] += v[CallGraph.FUNCTION_TIME_KEY]
                    pooled_nodes[key][CallGraph.CHILDREN_KEY].append(k)
            return (self._nodes, self._edges, pooled_nodes)
        return (self._nodes, self._edges)

    def get_json(self) -> str:
        '''returns call graph formatted as a Json string
        
        Returns:
            str: a Json string of the CallGraph
        '''
        return json.dumps({
            CallGraph.RUNTIME_KEY: self.total_time,
            CallGraph.TIME_TYPE_KEY: self.time_type,
            CallGraph.NODES_KEY: self._nodes,
            CallGraph.EDGES_KEY: self._edges},
            indent=4)
