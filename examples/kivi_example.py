from kivy.app import App
import numpy
from simplechart.backends.kiviChartPanel import kvChartPanel
import time

class TestApp(App):
    # def on_tick(self):
    def on_tick(self, *args):
        pass

    def build(self):
        # return a Button() as a root widget
        print("????")
        # Clock.schedule_interval(1000,self.on_tick)
        self.chart = kvChartPanel(fmtXTicks="DATE:%M:%S", margin=[60, 10, 30, 25])
        a = numpy.random.uniform(80, 126, 100)
        a = numpy.hstack([numpy.array([float("nan")] * 10), a])
        x = numpy.arange(int(time.time()) - 100, int(time.time()))
        y = numpy.random.choice(a, 100)
        a2 = numpy.random.uniform(60, 90, 100)
        a2 = numpy.hstack([numpy.array([float("nan")] * 10), a2])
        y2 = numpy.random.choice(a2, 100)
        self.chart.chart.get_axis(0).lockXRange([time.time() - 300, time.time()])
        self.chart.add_points(list(zip(x, y)))
        self.chart.add_points(list(zip(x, y2)), 1)
        self.chart.Refresh()
        return self.chart


def main():
    app = TestApp()
    app.run()


main()
