import serial as sr
import numpy as np
import scipy as sc

from matplotlib.lines import Line2D
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from PyQt4 import QtCore, QtGui

import threading
import Queue

import time
import sys
import random

class Data_Reader(threading.Thread):

	def __init__(self, ser, buffer):
		threading.Thread.__init__(self)
		self._buffer = buffer
		self._ser = ser
		
	def run(self):
		while (True):
			#Probably only want to read 3 bytes?
			#raw_data = ser.read(ser.inWaiting())
			raw_data = ''
			for k in range(10):
				raw_data = raw_data + str(random.randint(1,10))+','+str(random.randint(1,10))+','+str(random.randint(1,10))+','+str(random.randint(1,10))
				raw_data = raw_data + '\r\n'
				
			self.process_data(raw_data)
			self.move_data_to_buffer()
			time.sleep(1)
			
	def process_data(self, raw_data):
		"""Convert the raw data to a useful format"""
		print 'raw data'
		print raw_data
		
		EU_per_g = 250.9 #This corresponds to 1.23 volts which is really high! Should be 0.8 Volts
		initial_values = [130+EU_per_g, 338, 330] #Z,Y,X
		
		#Each read of X/Y/Z are split into lines separated by carriage returns
		lines = raw_data.split('\r\n')
		print 'lines'
		print lines
		#Beginning and ending lines are sometimes messed up
		good_lines = lines[3:-3]
		new_data_size = len(good_lines)
		
		good_data = ",".join(good_lines).split(",")
		
		print 'good lines'
		print good_lines
		#Split into X,Y,Z based on comma delimiter
		#split_data = good_lines.split(",")
		
		#Convert list of strings to list of integers
		try:
			int_data = map(int, good_data)
		except:
			print "Bad data read: dumping data"
			new_data_array = [0, 0, 0]
			new_data_size = 1

		print 'int data'
		print int_data
		
		int_data = np.array(int_data)
		int_data = int_data.reshape(new_data_size,4)
		
		print 'reshaped int data'
		print int_data
		new_g_data = int_data / EU_per_g
		
		print 'calibrated data'
		print new_g_data
		
		self._buffer.put(new_g_data)
		
	def move_data_to_buffer(self):
		"""Take the new data and put it into the buffer"""
		pass
		

class Data_Buffer():

	def __init__(self):
		self._fifo = np.array(0)
		
	def put(self, new_data):
		"""Put data in the buffer"""
		
		#print new_data
		#self._fifo = np.append(self._fifo,new_data)
		if np.size(self._fifo) > 1:
			self._fifo = np.vstack((self._fifo,new_data))
		else:
			self._fifo = new_data
		print 'fifo'
		print self._fifo
		
	def get(self):
		"""Get data from the buffer"""
		
		#Get the data to send out 
		temp_buffer = self._fifo
		print 'temp buffer'
		#print temp_buffer
		#Clear the buffer
		#self.clear()
		
		#Send out the data
		return temp_buffer
		
	def clear(self):
		"""Clear all data in the FIFOs"""

		self._fifo = np.array(0)
		

class Data_Plotter(QtGui.QMainWindow, FigureCanvas):

	def __init__(self, buffer, reader):
		"""Set up the plots"""
		
		#Set up the variables
		self._buffer = buffer
		self._reader = reader
		
		#Set up the Figures / GUI
		self.main_gui = QtGui.QMainWindow() 
		self.setup_window(self.main_gui)
		
		#Set up the timer
		self.setup_timer()
		self.main_gui.show()
		
		self._reader.start()
		
	def setup_timer(self):
		"""Set up the timer to update the plot"""
		
		self._timer = self.fig.canvas.new_timer()
		self._timer.interval = 100
		self._timer.add_callback(self.plot_data)
		self._timer.start()

        

		
	def setup_window(self, MainWindow):
		"""Set up the plotting window"""
		
		MainWindow.setObjectName(_fromUtf8("MainWindow"))
		MainWindow.resize(895, 601)
		self.centralwidget = QtGui.QWidget(MainWindow)
		self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
		self.plot_widget = QtGui.QWidget(self.centralwidget)
		self.plot_widget.setGeometry(QtCore.QRect(29, 29, 681, 501))
		self.plot_widget.setObjectName(_fromUtf8("plot_widget"))
		self.quitButton = QtGui.QPushButton(self.centralwidget)
		self.quitButton.setGeometry(QtCore.QRect(740, 390, 114, 32))
		self.quitButton.setObjectName(_fromUtf8("quitButton"))
		MainWindow.setCentralWidget(self.centralwidget)
		self.menubar = QtGui.QMenuBar(MainWindow)
		self.menubar.setGeometry(QtCore.QRect(0, 0, 895, 22))
		self.menubar.setObjectName(_fromUtf8("menubar"))
		MainWindow.setMenuBar(self.menubar)
		self.statusbar = QtGui.QStatusBar(MainWindow)
		self.statusbar.setObjectName(_fromUtf8("statusbar"))
		MainWindow.setStatusBar(self.statusbar)
		QtCore.QMetaObject.connectSlotsByName(MainWindow)
	
		MainWindow.setWindowTitle(QtGui.QApplication.translate("MainWindow", "MainWindow", None, QtGui.QApplication.UnicodeUTF8))
		self.quitButton.setText(QtGui.QApplication.translate("MainWindow", "Quit", None, QtGui.QApplication.UnicodeUTF8))

		self.fig = Figure()
        	self.canvas = FigureCanvas(self.fig)
		self.canvas.setParent(self.plot_widget)

		#Create the time domain subplot
		ax = self.fig.add_subplot(211)
		ax.set_xlabel('Data Sample')
		ax.set_ylabel('G Forces')
				
		#Create the frequency domain subplot
		ax2 = self.fig.add_subplot(212)
		ax2.set_xlabel('Frequency')
		ax2.set_ylabel('Power')
	
	        #Initialize the plot - run once
		self.ax = ax
		self.ax2 = ax2
		
		#Create the lines
		self.linex = Line2D([0,1], [0,1],color='r',marker='.',linestyle='none')
		self.liney = Line2D([0,1], [0,1],color='b',marker='.',linestyle='none')
		self.linez = Line2D([0,1], [0,1],color='k',marker='.',linestyle='none')
		self.ax.add_line(self.linex)
		self.ax.add_line(self.liney)
		self.ax.add_line(self.linez)
	
		self.linefft = Line2D([0,0], [0,0], color='k')
		self.ax2.add_line(self.linefft)
		
		#Create the legend
		ax.legend([self.linex,self.liney,self.linez],['X-axis','Y-axis','Z-axis'])
		
		#Set the x and y graph limits
		#self.ax.set_ylim(-2,2)
		#self.ax.set_xlim(0, 100)
        	self.ax.set_ylim(-.05,.05)
        	self.ax.set_xlim(-.05,.05)
        
        	#self.canvas.draw()
		self.canvas.draw()

	def plot_data(self):
		"""update new data"""
		
		print '==========================================================================='
		print 'updating plot'
		print '==========================================================================='
		#Get new data
		data_to_plot = self._buffer.get()
		#print data_to_plot
		if data_to_plot.size > 1:
			t = data_to_plot[:,0]
			x = data_to_plot[:,1]
			y = data_to_plot[:,2]
			z = data_to_plot[:,3]

			#Add this data to the plot
			self.linex.set_data(t, x)
			self.liney.set_data(t, y)
			self.linez.set_data(t, z)
	
			#fft_data_raw = sc.fft(z)
			#self.fftdata = abs(fft_data_raw[:np.size(z)/2])
			#self.fftfreq = np.arange(np.size(z)/2)
			fftfreq = [0,1]
			fftdata = [1,0]
			self.linefft.set_data(fftfreq, fftdata)
			
			#Modify the X-axis
			
			#Redraw the plots
			self.canvas.draw()


def setup_serial():
	#Set up the serial feed
	ser = sr.Serial('/dev/tty.usbmodem411', 9600)
	#ser = sr.Serial('/dev/tty.usbserial-A501CZ0O', 9600)
	#ser = sr.Serial('/dev/tty.usbserial-A900XWJU', 9600)

	#Pause to make sure the connection is setup
	time.sleep(1)

	return ser
	
	
if __name__ == "__main__":

	try:
		_fromUtf8 = QtCore.QString.fromUtf8
	except AttributeError:
		_fromUtf8 = lambda s: s
	
	
	#Set up the serial connection
	#ser = setup_serial()
	ser = ''
	
	#Create the instances of the data and buffer classes
	buffer  = Data_Buffer()
	#buffer = Queue()
	
	reader  = Data_Reader(ser,buffer)
	
	#Create the GUI
	app = QtGui.QApplication(sys.argv)
	plotter = Data_Plotter(buffer, reader)
	sys.exit(app.exec_())		

		
	#Create the plot window
	#plt.show()