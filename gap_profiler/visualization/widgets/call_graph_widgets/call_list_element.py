'''
call_list_element.py

defines widgets which can represent data about all calls of a given function for a given
profile, and more fine-grained data about each call specifically
'''

import sys
from typing import Callable
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QMouseEvent
from PyQt5.QtWidgets import QWidget, QLabel, QPushButton, QGridLayout, QProgressBar

from gap_profiler.data_types.call_graph import CallGraph


class CallListChild(QWidget):
    '''widget for individual calls in the call list, rendered as children of pooled functions (parents)

    Attributes:
        id (str) : the unique string ID of the call
        highlight_func (Callable) : the function to be called when this widget is clicked
    '''
    def __init__(self, parent: QWidget, id: str, name: str, call_time: int, total_time: int, highlight_func: Callable=None):
        '''
        Args:
            parent (QWidget) : this widgets assigned parent
            node (dict) : a dictionary of metadata about a given CallGraph
                node as pulled directly from the CallGraph nodes
            total_time (int) : the time taken by this function across all calls
            highlight_func (Callable) : function to be called when the widget is clicked (and hence highlighted)
                function must take in (node_id: str)
        '''
        super(CallListChild, self).__init__(parent)

        # data attributes
        self.id = id # unique ID of this function call, saved to link this widget to it's cousin in the CallTree
        self.highlight_func = highlight_func if highlight_func else print

        # label for the widget
        func_label = QLabel()
        func_label.setText(name)
        font = QFont()
        font.setBold(True)
        func_label.setFont(font)

        # label for the raw runtime of the function (including runtime of children)
        runtime_label = QLabel()
        runtime_label.setText(f'Time: {call_time}')

        # defines bar for the callgraph visualization
        if total_time == 0:
            time_percent = 100 # safeguard for divide by 0 errors if total time is 0
        else:
            time_percent = 100*call_time/total_time
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

        # arranges widgets in a layout
        lyt = QGridLayout()
        lyt.addWidget(func_label, 1, 1, Qt.AlignLeft)
        lyt.addWidget(runtime_label, 1, 2, Qt.AlignLeft)
        lyt.addWidget(runtime_percentage, 1, 3)

        # fixes alignment to make all buttons and progress bars about the same size
        lyt.setColumnStretch(1, 0.5)
        lyt.setColumnStretch(2, 2)
        lyt.setColumnStretch(3, 0)

        self.setLayout(lyt)

    def mousePressEvent(self, a0: QMouseEvent) -> None:
        '''overridden mouseclick event to link listview and tree view widgets
        
        Args:
            a0 (QMouseEvent) : not used directly here
        '''
        self.highlight_func(self.id)
        return super().mousePressEvent(a0)

class CallListParent(QWidget):
    '''widget representing a pooled node (i.e. aggregated data about all calls of a given
    function across a program run)

    Attributes:
        node (dict) : the pooled node containing data about the function (as returned from
            CallGraph.get_graph(include_pool=True))
        show_code_func (Callable) : the function to be called when the show_code button is pressed
    '''
    def __init__(self, parent: QWidget, node: dict, total_time: int, show_code_func: Callable=None):
        '''
        Args:
            parent (QWidget) : this widgets assigned parent
            node (dict) : a dictionary of data about a given function
                taken from the dictionary of pooled node data for a given function
            total_time (int) : the time the program takes as a whole
        '''
        super(CallListParent, self).__init__(parent)

        # defines the function to be called on button click
        self.show_code_func = show_code_func if show_code_func else print
        self.node = node

        # label for the widget
        func_label = QLabel()
        func_label.setText(node[CallGraph.FUNCTION_KEY])
        font = QFont()
        font.setBold(True)
        func_label.setFont(font)

        # label for the raw runtime of the function (including runtime of children)
        runtime_label = QLabel()
        runtime_label.setText(f'Time: {node[CallGraph.FUNCTION_TIME_KEY]}')

        # defines runtime percentage
        if total_time == 0:
            time_percent = 100 # safeguard for functions which take 0 time
        else:
            time_percent = int(100*node[CallGraph.FUNCTION_TIME_KEY]/total_time)
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
        lyt.setColumnStretch(4, 0)

        self.setLayout(lyt)

    def _show_code_button_pressed(self) -> None:
        '''function to be called when the button is pressed'''
        self.show_code_func(self.node)


# for development
if __name__=='__main__':
    from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QFrame

    # defines a test node to represent in the widget
    testNode = {
        CallGraph.FUNCTION_KEY: 'testfunc',
        CallGraph.FUNCTION_TIME_KEY: 10,
        CallGraph.TOTAL_TIME_KEY: 10
    }
    app = QApplication([])
    window = QMainWindow()
    
    # creates one parent and one child widget
    parent_lbl = QLabel('Parent:')
    parent = CallListParent(window, testNode, 100)
    child_lbl = QLabel('Child:')
    child = CallListChild(window, 'testfunc', 'name', 10, 100)

    # sets up layout
    lyt = QVBoxLayout()
    lyt.addWidget(parent_lbl)
    lyt.addWidget(parent)
    lyt.addWidget(child_lbl)
    lyt.addWidget(child)

    frm = QFrame()
    frm.setLayout(lyt)
    window.setCentralWidget(frm)
    window.show()
    sys.exit(app.exec())