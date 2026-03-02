'''
parser.py

this file is a parser which turns raw profiling data into a useful format
'''

import sys
import json
import gzip
import os.path
from zipfile import ZipFile

from gap_profiler.data_processing.scope import Scope
from gap_profiler.data_types.code_lookup import CodeLookup
from gap_profiler.data_types.call_graph import CallGraph
from gap_profiler.data_types.exceptions import UnrecognizedLineType, UnrecognizedTimeType

class TimeType:
    '''enum for profile configuration time types'''
    WALL_TIME = 'WallTime' # time as measured in fractional seconds
    CPU_TIME = 'CPUTime' # time as measured in fractional seconds
    MEMORY = 'Memory' # for recording memory usage of each line. not a type of time obviously

class Parser:
    '''parses raw profile data into a visualizable format

    Attributes:
        scope (Scope) : a Scope instance which stores the current state of the parse
        code_lookup (CodeLookup) : a custom data type to store basic information about
            functions and files
        call_graph (CallGraph) : a data structure containing all of the information to render
            a graph of each function call
    '''
    # line types
    EXECUTE = 'E'
    READ = 'R'
    NEW_FILE = 'S'
    ENTER_FUNC = 'I'
    EXIT_FUNC = 'O'

    # profile configuration fields
    IS_COVER = 'IsCover' # TEMP: coverage is not yet supported
    TIME_TYPE = 'TimeType'

    # constants for profiler field names
    TYPE = 'Type'
    FILE = 'File'
    FILE_ID = 'FileId'
    FUNCTION = 'Fun'
    TIME = 'Ticks'
    CURRLINE = 'Line'
    ENDLINE = 'EndLine'

    def __init__(self):
        self.scope = None
        self.code_lookup = None
        self.call_graph = None

    def generate_profile(self, output_path: str, data_path: str, project_root: str=None) -> bool:
        '''generates the profile zip archive which can be visualized
        only externally callable function, contains all of the parsing logic

        Args:
            output_path (str) : the file output file name specified as a path
            data_path (str) : a path to the profile data Json file 
            project_root (str) : a path to the root of the project being profiled if not specified,
                the paths in the profiler data are used
        
        Returns:
            bool: indicates whether the operation succeeded

        Raises:
            UnrecognizedTimeType: if the configuration line gives a time type which is not supported
            UnrecognizedTimeType: if the line has a value in "Type" which is not supported. Supported
                line types are: _, R, E, I, O, S (all class attributes of this class)
        '''
        # resets attributes
        self.scope = Scope()
        self.code_lookup = CodeLookup()
        self.call_graph = CallGraph()

        if project_root:
            self.code_lookup.set_project_root(project_root)
        
        # opens the profile file and begins parsing
        if os.path.splitext(data_path)[-1] == '.gz':
            file = gzip.open(data_path, mode='rt', encoding='utf8')
        else:
            file = open(data_path, 'r')

        # configures the parse
        config = json.loads(file.readline())
        time_type = config.get(Parser.TIME_TYPE)
        if time_type == TimeType.WALL_TIME or time_type == TimeType.CPU_TIME or time_type == TimeType.MEMORY:
            self.call_graph.time_type = time_type
        else:
            raise UnrecognizedTimeType(time_type)

        # parses each line of the profile into the data structure
        for line in file:
            line_dict = json.loads(line)
            line_type = line_dict[Parser.TYPE]
            if line_type == Parser.NEW_FILE:
                self._process_register_file(line_dict)
            elif line_type == Parser.ENTER_FUNC:
                self._process_enter_func(line_dict)
            elif line_type == Parser.EXIT_FUNC:
                self._process_exit_func(line_dict)
            elif line_type == Parser.EXECUTE:
                self._process_execution(line_dict)
            elif line_type == Parser.READ:
                self._process_read(line_dict)
            else:
                raise UnrecognizedLineType(line_type, line)

        # if we do not end in the unscoped state, the the call stack might not have been explicitly exited
        # hence the call stack is popped and added to the call graph
        while self.scope.curr_func() != Scope.TOP_LEVEL_FUNC:
            curr_scope = self.scope.exit_scope()
            self.call_graph.add_node(curr_scope)
            self.code_lookup.add_function(curr_scope)
 
        # adds the unscoped data to all data structures (i.e. data about code run outside of functions)
        unscoped_data = self.scope.end_call_stack()
        self.code_lookup.add_function(unscoped_data)
        self.call_graph.add_node(unscoped_data)

        file.close()
        return self._write_zip(output_path)

    # -- functions to process individual lines --

    def _get_funcname(self, line_dict: dict) -> str:
        '''returns the function name as parsed from the line dictionary'''
        return line_dict[Parser.FUNCTION].split(' ')[0]

    def _process_read(self, line_dict: dict) -> None:
        # TEMP: add coverage functionality here
        # the lines marked "R" in the profile correspond to the time taken to read and parse the code
        # which is not important to profiling hence the time is not recorded here
        pass

    def _process_register_file(self, line_dict: dict) -> None:
        '''called when a new file is registered as being connected to a given id'''
        path = os.path.abspath(line_dict[Parser.FILE])
        self.code_lookup.add_file(line_dict[Parser.FILE_ID], path)

    def _process_execution(self, line_dict: dict) -> None:
        '''updates the data structures when a line is executed'''
        # if there has been an unexpected exiting of the scope of the current function (could be multiple levels)
        while line_dict[Parser.CURRLINE] != 0 and not self.scope.in_scope(line_dict[Parser.CURRLINE]):
            curr_scope = self.scope.exit_scope()
            self.code_lookup.add_function(curr_scope)
            self.call_graph.add_node(curr_scope)
        # if the unscoped lines have not had a file id set for them yet, set the file id
        if self.scope.curr_func() == Scope.TOP_LEVEL_FUNC and self.scope.curr_file() == -1:
            self.scope.set_curr_file(line_dict[Parser.FILE_ID])
        self.scope.line_executed(line_dict[Parser.CURRLINE], line_dict[Parser.TIME])

    def _process_enter_func(self, line_dict: dict) -> None:
        '''updates the data structures when a new function is entered'''
        # adds the function to the code lookup
        func_name = self._get_funcname(line_dict)
        self.scope.enter_scope(line_dict[Parser.FILE_ID], func_name,
            line_dict[Parser.CURRLINE], line_dict[Parser.ENDLINE])

    def _process_exit_func(self, line_dict: dict) -> None:
        '''updates the data structures when the current function is exited'''
        # if the function being exited is the current function name, add it to the call graph
        # and lookup
        func_name = self._get_funcname(line_dict)
        if self.scope.curr_func() == func_name:
            curr_scope = self.scope.exit_scope()
            self.code_lookup.add_function(curr_scope)
            self.call_graph.add_node(curr_scope)

        # if we are not in any scope or exit a function without entering,
        # treat the current line like a single line function
        else:
            self.scope.enter_scope(line_dict[Parser.FILE_ID], line_dict[Parser.FUNCTION],
                line_dict[Parser.CURRLINE], line_dict[Parser.CURRLINE])
            curr_scope = self.scope.exit_scope()
            self.code_lookup.add_function(curr_scope)
            self.call_graph.add_node(curr_scope)

    # -- function to generate parser output --

    def _write_zip(self, output_path: str, project_root: str=None) -> bool:
        '''writes the profile as a zip archive
        format of zip is:
            - <id> : files containing repository content as a flat file id dir structure
            - code_lookup.json : json file containing the filesystem structure and which
                files contain which functions
        Args:
            output_path (str) : the path to write the zip of the profile to
            project_root (str) : absolute path to the root of the GAP project being profiled
                optional argument

        Returns:
            bool: a boolean indicating whether or not the operation succeeded
        '''
        # opens a zip archive with the given name
        with ZipFile(output_path, 'w') as zip:
            # write the full repository structure to the zip
            project_root = project_root if project_root else ''
            for id, path in self.code_lookup.get_files().items():
                path = os.path.join(project_root, path)
                if os.path.exists(path):
                    with open(os.path.join(project_root, path), 'r') as f:
                        zip.writestr(str(id), f.read())
                else:
                    zip.writestr(str(id), "file content not available")

            # writes the code lookup structure and visualization structures
            zip.writestr(CodeLookup.FILE_NAME, self.code_lookup.to_json())
            zip.writestr(CallGraph.FILE_NAME, self.call_graph.get_json())

if __name__=='__main__':
    args = sys.argv[1:]
    infile = args[0]
    outfile = args[1]
    if len(args) > 2 and not os.path.isdir(args[2]):
        print('Incorrect Usage: arguments must be in form <profile to parse> <path to output file> <(optional) project root path>')
        exit()
    if os.path.splitext(outfile)[-1] != '.zip':
        print("Incorrect Usage: output file must have a .zip extension")
        exit()
    project_root = None if len(args) <= 2 else os.path.expanduser(args[2])
    p = Parser()
    p.generate_profile(outfile, infile, project_root=project_root)
