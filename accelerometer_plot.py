import serial as sr
import numpy as np
from matplotlib.lines import Line2D
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import time

class Scope:
    def __init__(self, ax, maxt=1000, dt=1):
        #Initialize the plot - run once
        self.ax = ax
        self.dt = dt
        self.maxt = maxt
        
        #Zero the data
        self.tdata = [0]
        self.xdata = [0]
        self.ydata = [0]
        self.zdata = [0]
        
        #Create the line
        self.linex = Line2D(self.tdata, self.xdata,color='r')
        self.liney = Line2D(self.tdata, self.ydata,color='b')
        self.linez = Line2D(self.tdata, self.zdata,color='k')
        self.ax.add_line(self.linex)
        self.ax.add_line(self.liney)
        self.ax.add_line(self.linez)

        
        #Create the legend
        ax.legend([self.linex,self.liney,self.linez],['X-axis','Y-axis','Z-axis'])
        
        #Set the x and y graph limits
        self.ax.set_ylim(-2,2)
        self.ax.set_xlim(0, self.maxt)

    def update(self, new_data):
    	#Update the plot
    	#Calibration values
    	initial_values = [574.15, 587.94, 206.74*2]
    	EU_per_g = 250.9 #This corresponds to 1.23 volts which is really high! Should be 0.8 Volts
    	
    	#print new_data
    	#print np.size(new_data)
    	#Size of new data
    	new_data_size = np.size(new_data)
    	
    	#Split into a list of single element strings - very confusing syntax
    	new_data_array = ",".join(new_data).split(",")
    	#print new_data_array
    	#print np.size(new_data_array)
    	
    	#Convert list of strings to list of integers
    	new_data_array = map(int, new_data_array)
    	#print new_data_array
    	#print np.size(new_data_array)

    	#Make list into a numpy array
    	new_data_array = np.array(new_data_array)
    	#print new_data_array
    	#print np.size(new_data_array)
    	
    	#Reshape into a 2D array - size x 3
    	new_data_array = new_data_array.reshape(new_data_size,3)
    	#print new_data_array
    	#print np.size(new_data_array)

    	#Calibrate values
    	for axis in range(3):
		new_data_array[:,axis] -= initial_values[axis]
	
	#print new_data_array
		
	new_data_array = new_data_array / EU_per_g



	#print new_data_array

    	#Get the last timestep
        #lastt = self.tdata[-1]
        #print 'Time stuff'
        #print lastt
        #print self.tdata
        
        #If the end of the graph is reached, reset the arrays
        if self.tdata[-1] > self.tdata[0] + self.maxt: # reset the arrays
		self.tdata = [self.tdata[-1]]
		self.xdata = [self.xdata[-1]]
		self.ydata = [self.ydata[-1]]
		self.zdata = [self.zdata[-1]]
		self.ax.set_xlim(self.tdata[0], self.tdata[0] + self.maxt)
		self.ax.figure.canvas.draw()
		

	#Set the new t value to the dt more than the largest existing t value
        #t = self.tdata[-1] + self.dt
        t = [i+1+self.tdata[-1] for i in range(new_data_size)]
        
        #Add to the existing time array
        self.tdata.extend(t)
	#print 'TDATA'
        #print self.tdata
        
        #Update the existing y array with the value passed in to the function
        self.xdata.extend(new_data_array[:,0])
        self.ydata.extend(new_data_array[:,1])
        self.zdata.extend(new_data_array[:,2])
        #print 'XDATA'
        #print np.size(self.tdata)
        #print np.size(self.xdata)
        
        #print np.size(self.tdata), np.size(self.xdata), np.size(self.ydata), np.size(self.zdata)
        #Update the line
        self.linex.set_data(self.tdata, self.xdata)
        self.liney.set_data(self.tdata, self.ydata)
        self.linez.set_data(self.tdata, self.zdata)
        #print self.linex.get_data()
     
        #Rescale the y-axis here. Doesn't quite work yet
#       plotmax = max([self.xdata,self.ydata,self.zdata])
#       plotmin = min([self.xdata,self.ydata,self.zdata])
# 	self.ax.set_ylim(plotmin,plotmax)

        #time.sleep(1)
        return self.linex,self.liney,self.linez
	#return self.linex
	
def emitter():
	#Set up some debugging / error handling stuff
	read_attempts = 0
	succesful_read = False
	freshest_data_only = False
	
	#Read all the data in the buffer (maxes out at 128 bytes)
	raw_data = ser.read(ser.inWaiting())
	
	#Split them based on new lines
	lines = raw_data.split('\n')

	#Select the second to last line (sometimes the very last line is empty)
	#Beware - this throws away all the other data

	if freshest_data_only == True:
		while succesful_read == False and read_attempts < 40000:
			try:
				buffer = lines[-2]
				succesful_read = True
			except:
				read_attempts += 1
				print 'Bad Read'
		
		if read_attempts >= 40000:
			print 'Error reading serial data - exiting'
			sys.exit()
	else:
		while succesful_read == False and read_attempts < 40000:
			try:
				#The first and last are often only partials. The second element (index 1)
				#seems to have weird problems too. Not sure what to make of that yet
				buffer = lines[6:-2]
				succesful_read = True
			except:
				read_attempts += 1
				print 'Bad Read'
		
		if read_attempts >= 40000:
			print 'Error reading serial data - exiting'
			sys.exit()
	
	
			
    	#new_data = map(int,buffer.split(','))
	#buffer= new_data[0]
	yield buffer


#Set up the serial feed
ser = sr.Serial('/dev/tty.usbmodem411', 115200)
time.sleep(1)

#Create the figure
fig = plt.figure()

#Create the main subplot
ax = fig.add_subplot(111)
ax.set_xlabel('Data Sample')
ax.set_ylabel('G Forces')

#Create the scope class
scope = Scope(ax)

# pass a generator in "emitter" to produce data for the update function every 2 milliseconds
ani = animation.FuncAnimation(fig, scope.update, emitter, interval=2, blit=False)

#Create the plot window
plt.show()