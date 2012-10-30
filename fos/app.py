import sys
try:
    from PySide import QtGui
except ImportError:
    #raise ImportError('PySide is not installed')
    print('PySide is not installed')



def Init():
    """ Initializes the Application 
    """

    try:
        global app
        app = QtGui.QApplication(sys.argv)
    except RuntimeError:
        pass


def Run():
    """ Executes the Application
    """
    
    try:
        global app
        sys.exit(app.exec_())
    except NameError:
        pass


