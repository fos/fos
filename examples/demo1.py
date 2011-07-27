# Need to start with ipython --gui qt
import sys
from fos import *

from PySide.QtGui import QApplication

if __name__ == '__main__':
    app = QApplication(sys.argv)

    w = Window()
    w.new_region( regionname = "Main", transform = IdentityTranform(), resolution = ("mm", "mm", "mm") )
    w.add_actor_to_region( "Main", Axes() )
    w.show()

    sys.exit(app.exec_())
    


