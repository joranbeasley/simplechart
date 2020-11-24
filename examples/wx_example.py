import wx
import numpy
import time
from simplechart.backends.wxChartPanel import wxChartPanel

class Frame(wx.Frame):
    def __init__(self):
        super(Frame, self).__init__(None)
        self.SetTitle('My Title')
        self.SetClientSize((320, 120))
        self.Center()
        a = numpy.random.uniform(80, 126, 100)
        a = numpy.hstack([numpy.array([float("nan")] * 10), a])
        x = numpy.arange(int(time.time()) - 100, int(time.time()))
        y = numpy.random.choice(a, 100)
        a2 = numpy.random.uniform(60, 90, 100)
        a2 = numpy.hstack([numpy.array([float("nan")] * 10), a2])
        y2 = numpy.random.choice(a2, 100)
        self.last = [[x[-1], y[-1]], [x[-1], y2[-1]]]
        layout = wx.BoxSizer(wx.VERTICAL)
        self.view = wxChartPanel(self,
                                 bg="#FFFFFF",
                                 margin=[40, 8, 15, 30],
                                 fmtXTicks="DATE:%M:%S",
                                 fmtYTicks="%0.1f")
        self.view.add_points(list(zip(x, y)))
        self.view.add_points(list(zip(x, y2)), 1)
        layout.Add(self.view, 1, wx.ALL | wx.EXPAND, 10)
        self.view1 = wxChartPanel(self,
                                  bg="#FFFFFF",
                                  margin=[40, 8, 15, 10],
                                  fmtXTicks=None,
                                  fmtYTicks="%0.1f",
                                  size=(300, 200))
        self.view1.add_points(list(zip(x, y)))
        self.view1.add_points(list(zip(x, y2)), 1)
        layout.Add(self.view1, 1, wx.ALL | wx.EXPAND, 10)
        self.SetSizer(layout)
        self.add_point_tick()
        self.Layout()
        self.Fit()

    def add_point_tick(self):
        self.view.chart.get_axis(0).lockXRange([time.time() - 300, time.time()])
        y = self.last[0][1] + numpy.random.uniform(-2, 2)
        x = time.time()
        y2 = self.last[1][1] + numpy.random.uniform(-0.5, 0.5)
        self.last = [[x, y], [x, y2]]
        self.view.add_points([[x, y]])
        self.view.add_points([[x, y2]], 1)
        self.Refresh()
        wx.CallLater(1000, self.add_point_tick)


def main():
    app = wx.App(False)
    frame = Frame()
    frame.SetTitle("wx example")
    frame.Show()
    app.MainLoop()


main()
