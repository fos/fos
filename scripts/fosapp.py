#!/usr/bin/env python
"""Example integrating an IPython kernel into a GUI App with fos

A `foswin` variable exists in the IPython namespace where you can add Regions
and Actors.

"""
#-----------------------------------------------------------------------------
# Imports
#-----------------------------------------------------------------------------

from PySide import QtGui, QtCore

#from PyQt4 import Qt
import subprocess
import sys

from IPython.zmq.ipkernel import IPKernelApp

from fos import *

#-----------------------------------------------------------------------------
# Functions and classes
#-----------------------------------------------------------------------------
def pylab_kernel(gui):
    """Launch and return an IPython kernel with pylab support for the desired gui
    """
    kernel = IPKernelApp()
    # FIXME: we're hardcoding the heartbeat port b/c of a bug in IPython 0.11
    # that will set it to 0 if not specified.  Once this is fixed, the --hb
    # parameter can be omitted and all ports will be automatic
    kernel.initialize(['python', '--pylab=%s' % gui, '--hb=19999',
                       #'--log-level=10'
                       ])
    return kernel


def qtconsole_cmd(kernel):
    """Compute the command to connect a qt console to an already running kernel
    """
    ports = ['--%s=%d' % (name, port) for name, port in kernel.ports.items()]
    return ['ipython', 'qtconsole', '--existing'] + ports


class InternalIPKernel(object):

    def init_ipkernel(self, backend):
        # Start IPython kernel with GUI event loop and pylab support
        self.ipkernel = pylab_kernel(backend)

        # To create and track active qt consoles
        self._qtconsole_cmd = qtconsole_cmd(self.ipkernel)
        self.consoles = []

        # This application will also act on the shell user namespace
        self.namespace = self.ipkernel.shell.user_ns
        # Keys present at startup so we don't print the entire pylab/numpy
        # namespace when the user clicks the 'namespace' button
        self._init_keys = set(self.namespace.keys())

        # Example: a variable that will be seen by the user in the shell, and
        # that the GUI modifies (the 'Counter++' button increments it):
        self.namespace['app_counter'] = 0
        self.namespace['ipkernel'] = self.ipkernel  # dbg

    def print_namespace(self, evt=None):
        print "\n***Variables in User namespace***"
        for k, v in self.namespace.iteritems():
            if k not in self._init_keys and not k.startswith('_'):
                print '%s -> %r' % (k, v)
        sys.stdout.flush()

    def new_qt_console(self, evt=None):
        self.consoles.append(subprocess.Popen(self._qtconsole_cmd))

    def count(self, evt=None):
        self.namespace['app_counter'] += 1

    def cleanup_consoles(self, evt=None):
        for c in self.consoles:
            c.kill()

class SimpleWindow(QtGui.QWidget, InternalIPKernel):

    def __init__(self, app):
        QtGui.QWidget.__init__(self)
        self.app = app
        self.add_widgets()
        self.init_ipkernel('qt')
        # create fos window
        self.init_fos()
        self.new_qt_console()

    def init_fos(self):

        self.foswindow = Window()
        self.namespace['foswin'] = self.foswindow

    def add_widgets(self):
        self.setGeometry(300, 300, 400, 70)
        self.setWindowTitle('IPython with Fos')

        # Add simple buttons:
        console = QtGui.QPushButton('Qt Console', self)
        console.setGeometry(10, 10, 100, 35)
        self.connect(console, QtCore.SIGNAL('clicked()'), self.new_qt_console)

        namespace = QtGui.QPushButton('Namespace', self)
        namespace.setGeometry(120, 10, 100, 35)
        self.connect(namespace, QtCore.SIGNAL('clicked()'), self.print_namespace)

        # Quit and cleanup
        quit = QtGui.QPushButton('Quit', self)
        quit.setGeometry(320, 10, 60, 35)
        self.connect(quit, QtCore.SIGNAL('clicked()'), QtGui.qApp, QtCore.SLOT('quit()'))

        self.app.connect(self.app, QtCore.SIGNAL("lastWindowClosed()"),
                         self.app, QtCore.SLOT("quit()"))

        self.app.aboutToQuit.connect(self.cleanup_consoles)

#-----------------------------------------------------------------------------
# Main script
#-----------------------------------------------------------------------------

if __name__ == "__main__":
    app = QtGui.QApplication([])
    # Create our window
    win = SimpleWindow(app)
    win.show()
    
    # Very important, IPython-specific step: this gets GUI event loop
    # integration going, and it replaces calling app.exec_()
    win.ipkernel.start()
