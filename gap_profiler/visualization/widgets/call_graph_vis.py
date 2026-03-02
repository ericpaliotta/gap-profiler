'''
call_graph_vis.py

This file contains a wrapper class for all call graph visualizations to hold shared functionality
'''

from typing import Callable
from PyQt5.QtWidgets import QWidget, QTabWidget, QVBoxLayout, QHBoxLayout, \
    QGridLayout, QComboBox, QLineEdit, QLabel, QPushButton, QSpinBox

from gap_profiler.data_types.code_lookup import CodeLookup
from gap_profiler.visualization.widgets.call_graph_widgets.call_tree import CallTree
from gap_profiler.visualization.widgets.call_graph_widgets.call_list import CallList
from gap_profiler.visualization.widgets.call_graph_widgets.abstract_call_graph_widget import OrderBy
from gap_profiler.data_types.call_graph import CallGraph


class CallGraphWrapperWidget(QWidget):
    '''wrapper class for all CallGraph visualizations

    this class takes care of organizing all of the different visualization methods for the call graph
    as well as storing the functionality to link them together and filter their elements.
    
    Attributes:
        call_graph (CallGraph) : full call graph for the visualization
        code_lookup (CodeLookup) : the data structure holding all information about files
            and their functions
        call_tree_widget (CallTree) : the widget of the hierarchical call tree
        call_list_widget (CallList) : the list of pooled function call data
    '''
    def __init__(self, parent: QWidget, call_graph: CallGraph, code_lookup: CodeLookup, show_code_func: Callable):
        '''
        Args:
            call_graph (CallGraph) : the full call graph for the profile
            show_code_func (Callable) : the function to be called when the
                show code button on call graph eleemnt widgets is pressed
        '''
        super(CallGraphWrapperWidget, self).__init__(parent)

        # -- data attributes -- 
        self.call_graph = call_graph
        self.code_lookup = code_lookup

        # -- widgets --
        # order-by drop down
        order_by_lbl = QLabel('Order By:')
        self.order_by = QComboBox(self)
        self.order_by.addItem(OrderBy.DEC) # added first to make it default
        self.order_by.addItem(OrderBy.ASC)
        self.order_by.addItem(OrderBy.ALPHABETICAL)
        self.order_by.currentIndexChanged.connect(self._order_by_changed)

        # function search filter
        search_lbl = QLabel('Function Name:')
        self.search = QLineEdit(self)
        self.search.returnPressed.connect(self._search_functions)

        # filter by file path
        path_search_lbl = QLabel('Path:')
        self.path_search = QLineEdit()
        self.path_search.returnPressed.connect(self._search_paths)

        # filter by runtime percentage (excludes funcs under a certain runtime percentage)
        runtime_perc_filter_lbl = QLabel('Runtime Percentage:')
        self.runtime_perc_filter = QSpinBox()
        self.runtime_perc_filter.setMinimum(0)
        self.runtime_perc_filter.setMaximum(100)
        self.runtime_perc_filter.textChanged.connect(self._filter_runtime_percentage)

        # widget for filtering
        self.filters = QWidget(self)
        self.filters.setVisible(False)
        toggle_filters_btn = QPushButton("Filters")
        toggle_filters_btn.clicked.connect(self._toggle_filters)

        # arranges filters in filter widget
        filters_lyt = QGridLayout()
        filters_lyt.addWidget(order_by_lbl, 1, 1)
        filters_lyt.addWidget(self.order_by, 1, 2)
        filters_lyt.addWidget(search_lbl, 2, 1)
        filters_lyt.addWidget(self.search, 2, 2)
        filters_lyt.addWidget(path_search_lbl, 3, 1)
        filters_lyt.addWidget(self.path_search, 3, 2)
        filters_lyt.addWidget(runtime_perc_filter_lbl, 4, 1)
        filters_lyt.addWidget(self.runtime_perc_filter, 4, 2)
        self.filters.setLayout(filters_lyt)

        # graph visualization widgets
        self.call_tree_widget = CallTree(self, call_graph, show_code_func, self._tree_node_highlighted)
        self.call_list_widget = CallList(self, call_graph, show_code_func, self._list_node_highlighted)

        # configure tab widget for call graph exploration
        tab_widget = QTabWidget()
        tab_widget.addTab(self.call_tree_widget, 'Tree View')
        tab_widget.addTab(self.call_list_widget, 'List View')

        # -- configures layout for filter toggling alignment --
        hbtn_lyt = QHBoxLayout()
        hbtn_lyt.addWidget(toggle_filters_btn)
        hbtn_lyt.addStretch(1)

        # -- configure main layout --
        lyt = QVBoxLayout()
        lyt.addLayout(hbtn_lyt)
        lyt.addWidget(self.filters)
        lyt.addWidget(tab_widget)

        self.setLayout(lyt)

    # -- filters changed functions --
    def _toggle_filters(self) -> None:
        '''opens or closes the drop-down menu of filtering options.
        Called when the show filters button is pressed
        '''
        self.filters.setVisible(not self.filters.isVisible()) 

    def _order_by_changed(self) -> None:
        '''called when the order by widget has it's settings changed in the filters drop down'''
        self.call_tree_widget.order_by(self.order_by.currentText())
        self.call_list_widget.order_by(self.order_by.currentText())

    def _search_functions(self) -> None:
        '''connected to line edit for searching filter. Filters out all functions
        which do not match the specified regex name
        '''
        func_regex = self.search.text()
        self.call_tree_widget.apply_filters(func_name=func_regex)
        self.call_list_widget.apply_filters(func_name=func_regex)

    def _search_paths(self) -> None:
        '''connected to line edit for path searching filter. Filters out all functions
        whose file paths do not match that specified
        '''
        files = self.code_lookup.search_files_regex(self.path_search.text())
        self.call_tree_widget.apply_filters(files=files)
        self.call_list_widget.apply_filters(files=files)

    def _filter_runtime_percentage(self) -> None:
        '''filters out all call tree nodes with runtime percentage lower than the value
        in the slider
        '''
        thresh = self.runtime_perc_filter.value()
        self.call_tree_widget.apply_filters(thresh=thresh)
        self.call_list_widget.apply_filters(thresh=thresh)

    # -- other signal functions -- 
    def _tree_node_highlighted(self, node_id: str) -> None:
        '''called when a widget in the tree node is clicked (i.e. selected),
        selects corresponding nodes in all other views

        Args:
            node_id (str) : the unique string id for the function call of the
                widget being highlighted
        '''
        self.call_list_widget.highlight_node(node_id)

    def _list_node_highlighted(self, node_id: str) -> None:
        '''called when a widget in the tree node is clicked (i.e. selected),
        selects corresponding nodes in all other views

        Args:
            node_id (str) : the unique string id for the function call of the
                widget being highlighted
        '''
        self.call_tree_widget.highlight_node(node_id)

    def select_funcs_in_file(self, id: int) -> None:
        '''selects all nodes in each view which exist in a given file
        
        Args:
            id (int) : unique file id to select all nodes from
        '''
        self.call_tree_widget.highlight_in_file(id)
        self.call_list_widget.highlight_in_file(id)