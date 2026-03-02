'''
data_classes.py

This file contains common data classes for the visualization portion of this project
'''

from PyQt5.QtCore import Qt


class WidgetType:
    '''enum to specify widget type for the model delegate'''
    TREE_ELEMENT =     0
    LIST_VIEW_PARENT = 1
    LIST_VIEW_CHILD =  2

class DataRoles:
    '''enum for custom data roles in QStandardItem. Below are descriptions of the data the roles
    hold in their QStandardItems
    '''
    TOTAL_FUNC_TIME = Qt.UserRole+1 # amount of time the function takes incl functions it calls
    FUNC_TIME =       Qt.UserRole+2 # amount of time the function takes not incl functions it calls
    FUNC_ID =         Qt.UserRole+3 # the unique function ID from the call graph
    DISP_NAME =       Qt.UserRole+4 # name do display in the function widget (view element)
    NODE =            Qt.UserRole+5 # the function/function calls call graph node dictionary
    TOTAL_TIME =      Qt.UserRole+6 # total time taken by the parent of this node
    WIDGET_TYPE =     Qt.UserRole+7 # the type of widget as an integer from the WidgetType class
    FILE_ID =         Qt.UserRole+8 # the unique integer id for the file the function is in

class OrderBy:
    '''data class for ordering options in filters'''
    ALPHABETICAL = 'Alphabetical'
    ASC =          'Ascending'
    DEC =          'Descending'
