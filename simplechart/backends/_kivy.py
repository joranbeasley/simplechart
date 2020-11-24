import datetime
import itertools
import re
import sys
import time
from tkinter import font

import numpy
import six
from kivy.clock import Clock
from kivy.graphics import Color,Rectangle,Line
from kivy.graphics.vertex_instructions import Ellipse
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.core.text import Label as CoreLabel, DEFAULT_FONT
from simplechart import SimpleChartObject, RectangleArea

# import wx
from kivy.app import App
def hex2rgb(hex):
    if hex.startswith("0x"):
        hex = hex[2:]
    if hex.startswith("#"):
        hex = hex[1:]
    r = int(hex[:2],16)/255.0
    g = int(hex[2:4],16)/255.0
    b = int(hex[4:6],16)/255.0
    return (r,g,b)
class kvChartPanel(Widget):
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22',
              '#17becf']
    def __init__(self, bg="#FFFFFF",margin=(40,8,15,22),colors=None,
                 fmtXTicks="%0.1f",fmtYTicks="%0.1f",**kwargs):
        self.chart = SimpleChartObject()
        self.traces = None
        self.bg = bg
        self.lbl = CoreLabel()
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
        self.colors = itertools.cycle(map(hex2rgb,colors))
        self.trace_colors = {}
        self.kwargs = kwargs
        self.Ylabels = [
            Label(text="1.0", size=(-1, -1), pos=(20,0)),
            Label(text="0.0", size=(-1, -1), pos=(20,50)),
            Label(text="-1.0", size=(-1, -1), pos=(20,100))
        ]
        self.Xlabels = [
            Label(text="", size=(-1, -1), pos=(20, 0)),
            Label(text="", size=(-1, -1), pos=(20, 50)),
            Label(text="", size=(-1, -1), pos=(20, 100))
        ]
        # self.lbl.font_name=DEFAULT_FONT
        # self.lbl.font_size=16
        # def getSize(txt):
        #     self.Ylabels[0].()
        #     print(self.Ylabels[0].texture.size)
        #     return self.lbl.content_size
        # self.YlabelSizes = [getSize("12.55"),getSize("12.25"),getSize("12.15"),]
        self.YlabelSizes = [[1,1],[2,2],[3,3]]
        self.XlabelSizes = [[1,1],[2,2],[3,3]]
        print(max([sz[0] for sz in self.YlabelSizes]))
        # print("SSSSS",self.lbl.texture.size)
        if isinstance(margin,(int)):
            margin = [margin]
        if len(margin) == 1:
            margin = [margin,margin]
        if len(margin) == 2:
            margin = margin[:2] + margin[:2]
        self.margin = list(margin)
        Widget.__init__(self,**kwargs)
        for lbl in self.Ylabels:
            self.add_widget(lbl)
        for lbl in self.Xlabels:
            self.add_widget(lbl)

        self.Refresh()
        # if 'size' in kwargs:
        #     self.SetMinSize(kwargs['size'])
        #     self.SetSize(kwargs['size'])
        #     self.w,self.h = kwargs['size']
        # else:
        #     self.w, self.h = self.GetClientSize()
        # self._chart_area = RectangleArea(margin[:2],[self.w-margin[2],self.h-margin[3]])
        # self.trace_colors = {}

        # self.SetBackgroundStyle(wx.BG_STYLE_CUSTOM)
        # self.bind(size=self.on_size)
        # self.bind(pos=self.on_paint)
    def Refresh(self):
        self.prepare_paint()
        self.repaint()
    def repaint(self):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(0,0,0)
            Rectangle(pos=(0,0),size=self.size)
            Color(1,1,1)

            # print([self._chart_area.left,self._chart_area.top],[self._chart_area.left,self._chart_area.bottom],[self._chart_area.right,self._chart_area.bottom])
            Line(points=[self._chart_area.left,self._chart_area.top,
                         self._chart_area.left,self._chart_area.bottom,
                         self._chart_area.right,self._chart_area.bottom])
            if self.fmtYTicks:
                # Y Ticks
                Line(points=[self._chart_area.left,self._chart_area.top,self._chart_area.left-6,self._chart_area.top])
                Line(points=[self._chart_area.left,self._chart_area.midY,self._chart_area.left-6,self._chart_area.midY])
                Line(points=[self._chart_area.left,self._chart_area.bottom,self._chart_area.left-6,self._chart_area.bottom])
                for i,pos in enumerate(
                        [
                           [self._chart_area.left-self.YlabelSizes[0][0]/2.0-9, self._chart_area.top],
                           [self._chart_area.left-self.YlabelSizes[1][0]/2.0-9, self._chart_area.midY],
                           [self._chart_area.left-self.YlabelSizes[2][0]/2.0-9, self._chart_area.bottom]
                        ]
                                       ):
                    self.Ylabels[i].pos = pos

            if self.fmtXTicks:
                # X Ticks
                Line(points=[self._chart_area.left, self._chart_area.bottom, self._chart_area.left, self._chart_area.bottom-6])
                Line(points=[self._chart_area.midX, self._chart_area.bottom, self._chart_area.midX, self._chart_area.bottom-6])
                Line(points=[self._chart_area.right, self._chart_area.bottom, self._chart_area.right,self._chart_area.bottom-6])
                print("X:",self.XlabelSizes)
                for i,pos in enumerate([[self._chart_area.left, self._chart_area.bottom-self.XlabelSizes[0][1]/2.0-9],
                                       [self._chart_area.midX, self._chart_area.bottom-self.XlabelSizes[1][1]/2.0-9],
                                       [self._chart_area.right,self._chart_area.bottom-self.XlabelSizes[2][1]/2.0-9]]
                                       ):
                    self.Xlabels[i].pos = pos
            for trace_pk,trace in self.traces:
                if trace.config.get('color') is None and trace_pk not in self.trace_colors:
                    trace.config['color'] = next(self.colors)

                trace_color = trace.config['color']
                print(trace_color)
                Color(*trace_color)
                for line in trace.split_points():
                    if len(line) == 0:
                        continue
                    line[:, 1] = line[:, 1] * self._chart_area.height + self._chart_area.top
                    line[:, 0] = line[:, 0] * self._chart_area.width + self._chart_area.left

                    if len(line) == 1:
                        p = [line[0][0]-3,line[0][1]-3]
                        Ellipse(angle_start=0,angle_end=360,pos=p,size=[6,6])
                    else:
                        Line(points=line.tolist(),)
    def add_points(self,points_xy,traceID=0):
        self.chart.add_points(points_xy,traceID)

    def on_size(self, event,*args):
        self.prepare_paint()
        self.Refresh()

    def prepare_paint(self):
        self.axis = self.chart.get_axis(0)
        self.traces = self.axis.getTraces()
        if self.fmtXTicks or self.fmtYTicks:
            xTicks,yTicks = self.axis.get_xy_ticks(3,3)
            yTicks = yTicks[::-1]
            maxW = 0
            maxH = 0
            if self.fmtYTicks:
                y_label_sizes = []
                for i,lbl in enumerate(self.Ylabels):
                    lbl.text = self.fmtYTicks(yTicks[i])
                    lbl.texture_update()
                    y_label_sizes.append(lbl.texture_size)
                    maxW = max(maxW, y_label_sizes[-1][1])
                if maxW > self.margin[0]:
                    self.margin[0] = maxW
                self.YlabelSizes = y_label_sizes
            if self.fmtXTicks:
                x_label_sizes = []
                for i, lbl in enumerate(self.Xlabels):
                    lbl.text = self.fmtXTicks(xTicks[i])
                    lbl.texture_update()
                    x_label_sizes.append(lbl.texture_size)
                    maxH = max(maxH, x_label_sizes[-1][1])+5
                if maxH > self.margin[3]:
                    self.margin[3] = maxH
                self.XlabelSizes = x_label_sizes

        # calculate cached data
        print(self.size)
        self._chart_area = RectangleArea(
            [self.margin[0],   self.size[1]-self.margin[1]],
            [self.size[0] - self.margin[2], self.margin[3]])
    # def draw_text(self,dc,pt,text,align=wx.CENTER):
    #     x,y = pt
    #     tsz = dc.GetTextExtent(text)
    #     textW,textH = [tsz.width,tsz.height]
    #     if align & wx.ALIGN_RIGHT == wx.ALIGN_RIGHT:
    #         x = x-textW
    #     elif align & wx.ALIGN_CENTER_HORIZONTAL == wx.ALIGN_CENTER_HORIZONTAL:
    #         x = x - textW/2.0
    #     if align & wx.ALIGN_BOTTOM == wx.ALIGN_BOTTOM:
    #         y = y-textH
    #     elif align & wx.ALIGN_CENTER_VERTICAL == wx.ALIGN_CENTER_VERTICAL:
    #         y = y - textH / 2.0
    #
    #     dc.DrawText(text, [x,y])
    #     return textW
    # def on_paint(self, event):
    #     plt_area =  self._chart_area
    #     bg_brush = wx.Brush(wx.Colour(self.bg))
    #     dc = wx.AutoBufferedPaintDC(self)
    #     dc.SetBackground(bg_brush)
    #     dc.Clear()
    #     dc.SetPen(wx.BLACK_PEN)
    #     dc.DrawLines([[plt_area.left,plt_area.top],[plt_area.left,plt_area.bottom],[plt_area.right,plt_area.bottom]])
    #     axis = self.chart.get_axis(0)
    #     traces = axis.getTraces()
    #     # XTicks
    #     yTicks = [
    #         [plt_area.left,plt_area.top, plt_area.left-8,plt_area.top],
    #         [plt_area.left,plt_area.midY, plt_area.left-8,plt_area.midY],
    #         [plt_area.left,plt_area.bottom, plt_area.left-8,plt_area.bottom],
    #     ]
    #
    #     # YTicks
    #     xTicks = [
    #         [plt_area.left, plt_area.bottom, plt_area.left, plt_area.bottom + 8],
    #         [ plt_area.midX,plt_area.bottom, plt_area.midX, plt_area.bottom + 8],
    #         [plt_area.right, plt_area.bottom, plt_area.right, plt_area.bottom+8],
    #     ]
    #     ticksX,ticksY = axis.get_xy_ticks(3,3)
    #     print(datetime.datetime.fromtimestamp(ticksX[0]))
    #     print(datetime.datetime.fromtimestamp(ticksX[1]))
    #     print(datetime.datetime.fromtimestamp(ticksX[2]))
    #     print( ticksY,self)
    #     if self.fmtYTicks:
    #
    #         w1 = self.draw_text(dc,[plt_area.left-8,plt_area.top],self.fmtYTicks(ticksY[2]),wx.ALIGN_RIGHT|wx.ALIGN_CENTER)#|wx.ALIGN_CENTER_VERTICAL)
    #         w2 = self.draw_text(dc,[plt_area.left-8,plt_area.midY],self.fmtYTicks(ticksY[1]),wx.ALIGN_RIGHT|wx.ALIGN_CENTER)#|wx.ALIGN_CENTER_VERTICAL)
    #         w3 = self.draw_text(dc,[plt_area.left-8,plt_area.bottom],self.fmtYTicks(ticksY[0]),wx.ALIGN_RIGHT|wx.ALIGN_CENTER)#|wx.ALIGN_CENTER_VERTICAL)
    #     else:
    #         yTicks = []
    #     if self.fmtXTicks:
    #         self.draw_text(dc,[plt_area.left,plt_area.bottom+8],self.fmtXTicks(ticksX[0]),wx.ALIGN_TOP|wx.ALIGN_CENTER_HORIZONTAL)#|wx.ALIGN_CENTER_VERTICAL)
    #         self.draw_text(dc,[plt_area.midX,plt_area.bottom+8],self.fmtXTicks(ticksX[1]),wx.ALIGN_TOP|wx.ALIGN_CENTER_HORIZONTAL)#|wx.ALIGN_CENTER_VERTICAL)
    #         self.draw_text(dc,[plt_area.right,plt_area.bottom+8],self.fmtXTicks(ticksX[2]),wx.ALIGN_TOP|wx.ALIGN_CENTER_HORIZONTAL)#|wx.ALIGN_CENTER_VERTICAL)
    #     else:
    #         xTicks = []
    #     if self.fmtXTicks or self.fmtYTicks:
    #         print("T:",xTicks,yTicks)
    #         dc.DrawLineList(xTicks + yTicks)
    #     for trace_pk, trace in traces:
    #         if trace.config.get('color') is None and trace_pk not in self.trace_colors:
    #             trace.config['color'] = next(self.colors)
    #         dc.SetPen(wx.Pen(wx.Colour(trace.config['color']),width=2))
    #         dc.SetBrush(wx.Brush(wx.Colour(trace.config['color'])))
    #         for line in trace.split_points():
    #             if len(line) == 0:
    #                 continue
    #             line[:, 1] = line[:, 1] * plt_area.height + plt_area.top
    #             line[:, 0] = line[:, 0] * plt_area.width + plt_area.left
    #             if len(line)==1:
    #                 dc.DrawCircle(line[0][0],line[0][1],2)
    #             else:
    #                 dc.DrawLines(line)
        # for axisId in sorted(self.chart._axes.keys()):
        #     dc.DrawLineList(self.chart.,)

        # dc.DrawLine(0, 0, w, h)
        # dc.SetPen(wx.Pen(wx.BLACK, 5))
        # dc.DrawCircle(w / 2, h / 2, 100)



if __name__ == '__main__':



    class TestApp(App):
        # def on_tick(self):
        def on_tick(self,*args):
            pass
        def build(self):
            # return a Button() as a root widget
            print("????")
            # Clock.schedule_interval(1000,self.on_tick)
            self.chart = kvChartPanel(fmtXTicks="DATE:%M:%S",margin=[60,10,30,25])
            a = numpy.random.uniform(80, 126, 100)
            a = numpy.hstack([numpy.array([float("nan")] * 10), a])
            x = numpy.arange(int(time.time()) - 100, int(time.time()))
            y = numpy.random.choice(a, 100)
            a2 = numpy.random.uniform(60, 90, 100)
            a2 = numpy.hstack([numpy.array([float("nan")] * 10), a2])
            y2 = numpy.random.choice(a2, 100)
            self.chart.chart.get_axis(0).lockXRange([time.time()-300,time.time()])
            self.chart.add_points(list(zip(x, y)))
            self.chart.add_points(list(zip(x, y2)), 1)
            self.chart.Refresh()
            return self.chart


    def main():
        app = TestApp()
        app.run()
    main()
