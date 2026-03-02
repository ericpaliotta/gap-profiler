'''
call_tree.py

this file contains an implementation of AbstractCallGraph widget for an expandable
tree view of the call tree in CallGraph
'''

import sys
from PyQt5.QtCore import QItemSelectionModel

from gap_profiler.data_types.call_graph import CallGraph
from gap_profiler.data_processing.scope import Scope, FunctionCall
from gap_profiler.visualization.data_classes import WidgetType, DataRoles
from gap_profiler.visualization.widgets.call_graph_widgets.abstract_call_graph_widget import AbstractCallGraphWidget


class CallTree(AbstractCallGraphWidget):
    '''This class creates a tree view of the call graph.
    
    This call tree is expandable and only works
    because call graphs are always acyclic (if each function call is a distinct node)

    Attributes:
        _func_items (dict) : a dictionary of PyQt5 QStandardItems mapped from their unique function ids. These items are
            what link to the widgets displayed and store data for sorting and filtering
    '''
    def _config_models(self) -> None:
        '''
        here the models are configured into a tree which is recursively defined as each node is a function call
        with it's children being functions which this function call calls
        '''
        # class-specific data attributes
        self._func_items = {} # dictionary mapping node names to QStandardItem

        # constructs a tree item for each function call in the graph
        widget_total_times = {CallGraph.TOP_LEVEL_FUNC: self.call_graph.total_time} # the total time taken on this level of the call tree for normalizing percentages
        nodes, edges = self.call_graph.get_graph()

        # builds total times for each level in the call tree
        for e in edges:
            widget_total_times[e[1]] = nodes[e[0]][CallGraph.TOTAL_TIME_KEY] \
                - nodes[e[0]][CallGraph.FUNCTION_TIME_KEY]

        for k, v in nodes.items():
            self._func_items[k] = self._create_item(k, widget_total_times[k], WidgetType.TREE_ELEMENT, v)

        # builds the tree from the item dictionary
        self.model_root.appendRow(self._func_items[Scope.TOP_LEVEL_FUNC])
        for e in edges:
            self._func_items[e[0]].appendRow(self._func_items[e[1]])

    def highlight_node(self, node_id: str, mode=None) -> None:
        '''highlights a node with the given id

        Args:
            node_id (str) : the unique string id of the function call widget to highlight
            mode (QItemSelectionModel.SelectionFlag) : the mode to select the nodes with
                usually specified to indicate whether 1 or > 1 node should be selected at a time
        '''
        self.selection_model.clearSelection()
        mode = mode if mode else QItemSelectionModel.SelectCurrent
        self.selection_model.setCurrentIndex(
            self.sort_model.mapFromSource(self._func_items[node_id].index()), mode)

    def highlight_in_file(self, id: int) -> None:
        '''highlights all nodes which represent functions in a given file
        
        Args:
            id (int) : the unique integer id of the file
        '''
        self.selection_model.clearSelection()
        for _, v in self._func_items.items():
            if v.data(DataRoles.FILE_ID) == id:
                self.selection_model.setCurrentIndex(self.sort_model.mapFromSource(v.index()),
                    QItemSelectionModel.Select)


# for development
if __name__=='__main__':
    from PyQt5.QtWidgets import QApplication, QMainWindow

    # builds a call graph for testing
    cg = CallGraph()
    node = FunctionCall(1, 'test_func', 8, 10, 20, [18, 1, 1], caller=CallGraph.TOP_LEVEL_FUNC, call_num=1)
    unscoped = FunctionCall(1, 'unscoped', 8, 10, 50, [28, 1, 1])
    cg.add_node(node)
    cg.add_node(unscoped)

    app = QApplication([])
    window = QMainWindow()
    w = CallTree(window, cg, print)
    window.setCentralWidget(w)
    window.show()
    sys.exit(app.exec())