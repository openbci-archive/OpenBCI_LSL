#!/usr/bin/python
'''
  lsl_openbci.py
  ---------------

  LSL is a 
'''

import sys
import open_bci_v3 as bci
import threading
from PyQt4 import QtGui,QtCore
from pylsl import StreamInfo,StreamOutlet
import signal
from collections import OrderedDict
import time
import gui


class StreamerLSL():

    def __init__(self,GUI=False):
      self.default_settings = OrderedDict()
      self.current_settings = OrderedDict()
      self.eeg_channels = 8
      self.aux_channels = 3

      if not GUI:
        self.initialize_board(autodetect=True)
      self.init_board_settings()

        
    def initialize_board(self,autodetect=False,port=None,daisy=None):
      print ("\n-------INSTANTIATING BOARD-------")
      if autodetect:
        self.board = bci.OpenBCIBoard()
      else:
        self.board = bci.OpenBCIBoard(port,daisy)
      self.eeg_channels = self.board.getNbEEGChannels()
      self.aux_channels = self.board.getNbAUXChannels()
      self.sample_rate = self.board.getSampleRate()
      print('{} EEG channels and {} AUX channels at {} Hz'.format(self.eeg_channels, self.aux_channels,self.sample_rate))

    def init_board_settings(self):
      #set default board configuration
      if self.eeg_channels == 16:
        self.default_settings["Number_Channels"] = [b'C']
      else:
        self.default_settings["Number_Channels"] = [b'c']
      for i in range(16):
        current = "channel{}".format(i+1)
        self.default_settings[current] = []
        self.default_settings[current].append(b'x')
        self.default_settings[current].append(str(i+1).encode())
        self.default_settings[current].append(b'0')           
        self.default_settings[current].append(b'6')
        self.default_settings[current].append(b'0')
        self.default_settings[current].append(b'1')
        self.default_settings[current].append(b'1')
        self.default_settings[current].append(b'0')
        self.default_settings[current].append(b'X')
      self.default_settings["SD_Card"] = b" "
      self.current_settings = self.default_settings.copy()
   
    def set_board_settings(self):
      for item in self.current_settings:
        if self.current_settings[item] != self.default_settings[item]:
          print(item)
          print(self.current_settings[item])
          for byte in self.current_settings[item]:
            self.board.ser.write(byte)
            time.sleep(.2)


    def send(self,sample):
        print(sample.channel_data)
        self.outlet_eeg.push_sample(sample.channel_data)
        self.outlet_aux.push_sample(sample.aux_data)

    def create_lsl(self,default=True,stream1=None,stream2=None):
      if default:
        info_eeg = StreamInfo("OpenBCI_EEG", 'EEG', self.eeg_channels, self.sample_rate,'float32',"openbci_eeg_id1");
        info_aux = StreamInfo("OpenBCI_AUX", 'AUX', self.aux_channels,self.sample_rate,'float32',"openbci_aux_id1")
        self.outlet_eeg = StreamOutlet(info_eeg)
        self.outlet_aux = StreamOutlet(info_aux)
      else:
        info_eeg = StreamInfo(stream1['name'], stream1['type'], 
                        stream1['channels'], stream1['sample_rate'],stream1['datatype'],stream1['id']);
        
        info_aux = StreamInfo(stream2['name'], stream2['type'], 
                        stream2['channels'], stream2['sample_rate'],stream2['datatype'],stream2['id']);
        self.outlet_eeg = StreamOutlet(info_eeg)
        self.outlet_aux = StreamOutlet(info_aux)
    def cleanUp():
        board.disconnect()
        print ("Disconnecting...")
        atexit.register(cleanUp)

    def start_streaming(self):
      boardThread = threading.Thread(target=self.board.start_streaming,args=(self.send,-1))
      boardThread.daemon = True # will stop on exit
      boardThread.start()
      print("Streaming data...")
    def stop_streaming(self):
      self.board.stop()

    def begin(self):

      print ("--------------INFO---------------")
      print ("User serial interface enabled...\n" + \
        "View command map at http://docs.openbci.com.\n" + \
        "Type /start to run -- and /stop before issuing new commands afterwards.\n" + \
        "Type /exit to exit. \n" + \
        "Board outputs are automatically printed as: \n" +  \
        "%  <tab>  message\n" + \
        "$$$ signals end of message")

      print("\n-------------BEGIN---------------")
      # Init board state
      # s: stop board streaming; v: soft reset of the 32-bit board (no effect with 8bit board)
      s = 'sv'
      # Tell the board to enable or not daisy module
      if self.board.daisy:
        s = s + 'C'
      else:
        s = s + 'c'
      # d: Channels settings back to default
      s = s + 'd'

      while(s != "/exit"):
        # Send char and wait for registers to set
        if (not s):
          pass
        elif("help" in s):
          print ("View command map at:" + \
              "http://docs.openbci.com/software/01-OpenBCI_SDK.\n" +\
              "For user interface: read README or view" + \
              "https://github.com/OpenBCI/OpenBCI_Python")

        elif self.board.streaming and s != "/stop":
          print ("Error: the board is currently streaming data, please type '/stop' before issuing new commands.")
        else:
          # read silently incoming packet if set (used when stream is stopped)
          flush = False

          if('/' == s[0]):
            s = s[1:]
            rec = False  # current command is recognized or fot

            if("T:" in s):
              lapse = int(s[string.find(s, "T:")+2:])
              rec = True
            elif("t:" in s):
              lapse = int(s[string.find(s, "t:")+2:])
              rec = True
            else:
              lapse = -1

            if("start" in s):
              # start streaming in a separate thread so we could always send commands in here
              boardThread = threading.Thread(target=self.board.start_streaming,args=(self.send,-1))
              boardThread.daemon = True # will stop on exit
              try:
                boardThread.start()
                print("Streaming data...")
              except:
                raise
              rec = True
            elif('test' in s):
              test = int(s[s.find("test")+4:])
              self.board.test_signal(test)
              rec = True
            elif('stop' in s):
              self.board.stop()
              rec = True
              flush = True
            if rec == False:
              print("Command not recognized...")

            elif s:
              for c in s:
                if sys.hexversion > 0x03000000:
                    self.board.ser.write(bytes(c, 'utf-8'))
                else:
                    self.board.ser.write(bytes(c))
                time.sleep(0.100)

            line = ''
            time.sleep(0.1) #Wait to see if the board has anything to report
            while self.board.ser.inWaiting():
              c = self.board.ser.read().decode('utf-8', errors='replace')
              line += c
              time.sleep(0.001)
              if (c == '\n') and not flush:
                line = ''

            if not flush:
              print(line)

          # Take user input
          #s = input('--> ')
          if sys.hexversion > 0x03000000:
            s = input('--> ')
          else:
             s = raw_input('--> ')


def main(argv):
  if not argv:
    app = QtGui.QApplication(sys.argv)
    window = gui.GUI()
    sys.exit(app.exec_())

  elif argv[0] == '--stream':
    lsl = StreamerLSL(GUI=False)
    lsl.create_lsl()
    lsl.begin()
  else:
    print("Command '%s' not recognized" % argv[0])

    

if __name__ == '__main__':
  main(sys.argv[1:])