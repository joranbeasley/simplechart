import datetime
import itertools
import re
import sys
import time
from tkinter import font

import numpy
import six

from simplechart import SimpleChartObject, RectangleArea

import wx

class wxChartPanel(wx.Panel):
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22',
              '#17becf']
    def __init__(self, parent,bg="#FFFFFF",margin=(35,8,15,22),colors=None,
                 fmtXTicks="%0.1f",fmtYTicks="%0.1f",**kwargs):
        self.bg = bg
        if isinstance(fmtXTicks,(bytes,six.string_types)):
            if fmtXTicks.startswith("DATE:%"):
                fmtXTicks = lambda x,fmt=fmtXTicks[5:]:datetime.datetime.fromtimestamp(x).strftime(fmt)
            else:
                if re.search("\{0?[:!][^}]*\}",fmtXTicks):
                    fmtXTicks = fmtXTicks.format
                else:
                    fmtXTicks = lambda x,msg=fmtXTicks:msg%(x,)
        self.fmtXTicks = fmtXTicks

        if isinstance(fmtYTicks,(bytes,six.string_types)):
            if fmtYTicks.startswith("DATE:%"):
                fmtYTicks = lambda x,fmt=fmtYTicks[5:]:datetime.datetime.fromtimestamp(x).strftime(fmt)
            else:
                if re.search("\{0?[:!][^}]*\}",fmtYTicks):
                    fmtYTicks = fmtYTicks.format
                else:
                    fmtYTicks = lambda x,msg=fmtYTicks:msg%(x,)
        self.fmtYTicks = fmtYTicks
        colors = colors or self.colors
        self.colors = itertools.cycle(colors)
        self.kwargs = kwargs
        if isinstance(margin,(int)):
            margin = [margin]
        if len(margin) == 1:
            margin = [margin,margin]
        if len(margin) == 2:
            margin = margin[:2] + margin[:2]
        self.margin = list(margin)
        wx.Panel.__init__(self,parent)
        if 'size' in kwargs:
            self.SetMinSize(kwargs['size'])
            self.SetSize(kwargs['size'])
            self.w,self.h = kwargs['size']
        else:
            self.w, self.h = self.GetClientSize()
        self._chart_area = RectangleArea(margin[:2],[self.w-margin[2],self.h-margin[3]])
        self.trace_colors = {}
        self.chart = SimpleChartObject()
        self.SetBackgroundStyle(wx.BG_STYLE_CUSTOM)
        self.Bind(wx.EVT_SIZE, self.on_size)
        self.Bind(wx.EVT_PAINT, self.on_paint)

    def add_points(self,points_xy,traceID=0):
        self.chart.add_points(points_xy,traceID)

    def on_size(self, event):
        event.Skip()
        if 'size' in self.kwargs:
            self.w, self.h = self.kwargs['size']
        else:
            self.w, self.h = self.GetClientSize()
        if hasattr(self,"margin"):
            self.prepare_paint()
            self.Refresh()
    def prepare_paint(self):
        # calculate cached data
        self._chart_area = RectangleArea(self.margin[:2], [self.w - self.margin[2], self.h - self.margin[3]])
    def draw_text(self,dc,pt,text,align=wx.CENTER):
        x,y = pt
        tsz = dc.GetTextExtent(text)
        textW,textH = [tsz.width,tsz.height]
        if align & wx.ALIGN_RIGHT == wx.ALIGN_RIGHT:
            x = x-textW
        elif align & wx.ALIGN_CENTER_HORIZONTAL == wx.ALIGN_CENTER_HORIZONTAL:
            x = x - textW/2.0
        if align & wx.ALIGN_BOTTOM == wx.ALIGN_BOTTOM:
            y = y-textH
        elif align & wx.ALIGN_CENTER_VERTICAL == wx.ALIGN_CENTER_VERTICAL:
            y = y - textH / 2.0

        dc.DrawText(text, [x,y])
        return textW
    def on_paint(self, event):
        plt_area =  self._chart_area
        bg_brush = wx.Brush(wx.Colour(self.bg))
        dc = wx.AutoBufferedPaintDC(self)
        dc.SetBackground(bg_brush)
        dc.Clear()
        dc.SetPen(wx.BLACK_PEN)
        dc.DrawLines([[plt_area.left,plt_area.top],[plt_area.left,plt_area.bottom],[plt_area.right,plt_area.bottom]])
        axis = self.chart.get_axis(0)
        traces = axis.getTraces()
        # XTicks
        yTicks = [
            [plt_area.left,plt_area.top, plt_area.left-8,plt_area.top],
            [plt_area.left,plt_area.midY, plt_area.left-8,plt_area.midY],
            [plt_area.left,plt_area.bottom, plt_area.left-8,plt_area.bottom],
        ]

        # YTicks
        xTicks = [
            [plt_area.left, plt_area.bottom, plt_area.left, plt_area.bottom + 8],
            [ plt_area.midX,plt_area.bottom, plt_area.midX, plt_area.bottom + 8],
            [plt_area.right, plt_area.bottom, plt_area.right, plt_area.bottom+8],
        ]
        ticksX,ticksY = axis.get_xy_ticks(3,3)
        print(datetime.datetime.fromtimestamp(ticksX[0]))
        print(datetime.datetime.fromtimestamp(ticksX[1]))
        print(datetime.datetime.fromtimestamp(ticksX[2]))
        print( ticksY,self)
        if self.fmtYTicks:

            w1 = self.draw_text(dc,[plt_area.left-8,plt_area.top],self.fmtYTicks(ticksY[2]),wx.ALIGN_RIGHT|wx.ALIGN_CENTER)#|wx.ALIGN_CENTER_VERTICAL)
            w2 = self.draw_text(dc,[plt_area.left-8,plt_area.midY],self.fmtYTicks(ticksY[1]),wx.ALIGN_RIGHT|wx.ALIGN_CENTER)#|wx.ALIGN_CENTER_VERTICAL)
            w3 = self.draw_text(dc,[plt_area.left-8,plt_area.bottom],self.fmtYTicks(ticksY[0]),wx.ALIGN_RIGHT|wx.ALIGN_CENTER)#|wx.ALIGN_CENTER_VERTICAL)
        else:
            yTicks = []
        if self.fmtXTicks:
            self.draw_text(dc,[plt_area.left,plt_area.bottom+8],self.fmtXTicks(ticksX[0]),wx.ALIGN_TOP|wx.ALIGN_CENTER_HORIZONTAL)#|wx.ALIGN_CENTER_VERTICAL)
            self.draw_text(dc,[plt_area.midX,plt_area.bottom+8],self.fmtXTicks(ticksX[1]),wx.ALIGN_TOP|wx.ALIGN_CENTER_HORIZONTAL)#|wx.ALIGN_CENTER_VERTICAL)
            self.draw_text(dc,[plt_area.right,plt_area.bottom+8],self.fmtXTicks(ticksX[2]),wx.ALIGN_TOP|wx.ALIGN_CENTER_HORIZONTAL)#|wx.ALIGN_CENTER_VERTICAL)
        else:
            xTicks = []
        if self.fmtXTicks or self.fmtYTicks:
            print("T:",xTicks,yTicks)
            dc.DrawLineList(xTicks + yTicks)
        for trace_pk, trace in traces:
            if trace.config.get('color') is None and trace_pk not in self.trace_colors:
                trace.config['color'] = next(self.colors)
            dc.SetPen(wx.Pen(wx.Colour(trace.config['color']),width=2))
            dc.SetBrush(wx.Brush(wx.Colour(trace.config['color'])))
            for line in trace.split_points():
                if len(line) == 0:
                    continue
                line[:, 1] = line[:, 1] * plt_area.height + plt_area.top
                line[:, 0] = line[:, 0] * plt_area.width + plt_area.left
                if len(line)==1:
                    dc.DrawCircle(line[0][0],line[0][1],2)
                else:
                    dc.DrawLines(line)
        # for axisId in sorted(self.chart._axes.keys()):
        #     dc.DrawLineList(self.chart.,)

        # dc.DrawLine(0, 0, w, h)
        # dc.SetPen(wx.Pen(wx.BLACK, 5))
        # dc.DrawCircle(w / 2, h / 2, 100)



if __name__ == '__main__':
    class Frame(wx.Frame):
        def __init__(self):
            super(Frame, self).__init__(None)
            self.SetTitle('My Title')
            self.SetClientSize((320 , 120))
            self.Center()
            a = numpy.random.uniform(80, 126, 100)
            a = numpy.hstack([numpy.array([float("nan")] * 10), a])
            x = numpy.arange(int(time.time()) - 100, int(time.time()))
            y = numpy.random.choice(a, 100)
            a2 = numpy.random.uniform(60, 90, 100)
            a2 = numpy.hstack([numpy.array([float("nan")] * 10), a2])
            y2 = numpy.random.choice(a2, 100)
            self.last = [[x[-1],y[-1]],[x[-1],y2[-1]]]
            layout = wx.BoxSizer(wx.VERTICAL)
            self.view = wxChartPanel(self,
                                     bg="#FFFFFF",
                                     margin=[40,8,15,30],
                                     fmtXTicks="DATE:%M:%S",
                                     fmtYTicks="%0.1f")
            self.view.add_points(list(zip(x,y)))
            self.view.add_points(list(zip(x,y2)),1)
            layout.Add(self.view,1,wx.ALL|wx.EXPAND,10)
            self.view1 = wxChartPanel(self,
                                     bg="#FFFFFF",
                                     margin=[40, 8, 15, 10],
                                     fmtXTicks=None,
                                     fmtYTicks="%0.1f",
                                     size=(300,200))
            self.view1.add_points(list(zip(x, y)))
            self.view1.add_points(list(zip(x, y2)), 1)
            layout.Add(self.view1,1,wx.ALL|wx.EXPAND,10)
            self.SetSizer(layout)
            self.add_point_tick()
            self.Layout()
            self.Fit()


        def add_point_tick(self):
            self.view.chart.get_axis(0).lockXRange([time.time()-300,time.time()])
            y = self.last[0][1] + numpy.random.uniform(-2,2)
            x = time.time()
            y2 = self.last[1][1] +  numpy.random.uniform(-0.5,0.5)
            self.last = [[x,y],[x,y2]]
            self.view.add_points([[x,y]])
            self.view.add_points([[x,y2]],1)
            self.Refresh()
            wx.CallLater(1000,self.add_point_tick)


    def main():
        app = wx.App(False)
        frame = Frame()
        frame.Show()
        app.MainLoop()
    main()
