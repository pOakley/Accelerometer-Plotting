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

class Data():

	def __init__(self):
		self.t = []
		self.x = []
		self.y = []
		self.z = []
		

class Data_Reader(threading.Thread):

	def __init__(self, ser, buffer):
		threading.Thread.__init__(self)
		self._buffer = buffer
		self._ser = ser
		self.data_stored_counter = 0
		self.start_time_reader = time.time()
		
		
	def run(self):
		while (True):
			#Probably only want to read 3 bytes?
			raw_data = ser.read(ser.inWaiting())
			#raw_data = ''
			# for k in range(10):
# 				raw_data = raw_data + str(random.randint(100,1000))+','+str(random.randint(100,1000))+','+str(random.randint(100,1000))+','+str(random.randint(100,1000))
# 				raw_data = raw_data + '\r\n'
				
			self.process_data(raw_data)
			self.move_data_to_buffer()
			time.sleep(.1)
			
	def process_data(self, raw_data):
		"""Convert the raw data to a useful format"""
# 		print 'raw data'
# 		print raw_data
		
		EU_per_g = 250.9 #This corresponds to 1.23 volts which is really high! Should be 0.8 Volts
		initial_values = [130+EU_per_g, 338, 330] #Z,Y,X
		
		#Each read of X/Y/Z are split into lines separated by carriage returns
		lines = raw_data.split('\r\n')
# 		print 'lines'
# 		print lines
		#Beginning and ending lines are sometimes messed up
		good_lines = lines[2:-2]
		new_data_size = len(good_lines)
#		print new_data_size
# 		print 'size'
# 		print new_data_size		
		
		if new_data_size > 1:
		
			good_data = ",".join(good_lines).split(",")
			
# 			print 'good lines'
# 			print good_lines
			#Split into X,Y,Z based on comma delimiter
			#split_data = good_lines.split(",")
			
			#Convert list of strings to list of integers
			try:
				int_data = map(int, good_data)
			except:
				print "Bad data read: dumping data"
				new_data_array = [0, 0, 0, 0]
				new_data_size = 1
	
# 			print 'int data'
# 			print int_data
			
			int_data = np.array(int_data)
			try:
				int_data = int_data.reshape(new_data_size,4)
			except:
				print "Bad data read: dumping data"
				int_data = np.array([[0, 0, 0, 0],[0,0,0,0]])
				new_data_size = 1
								
# 			print 'reshaped int data'
# 			print int_data
			self.new_g_data = int_data / EU_per_g
			
# 			print 'calibrated data'
# 			print self.new_g_data
			
			
	def move_data_to_buffer(self):
		"""Take the new data and put it into the buffer"""
		self.data_stored_counter += np.size(self.new_g_data)/4
#		print self.data_stored_counter
#		print (self.data_stored_counter / (time.time() - self.start_time_reader))

		self._buffer.put_nowait(self.new_g_data)

		

# class Data_Buffer():
# 
# 	def __init__(self):
# 		self._fifo = np.array(0)
# 		
# 	def put(self, new_data):
# 		"""Put data in the buffer"""
# 		
# 		#print new_data
# 		#self._fifo = np.append(self._fifo,new_data)
# 		if np.size(self._fifo) > 1:
# 			self._fifo = np.vstack((self._fifo,new_data))
# 		else:
# 			self._fifo = new_data
# 		print 'fifo'
# 		print self._fifo
# 		
# 	def get(self):
# 		"""Get data from the buffer"""
# 		
# 		#Get the data to send out 
# 		temp_buffer = self._fifo
# 		print 'temp buffer'
# 		#print temp_buffer
# 		#Clear the buffer
# 		#self.clear()
# 		
# 		#Send out the data
# 		return temp_buffer
# 		
# 	def clear(self):
# 		"""Clear all data in the FIFOs"""
# 
# 		self._fifo = np.array(0)
		

class Data_Plotter(QtGui.QMainWindow, FigureCanvas):

	def __init__(self, buffer, reader, data):
		"""Set up the plots"""
		
		#Set up the variables
		self._buffer = buffer
		self._reader = reader
		self._data = data
		
		#Set up the Figures / GUI
		self.main_gui = QtGui.QMainWindow() 
		self.setup_window(self.main_gui)
		
		#Set up the timer
		self.setup_timer()
		self.main_gui.show()
		
		self._reader.daemon = True
		self._reader.start()
		self.start_time = time.time()
		self.new_time = self.start_time
		self.total_data_plotted = 0
		self.new_num=0
		
	def setup_timer(self):
		"""Set up the timer to update the plot"""
		
		self._timer = self.fig.canvas.new_timer()
		self._timer.interval = 500
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
		self.linex = ax.plot(0,0,color='r')#Line2D([0,2], [0,2],color='r')
		self.liney = ax.plot(0,0,color='b')#Line2D([0,2], [0,2],color='b')
		self.linez = ax.plot(0,0,color='k')#Line2D([0,2], [0,2],color='k')
		#self.ax.add_line(self.linex)
		#self.ax.add_line(self.liney)
		#self.ax.add_line(self.linez)
	
		self.linefft = Line2D([0,0], [0,0], color='k')
		self.ax2.add_line(self.linefft)
		
		#Create the legend
		#ax.legend([self.linex,self.liney,self.linez],['X-axis','Y-axis','Z-axis'])
		
		#Set the x and y graph limits
		self.ax.set_ylim(0,5)
		self.ax.set_xlim(0, 100)
        	#self.ax.set_ylim(-.05,.05)
        	#self.ax.set_xlim(-.05,.05)
        
        	#self.canvas.draw()
		self.canvas.draw()

	def plot_data(self):
		"""update new data"""
		
# 		print '==========================================================================='
# 		print 'updating plot '
# 		print  str(len(self._data.t))
# 		print  str(len(self._data.x))
# 		print  str(len(self._data.y))
# 		print  str(len(self._data.z))	
# 		print '==========================================================================='
		#Get new data
		self.retrieve_queue()
		
		#Add this data to the plot
		start_plot = 0
		stop_plot = max(self._data.t)
		if stop_plot > 1000:
			start_plot = stop_plot - 1000
			self._data.t = self._data.t[start_plot:stop_plot]
			self._data.x = self._data.x[start_plot:stop_plot]
			self._data.y = self._data.y[start_plot:stop_plot]
			self._data.z = self._data.z[start_plot:stop_plot]
		
		self.linex[0].set_data(self._data.t, self._data.x)
		self.liney[0].set_data(self._data.t, self._data.y)
		self.linez[0].set_data(self._data.t, self._data.z)

		#fft_data_raw = sc.fft(z)
		#self.fftdata = abs(fft_data_raw[:np.size(z)/2])
		#self.fftfreq = np.arange(np.size(z)/2)
		fftfreq = [0,1]
		fftdata = [1,0]
		self.linefft.set_data(fftfreq, fftdata)
		
		#Modify the X-axis
		
		#Redraw the plots
		self.ax.set_xlim(start_plot,stop_plot)
		print (self.total_data_plotted - self.new_num) / (time.time() - self.new_time)
		self.new_time = time.time()
		self.new_num = self.total_data_plotted
		self.canvas.draw()
			
	def retrieve_queue(self):
 		read_counter = np.size(self._data.x)
	
		for looper in range(self._buffer.qsize()):
			#print looper
			self.data_to_plot = self._buffer.get_nowait()
			#print self.data_to_plot
			#print '='
			self._data.x.extend(self.data_to_plot[:,1])
			self._data.y.extend(self.data_to_plot[:,2])
			self._data.z.extend(self.data_to_plot[:,3])
			self._data.t = np.arange(np.size(self._data.x))
			
 		read_counter = np.size(self._data.x) - read_counter
 		self.total_data_plotted += read_counter
# 		print 'read counter'
# 		print read_counter
 			

def setup_serial():
	#Set up the serial feed
	ser = sr.Serial('/dev/tty.usbmodem411', 57600,timeout=1)
	#ser = sr.Serial('/dev/tty.usbserial-A501CZ0O', 9600)
	#ser = sr.Serial('/dev/tty.usbserial-A900XWJU', 9600)

	#Pause to make sure the connection is setup
	time.sleep(1)
	flush_buffer(ser)
	return ser
	
def flush_buffer(ser):
	while (ser.inWaiting()>1):
		ser.read(ser.inWaiting())

	
if __name__ == "__main__":

	try:
		_fromUtf8 = QtCore.QString.fromUtf8
	except AttributeError:
		_fromUtf8 = lambda s: s
	
	#This is the data class to store everything
	data = Data()
	
	#Set up the serial connection
	ser = setup_serial()
	
	#Create the instances of the data and buffer classes
	#buffer  = Data_Buffer()
	buffer = Queue.Queue()
	
	reader  = Data_Reader(ser,buffer)
	
	#Create the GUI
	app = QtGui.QApplication(sys.argv)
	plotter = Data_Plotter(buffer, reader, data)
	sys.exit(app.exec_())		

		
	#Create the plot window
	#plt.show()