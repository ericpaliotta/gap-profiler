'''
code_lookup.py

this file stores a data type to lookup code in the project.
This file works can create and store information from json
files corresponding to the zip archives generated from code profiling
'''

import os
import json
import re
from zipfile import ZipFile

from gap_profiler.data_processing.scope import FunctionCall

class CodeLookup:
    '''
    this class is a data structure to find code in the code base
    
    Attributes:
        _zip (zipfile.ZipFile) : a zipfile object for code retrieval. This attribute should not
            be externally accessed
        _files (dict) : a dictionary in the form { file id: file path }
        _functions (dict) : a dictionary in the form { function name: [file id, start line, end line] } 
    '''
    FILE_NAME = 'code_lookup.json' # standard name for every profiler code lookup name
    FILES_KEY = 'files'
    FILE_FUNCS_KEY = 'file_functions'
    FUNCTIONS_KEY = 'functions'
    PROJECT_ROOT_KEY = 'project_root'

    def __init__(self, path: str=None):
        '''
        Args:
            path (str) : the path to the zip archive containing all profiling information
        '''
        # if a path is passed into the function, reload from the zip archive
        if path:
            self._zip = ZipFile(path, 'r')
            content = json.loads(self._zip.read(CodeLookup.FILE_NAME))
            self._files = content.get(CodeLookup.FILES_KEY, {})
            self._functions = content.get(CodeLookup.FUNCTIONS_KEY, {})
            self._project_root = content.get(CodeLookup.PROJECT_ROOT_KEY, '')
        else:
            self._zip = None
            self._files = {} # id : path file mappings
            self._functions = {} # function name-fileid : [file id, start_line, end_line]
            self._project_root = '' # path to the root of the GAP project to make filesystem visualization easier

    def _gen_func_id(self, func: str, file: int):
        '''private function to generate function ids for
        internal use
        '''
        return f'{func}-{file}'

    def set_project_root(self, root: str):
        '''sets the project root

        done so that the correct sub-part of the filesystem will be visualized in the GUI

        Args:
            root (str) : the project root as an absolute path
        '''
        if not os.path.isabs(root):
            raise ValueError('root path must be an absolute path')
        self._project_root = root

    def add_function(self, fc: FunctionCall) -> None:
        '''adds a function to the registry in the code lookup

        Args:
            fc (FunctionCall) : the data structure associated with a given
                call of the function to be added
        '''
        # case where the file is not known, use default ID of -1 here
        key = self._gen_func_id(fc.function, fc.file)
        if fc.file == -1:
            self._files[fc.file] = 'missing filename'
            self._functions[key] = (fc.file, fc.start, fc.end)
        # case where the file does not yet exist
        elif fc.file not in self._files.keys():
            raise ValueError(f'file {fc.file} does not exist')
        # standard valid case
        else:
            self._functions[key] = (fc.file, fc.start, fc.end)

    def add_file(self, id: int, path: str) -> None:
        '''adds a file to the code lookup structure

        Args:
            id (int) : the file's id
            path (str) : the file's absolute path
        '''
        self._files[id] = path

    def get_files(self):
        '''returns the files dictionary
        
        Returns:
            dict: files dict of form { integer_id: path }
        '''
        return self._files

    def get_function(self, func: str, file: int) -> list:
        '''returns the file and line numbers for a given function

        Args:
            func (str) : the function name
            file (int) : the unique file id which the function is in
        Returns:
            list: a list in the form [file id, start line, end line]
        '''
        return self._functions[self._gen_func_id(func, file)]

    def get_file_content(self, id: int) -> str:
        '''returns file content given a file id

        Args:
            id (int) : the unique ID of the file in the project 
        Returns: 
            str: the file content as a string
        '''
        if self._zip is None:
            raise ValueError('file content could not be retrieved: no zip file is attached to this code lookup')
        # file was not given by the profiler
        elif id == -1:
            return 'file content unavailable'
        return self._zip.read(str(id)).decode('utf8')

    def search_files_regex(self, exp: str) -> list:
        '''searches all file names for a given regular expression, returning their ids if any element
        of their path matches exp

        Args:
            exp (str) : a regex to match to the file paths
        Returns:
            list: a list of integer file ids which match the given regex
        '''
        file_matches = []
        pattern = re.compile(exp)
        for k, v in self._files.items():
            if pattern.search(v):
                file_matches.append(int(k))
        return file_matches

    def to_json(self) -> str:
        '''returns json data stored by this class as a string'''
        return json.dumps({
            CodeLookup.PROJECT_ROOT_KEY: self._project_root,
            CodeLookup.FILES_KEY: self._files,
            CodeLookup.FUNCTIONS_KEY: self._functions},
            indent=4)

    def get_filesystem(self) -> dict:
        '''returns a virtual filesystem

        Returns:
            (dict) : a dictionary of form { dir_name: { files: [(id, name)], dir_name: {} ... } }
        '''
        # instantiates the filesystem
        main_fs = { 'files': [] }

        # splits the project root into a list of directories to not include in the filesystem
        if self._project_root != '':
            root_dirs = self._project_root.strip().split('/')
            root_dirs = root_dirs[1:] if root_dirs[0] == '' else root_dirs # if path starts with / split adds a ''
            root_dirs = root_dirs[:-1] if root_dirs[-1] == '' else root_dirs # if path ends with / split adds a ''
            main_fs[self._project_root] = { 'files': [] }

        # inserts the path into the filesystem data structures
        for id, path in self._files.items():
            layer = main_fs # defines the current level of the filesystem the path is on
            components = path.strip().split('/') # each directory and name in the path
            components = components[1:] if components[0] == '' else components # if path starts with / split adds a ''
            file_name = components.pop() # file name is always last on the path

            # filters components which match the project root out, provided there is a project root defined
            if self._project_root != '' and len(root_dirs) <= len(components):
                in_project = True
                for i in range(len(root_dirs)):
                    if root_dirs[i] != components[i]:
                        in_project = False
                # if the path is in a sub-dir of project_root, truncate the path and insert into project filesystem
                if in_project:
                    components = components[len(root_dirs):]
                    layer = layer[self._project_root]

            # adds file to the existing data structure, adding dirs if they don't exist yet
            for c in components:
                # moves down a level
                if not layer.get(c, None):
                    layer[c] = { 'files': [] }
                layer = layer[c]
            layer['files'].append((id, file_name))
        # merges and returns the respective filesystems
        return main_fs
