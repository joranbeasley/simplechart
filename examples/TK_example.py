try:
    import tkinter as tk
except:
    import Tkinter as tk
import numpy
import time
import datetime

from simplechart.backends.TKChartCanvas import TKChartCanvas


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
chart.add_points(list(zip(x,y)))
chart.add_points(list(zip(x,y2)),1)

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
