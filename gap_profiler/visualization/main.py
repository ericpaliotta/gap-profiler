'''
main.py

This file holds the main window for the profiler
'''

import sys
from PyQt5.QtWidgets import QMainWindow, QApplication, QFrame, QHBoxLayout, QSplitter, QSizePolicy

from gap_profiler.visualization.widgets.editor import Editor
from gap_profiler.visualization.widgets.call_graph_vis import CallGraphWrapperWidget
from gap_profiler.data_types.code_lookup import CodeLookup
from gap_profiler.data_types.call_graph import CallGraph


class MainWindow(QMainWindow):
    '''
    This is the main widget and window for the profiler app. All of the main administration and
    communication between the smaller pieces of the application happen via this widget
    Each instance of this class corresponds to a specific profiling instance
    
    Attributes:
        editor (Editor) : the code editor-like widget for file viewing
        call_graph_widget (GraphWidget) : the widget displaying the call graph
    '''
    def __init__(self, path: str):
        '''
        Args:
            path (str) : the path to the zip containing all of the profiling data
        '''
        super(MainWindow, self).__init__()

        # -- load in the data structure for visualization
        code_lookup = CodeLookup(path=path)
        call_graph = CallGraph(path=path)

        # -- basic configuration -- 
        self.setWindowTitle(f'Profile For: {path}')
        self.setGeometry(0, 0, 1000, 2000)

        # -- configure main layout -- 
        body_frame = QFrame()
        body_frame.setFrameShape(QFrame.NoFrame)
        body_frame.setFrameShadow(QFrame.Plain)
        body_frame.setLineWidth(0)
        body_frame.setMidLineWidth(0)
        body_frame.setContentsMargins(0, 0, 0, 0)
        body_frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        body = QHBoxLayout()
        body_frame.setLayout(body)

        splitter = QSplitter()

        # -- configure main widgets -- 
        self.editor = Editor(self, code_lookup)
        self.call_graph_widget = CallGraphWrapperWidget(self, call_graph, code_lookup, self.show_function_in_editor)
        self.editor.set_file_clicked_func(self.call_graph_widget.select_funcs_in_file)

        # -- add widgets to layout -- 
        splitter.addWidget(self.editor)
        splitter.addWidget(self.call_graph_widget)
        body.addWidget(splitter)

        self.setCentralWidget(body_frame)

    def show_function_in_editor(self, node: dict) -> None:
        '''called when the show code button is clicked in one of the Call Graph views
        
        This function will open a tab in the editor and open the file containing
        the clicked function, and highlight the function

        Args:
            node (dict) : the dictionary of node data stored by the call graph
        '''
        self.editor.open_function(node[CallGraph.FUNCTION_KEY], node[CallGraph.FILE_ID_KEY])


def run(path: str) -> None:
    '''takes care of all of the admin for the profiler application

    Args:
        path (str) : the path to the zip archive containing the profile to view
    '''
    app = QApplication([])
    window = MainWindow(path)
    window.show()
    sys.exit(app.exec())


if __name__=='__main__':
    args = sys.argv[1:]
    if len(args) > 1:
        print('Incorrect Usage: arguments must be in form <path to profile zip>')
    path = args[0]
    run(path)