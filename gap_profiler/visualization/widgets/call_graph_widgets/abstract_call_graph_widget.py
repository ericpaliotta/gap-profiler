'''
graph_vis_parent.py

This file contains the definition for the parent of all call graph visualization widgets
'''

from typing import Callable
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtWidgets import QTreeView, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel

from gap_profiler.data_types.call_graph import CallGraph
from gap_profiler.data_types.exceptions import UnrecognizedItemOrder
from gap_profiler.visualization.data_classes import DataRoles, OrderBy, WidgetType
from gap_profiler.visualization.multi_filter_model import MultiFilterModel
from gap_profiler.visualization.widgets.call_graph_widgets.call_graph_delegate import CallGraphVisualizationDelegate


class AbstractCallGraphWidget(QWidget):
    '''abstract class which contains all shared functionality for call graph visualization widgets

    Attributes:
        call_graph (CallGraph) : the data structure storing the function call graph to be displayed
        show_code_func (Callable) : the function to be called for each widget's button, receives a node
            dict from call_graph as an argument
        tree_view (QTreeView) : the view which displays widgets for each of the functions
        tree_model (QStandardItemModel) : model to store the hierarchical structure of the function calls
    '''
    def __init__(self, parent: QWidget, call_graph: CallGraph, show_code_func: Callable, highlight_func: Callable=None):
        '''
        Args:
            parent (QWidget) : the parent to this widget
            call_graph (CallGraph) : the graph of all function calls to display
            show_code_func (Callable) : the function to get called when the buttons in each widget are clicked
        '''
        super(AbstractCallGraphWidget, self).__init__(parent)

        # data attributes
        self.call_graph = call_graph
        self.show_code_func = show_code_func
        self.highlight_func = highlight_func

        self.path_regexp = ''
        self.func_name_regexp = ''
        self.less_than_regexp = ''

        # creates the model to hold the tree data
        self.tree_model = QStandardItemModel(self)
        self.model_root = self.tree_model.invisibleRootItem()

        # proxy model to map initial indices to sorted and filtered indices to be displayed
        self.sort_model = MultiFilterModel(self)
        self.sort_model.setSortRole(DataRoles.TOTAL_FUNC_TIME) # default
        self.sort_model.sort(Qt.DescendingOrder) # default
        self.sort_model.setSortCaseSensitivity(False)
        self.sort_model.setFilterRole(DataRoles.FUNC_ID) # default
        self.sort_model.setSourceModel(self.tree_model)

        # creates tree and sets tree properties
        self.tree_view = QTreeView(self)
        self.tree_view.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.tree_view.setEditTriggers(QTreeView.NoEditTriggers)
        self.tree_view.setAlternatingRowColors(True)
        self.tree_view.setUniformRowHeights(True)
        self.tree_view.setIndentation(10)
        self.tree_view.setItemsExpandable(True)
        self.tree_view.setHeaderHidden(True)
        self.tree_view.setSortingEnabled(True)
        self.tree_view.setModel(self.sort_model)

        # defines persistent selection model to select indices
        self.selection_model = self.tree_view.selectionModel()

        # sets the delegate for all of the views
        self.delegate = CallGraphVisualizationDelegate(self.tree_view,
            self.show_code_func, self.highlight_func)
        self.tree_view.setItemDelegate(self.delegate)

        # configures the widgets and such in the tree
        self._config_models()

        # label for time type
        time_type_lbl = QLabel(f'Time Type: {self.call_graph.time_type}')

        # expand all button
        expand_btn = QPushButton()
        expand_btn.setText('Expand All')
        expand_btn.setFixedWidth(100)
        expand_btn.clicked.connect(self.tree_view.expandAll)

        # collapse all button
        self.collapse_btn = QPushButton()
        self.collapse_btn.setText('Collapse All')
        self.collapse_btn.setFixedWidth(100)
        self.collapse_btn.clicked.connect(self.tree_view.collapseAll)

        # organizes the layout for the widget and inserts the tree view
        btn_lyt = QHBoxLayout()
        btn_lyt.addWidget(time_type_lbl)
        btn_lyt.addStretch()
        btn_lyt.addWidget(expand_btn)
        btn_lyt.addWidget(self.collapse_btn)

        lyt = QVBoxLayout()
        lyt.addLayout(btn_lyt)
        lyt.addWidget(self.tree_view)

        self.setLayout(lyt)

    def _config_models(self) -> None:
        '''This function is called during class instantiation and must use the call graph to insert
        the CallGraph data into the given models

        must be implemented in all child classes
        '''
        raise NotImplementedError('Cannot instantiate abstract class GraphVisParent')

    def _create_item(self, id: str, total_time: int, widget_type: WidgetType, node: dict, disp_name: str=None) -> QStandardItem:
        '''private utility function to create an item for the model and assign data to it

        should not be re-implemented in child classes

        Args:
            id (str) : the unique function id as a string
            node (dict) : the node dictionary stored in CallGraph. Either returned as an individual
                call or pooled function node
            total_time (int) : the total time for the function time to be taken as a percentage of. Passed
                explicitly here because it varies from widget to widget
            name (str) : name to be displayed on the node widget, default is node[CallGraph.FUNCTION_KEY]
            disp_name (str) : optional argument if the name to be displayed is different from the name
                of the node

        Returns:
            (QStandardItem) : an item to put into the model with stored data about runtime and function name
        '''
        # generates the name to be displayed in the widget
        name = disp_name if disp_name else node[CallGraph.FUNCTION_KEY]

        item = QStandardItem()
        item.setData(id, DataRoles.FUNC_ID)
        item.setData(total_time, DataRoles.TOTAL_TIME)
        item.setData(widget_type, DataRoles.WIDGET_TYPE)
        item.setData(name, DataRoles.DISP_NAME)
        item.setData(node[CallGraph.TOTAL_TIME_KEY], DataRoles.TOTAL_FUNC_TIME) # total time of parent for constructing call time percentage
        item.setData(node[CallGraph.FUNCTION_TIME_KEY], DataRoles.FUNC_TIME)
        item.setData(node, DataRoles.NODE)
        item.setData(node[CallGraph.FILE_ID_KEY], DataRoles.FILE_ID)

        return item
    
    def order_by(self, order: str) -> None:
        '''orders the widgets by the order given
        
        Args:
            order (str) : the order to sort the view by as a string from the OrderBy data class
        '''
        # sets ordering data role and order mode based upon arg order
        mode = Qt.DescendingOrder
        if order == OrderBy.ASC:
            self.sort_model.setSortRole(DataRoles.TOTAL_FUNC_TIME)
            mode = Qt.AscendingOrder
        elif order == OrderBy.DEC:
            self.sort_model.setSortRole(DataRoles.TOTAL_FUNC_TIME)
            mode = Qt.DescendingOrder
        elif order == OrderBy.ALPHABETICAL:
            self.sort_model.setSortRole(DataRoles.DISP_NAME)
            mode = Qt.AscendingOrder
        else:
            raise UnrecognizedItemOrder(order)

        # sets order for all columns
        for i in range(self.sort_model.columnCount()):
            self.sort_model.sort(i, mode)

    def apply_filters(self, func_name: str=None, files: list=None, thresh: int=None, cs: bool=False) -> None:
        '''this function applies filters to the call tree given parameters
        
        Args:
            func_name (str) : a string to regex match to the function names in the call tree
            files (list) : a list of file IDs such that all functions inside any of the given files and their
                parents are shown upon filtering
            thresh (int) : a runtime percentage for which anything under this percentage should be
                filtered out
        '''
        if func_name is not None: self.sort_model.set_func_regex(func_name)
        if files is not None: self.sort_model.set_files(files)
        if thresh is not None: self.sort_model.time_percentage = thresh
        self.sort_model.invalidate() # refreshes filtering

    def highlight_node(self, node_id: str, mode=None) -> None:
        '''highlights the function call with the given string ID
        
        Args:
            node_id (str) : the unique string id of the function in the CallGraph
            mode (QItemSelectionModel.SelectionFlags) : the mode to use to select the node
        '''
        raise NotImplementedError('all children of AbstractCallGraphWidget must implement highlight_node')

    def highlight_in_file(self, id: int) -> None:
        '''highlights all nodes which represent functions in a given file
        
        Args:
            id (int) : the unique integer id of the file
        '''
        raise NotImplementedError('all children of AbstractCallGraphWidget must implement highlight_in_file')

