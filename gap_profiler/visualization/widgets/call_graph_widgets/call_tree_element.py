'''
call_tree_element.py

defines a widget which represents a function as an element of the
function call tree
'''

import sys
from typing import Callable
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QMouseEvent
from PyQt5.QtWidgets import QWidget, QLabel, QPushButton, QGridLayout, QProgressBar

from gap_profiler.data_types.call_graph import CallGraph


class CallTreeElement(QWidget):
    '''each function in the call tree has a corresponding CallTreeElement

    Attributes:
        show_code_func (Callable) : function to be called when the show code button is clicked
        highlight_func (Callable) : function to be called when the item is selected
        id (str) : the unique string id of the function call
        node (dict) : the dictionary of metadata for the function call
    '''
    def __init__(self, parent: QWidget, id: str, node: dict, total_time: int, show_code_func: Callable=None, highlight_func: Callable=None):
        '''
        Args:
            parent (QWidget) : this widgets assigned parent
            id (str) : the string id of the function call
            node (dict) : a dictionary of metadata about a given CallGraph
                node as pulled directly from the CallGraph nodes
            total_time (int) : the time it took for the entire program to run
            show_code_func (Callable) : function to be called when "show code" button is clicked
            highlight_func (Callable) : function to be called when the widget is clicked (and hence highlighted)
        '''
        super(CallTreeElement, self).__init__(parent)

        # defines the function to be called on button click
        self.show_code_func = show_code_func if show_code_func else print
        self.highlight_func = highlight_func if highlight_func else print
        self.id = id # unique ID of this function call, saved to link this widget to it's cousin in the CallList
        self.node = node

        # label for the widget
        func_label = QLabel()
        func_label.setText(node[CallGraph.FUNCTION_KEY])
        font = QFont()
        font.setBold(True)
        func_label.setFont(font)

        # label for the raw runtime of the function (including runtime of children)
        runtime_label = QLabel()
        runtime_label.setText(f'Time: {node[CallGraph.TOTAL_TIME_KEY]}')

        # ad-hoc bug fix for some functions which get recorded as 0 time
        if total_time == 0:
            total_time = 1

        # defines bar for the callgraph visualization
        time_percent = int(100*node[CallGraph.TOTAL_TIME_KEY]/total_time)
        bar_color = 'cornflowerblue'
        if time_percent >= 75:
            bar_color = 'lightcoral'
        elif time_percent <= 25:
            bar_color = 'palegreen'
        runtime_percentage = QProgressBar()
        runtime_percentage.setMinimum(0)
        runtime_percentage.setMaximum(100)
        runtime_percentage.setValue(time_percent)
        runtime_percentage.setStyleSheet("QProgressBar::chunk "
            "{" 
            f"background-color: {bar_color};"
            "}")

        # button for showing code
        show_code_button = QPushButton()
        show_code_button.setText('show code')
        show_code_button.clicked.connect(self._show_code_button_pressed)

        # arranges widgets in a layout
        lyt = QGridLayout()
        lyt.addWidget(func_label, 1, 1, Qt.AlignLeft)
        lyt.addWidget(runtime_label, 1, 2, Qt.AlignLeft)
        lyt.addWidget(runtime_percentage, 1, 3)
        lyt.addWidget(show_code_button, 1, 4)

        # fixes alignment to make all buttons and progress bars about the same size
        lyt.setColumnStretch(1, 0)
        lyt.setColumnStretch(2, 2)
        lyt.setColumnStretch(3, 0)

        self.setLayout(lyt)

    def _show_code_button_pressed(self) -> None:
        '''function to be called when the button is pressed'''
        self.show_code_func(self.node)

    def mousePressEvent(self, a0: QMouseEvent) -> None:
        '''overridden mouseclick event to link listview and tree view widgets
        
        Args:
            a0 (QMouseEvent) : the clicking event used to highlight the node (not used directly here)
        '''
        self.highlight_func(self.id)
        super().mousePressEvent(a0)


# for development
if __name__=='__main__':
    from PyQt5.QtWidgets import QApplication, QMainWindow

    # defines a test node to represent in the widget
    testNode = {
        CallGraph.FUNCTION_KEY: 'testfunc',
        CallGraph.TOTAL_TIME_KEY: 10
    }
    app = QApplication([])
    window = QMainWindow()
    w = CallTreeElement(window, 'testfunc', testNode, 100)
    window.setCentralWidget(w)
    window.show()
    sys.exit(app.exec())