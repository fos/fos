import sys
from fos import *

from PySide.QtGui import QApplication

if __name__ == '__main__':
    app = QApplication(sys.argv)

    w = Window()

    mytransform = IdentityTranform()
    mytransform.set_translation( x = 5 )
    mytransform.rotate( 45, 1.0, 0, 0 )
    w.new_region( regionname = "Main", transform = mytransform, resolution = ("mm", "mm", "mm") )
    w.add_actor_to_region( "Main", Axes( name = "3 axes", scale = 10.0, linewidth = 5.0) )

    mytransform = IdentityTranform()
    mytransform.set_translation( x = -10 )
    w.new_region( regionname = "Main2", transform = mytransform, resolution = ("mm", "mm", "mm") )
    w.add_actor_to_region( "Main2", Axes( name = "3 axes", scale = 5.0, linewidth = 2.0) )

    w.show()

    sys.exit(app.exec_())
