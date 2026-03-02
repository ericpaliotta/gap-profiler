'''
editor_body.py

this file contains the widget for the code displaying part
of the code viewer
'''

import sys
from PyQt5.QtWidgets import QWidget, QApplication, QVBoxLayout
from PyQt5.Qsci import QsciScintilla

from gap_profiler.visualization.gap_lexer import QSciLexerGAP


class EditorBody(QsciScintilla):
    '''
    This class is derived from the QScintilla editor to allow for
    default read-only behaviour, coverage highlighting, etc.
    
    Attributes:
        current_selection (tuple) : a pair of the form (startline, endline) for the currently highlighted
            code. Usually used for highlighting a function being inspected
        coverage (list) : a list of tuples specifying which lines of code were read by the GAP interpreter
            during the program's run (not implemented yet)
    '''
    COVERAGE_INDICATOR = 0 # highlighting for code coverage
    SELECTION_INDICATOR = 2 # 1 does not work here 

    def __init__(self, parent: QWidget, text: str, coverage: list=None):
        '''
        Args:
            parent (QWidget) : the widget which this widget is contained in
            text (str) : the text to display in this widget as a string
            coverage (list) : a list of all of the lines in the file which
                have been run to highlight in the editor
        '''
        super(EditorBody, self).__init__(parent)

        # -- state vars -- 
        self.current_selection = (0, 0)
        self.coverage = coverage if coverage else []

        # -- basic setup --
        self.setReadOnly(True)
        self.setMarginType(0, QsciScintilla.NumberMargin)
        self.setMarginWidth(0, '0000')
        self.setText(text)

        # -- sets up custom lexer --
        self.lexer = QSciLexerGAP(self)
        self.setLexer(self.lexer)

        # -- setup for section highlighting --
        self.indicatorDefine(QsciScintilla.FullBoxIndicator, EditorBody.COVERAGE_INDICATOR)
        self.setIndicatorDrawUnder(False, EditorBody.COVERAGE_INDICATOR)
        for range in self.coverage:
            self.fillIndicatorRange(range[0], 0, range[1], 0, EditorBody.COVERAGE_INDICATOR)

        self.indicatorDefine(QsciScintilla.FullBoxIndicator, EditorBody.SELECTION_INDICATOR)
        self.setIndicatorDrawUnder(False, EditorBody.SELECTION_INDICATOR)

    def set_current_selection(self, start: int, end: int) -> None:
        '''sets the currently selected section of code
        
        Args:
            start (int) : the line of the selection range to start at
            end (int) : the line of the selection range to end at
        '''
        self.clearIndicatorRange(self.current_selection[0], 0, self.current_selection[1], 0, EditorBody.SELECTION_INDICATOR)
        self.fillIndicatorRange(start, 0, end, 0, EditorBody.SELECTION_INDICATOR)
        self.current_selection = (start, end)
        self.setCursorPosition(start, 0)
        self.setSelection(start, 0, start, 0)


# for easy testing of changes
if __name__=='__main__':
    app = QApplication(sys.argv)
    window = QWidget()
    lyt = QVBoxLayout()
    lyt.addWidget(EditorBody(window,
        open('./widgets/editor_body.py', 'r').read(),
        coverage=[(0,10),(15,20)]))
    window.setLayout(lyt)
    window.setGeometry(0, 0, 1300, 900)
    window.show()
    sys.exit(app.exec())
