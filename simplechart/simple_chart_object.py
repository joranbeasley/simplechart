import numpy

class Trace(object):
    def __init__(self,axis,trace_id,name="",config=None):
        self.hidden = False
        print("INIT!!!")
        self.axis = axis
        if trace_id in self.axis.traces:
            raise TypeError("This Trace ID is already in use in this axis!!!")
        elif trace_id in self.axis.chart._traces:
            raise TypeError("This TraceID is already in use in this chart")
        self.axis.chart._traces[trace_id] = self
        self.axis.traces[trace_id] = self
        self.type = type
        self.name = name
        self.config = config or {}
        self.chart = axis.chart
        if trace_id in self.chart._unknownHiddenTraces:
            self.chart._unknownHiddenTraces.remove(trace_id)
            self.hidden = True
        self._points = numpy.array([])
        self.xRange = [-1,1]
        self.yRange = [-1,1]
        self.visible = True
        self.dirty = True

    @property
    def points(self):
        return self._points
    @points.setter
    def points(self,value):
        value = numpy.array(value,dtype=float)
        if numpy.all(value == self._points):
            return
        self.dirty = True
        self._points = value
        assert self._points.shape[1] == 2, "Error expecting list of [[x,y],[x1,y1]]..."

    def append_points(self,points_xy):
        if len(self.points) == 0:
            self.points = points_xy
        else:
            try:
                self.points = numpy.vstack([self.points,points_xy])
            except:
                print("ERROR STACKING:",self.points)
        x,y = self.points[:,0],self.points[:,1]
        self.xRange = [numpy.nanmin(x),numpy.nanmax(x)]
        self.yRange = [numpy.nanmin(y),numpy.nanmax(y)]

    def add_point(self,x,y):
        self.append_points([[x,y]])


    def to_ratios(self,xRange,yRange,invertY=True):
        """
        returns the list of points as a ratio to the available space

        :param xRange: [MinX,MaxX]
        :param yRange: [MinY,MaxY]
        :return:
        """

        if not len(self.points):
            return self.points
        points = self.points[(self.points[:,0]>=xRange[0]) & (self.points[:,0]<=xRange[1])].T
        points[0] = (points[0] - xRange[0])/float(xRange[1] - xRange[0])
        if invertY:
            points[1] = 1-(points[1] - yRange[0])/float(yRange[1]-yRange[0])
        else:
            points[1] = (points[1] - yRange[0])/float(yRange[1]-yRange[0])
        # print(self.points,points,xRange)
        return points.T

    def clear_data_before_x(self, minX):
        self.points = self.points[self.points[:,0] >= minX]
    def split_points(self,translated=True,invertY=True):
        if len(self.points) > 0:
            if translated:
                points = self.to_ratios(self.axis.xRange,self.axis.yRange,invertY).T
            else:
                points = self.points.T
            indexes = [-1]+numpy.where(numpy.isnan(points[1]) | numpy.isnan(points[1]))[0].tolist() + [len(points[0])]
            ranges = [(i+1,j)for i,j in zip(indexes,indexes[1:]) if i+1 != j]
            points = points.T
            for r in ranges:
                yield points[r[0]:r[1]]

class RectangleArea:
    @staticmethod
    def from_size(topleft,width,height):
        return RectangleArea(topleft,[topleft[0]+width,topleft[1]+height])
    def __init__(self,topleft,bottomright):
        self.topleft = topleft
        self.bottomright = bottomright
        self.width = self.right - self.left
        self.height = self.bottom - self.top
        self.midX = (self.right+self.left)/2.0
        self.midY = (self.top+self.bottom)/2.0


    def __getattr__(self, item):
        if item in 'x y left top bottom right':
           return {
             "x":self.topleft[0],
             "y":self.topleft[1],
             "left": self.topleft[0],
             "top": self.topleft[1],
             "bottom":self.bottomright[1],
             "right":self.bottomright[0]
           }[item.lower()]
        return{
            'topright':[self.right,self.top],
            'bottomleft':[self.left,self.bottom],
            'centerleft':[self.left,self.midY],
            'centerright':[self.right,self.midY],
            'centertop':[self.midX,self.top],
            'centerbottom':[self.midY,self.bottom]
        }[item.lower()]



class Axis(object):
    def __init__(self,chart,name="",colors=None):
        self.colors = colors
        self.chart = chart
        self.traces = {}
        self.lock_axes = {}
        self.xRange = [0,1]
        self.yRange = [-1,1]
    def dirty(self):
        for t in self.traces.values():
            if t.dirty:
                return True
        return False
    def get_y_ticks(self, nTicks=2):
        if self.dirty():
            self._refreshMinMax()
        return numpy.linspace(self.yRange[0],self.yRange[1],nTicks)
    def get_x_ticks(self, nTicks=2):
        if self.dirty():
            self._refreshMinMax()
        return numpy.linspace(self.xRange[0],self.xRange[1],nTicks)
    def get_xy_ticks(self,nTicksX=2,nTicksY=3):
        if self.dirty():
            self._refreshMinMax()
        return (numpy.linspace(self.xRange[0], self.xRange[1], nTicksX),
                numpy.linspace(self.yRange[0], self.yRange[1], nTicksY))
    def lockXRange(self,xRange):
        self.lock_axes['X'] = xRange
    def lockYRange(self,yRange):
        self.lock_axes['Y'] = yRange
    def _getPointsAsRatios(self,traceId,refreshMinMax=False):
        if self.dirty():
            self._refreshMinMax()
        return self.traces[traceId].to_ratios(self.xRange,self.yRange)
    def getTracesAsRatios(self):
        if self.dirty():
            self._refreshMinMax()
        return [{'id':idx,'points':self._getPointsAsRatios(idx),'name':self.traces[idx].name, 'color':self.traces[idx].color} \
                                                                   for idx in sorted(self.traces.keys())]
    def getTraces(self):
        if self.dirty():
            self._refreshMinMax()
        return [(idx, self.traces[idx]) for idx in sorted(self.traces.keys())]

    def _refreshMinMax(self):
        Xmins = []
        Xmaxes = []
        Ymins = []
        Ymaxes = []
        if 'X' in self.lock_axes and 'Y' in self.lock_axes:
            self.xRange = self.lock_axes['X']
            self.yRange = self.lock_axes['Y']
            return
        for trace in self.traces.values():
            trace.dirty = False
            if trace.visible:
                Xmins.append(trace.xRange[0])
                Xmaxes.append(trace.xRange[1])
                Ymins.append(trace.yRange[0])
                Ymaxes.append(trace.yRange[1])
        self.xRange = self.lock_axes.get('X',[max(0,numpy.nanmin(Xmins)-1),numpy.nanmax(Xmaxes)+1])
        self.yRange = self.lock_axes.get('Y',[numpy.nanmin(Ymins)-1,numpy.nanmax(Ymaxes)+1])



class SimpleChartObject(object):
    def __init__(self):
        self._unknownHiddenTraces = set()
        self._axes = {}
        self._traces = {}


    def show_trace(self,tracePk,show=True):
        if tracePk in self._traces:
            self._traces[tracePk].visible = show
        elif show is False:
            self._unknownHiddenTraces.add(tracePk)
    def hide_trace(self,tracePk):
        self.show_trace(tracePk,False)
    def add_axis(self,name=""):
        self._axes[len(self._axes)] = Axis(self,name)
    def configure_trace(self,traceId,color=None,name=None,type=None):
        pass
    def add_trace(self,name="",initialPoints=None,color=None,axisId=0,type="line"):
        if axisId not in self._axes:
            self._axes[axisId] = Axis(self)
        traceId = len(self._traces)
        self._traces[traceId] = Trace(self._axes[axisId],traceId,name,type,color)
        if len(initialPoints):
           self._traces[traceId].add_points(initialPoints)
    def add_point(self,x,y,traceID=0):
        if traceID not in self._traces:
            self._traces[traceID] = Trace(self._axes[0],traceID)
        self._traces[traceID].add_point(x,y)
    def clear_data_before_minX(self,minX):
        for t in self._traces:
            t.clear_data_before_x(minX)
    def get_axis(self,axisId):
        if axisId not in self._axes:
            self._axes[axisId] = Axis(self)
        return self._axes[axisId]
    def add_points(self,points_xy,traceID=0):
        if traceID not in self._traces:
            self._traces[traceID] = Trace(self._axes[0], traceID)
        self._traces[traceID].append_points(points_xy)


if __name__ == "__main__":
    c = SimpleChartObject()
    c.add_points([[1,2],[2,float('nan')],[3,float("nan")],[4,5],[5,float('nan')],[6,7]])
    for idx,t in c.get_axis(0).getTraces():
        for line in t.split_points(False):
            print(line)
