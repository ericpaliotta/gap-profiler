'''
editor.py

This file contains the code for the file explorer and multi-tab portions of the code viewer
'''

import os
import sys
from typing import Callable
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QSplitter, QTabWidget, \
    QTreeWidget, QTreeWidgetItem, QWidget, QSizePolicy, QApplication

from gap_profiler.data_types.code_lookup import CodeLookup
from gap_profiler.visualization.widgets.editor_body import EditorBody

class Editor(QWidget):
    '''editor widget adapted from: https://github.com/Fus3n/pyqt-code-editor-yt 
    
    Attributes:
        code_lookup (CodeLookup) : the data structure to allow for file viewing
        file_clicked_func (Callable) : the function called when a file in the filesystem tree is clicked

        _side_bar_clr (str) : string of a hex value for the side bar color
        _current_side_bar ()
        _window_font (QFont) : the font to use in the editor
        _file_manager_frame (QFrame) : the frame which the tree view of the filesystem in
        _hsplit (QSplitter) : the Qt widget to allow the dynamically sized filesystem tree and
            editor widget to be side by side
        _tab_view (QTabWidget) : the widget to manage all of the file tabs
    '''
    def __init__(self, parent: QWidget, code_lookup: CodeLookup, file_clicked_func: Callable=None):
        '''
        Args:
            parent (QWidget) : the widget to set as the parent of this widget
            code_lookup (CodeLookup) : the filesystem representation to be used by the editor to
                retrieve files by ID and lookup functions
            file_clicked_func (Callable) : the function to be called when a file in the tree view is
                clicked
        '''
        super(Editor, self).__init__(parent)
        
        # -- set up data attributes -- 
        self.file_clicked_func = file_clicked_func if file_clicked_func else print
        
        # add before init
        self._side_bar_clr = "#282c34"

        # -- data attributes --
        self.code_lookup = code_lookup
        self._current_side_bar = None

        self.setWindowTitle("GAP Profiler")
        self.resize(1300, 900)

        # sets window font to monospace font Courier
        self._window_font = QFont("Courier")
        self._window_font.setPointSize(12)
        self.setFont(self._window_font)

        self.set_up_body()

    def set_up_body(self) -> None:
        '''configures the main elements of the interface'''
        # Body
        body = QHBoxLayout()
        body.setContentsMargins(0, 0, 0, 0)
        body.setSpacing(0)

        # -- side bar --
        side_bar = QFrame()
        side_bar.setFrameShape(QFrame.StyledPanel)
        side_bar.setFrameShadow(QFrame.Plain)
        side_bar.setStyleSheet(f'''
            background-color: {self._side_bar_clr};
        ''')   
        side_bar_layout = QVBoxLayout()
        side_bar_layout.setContentsMargins(5, 10, 5, 0)
        side_bar_layout.setSpacing(0)
        side_bar_layout.setAlignment(Qt.AlignTop | Qt.AlignCenter)

        side_bar.setLayout(side_bar_layout)

        # split view
        self._hsplit = QSplitter(Qt.Horizontal)

        # -- file manager --
        # frame and layout to hold tree view (file manager)
        self._file_manager_frame = self.get_frame()
        self._file_manager_frame.setMaximumWidth(400)
        self._file_manager_frame.setMinimumWidth(200)
        tree_frame_layout = QVBoxLayout()
        tree_frame_layout.setContentsMargins(0, 0, 0, 0)
        tree_frame_layout.setSpacing(0)

        # -- file viewer --
        tree_view = QTreeWidget(self)
        filesystem = self.code_lookup.get_filesystem()
        root_item = self._construct_tree_items('root', filesystem)
        tree_view.insertTopLevelItem(0, root_item)
        tree_view.setColumnHidden(1, True)
        tree_view.setColumnHidden(2, True)
        tree_view.setColumnHidden(3, True)
        # handling click
        tree_view.setIndentation(10)
        tree_view.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        tree_view.itemClicked.connect(self.tree_view_clicked)

        # setup layout
        tree_frame_layout.addWidget(tree_view)
        self._file_manager_frame.setLayout(tree_frame_layout)

        # -- tab view --
        # Tab Widget to add editor to
        self._tab_view = QTabWidget()
        self._tab_view.setContentsMargins(0, 0, 0, 0)
        self._tab_view.setTabsClosable(True)
        self._tab_view.setMovable(True)
        self._tab_view.setDocumentMode(True)
        self._tab_view.tabCloseRequested.connect(self.close_tab)

        # -- setup widgets --
        # add tree view and tab view
        self._hsplit.addWidget(self._file_manager_frame)
        self._hsplit.addWidget(self._tab_view)

        body.addWidget(side_bar)
        body.addWidget(self._hsplit)

        self.setLayout(body)

    def _construct_tree_items(self, name: str, fs: dict) -> QTreeWidgetItem:
        '''recursive utility method to build the filesystem item tree
        
        should only be called in the constructor

        Args:
            name (str) : name of the current directory
            fs (dict) : the sub-filesystem in the form: { dict_name: { files: [(id, name)], dict_name: {} ... } }
        
        Returns:
            QTreeWidgetItem: the item having its children appended to it. In the top level of the recursion this
                is the tree's root item
        '''
        curr_item = QTreeWidgetItem()
        curr_item.setText(0, name)
        children = []
        for i in fs.pop('files', []):
            temp = QTreeWidgetItem()
            temp.setText(0, i[1])
            temp.setData(0, Qt.UserRole, int(i[0]))
            children.append(temp)
        for k, v in fs.items():
            children.append(self._construct_tree_items(k, v))
        curr_item.addChildren(children)
        return curr_item

    def get_frame(self) -> QFrame:
        frame = QFrame()
        frame.setFrameShape(QFrame.NoFrame)
        frame.setFrameShadow(QFrame.Plain)
        frame.setContentsMargins(0, 0, 0, 0)
        frame.setStyleSheet('''
            QFrame {
                background-color: #21252b;
                border-radius: 5px;
                border: none;
                padding: 5px;
                color: #D3D3D3;
            }
            QFrame:hover {
                color: white;
            }
        ''')
        return frame

    def show_hide_tab(self, e, type_) -> None:
        if type_ == "folder-icon":
            if not (self._file_manager_frame in self._hsplit.children()):
                self._hsplit.replaceWidget(0, self._file_manager_frame)
        elif type_ == "search-icon":
            if not (self.search_frame in self._hsplit.children()):
                self._hsplit.replaceWidget(0, self.search_frame)

        if self._current_side_bar == type_:
            frame = self._hsplit.children()[0]
            if frame.isHidden():
                frame.show()
            else:
                frame.hide()
        
        self._current_side_bar = type_

    def open_function(self, func: str, file: int) -> None:
        '''opens a file and highlights the function given
        
        Args:
            func (str) : the function name
            file (int) : the unique file id which the function is in
        '''
        func_data = self.code_lookup.get_function(func, file)
        self.set_new_tab(func_data[0], selection=func_data[1:])
    
    def set_new_tab(self, id: int, selection=None, coverage=None) -> None:
        '''opens a new file in a tab given its unique id
        
        Args:
            id (int) : file id to open
            selection (list) : a list of the form [startline, endline]
        '''
        # profiler did not give a valid file
        name = self.code_lookup.get_files()[str(id)]
        name = os.path.basename(name)
        editor = EditorBody(self, name, coverage=[(0,10)])
        selection = selection if selection else [0,0]

        # check if file already open
        for i in range(self._tab_view.count()):
            if self._tab_view.tabText(i) == name:
                self._tab_view.setCurrentIndex(i)
                self._tab_view.widget(i).set_current_selection(*selection)
                return

        # create new tab
        self._tab_view.addTab(editor, name)
        editor.setText(self.code_lookup.get_file_content(id))
        self._tab_view.setCurrentIndex(self._tab_view.count() - 1)

        # selects the desired lines if given
        if selection and type(selection) == list:
            editor.set_current_selection(*selection)
    
    def close_tab(self, index) -> None:
        self._tab_view.removeTab(index)

    def tree_view_clicked(self, item: QTreeWidgetItem, column: int) -> None:
        '''opens a new file'''
        id = item.data(column, Qt.UserRole)
        # self.file_clicked_func(self.code_lookup.get_file_functions(id))
        self.file_clicked_func(id)
        if id:
            self.set_new_tab(id)

    def set_cursor_pointer(self, e) -> None:
        self.setCursor(Qt.PointingHandCursor)

    def set_cursor_arrow(self, e) -> None:
        self.setCursor(Qt.ArrowCursor)

    def set_file_clicked_func(self, func: Callable) -> None:
        self.file_clicked_func = func


if __name__ == '__main__':
    app = QApplication([])
    window = Editor(None, CodeLookup())
    window.show()
    sys.exit(app.exec())
