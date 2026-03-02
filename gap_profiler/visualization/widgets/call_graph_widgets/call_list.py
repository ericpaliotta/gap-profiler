'''
function_list.py

This file contains a class which displays the function calls as a list
'''

import sys
from PyQt5.QtCore import QItemSelectionModel

from gap_profiler.data_types.call_graph import CallGraph
from gap_profiler.data_processing.scope import FunctionCall
from gap_profiler.visualization.widgets.call_graph_widgets.abstract_call_graph_widget import *
from gap_profiler.visualization.widgets.call_graph_widgets.call_list_element import *


class CallList(AbstractCallGraphWidget):
    '''A class for visualization of function calls as a list

    Here each function call is displayed on the same level of a list, with children displaying data about each call

    Attributes:
        _parent_items (dict) : a dictionary of PyQt5 QStandardItems mapped from their function names. These items are
            what link to the widgets displayed and store data for sorting and filtering
        _child_items (dict) : a dictionary of PyQt5 QStandardItems mapped from their unique function ids. These items are
            what link to the widgets displayed and store data for sorting and filtering for the children
    '''
    def _config_models(self):
        # class specific data attributes
        self._parent_items = {} # all items for pooled nodes
        self._child_items = {} # items in the model for each widget

        # builds the function list (here parents are functions as entities and their children are each individual call)
        nodes, _, pooled = self.call_graph.get_graph(include_pool=True)
        for k, v in pooled.items():
            self._parent_items[k] = self._create_item(v[CallGraph.FUNCTION_KEY], self.call_graph.total_time,
                WidgetType.LIST_VIEW_PARENT, v)
            self.model_root.appendRow(self._parent_items[k])
            # creates widgets for each individual call of the function
            for n in v[CallGraph.CHILDREN_KEY]:
                name = 'Call: ' + n.split('-')[-1] if n != 'unscoped' else 'Call: 1'
                self._child_items[n] = self._create_item(n, v[CallGraph.TOTAL_TIME_KEY],
                    WidgetType.LIST_VIEW_CHILD, nodes[n], disp_name=name)
                self._parent_items[k].appendRow(self._child_items[n])

    def highlight_node(self, node_id: str, mode: QItemSelectionModel.SelectionFlag=None) -> None:
        '''highlights a child node with the given id

        note each child node is a function call
        
        Args:
            node_id (str) : the unique string id of the function call widget to highlight
            mode (QItemSelectionModel.SelectionFlag) : the mode to select the nodes with
                usually specified to indicate whether 1 or > 1 node should be selected at a time
        '''
        self.selection_model.clearSelection()
        mode = mode if mode else QItemSelectionModel.SelectCurrent
        self.tree_view.selectionModel().setCurrentIndex(
            self.sort_model.mapFromSource(self._child_items[node_id].index()), mode)

    def highlight_in_file(self, id: int) -> None:
        '''highlights all nodes which represent functions in a given file
        
        Args:
            id (int) : the unique integer id of the file
        '''
        self.selection_model.clearSelection()
        for _, v in self._parent_items.items():
            if v.data(DataRoles.FILE_ID) == id:
                self.tree_view.selectionModel().setCurrentIndex(
                    self.sort_model.mapFromSource(v.index()),
                    QItemSelectionModel.Select)

# for development
if __name__=='__main__':
    from PyQt5.QtWidgets import QApplication, QMainWindow

    # builds a call graph for testing
    cg = CallGraph()
    unscoped = FunctionCall(1, "unscoped", 1, 3, 6, [1, 1, 1])
    node = FunctionCall(1, "test_func", 8, 10, 3, [1, 1, 1], call_num=1, called_from=1, caller='unscoped')
    cg.add_node(node)
    cg.add_node(unscoped)

    app = QApplication([])
    window = QMainWindow()
    w = CallList(window, cg, print)
    window.setCentralWidget(w)
    window.show()
    sys.exit(app.exec())