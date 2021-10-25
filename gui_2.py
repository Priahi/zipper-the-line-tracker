from tkinter import *
import matplotlib
import matplotlib.pyplot as plt
matplotlib.use('TkAgg')
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import math
import time
import main
from PID import PID as pid

class Plotter:
    def __init__(self, frame):
        self.fig = Figure(figsize=(6,4))
        self.figCanvas = FigureCanvasTkAgg(self.fig, master=frame)
        self.p = self.fig.add_subplot(1,1,1)

    # method for setting the labels of the current plot
    def set_labels(self, title=None, xlabel=None, ylabel=None):
        self.p.set_title(title)
        self.p.set_xlabel(xlabel)
        self.p.set_ylabel(ylabel)

    # method for showing the plot at a specific location on the grid
    def show_plot(self, xloc=0, yloc=0, padx=0, pady=0):
        self.figCanvas.get_tk_widget().grid(row=xloc,column=yloc,padx=padx,pady=pady)

    # method for making the plot disappear off of the current window
    def hide_plot(self):
        self.figCanvas.get_tk_widget().grid_remove()

    # method for clearing the plot and displaying the specified data
    def graph(self, xdata, ydata, color, title, xtitle, ytitle):
        self.p.clear()
        self.set_labels(title, xtitle, ytitle)
        self.p.plot(xdata, ydata, color)
        self.figCanvas.draw()
        plt.xticks(rotation=45, ha='right')

class RobotGUI:
    def __init__(self):
        self.root = Tk()

        self.turnVal = 0
        self.speed = 1

        self.x = 0
        self.y = 0
        self.yDir = 1
        self.xDir = 0
        self.hyp = 0
        self.theta1 = math.pi / 2
        self.phi1 = 0
        self.theta2 = 0
        self.phi2 = math.pi - self.theta2

        self.xVals = []
        self.yVals = []

        self.flag = 1

        self.running = False

        self.message = StringVar()
        self.message.set("Welcome to PathPlotter!")

        button = Button(self.root, text="Quit", command=self.stop_program)
        button.grid(row=0, column=0)

        self.plot = Plotter(self.root)
        self.plot.show_plot(1,0)
        self.begin_measure()

        self.root.mainloop()

    def begin_measure(self):
        self.running = True

        result = main.main_robot(self.flag)
        self.flag = result[0]
        self.turnVal = result[1]

        # if we implement speed just comment out this line
        #speed = 1
        self.hyp = math.sqrt(math.pow(self.x, 2) + math.pow(self.y, 2) + self.speed
                            - 2 * math.sqrt(math.pow(self.x, 2) + math.pow(self.y, 2))
                            * math.cos(math.pi * (1 - self.turnVal / 2)))
        if self.x != 0:
            self.theta1 = math.atan(self.y / self.x)
        else:
            self.theta1 = math.pi / 2
        self.theta2 = self.turnVal * math.pi / 2
        self.phi2 = math.pi - self.theta2
        self.phi1 = math.asin(math.sin(self.phi2) / self.hyp)
        self.y = self.hyp * math.sin(self.phi1 + self.theta1)
        self.x = self.hyp * math.cos(self.phi1 + self.theta1)

        self.x = round(self.x, 2)
        self.y = round(self.y, 2)

        self.xVals.append(self.x)
        self.yVals.append(self.y)

        self.plot.graph(self.xVals, self.yVals, 'b', "Path Travelled So Far", "x", "y")

        self.loop = self.root.after(1, lambda: self.begin_measure())

    # method for terminating the program
    def stop_program(self):
        try:
            if self.running:
                self.root.after_cancel(self.loop)
            self.root.destroy()
        except:
            print("Program terminated")

    # method for running the current program
    def run_program(self):
        self.message.set("Program running...")
        if not self.running:
            self.begin_measure()

rg = RobotGUI()
