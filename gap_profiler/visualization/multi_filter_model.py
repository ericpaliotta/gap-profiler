'''
multi_filter_model.py

This file contains a sub-class of QSortFilterProxyModel which can filter
on the basis of multiple data roles and multiple filter types
'''

import re
from typing import Optional
from PyQt5.QtCore import QSortFilterProxyModel, QModelIndex, QObject

from gap_profiler.visualization.data_classes import DataRoles


class MultiFilterModel(QSortFilterProxyModel):
    '''this class is a modified version of QSortFilterProxyModel which allows for filtering with multiple conditions

    note that this class only works for models which use QTreeView currently
    
    Attributes:
        func_regex (str) : a string storing a regex to match to function names. Function calls are included
            if their names match the given regex
        self.files_search (set) : a set of integer file ids. All functions contained within one of these files
            will be shown in the view
        time_percentage (int) : an integer between 0 and 100. If the percentage of the total time of the node
            is < this integer it is excluded
    '''
    def __init__(self, parent: Optional[QObject] = ...) -> None:
        super().__init__(parent)
        self.func_regex = ''
        self.files_search = None
        self.time_percentage = 0

    def set_func_regex(self, func_regex: str) -> None:
        '''sets the regex to filter the function names by
        
        Args:
            func_regex (str) : the string to filter the function names by using regex
        '''
        self.func_regex = func_regex

    def set_files(self, files: list) -> None:
        '''sets the set of file ids which are to be accepted via filtering

        Args:
            files (list) : a list of integer file IDs. If the list is empty,
                all indices are allowed. To disallow any indices pass [-1]
        '''
        self.files_search = set(files)

    def set_time_percentage(self, thresh: int) -> None:
        '''sets the time threshold such that nodes with time percentage < this threshold
        are filtered out

        Args:
            thresh (int) : an integer between 1 and 100

        Raises:
            ValueError: if thresh is out of the 0-100 range
        '''
        if thresh < 0 or thresh > 100:
            raise ValueError('thresh must be in the range 0-100 as it is a percentage')
        self.time_percentage = thresh

    def filterAcceptsRow(self, source_row: int, source_parent: QModelIndex) -> bool:
        '''overridden method. Uses the attributes of the class to determine whether the given item should be
        filtered out or not

        Returns:
            bool: True if the given item is to be included, False otherwise
        '''
        # gets the source index and makes sure it is not None
        source_index = self.sourceModel().index(source_row, 0, source_parent)
        if source_index.data(DataRoles.FUNC_ID) is None or \
            source_index.data(DataRoles.TOTAL_FUNC_TIME) is None or \
            source_index.data(DataRoles.TOTAL_TIME) is None:
            return False

        # sets func_bool = True if the current index's name contains the specified function name
        func_bool = self.filter_accepts_funcname(source_index)

        # matches the function name regex if the set is empty, all indices are included.
        # includes everything on first run when self.files_search = None
        path_bool = True if self.files_search is None else self.filter_accepts_files(source_index)

        # if the runtime percentage is < self.time_percentage filter out
        time_bool = True
        percentage = 0
        if source_index.data(DataRoles.TOTAL_TIME) != 0:
            percentage = int(100 * source_index.data(DataRoles.TOTAL_FUNC_TIME) / source_index.data(DataRoles.TOTAL_TIME))
        if percentage < self.time_percentage:
            time_bool = False
    
        # returns True if all conditions are true
        return (func_bool and path_bool and time_bool)

    # -- functions for each of filterAcceptsRow --

    def filter_accepts_funcname(self, source_index: QModelIndex) -> bool:
        '''returns a boolean as to whether the current item should be kept in view based upon a filter string

        this method returns true if the function name matches the filter string or if any of it's children match
        partial matches count

        Args:
            source_index (QModelIndex) : the item to filter

        Returns:
            bool: indicating whether or not the node should be kept
        '''
        # sets func_bool = True if the current index's name contains the specified function name
        pattern = re.compile(self.func_regex, re.IGNORECASE)

        # checks child indices for matches using DFS of the model (no informed search is possible here)
        agenda = [source_index]
        while len(agenda) != 0:
            curr_index = agenda.pop()
            if pattern.search(curr_index.data(DataRoles.FUNC_ID)):
                return True
            for r in range(self.sourceModel().rowCount(curr_index)):
                agenda.append(self.sourceModel().index(r, 0, curr_index))
        return False

    def filter_accepts_files(self, source_index: QModelIndex) -> bool:
        '''returns a boolean as to whether the current item should be kept in view based upon a list of function names

        this method returns true if the function name is in the list or if any of its children match
        partial matches do not count here

        Args:
            source_index (QModelIndex) : the item to filter

        Returns:
            bool: indicating whether or not the node should be kept
        '''
        # checks child indices for matches using DFS of the model (no informed search is possible here)
        agenda = [source_index]
        while len(agenda) != 0:
            curr_index = agenda.pop()
            if curr_index.data(DataRoles.FILE_ID) in self.files_search:
                return True
            for r in range(self.sourceModel().rowCount(curr_index)):
                agenda.append(self.sourceModel().index(r, 0, curr_index))
        return False
