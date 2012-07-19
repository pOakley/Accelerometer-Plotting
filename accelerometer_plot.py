import serial as sr
import numpy as np
from matplotlib.lines import Line2D
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import time

class Scope:
    def __init__(self, ax, maxt=500, dt=1):
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
        self.ax.set_ylim(-.1, 1000)
        self.ax.set_xlim(0, self.maxt)

    def update(self, new_data):
    	#Update the plot
    	
    	#Split the string into 3 integers
    	new_data = map(int,new_data.split(','))

    	#Get the last timestep
        lastt = self.tdata[-1]
        
        #If the end of the graph is reached, reset the arrays
        if lastt > self.tdata[0] + self.maxt: # reset the arrays
		self.tdata = [self.tdata[-1]]
		self.xdata = [self.xdata[-1]]
		self.ydata = [self.ydata[-1]]
		self.zdata = [self.zdata[-1]]
		self.ax.set_xlim(self.tdata[0], self.tdata[0] + self.maxt)
		self.ax.figure.canvas.draw()

	#Set the new t value to the dt more than the largest existing t value
        t = self.tdata[-1] + self.dt
        
        #Add to the existing time array
        self.tdata.append(t)
        
        #Update the existing y array with the value passed in to the function
        self.xdata.append(new_data[0])
        self.ydata.append(new_data[1])
        self.zdata.append(new_data[2])
        
        #Update the line
        self.linex.set_data(self.tdata, self.xdata)
        self.liney.set_data(self.tdata, self.ydata)
        self.linez.set_data(self.tdata, self.zdata)
        return self.linex,self.liney,self.linez
	#return self.linex

def emitter():

	#Read all the data in the buffer (maxes out at 128 bytes)
	a=ser.read(ser.inWaiting())
	
	#Split them based on new lines
	lines = a.split('\n')

	#Select the second to last line (sometimes the very last line is empty)
	#Beware - this throws away all the other data
	#print np.size(lines)
	#print lines
	buffer = lines[-2]
    	#new_data = map(int,buffer.split(','))
	#buffer= new_data[0]
	yield buffer


#Set up the serial feed
ser = sr.Serial('/dev/tty.usbmodem411', 9600)
time.sleep(1)

#Create the figure
fig = plt.figure()

#Create the main subplot
ax = fig.add_subplot(111)
#ax.set_xlabel('Data Sample')
#ax.set_ylabel('G Forces')

#Create the scope class
scope = Scope(ax)

# pass a generator in "emitter" to produce data for the update function every 2 milliseconds
ani = animation.FuncAnimation(fig, scope.update, emitter, interval=50,
    blit=True)

#Create the plot window
plt.show()