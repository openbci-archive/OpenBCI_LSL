#!/usr/bin/python
'''
  openbci_lsl.py
  ---------------

  This is the main module for establishing an OpenBCI stream through the Lab Streaming Layer (LSL).

  Lab streaming layer is a networking system for real time streaming, recording, and analysis of time-series 
  data. LSL can be used to connect OpenBCI to applications that can record, analyze, and manipulate the data, 
  such as Matlab, NeuroPype, BCILAB, and others.

  To run the program as a GUI application, enter `python openbci_lsl.py`. 

  To run the program as a command line interface, enter `python openbci_lsl.py [port] --stream`. The port argument
  is optional, since the program automatically detects the OpenBCI port. However, if this functionality fails, the 
  port must be specified as an argument.

  For more information, see the readme on the Github repo:

  https://github.com/gabrielibagon/OpenBCI_LSL

'''

import sys
import lib.streamerlsl as streamerlsl

def main(argv):
  
  # if no arguments are provided, default to the GUI application
  if not argv:
    import lib.gui as gui
    from PyQt4 import QtGui
    app = QtGui.QApplication(sys.argv)
    window = gui.GUI()
    sys.exit(app.exec_())
 
  # if user specifies CLI using the "--stream" argument, check if a port is also specified
  else:
    if argv[0] == '--stream':
      lsl = streamerlsl.StreamerLSL(GUI=False)
    else:
      try:
        if argv[1] != '--stream':
          print ("Command '%s' not recognized" % argv[1])
          return
      except IndexError:
        print("Command '%s' not recognized" % argv[0])
        return
      port = argv[0]
      lsl = streamerlsl.StreamerLSL(port=port,GUI=False)
    lsl.create_lsl()
    lsl.begin()
    

if __name__ == '__main__':
  main(sys.argv[1:])
