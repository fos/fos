import sys
import numpy as np
from fos import *

from PySide.QtGui import QApplication

if __name__ == '__main__':
    app = QApplication(sys.argv)

    w = Window( width = 1200, height = 800, bgcolor = (0.2,0,0) )

    w.screenshot( 'myscreenshot.png' )
    
    sys.exit(app.exec_())
