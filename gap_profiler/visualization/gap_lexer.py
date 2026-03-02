'''
gap_lexer.py

this file stores the definition for a custom lexer in QScintilla to handle
syntax highlighting for GAP
'''

import re
from PyQt5.QtGui import QColor, QFont
from PyQt5.Qsci import QsciLexerCustom


# set of GAP keywords to facilitate in syntax highlighting. Should not be available outside this file
GAP_KEYWORDS = set(['Assert', 'Info', 'IsBound', 'QUIT',
    'TryNextMethod', 'Unbind', 'and', 'atomic',
    'break', 'continue', 'do', 'elif',
    'else', 'end', 'false', 'fi',
    'for', 'function', 'if', 'in',
    'local', 'mod', 'not', 'od',
    'or', 'quit', 'readonly', 'readwrite',
    'rec', 'repeat', 'return', 'then',
    'true', 'until', 'while'])
# list of GAP delimiters to use in syntax highlighting
DELIMITERS = set(['(', ')', '{', '}', '[', ']'])

class QSciLexerGAP(QsciLexerCustom):
    '''lexer to provide syntax highlighting and styling for GAP files.

    Adapted from the lexer example at: https://qscintilla.com/#syntax_highlighting/custom_lexer_example
    '''
    def __init__(self, parent):
        super(QSciLexerGAP, self).__init__(parent)

        # default styling
        self.setDefaultColor(QColor('#ff000000'))
        self.setDefaultPaper(QColor('#ffffffff'))
        self.setDefaultFont(QFont('Courier', 10, weight=QFont.Bold))

        # -- styling for highlighting keywords --
        self.setColor(QColor('#8a00c2'), 1)   # purple highlighting for keywords

        # -- styling for highlighting delimiters --
        self.setColor(QColor('#ff0000bf'), 2)   # Style 2: blue

        # -- styling for comments --
        self.setColor(QColor('#ff007f00'), 3)   # green for comments

    def language(self) -> str:
        '''returns the language of this lexer as a string'''
        return 'GAP'

    def description(self, style: int) -> str:
        '''returns a string description of the styling of some text given the style integer
        
        Returns:
            str: a string description of some text's styling
        '''
        if style == 0:
            return 'default style'
        elif style == 1:
            return 'keyword'
        elif style == 2:
            return 'delimiters'
        elif style == 3:
            return 'comment'

    def styleText(self, start: int, end: int) -> None:
        '''this function takes care of styling a given section of text
        
        Args:
            start (int) : an integer marking the start of the current file's
                text to style
            end (int) : an integer marking the end of the current file's
                text to style
        '''
        self.startStyling(start)
        text = self.parent().text()[start:end]

        # tokenizes the text using a regex
        p = re.compile(r'[*]\/|\/[*]|\s+|\w+|\W')

        # 'token_list' is a list of tuples: (token_name, token_len)
        token_list = [ (token, len(bytearray(token, 'utf-8'))) for token in p.findall(text)]

        in_comment = False
        for i, token in enumerate(token_list):
            # exits the commment if a newline is seen
            if in_comment:
                self.setStyling(token[1], 3)
                if '\n' in token[0] or '\r' in token[0]:
                    in_comment = False
            else:
                if token[0] in GAP_KEYWORDS:
                    self.setStyling(token[1], 1)
                elif token[0] in DELIMITERS:
                    self.setStyling(token[1], 2)
                # enters a comment (i.e. once # is seen the rest of the line is a comment)
                elif token[0] == '#':
                    in_comment = True
                    self.setStyling(token[1], 3)
                # Default style
                else:
                    self.setStyling(token[1], 0)
