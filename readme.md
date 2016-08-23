OpenBCI_LSL
==============

****Currently Under Development****

This tutorial contains information on how to stream [OpenBCI](http://openbci.com/) data through the [Lab Streaming Layer (LSL)](https://github.com/sccn/labstreaminglayer) network protocol.

Lab streaming layer is a networking system for real time streaming, recording, and analysis of time-series data. LSL can be used to connect OpenBCI to applications that can record, analyze, and manipulate the data, such as Matlab, NeuroPype, BCILAB, and others.

The [OpenBCI_LSL](link) repo contains a Python script that establishes an LSL stream of OpenBCI data, as well as the libraries and files needed to run LSL.


# SETUP

1. **Download or clone the [OpenBCI_LSL](link) repo from Github**

2. **Download and install [Python](https://www.python.org/downloads/) (either version 2 or 3).**

	Python might already be installed on your computer. Type `python --version` to check if you have Python version 2.7+ installed. 

3. **Install Python requirements**

	Navigate to the "OpenBCI_LSL" folder on your command line and terminal, and type:

	`pip install -r requirements.txt`

	Note: If you get the message "pip: command not found", you need to install pip: `sudo easy_install pip`. Then retry the command above.


# Usage

### Simple Stream

If you would like to start an OpenBCI stream with the default board settings, go the the "OpenBCI_LSL" folder and simply type the following command:

`python openbci_lsl.py --stream`

After board initialization, you are now ready to start streaming.

To begin streaming, type `/start`

To stop streaming, type `/stop`

To disconnect from the serial port, type `/exit` 

If you get an error message at any point, check the [Troubleshooting](#troubleshooting) section, or pull up an issue on the Github repository.

### GUI
If you would like the ability to configure the board and LSL stream with advanced settings, you can do so by running the GUI. The GUI comes up by default if you run the program with no flags:

`python openbci_lsl.py`

# Troubleshooting

Here are some frequently encountered errors and their solutions:

1. **"WARNING:root:Skipped x bytes before start found"**

	This is a known issue with the Python serial port parser. This should not cause any major issues with your data, and it can be ignored.

2. **"UnicodeDecodeError: 'utf-8' codec can't decode byte 0xc0 in position 0: invalid start byte"**

	This is another known issue with the serial port parser. If you get this error, simply unplug the dongle and power down the board and try again.

