'''
call_graph_delegate.py

this function contains the class definition for the call graph delegate.
This delegate takes care of instantiating the element widgets for the call
graph views
'''

from typing import Callable
from PyQt5.QtCore import QSize, QModelIndex
from PyQt5.QtGui import QPainter
from PyQt5.QtWidgets import QTreeView, QWidget, QStyledItemDelegate, QStyleOptionViewItem

from gap_profiler.data_types.exceptions import UnrecognizedWidgetType
from gap_profiler.visualization.data_classes import DataRoles, WidgetType
from gap_profiler.visualization.widgets.call_graph_widgets.call_tree_element import CallTreeElement
from gap_profiler.visualization.widgets.call_graph_widgets.call_list_element import CallListParent, CallListChild


class CallGraphVisualizationDelegate(QStyledItemDelegate):
    '''delegate for creating widgets for QTreeView indices (for children of AbstractCallGraphWidget)

    To use in child implementations of AbstractCallGraphWidget

    Attributes:
        tree_view (QTreeView) : the tree view which the widgets are displayed in
        show_code_func (Callable) : the function called when the show code button (or similar) is pressed
            on the node widgets
        highlight_func (Callable) : the function called when the widget is clicked (not on a particular button)
    '''
    def __init__(self, tree_view: QTreeView, show_code_func: Callable, highlight_func: Callable) -> None:
        super(CallGraphVisualizationDelegate, self).__init__()
        self.tree_view = tree_view
        self.show_code_func = show_code_func
        self.highlight_func = highlight_func

    def createEditor(self, parent: QWidget, option: QStyleOptionViewItem, index: QModelIndex) -> QWidget:
        '''creates widgets for the views based upon the model index's widget type
        
        Args:
            parent (QWidget) : the widget to be created's parent

        Returns:
            QWidget: the widget to display in the view

        Raises:
            UnrecognizedWidgetType: if the DataRoles.WIDGET_TYPE of the given model index is
                not one of the class attributes of WidgetType
        '''
        widget_type = index.data(DataRoles.WIDGET_TYPE)
        if widget_type == WidgetType.TREE_ELEMENT:
            widget = CallTreeElement(parent, index.data(DataRoles.FUNC_ID), index.data(DataRoles.NODE),\
                index.data(DataRoles.TOTAL_TIME), show_code_func=self.show_code_func, highlight_func=self.highlight_func)
        elif widget_type == WidgetType.LIST_VIEW_PARENT:
            widget = CallListParent(parent, index.data(DataRoles.NODE), index.data(DataRoles.TOTAL_TIME),\
                show_code_func=self.show_code_func)
        elif widget_type == WidgetType.LIST_VIEW_CHILD:
            widget = CallListChild(parent, index.data(DataRoles.FUNC_ID), index.data(DataRoles.DISP_NAME),\
                index.data(DataRoles.FUNC_TIME), index.data(DataRoles.TOTAL_TIME), highlight_func=self.highlight_func)
        else:
            raise UnrecognizedWidgetType()
        return widget

    def paint(self, painter: QPainter, option: QStyleOptionViewItem, index: QModelIndex) -> None:
        super().paint(painter, option, index)
        self.tree_view.resizeColumnToContents(index.column()) # keep for now, could be inefficient
        self.tree_view.openPersistentEditor(index)

    def sizeHint(self, option: QStyleOptionViewItem, index: QModelIndex) -> QSize:
        size = super().sizeHint(option, index)
        size.setHeight(50)
        return size
