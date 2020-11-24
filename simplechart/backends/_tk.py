import datetime
import itertools
import sys
import time
from tkinter import font

import numpy

from simplechart import SimpleChartObject, RectangleArea as Rectangle

try:
    import tkinter as tk
except:
    import Tkinter as tk
class ResizingCanvas(tk.Canvas):
    def __init__(self,parent,**kwargs):
        super(ResizingCanvas,self).__init__(parent,**kwargs)
        self.bind("<Configure>", self.on_resize)
        self.height = self.winfo_reqheight()
        self.width = self.winfo_reqwidth()
    def on_resize(self,event):
        # determine the ratio of old width/height to new width/height
        print("RESIZE:", event.width, event.height, self.width, self.height,self.winfo_reqwidth(),self.winfo_reqheight())
        wscale = float(event.width)/self.width
        hscale = float(event.height)/self.height
        print(wscale,hscale)
        self.width = event.width
        self.height = event.height
        # resize the canvas
        # self.config(width=self.width, height=self.height)
        # rescale all the objects tagged with the "all" tag

        self.scale("all",0,0,wscale,hscale)

class TKChartCanvas(tk.Canvas):
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22',
                '#17becf']
    def __init__(self,master,**kwargs):
        self.darkTheme = kwargs.pop("dark",False)
        margin = kwargs.pop("margin",[40,8,8,21])
        colors = kwargs.pop("colors",self.colors)
        self.xFmt = kwargs.pop("xFmt",lambda x:"%0.1f"%float(x))

        self.colors = itertools.cycle(colors)
        if isinstance(margin,(int,float)):
            margin = [margin]*4
        if len(margin) == 1:
            margin = margin * 4
        if len(margin) == 2:
            margin = margin[:2] + margin[:2]
        self.margin = margin
        tk.Canvas.__init__(self,master,**kwargs)
        self.chart = SimpleChartObject()

        self.trace_colors = {}
        if sys.version[0] == 3:
            self.text_extra = {'angle':45}
        else:
            self.text_extra = {}
        self.refresh()

    def create_circle(self,x, y, r, **kwargs):
        return self.create_oval(x - r, y - r, x + r, y + r, **kwargs)

    def add_points(self,points_xy,traceID=0):
        self.chart.add_points(points_xy,traceID)

    def get_chart_area(self):
        area = Rectangle(self.margin[:2],[int(self['width'])-self.margin[2],int(self['height'])-self.margin[3]])
        return area
    def lockXAxis(self,minX,maxX,truncate=True):

        for axisId in self.chart._axes:
            self.chart.get_axis(axisId).lockXRange([minX,maxX])
            if truncate:
                for trace_id,trace in self.chart.get_axis(axisId).getTraces():
                    points = trace.points
                    x = points[:,0]
                    trace.points = points[(x >= minX)&(x <= maxX)]
    def refresh(self):
        self.delete(tk.ALL)
        w = int(self['width'])
        h = int(self['height'])
        bg = self['bg']
        stroke = "black" if not self.darkTheme else "white"
        self.create_rectangle(0,0,w+5,h+5,fill=bg)
        axis = self.chart.get_axis(0)
        data = axis.getTraces()

        a = self.get_chart_area()
        self.create_line(a.left,a.top,a.right,a.top,a.right,a.bottom,fill="light grey")
        self.create_line(a.left,a.top,a.left,a.bottom,a.right,a.bottom,fill=stroke)

        #ticks Y
        maxW = float("-inf")
        self.create_line(a.left,a.top,a.left-8,a.top,fill=stroke)
        c_id = self.create_text(a.left-9,a.top,anchor=tk.E,text="%0.1f" % axis.yRange[1])
        current_font = self.itemcget(id, 'font')# or just c.itemcget(id, 'font')
        new_named_font = font.Font(font=current_font)
        maxW = max(new_named_font.measure("%0.1f" % axis.yRange[1]),maxW)

        midY = (a.top+a.bottom)/2.0
        midVal = (axis.yRange[1] + axis.yRange[0])/2.0
        self.create_line(a.left,midY,a.left-8,midY,fill=stroke)
        self.create_text(a.left-9,midY,anchor=tk.E,text="%0.1f" % midVal)
        maxW = max(new_named_font.measure("%0.1f" % midVal), maxW)
        self.create_line(a.left,a.bottom,a.left-8,a.bottom,fill=stroke)
        self.create_text(a.left-9,a.bottom,anchor=tk.E,text="%0.1f" % axis.yRange[0])
        maxW = max(new_named_font.measure("%0.1f" % axis.yRange[0]), maxW)
        if maxW > a.left:
            self.margin[0] = maxW
            return self.refresh()
        # ticks X
        self.create_line(a.left, a.bottom, a.left , a.bottom+8, fill=stroke)
        self.create_text(a.left, a.bottom+9, anchor=tk.NW, text=self.xFmt(axis.xRange[0]))

        midX = (a.left + a.right) / 2.0
        midVal = (axis.xRange[1] + axis.xRange[0]) / 2.0
        self.create_line(midX,a.bottom,midX, a.bottom + 8, fill=stroke)
        self.create_text(midX, a.bottom + 9, anchor=tk.N, text=self.xFmt(midVal))
        self.create_line(a.right, a.bottom, a.right, a.bottom+8, fill=stroke)
        self.create_text(a.right, a.bottom+9, anchor=tk.NE, text=self.xFmt(axis.xRange[1]))
        for trace_pk,trace in data:
            if trace.config.get('color') is None and trace_pk not in self.trace_colors:
                trace.config['color'] = next(self.colors)
            lineEnd = None
            for line in trace.split_points():
                if len(line) == 0:
                    continue
                line[:,1] = line[:,1]*a.height + a.top
                line[:,0] = line[:,0]*a.width + a.left
                if lineEnd:
                    self.create_line(lineEnd[0],lineEnd[1],line[0][0],line[0][1],dash=(3,5),fill=trace.config['color'])
                lineEnd = line[-1].tolist()
                if len(line)==1:
                    self.create_circle(line[0][0],line[0][1],2,fill=trace.config['color'])
                else:
                    self.create_line(*line.flatten(),fill=trace.config['color'],width=1.5)



if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("320x240")
    chart = TKChartCanvas(root,width=320,height=80,bg="white",
                          xFmt=lambda x:datetime.datetime.fromtimestamp(int(x)).strftime("%M:%S"))
    a = numpy.random.uniform(80,126,100)
    a = numpy.hstack([numpy.array([float("nan")]*10), a])
    x = numpy.arange(int(time.time())-100,int(time.time()))
    y = numpy.random.choice(a,100)
    a2 = numpy.random.uniform(60, 90, 100)
    a2 = numpy.hstack([numpy.array([float("nan")] * 10), a2])
    y2 = numpy.random.choice(a2,100)
    chart.add_points(zip(x,y))
    chart.add_points(zip(x,y2),1)

    def update_fn():
        x = time.time()
        chart.add_points([[x,numpy.random.choice(a)]],0)
        chart.add_points([[x,numpy.random.choice(a2)]],1)
        chart.lockXAxis(time.time()-120,time.time())
        chart.refresh()
        root.after(1000,update_fn)
    update_fn()
    tk.Label(text="ASDASDASD").pack()
    chart.pack()
    b1 = tk.Button(text="1")
    b2 = tk.Button(text="2")
    tk.Label(text="ASDASDASD").pack()
    b1.pack(side=tk.LEFT,fill=tk.BOTH,expand=1)
    b2.pack(side=tk.LEFT,fill=tk.BOTH,expand=1)
    root.mainloop()

