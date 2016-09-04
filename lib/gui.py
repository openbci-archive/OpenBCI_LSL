'''
  gui.py
  ------

  This module creates and controls GUI function, using the PyQt4 framework. Using the GUI,
  the user can manipulate LSL parameters and board configuration, as well as control the 
  creation, start, and stop of the streams.


'''

from collections import OrderedDict,deque
import signal
import lib.streamerlsl as streamerlsl
import lib.open_bci_v3 as bci
import pyqtgraph as pg
import numpy as np
import time
import sys
import lib.filters as filters
np.set_printoptions(threshold=np.inf)


try:
  from PyQt4 import QtGui,QtCore
except ImportError:
  print("GUI unavailable: PyQt4 not installed. \n" + \
    "Use command line interface: \n" + \
  "   python lsl_openbci.py [port] --stream")
  sys.exit(0)


class GUI(QtGui.QWidget):
  def __init__(self):
    super(GUI, self).__init__()
    self.gui_setup()
    self.lsl = streamerlsl.StreamerLSL(GUI=True)
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    
  def gui_setup(self):
    self.setWindowTitle("OpenBCI - Lab Streaming Layer")
    self.setFixedSize(515,460)
    self.find_defaults()
    self.set_layout()
    self.show()


  def set_layout(self,monitor=False):
    #Layout
    self.layout = QtGui.QGridLayout()

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
    board_configuration.clicked.connect(self.board_config)

    # Display Monitor
    self.display_monitor = QtGui.QPushButton("Show Monitor >")
    self.display_monitor.setFixedWidth(150)
    self.display_monitor.clicked.connect(self.show_monitor)


    #PORT
    port_label = QtGui.QLabel("Port")
    self.port_entry = QtGui.QLineEdit()
    self.port_entry.setFixedWidth(150)
    self.port_entry.setText(self.port)

    #DAISY
    daisy_label = QtGui.QLabel("Daisy (16 chan)")
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
    # stream1_name_label.setFixedWidth(120)
    self.stream1_name_entry = QtGui.QLineEdit()
    self.stream1_name_entry.setText("OpenBCI_EEG")
    self.stream1_name_entry.setFixedWidth(125)


    stream1_type_label = QtGui.QLabel("Type")
    self.stream1_type_entry = QtGui.QLineEdit()
    self.stream1_type_entry.setText("EEG")
    self.stream1_type_entry.setFixedWidth(125)
    stream1_channels_label = QtGui.QLabel("# of Channels")
    self.stream1_channels_entry  = QtGui.QLineEdit()
    self.stream1_channels_entry.setText(str(self.data_channels))
    self.stream1_channels_entry.setFixedWidth(125)
    stream1_hz_label = QtGui.QLabel("Sample Rate")
    self.stream1_hz_entry  = QtGui.QLineEdit()
    self.stream1_hz_entry.setText(str(self.sample_rate))
    self.stream1_hz_entry.setFixedWidth(125)
    stream1_datatype_label = QtGui.QLabel("Data Type")
    self.stream1_datatype_entry  = QtGui.QLineEdit()
    self.stream1_datatype_entry.setText("float32")
    self.stream1_datatype_entry.setFixedWidth(125)
    stream1_streamid_label = QtGui.QLabel("Stream ID")
    self.stream1_streamid_entry  = QtGui.QLineEdit()
    self.stream1_streamid_entry.setText("openbci_eeg_id1")
    self.stream1_streamid_entry.setFixedWidth(125)
    #stream2
    stream2_label = QtGui.QLabel("Stream 2")
    stream2_label.setFont(title_font)
    stream2_name_label = QtGui.QLabel("Name")
    # stream2_name_label.setFixedWidth(120)

    self.stream2_name_entry = QtGui.QLineEdit()
    self.stream2_name_entry.setText("OpenBCI_AUX")
    self.stream2_name_entry.setFixedWidth(125)
    stream2_type_label = QtGui.QLabel("Type")
    self.stream2_type_entry = QtGui.QLineEdit()
    self.stream2_type_entry.setText("AUX")
    self.stream2_type_entry.setFixedWidth(125)
    stream2_channels_label = QtGui.QLabel("# of Channels")
    self.stream2_channels_entry  = QtGui.QLineEdit()
    self.stream2_channels_entry.setText(str(self.aux_channels))
    self.stream2_channels_entry.setFixedWidth(125)
    stream2_hz_label = QtGui.QLabel("Sample Rate")
    self.stream2_hz_entry  = QtGui.QLineEdit()
    self.stream2_hz_entry.setText(str(self.sample_rate))
    self.stream2_hz_entry.setFixedWidth(125)
    stream2_datatype_label = QtGui.QLabel("Data Type")
    self.stream2_datatype_entry  = QtGui.QLineEdit()
    self.stream2_datatype_entry.setText("float32")
    self.stream2_datatype_entry.setFixedWidth(125)
    stream2_streamid_label = QtGui.QLabel("Stream ID")
    self.stream2_streamid_entry  = QtGui.QLineEdit()
    self.stream2_streamid_entry.setText("openbci_aux_id1")
    self.stream2_streamid_entry.setFixedWidth(125)

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
    self.layout.addWidget(title,0,0,1,3)    
    self.layout.addWidget(verticalLine0,1,0,1,4)
    self.layout.addWidget(port_label,2,0)
    self.layout.addWidget(self.port_entry,2,1,1,2)
    self.layout.addWidget(daisy_label,3,0)
    self.layout.addWidget(self.daisy_entry,3,1)
    self.layout.addWidget(board_configuration,4,0)
    self.layout.addWidget(self.display_monitor,4,2,1,1)

    #stream config area
    stream_widget = QtGui.QWidget()
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
    stream_widget.setLayout(stream_layout)
    stream_widget.setFixedWidth(500)
    self.layout.addWidget(verticalLine1,5,0,1,4)
    self.layout.addWidget(stream_widget,6,0,1,4)
    self.layout.addWidget(verticalLine2,7,0,1,4)
    self.layout.addWidget(self.connect_button,8,0,1,1)
    self.layout.addWidget(self.start_button,9,0,1,1)
    self.layout.addWidget(self.console,8,1,2,1)

    self.setLayout(self.layout)
  
  def show_monitor(self):
    self.smw = Stream_Monitor_Widget(parent=self)
    self.smw.setFixedWidth(985)
    self.layout.addWidget(self.smw,0,3,10,1000)
    self.setFixedSize(1500,460)
    self.display_monitor.setText("Hide Monitor <")
    self.display_monitor.clicked.disconnect(self.show_monitor)
    self.display_monitor.clicked.connect(self.hide_monitor)

  def hide_monitor(self):
    self.layout.removeWidget(self.smw)
    self.lsl.new_data.disconnect(self.smw.update_plot)
    self.setFixedSize(510,460)
    self.display_monitor.setText("Show Monitor >")
    self.display_monitor.clicked.disconnect(self.hide_monitor)
    self.display_monitor.clicked.connect(self.show_monitor)


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
    self.console.setText("  Searching for board...")

    # Get port
    port = self.port_entry.text()

    #Throw error if port is at not specified ('--')
    if port == "--":
      self.console.setText("  Error: No Port Specified")
      print("Error: No Port Specified")
      return
    #Get daisy setting
    if self.daisy_entry.currentIndex:
      daisy=False
    else:
      daisy=True
    try:
      self.lsl.initialize_board(port=port,daisy=daisy)
    except:
      self.lsl.board.disconnect()  #close the serial
      self.console.setText("  Error connecting to the board")
      print("Error connecting to the board") 
      return
    
    self.lsl.set_board_settings()
    self.start_button.setEnabled(True)
    self.console.setText("  Board connected. Ready to stream")
    self.connect_button.setText("Disconnect")
    self.connect_button.clicked.disconnect(self.connect_board)
    self.connect_button.clicked.connect(self.disconnect_board)
  
  def disconnect_board(self):
    self.lsl.board.disconnect()
    try:
      self.lsl.outlet_eeg.close_stream()
      self.lsl.outlet_eeg.close_stream()
    except:
      pass
    self.connect_button.setText("Connect")
    self.console.setText("  Board disconnected")
    self.connect_button.clicked.disconnect(self.disconnect_board)
    self.connect_button.clicked.connect(self.connect_board)
    if self.start_button.text() == "Stop Streaming": 
      self.start_button.clicked.disconnect(self.stop_streaming)
      self.start_button.clicked.connect(self.start_streaming)
    elif self.start_button.text() == "Resume Streaming":
      self.start_button.clicked.disconnect(self.start_streaming)
      self.start_button.clicked.connect(self.init_streaming)
    # elif self.start_button.text() == "Start Streaming":
    #   self.start_button.clicked.disconnect(self.init_streaming)

    self.start_button.setEnabled(False)
    self.start_button.setText("Start Streaming")


  def init_streaming(self):
    #create LSL stream
    try:
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
    except:
      self.console.setText("  LSL Error: check your inputs")
      print("LSL Error: check your inputs")
      return
    try:
      self.lsl.create_lsl(default=False,stream1=stream1,stream2=stream2)
    except:
      self.console.setText("  LSL Error: check your inputs")
    try:
      self.lsl.start_streaming()
    except:
      self.console.setText("  Streaming could not start. Check your board/dongle.")
      return
    else:
      self.console.setText("  Streaming data")
    self.start_button.setText("Stop Streaming")
    self.start_button.clicked.disconnect(self.init_streaming)
    self.start_button.clicked.connect(self.stop_streaming)

  def start_streaming(self):
    self.lsl.start_streaming()
    self.console.setText("  Streaming data.")
    self.start_button.setText("Stop Streaming")
    self.start_button.clicked.disconnect(self.start_streaming)
    self.start_button.clicked.connect(self.stop_streaming)

  def stop_streaming(self):
    self.console.setText("  Streaming paused.")
    self.lsl.stop_streaming()
    self.start_button.setText("Resume Streaming")
    self.start_button.clicked.disconnect(self.stop_streaming)
    self.start_button.clicked.connect(self.start_streaming)

  def board_config(self):
    self.config_widget = Board_Config_Widget(parent=self)
    self.config_widget.show()

class Stream_Monitor_Widget(QtGui.QWidget):

  def __init__(self,parent=None):
    QtGui.QWidget.__init__(self)
    self.parent = parent
    self.curves = OrderedDict()
    self.data_buffer = OrderedDict()
    self.filtered_data = OrderedDict()
    self.create_plot()
    self.filters = filters.Filters(self.buffer_size,1,50)

    self.parent.lsl.new_data.connect(self.update_plot)



  def create_plot(self):

    self.stream_scroll = pg.PlotWidget(title='Stream Monitor')

    if not self.parent.daisy_entry.currentIndex():
      self.channel_count = 16
      self.buffer_size = 1000
      samples = 125
      self.stream_scroll.setYRange(-.5,16,padding=.01)
    else:
      self.channel_count = 8
      samples = 250
      self.buffer_size = 2000
      self.stream_scroll.setYRange(-.5,8,padding=.01)

    self.stream_scroll_time_axis = np.linspace(-5,0,samples)
    self.stream_scroll.setXRange(-5,0, padding=.01)
    self.stream_scroll.setLabel('bottom','Time','Seconds')
    self.stream_scroll.setLabel('left','Channel')
    for i in range(self.channel_count-1,-1,-1):
      self.data_buffer['buffer_channel{}'.format(i+1)] = deque([0]*self.buffer_size)
      self.filtered_data['filtered_channel{}'.format(i+1)] = deque([0]*samples)
      self.curves['curve_channel{}'.format(i+1)] = self.stream_scroll.plot()
      self.curves['curve_channel{}'.format(i+1)].setData(x=self.stream_scroll_time_axis,y=([point+i+1 for point in self.filtered_data['filtered_channel{}'.format(i+1)]]))
    self.set_layout()

  def set_layout(self):
    self.layout = QtGui.QGridLayout()
    self.layout.addWidget(self.stream_scroll,0,0)
    self.setLayout(self.layout)

  @QtCore.pyqtSlot('PyQt_PyObject')
  def update_plot(self,data):
    for i in range(self.channel_count):
      self.data_buffer['buffer_channel{}'.format(i+1)].popleft()
      self.data_buffer['buffer_channel{}'.format(i+1)].append(data.channel_data[i])
      
      current = self.data_buffer['buffer_channel{}'.format(i+1)]
      current = self.filters.high_pass(current)
      current = [((point/100 + (i+1))) for point in current]
      
      self.filtered_data['filtered_channel{}'.format(i+1)].popleft()
      self.filtered_data['filtered_channel{}'.format(i+1)].append(current[-1])
      filtered = self.filtered_data['filtered_channel{}'.format(i+1)]
      self.curves['curve_channel{}'.format(i+1)].setData(x=self.stream_scroll_time_axis,y=([point for point in filtered]))

class Board_Config_Widget(QtGui.QWidget):
  def __init__(self,parent=None):
    QtGui.QWidget.__init__(self)
    self.parent = parent
    self.lsl = parent.lsl
    self.setFixedSize(700,715)
    self.setWindowTitle("Board Configuration Window")
    self.set_layout()
  
  def set_layout(self):    
    self.layout = QtGui.QGridLayout()
    self.channel_options_layout = QtGui.QGridLayout()

    verticalLine0 = QtGui.QFrame()
    verticalLine0.setFrameShape(QtGui.QFrame().HLine)
    verticalLine0.setFrameShadow(QtGui.QFrame().Sunken)
    verticalLine1 = QtGui.QFrame()
    verticalLine1.setFrameShape(QtGui.QFrame().HLine)
    verticalLine1.setFrameShadow(QtGui.QFrame().Sunken)
    verticalLine2 = QtGui.QFrame()
    verticalLine2.setFrameShape(QtGui.QFrame().HLine)
    verticalLine2.setFrameShadow(QtGui.QFrame().Sunken)
    #Title
    title = QtGui.QLabel("Board Settings")
    title_font = QtGui.QFont('default',weight=QtGui.QFont.Bold)
    title_font.setPointSize(12)
    title.setFont(title_font)

  
    number_of_chans = int(self.parent.stream1_channels_entry.text())

    if self.parent.daisy_entry.currentIndex() == 0:
      daisy = True
    else:
      daisy = False
    #Channel Number
    if daisy:
      channel_number = QtGui.QLabel("Number of Channels: {}  [Daisy {}]".format("16", "Enabled"))
    else:
      channel_number = QtGui.QLabel("Number of Channels: {}  [Daisy {}]".format("8", "Disabled"))


    #SD Card Options
    sd_label = QtGui.QLabel("SD Card Record:")
    self.sd_entry = QtGui.QComboBox()
    self.sd_entry.addItem("None")
    self.sd_entry.addItem("5 MIN")
    self.sd_entry.addItem("15 MIN")
    self.sd_entry.addItem("30 MIN")
    self.sd_entry.addItem("1 HR")
    self.sd_entry.addItem("2 HR")
    self.sd_entry.addItem("4 HR")
    self.sd_entry.addItem("12 HR")
    self.sd_entry.addItem("24 HR")
    self.sd_entry.addItem("14 SEC")

    #Save Button
    save_button = QtGui.QPushButton("Save Settings")
    save_button.clicked.connect(self.save_settings)

    #Set rest of the layout
    self.layout.addWidget(title,0,0)
    self.layout.addWidget(verticalLine0,1,0,1,4)
    self.layout.addWidget(channel_number,2,0)
    self.layout.addWidget(verticalLine2,3,0,1,4)
    self.set_channel_options_layout()
    self.layout.addLayout(self.channel_options_layout,4,0,1,4)
    self.layout.addWidget(sd_label,5,0)
    self.layout.addWidget(self.sd_entry,5,1)
    self.layout.addWidget(verticalLine1,6,0,1,4)
    self.layout.addWidget(save_button,7,0,)
    self.setLayout(self.layout)

  def set_channel_options_layout(self):
    option_headers = []
    #Channel options
    self.channels = OrderedDict()
    self.channel_attributes = ['channel_label{}','power_entry{}','gain{}','input{}','bias{}','srb2{}','srb1{}']
    self.NUM_ATTRIBUTES = len(self.channel_attributes)

    #header font
    header_font = QtGui.QFont('default',weight=QtGui.QFont.Bold)
    header_font.setPointSize(8)

    #Option Headers
    channel_number = QtGui.QLabel("CHANNEL")
    option_headers.append(channel_number)
    channel_power = QtGui.QLabel("POWER")
    option_headers.append(channel_power)
    channel_gain = QtGui.QLabel("GAIN")
    option_headers.append(channel_gain)
    channel_input = QtGui.QLabel("INPUT")
    option_headers.append(channel_input)
    channel_bias = QtGui.QLabel("BIAS")
    option_headers.append(channel_bias)
    channel_srb2 = QtGui.QLabel("SRB2")
    option_headers.append(channel_srb2)
    channel_srb1 = QtGui.QLabel("SRB1")
    option_headers.append(channel_srb1)


    # Iteratively add options for all channels.
    # There is a dictionary to hold all of the channels,
    # and then each channel has its own subdictionary to
    # hold all of the attributes. This method fills all of those
    # things out.
    for i in range(16):
      current = "channel{}".format(i+1)
      self.channels[current] = OrderedDict()
      for j,attribute in enumerate(self.channel_attributes):
        self.channels[current][attribute.format(i+1)] = ''
        current_attribute = attribute.format(i+1)
        if j == 0:
          self.channels[current][current_attribute] = QtGui.QLabel("Channel {}".format(i+1))
        elif j == 1:
          self.channels[current][current_attribute] = QtGui.QComboBox()
          self.channels[current][current_attribute].addItem("On")
          self.channels[current][current_attribute].addItem("Off")
          index = int((self.lsl.current_settings[current][j+1]).decode())
          self.channels[current][current_attribute].setCurrentIndex(index)
        elif j == 2:
          self.channels[current][current_attribute] = QtGui.QComboBox()
          self.channels[current][current_attribute].addItem("0")
          self.channels[current][current_attribute].addItem("2")
          self.channels[current][current_attribute].addItem("4")
          self.channels[current][current_attribute].addItem("6")
          self.channels[current][current_attribute].addItem("8")
          self.channels[current][current_attribute].addItem("12")
          self.channels[current][current_attribute].addItem("24")
          index = int((self.lsl.current_settings[current][j+1]).decode())
          self.channels[current][current_attribute].setCurrentIndex(index)
        elif j == 3:
          self.channels[current][current_attribute] = QtGui.QComboBox()
          self.channels[current][current_attribute].addItem("Normal")
          self.channels[current][current_attribute].addItem("Shorted")
          self.channels[current][current_attribute].addItem("Bias Meas")
          self.channels[current][current_attribute].addItem("MVDD")
          self.channels[current][current_attribute].addItem("Temp")
          self.channels[current][current_attribute].addItem("Test Sig")
          self.channels[current][current_attribute].addItem("Bias DRP")
          self.channels[current][current_attribute].addItem("Bias DRN")
          index = int((self.lsl.current_settings[current][j+1]).decode())
          self.channels[current][current_attribute].setCurrentIndex(index)
        elif j == 4:
          self.channels[current][current_attribute] = QtGui.QComboBox()
          self.channels[current][current_attribute].addItem("Include")
          self.channels[current][current_attribute].addItem("Don't Include")
          index = 1 - int((self.lsl.current_settings[current][j+1]).decode())
          self.channels[current][current_attribute].setCurrentIndex(index)
        elif j == 5:
          self.channels[current][current_attribute] = QtGui.QComboBox()
          self.channels[current][current_attribute].addItem("Connect")
          self.channels[current][current_attribute].addItem("Disconnect")
          index = 1 - int((self.lsl.current_settings[current][j+1]).decode())
          self.channels[current][current_attribute].setCurrentIndex(index)
        elif j == 6:
          self.channels[current][current_attribute] = QtGui.QComboBox()
          self.channels[current][current_attribute].addItem("Disconnect")
          self.channels[current][current_attribute].addItem("Connect")
          index = int((self.lsl.current_settings[current][j+1]).decode())
          self.channels[current][current_attribute].setCurrentIndex(index)


    # Set channel options layout
    # Set the headers
    for header in option_headers:
      header.setFont(header_font)
    for i,header in enumerate(option_headers):
      self.channel_options_layout.addWidget(header,2,i)
    # Set the options
    for i,ch in enumerate(self.channels):
      for j,attribute in enumerate(self.channels[ch]):
        if self.parent.daisy_entry.currentIndex() == 0:
          current = self.channels[ch][attribute]
          self.channel_options_layout.addWidget(current,i+3,j)
          self.setFixedSize(700,715)

        else:
          if i < 8:
            current = self.channels[ch][attribute]
            self.channel_options_layout.addWidget(current,i+3,j)
          else:
            current = self.channels[ch][attribute]
            current.hide()
            self.channel_options_layout.addWidget(current,i+3,j)
          self.setFixedSize(700,450)


  def channel_number_select(self):
    print(self.parent.daisy_entry.currentIndex())

  def save_settings(self):

    self.settings = OrderedDict()
    sd_commands = [b" ", b'A', b'S', b'F',b'G',b'H',b'J',b'K',b'L']

    #Channel number
    if self.parent.daisy_entry.currentIndex() == 1:
      self.settings['Number_Channels'] = [b'c']
      channel_number = 8
    elif self.parent.daisy_entry.currentIndex() == 0:
      self.settings['Number_Channels'] = [b'C']
      channel_number = 16


    for i in range(16):
      current = "channel{}".format(i+1)
      self.settings[current] = []
      self.settings[current].append(b'x')
      self.settings[current].append(str.encode(str(i+1)))
      for j,attribute in enumerate(self.channel_attributes):
        temp = self.channels[current][attribute.format(i+1)]
        if j == 1:
            self.settings[current].append(str(temp.currentIndex()).encode())
        elif j == 2:
          self.settings[current].append(str(temp.currentIndex()).encode())
        elif j == 3:
          self.settings[current].append(str(temp.currentIndex()).encode())
        elif j == 4:
          self.settings[current].append(str(1-temp.currentIndex()).encode())
        elif j == 5:
          self.settings[current].append(str(1-temp.currentIndex()).encode())
        elif j == 6:
          self.settings[current].append(str(temp.currentIndex()).encode())  
      self.settings[current].append(b'X')

    sd_index = self.sd_entry.currentIndex()
    self.settings["SD_Card"] = [sd_commands[sd_index]]


    for item in self.settings:
      if self.settings[item] != self.parent.lsl.current_settings[item]:
        self.parent.lsl.current_settings[item] = self.settings[item]
    self.close()