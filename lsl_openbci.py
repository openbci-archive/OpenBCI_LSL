#!/usr/bin/python

import sys
import open_bci_v3 as bci
import threading
from PyQt4 import QtGui,QtCore
from pylsl import StreamInfo,StreamOutlet
import signal


class StreamerLSL():

    def __init__(self,GUI=False):
      if not GUI:
        self.initialize_board(autodetect=True)
        
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
                        # print('%\t'+line[:-1])
                        line = ''

                if not flush:
                    print(line)

            # Take user input
            #s = input('--> ')
            if sys.hexversion > 0x03000000:
                s = input('--> ')
            else:
                s = raw_input('--> ')


class GUI(QtGui.QWidget):
  def __init__(self):
    super(GUI, self).__init__()
    self.gui_setup()
    self.lsl = StreamerLSL(GUI=True)
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    
  def gui_setup(self):
    self.setWindowTitle("OpenBCI - Lab Streaming Layer")
    # self.resize(520, 400)
    self.setFixedSize(500,460)
    self.find_defaults()
    self.set_layout()


  def set_layout(self):
    #Layout
    layout = QtGui.QGridLayout()

    #title font
    header_font = QtGui.QFont('default',weight=QtGui.QFont.Bold)
    header_font.setPointSize(16)
    title_font = QtGui.QFont('default',weight=QtGui.QFont.Bold)
    title_font.setUnderline(True)


    title = QtGui.QLabel("OpenBCI - Lab Streaming Layer")
    title.setFont(header_font)


    #Board Configuration
    board_configuration = QtGui.QPushButton("Board Config")
    board_configuration.setFixedWidth(120)

    #PORT
    port_label = QtGui.QLabel("Port")
    self.port_entry = QtGui.QLineEdit()
    self.port_entry.setFixedWidth(150)
    self.port_entry.setText(self.port)

    #DAISY
    daisy_label = QtGui.QLabel("Daisy")
    self.daisy_entry = QtGui.QComboBox()
    self.daisy_entry.addItem("Enabled")
    self.daisy_entry.addItem("Disabled")
    self.daisy_entry.setFixedWidth(100)
    if self.daisy:
      self.daisy_entry.setCurrentIndex(0)
    else:
      self.daisy_entry.setCurrentIndex(1)

    #lines and separators
    verticalLine0 = QtGui.QFrame()
    verticalLine0.setFrameShape(QtGui.QFrame().HLine)
    verticalLine0.setFrameShadow(QtGui.QFrame().Sunken)
    verticalLine1 = QtGui.QFrame()
    verticalLine1.setFrameShape(QtGui.QFrame().HLine)
    verticalLine1.setFrameShadow(QtGui.QFrame().Sunken)
    verticalLine2 = QtGui.QFrame()
    verticalLine2.setFrameShape(QtGui.QFrame().HLine)
    verticalLine2.setFrameShadow(QtGui.QFrame().Sunken)
    horizontalLine = QtGui.QFrame()
    horizontalLine.setFrameShape(QtGui.QFrame().VLine)
    horizontalLine.setFrameShadow(QtGui.QFrame().Sunken)


    #STREAM CONFIG
    stream_layout = QtGui.QGridLayout()
    title_font.setUnderline(True)
    #stream 1
    stream1_label = QtGui.QLabel("Stream 1")
    stream1_label.setFont(title_font)
    stream1_name_label = QtGui.QLabel("Name")
    self.stream1_name_entry = QtGui.QLineEdit()
    self.stream1_name_entry.setText("OpenBCI_EEG")

    stream1_type_label = QtGui.QLabel("Type")
    self.stream1_type_entry = QtGui.QLineEdit()
    self.stream1_type_entry.setText("EEG")
    stream1_channels_label = QtGui.QLabel("# of Channels")
    self.stream1_channels_entry  = QtGui.QLineEdit()
    self.stream1_channels_entry.setText(str(self.data_channels))
    stream1_hz_label = QtGui.QLabel("Sample Rate")
    self.stream1_hz_entry  = QtGui.QLineEdit()
    self.stream1_hz_entry.setText(str(self.sample_rate))
    stream1_datatype_label = QtGui.QLabel("Data Type")
    self.stream1_datatype_entry  = QtGui.QLineEdit()
    self.stream1_datatype_entry.setText("float32")
    stream1_streamid_label = QtGui.QLabel("Stream ID")
    self.stream1_streamid_entry  = QtGui.QLineEdit()
    self.stream1_streamid_entry.setText("openbci_eeg_id1")
    #stream2
    stream2_label = QtGui.QLabel("Stream 2")
    stream2_label.setFont(title_font)
    stream2_name_label = QtGui.QLabel("Name")
    self.stream2_name_entry = QtGui.QLineEdit()
    self.stream2_name_entry.setText("OpenBCI_AUX")
    stream2_type_label = QtGui.QLabel("Type")
    self.stream2_type_entry = QtGui.QLineEdit()
    self.stream2_type_entry.setText("AUX")
    stream2_channels_label = QtGui.QLabel("# of Channels")
    self.stream2_channels_entry  = QtGui.QLineEdit()
    self.stream2_channels_entry.setText(str(self.aux_channels))
    stream2_hz_label = QtGui.QLabel("Sample Rate")
    self.stream2_hz_entry  = QtGui.QLineEdit()
    self.stream2_hz_entry.setText(str(self.sample_rate))
    stream2_datatype_label = QtGui.QLabel("Data Type")
    self.stream2_datatype_entry  = QtGui.QLineEdit()
    self.stream2_datatype_entry.setText("float32")
    stream2_streamid_label = QtGui.QLabel("Stream ID")
    self.stream2_streamid_entry  = QtGui.QLineEdit()
    self.stream2_streamid_entry.setText("openbci_aux_id1")

    #Connect Board
    self.connect_button = QtGui.QPushButton("Connect Board")
    self.connect_button.clicked.connect(self.connect_board)
    self.connect_button.setFixedWidth(150)
    #Start Streaming
    self.start_button = QtGui.QPushButton("Start Streaming")
    self.start_button.clicked.connect(self.init_streaming)
    self.start_button.setEnabled(False)
    self.start_button.setFixedWidth(150)

    #Console
    self.console = QtGui.QLineEdit()
    self.console.setStyleSheet("font-family:Times;font-size:17px;color: rgb(255, 255, 255);background: rgb(0, 0, 0)")
    self.console.setReadOnly(True)
    self.consoleSizePolicy = QtGui.QSizePolicy()
    self.consoleSizePolicy.setVerticalPolicy(QtGui.QSizePolicy.Expanding)
    self.console.setSizePolicy(self.consoleSizePolicy)
    self.console.setFixedWidth(300)
    self.console.setText("  --")
    # self.console.setAlignment(QtCore.Qt.AlignRight)

    spacer = QtGui.QSpacerItem(20,40,QtGui.QSizePolicy.Minimum,QtGui.QSizePolicy.Expanding)
    #set layout
    layout.addWidget(title,0,0,1,3)    
    layout.addWidget(verticalLine0,1,0,1,4)
    layout.addWidget(port_label,2,0)
    layout.addWidget(self.port_entry,2,1,1,2)
    layout.addWidget(daisy_label,3,0)
    layout.addWidget(self.daisy_entry,3,1)
    layout.addWidget(board_configuration,4,0,1,3)    
    #stream config area
    stream_layout.addWidget(horizontalLine,1,2,7,1)
    stream_layout.addWidget(stream1_label,0,0,1,2)
    stream_layout.addWidget(stream1_name_label,1,0)
    stream_layout.addWidget(self.stream1_name_entry,1,1)
    stream_layout.addWidget(stream1_type_label,2,0)
    stream_layout.addWidget(self.stream1_type_entry,2,1)
    stream_layout.addWidget(stream1_channels_label,3,0)
    stream_layout.addWidget(self.stream1_channels_entry,3,1)
    stream_layout.addWidget(stream1_hz_label,4,0)
    stream_layout.addWidget(self.stream1_hz_entry,4,1)
    stream_layout.addWidget(stream1_datatype_label,5,0)
    stream_layout.addWidget(self.stream1_datatype_entry,5,1)
    stream_layout.addWidget(stream1_streamid_label,6,0)
    stream_layout.addWidget(self.stream1_streamid_entry,6,1)
    stream_layout.addWidget(stream2_label,0,2,1,3)
    stream_layout.addWidget(stream2_name_label,1,3)
    stream_layout.addWidget(self.stream2_name_entry,1,4)
    stream_layout.addWidget(stream2_type_label,2,3)
    stream_layout.addWidget(self.stream2_type_entry,2,4)
    stream_layout.addWidget(stream2_channels_label,3,3)
    stream_layout.addWidget(self.stream2_channels_entry,3,4)
    stream_layout.addWidget(stream2_hz_label,4,3)
    stream_layout.addWidget(self.stream2_hz_entry,4,4)
    stream_layout.addWidget(stream2_datatype_label,5,3)
    stream_layout.addWidget(self.stream2_datatype_entry,5,4)
    stream_layout.addWidget(stream2_streamid_label,6,3)
    stream_layout.addWidget(self.stream2_streamid_entry,6,4)
    layout.addWidget(verticalLine1,5,0,1,4)
    layout.addLayout(stream_layout,6,0,1,4)
    layout.addWidget(verticalLine2,7,0,1,4)

    layout.addWidget(self.connect_button,8,0,1,1)
    layout.addWidget(self.start_button,9,0,1,1)
    # layout.addItem(spacer,8,2,1,1)
    layout.addWidget(self.console,8,1,2,1)

    self.setLayout(layout)
    self.show()

  
  def find_defaults(self):
    try:
      board = bci.OpenBCIBoard(print_enable=False)
      self.port = board.port
      self.daisy = board.daisy
      self.data_channels = board.getNbEEGChannels()
      self.aux_channels = board.getNbAUXChannels()
      self.sample_rate = board.getSampleRate()
      board.disconnect()
    except Exception as e:
      print(str(e))
      print("Using default configurations")
      self.port = "--"
      self.daisy = None
      self.data_channels = 8
      self.aux_channels = 3
      self.sample_rate = 250

  def connect_board(self):
    self.connect_button.setText("Disconnect")
    self.connect_button.clicked.disconnect(self.connect_board)
    self.connect_button.clicked.connect(self.disconnect_board)
    port = self.port_entry.text()
    if self.daisy_entry.currentIndex:
      daisy=False
    else:
      daisy=True
    try:
      self.lsl.initialize_board(port=port,daisy=daisy)
      self.start_button.setEnabled(True)
      self.console.setText("  Board connected. Ready to stream")
    except:
       self.console.setText("  Error connecting to the board")
  
  def disconnect_board(self):
    self.lsl.board.disconnect()
    self.connect_button.setText("Connect")
    self.console.setText("  Board disconnected")

    self.connect_button.clicked.disconnect(self.disconnect_board)
    self.connect_button.clicked.connect(self.connect_board)
    self.start_button.clicked.disconnect(self.stop_streaming)
    self.start_button.clicked.connect(self.start_streaming)
    self.start_button.setEnabled(False)
    self.start_button.setText("Start Streaming")


  def init_streaming(self):
    #create LSL stream
    stream1 = {
        'name' : self.stream1_name_entry.text(),
        'type' : self.stream1_type_entry.text(),
        'channels' : int(self.stream1_channels_entry.text()),
        'sample_rate' : float(self.stream1_hz_entry.text()),
        'datatype' : self.stream1_datatype_entry.text(),
        'id' : self.stream1_streamid_entry.text()
    }
    stream2 = {
        'name' : self.stream2_name_entry.text(),
        'type' : self.stream2_type_entry.text(),
        'channels' : int(self.stream2_channels_entry.text()),
        'sample_rate' : float(self.stream2_hz_entry.text()),
        'datatype' : self.stream2_datatype_entry.text(),
        'id' : self.stream2_streamid_entry.text()
    }
    try:
      self.lsl.create_lsl(default=False,stream1=stream1,stream2=stream2)
    except:
      self.console.setText("  LSL Error: check your inputs")
    try:
      self.lsl.start_streaming()
    except:
      self.console.setText("  Streaming could not start. Check your board/dongle.")
    else:
      self.console.setText("  Streaming data")
    self.start_button.setText("Stop Streaming")
    self.start_button.clicked.disconnect(self.init_streaming)
    self.start_button.clicked.connect(self.stop_streaming)

  def start_streaming(self):
    self.lsl.start_streaming()
    self.console.setText("  Streaming data")
    self.start_button.setText("Stop Streaming")
    self.start_button.clicked.disconnect(self.start_streaming)
    self.start_button.clicked.connect(self.stop_streaming)

  def stop_streaming(self):
    self.lsl.stop_streaming()
    self.console.setText("  Streaming paused.")
    self.start_button.setText("Resume Streaming")
    self.start_button.clicked.disconnect(self.stop_streaming)
    self.start_button.clicked.connect(self.start_streaming)


def main(argv):
  if not argv:
    app = QtGui.QApplication(sys.argv)
    gui = GUI()
    sys.exit(app.exec_())

  elif argv[0] == '--stream':
    lsl = StreamerLSL(GUI=False)
    lsl.create_lsl()
    lsl.begin()
  else:
    print("Command '%s' not recognized" % argv[0])

    

if __name__ == '__main__':
  main(sys.argv[1:])