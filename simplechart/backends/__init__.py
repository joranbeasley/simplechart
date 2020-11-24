#from ._util import RectangleArea
try:
    from ._kivy import kvChartPanel
except:
    print("Unable to import kvChartPanel")
try:
    from ._wx import wxChartPanel
except:
    print("Unable to import wxChartPanel")
try:
    from ._tk import TKChartCanvas
except:
    print("Unable to import TKChartCanvas")
