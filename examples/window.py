import sys
import numpy as np
from fos import *

from PySide.QtGui import QApplication

if __name__ == '__main__':
    app = QApplication(sys.argv)

    w = Window( width = 1200, height = 800, bgcolor = (1.0,0,0) )

    sys.exit(app.exec_())
