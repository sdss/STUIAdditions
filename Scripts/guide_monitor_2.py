"""A combination of the scale error and focus error plots, based on the
    axisError script. It was inspired by the business of the guide monitor,
    which was too hard to read and borderline useless, as well as a discontent
    with how the scale monitor shows scale error, but the focus monitor shows
    net offset, which is inconsistent.

History:
2019-12-20  DG  Init
"""

import RO.Wdg
import TUI
import matplotlib as mpl

class ScriptClass(object):
    def __init__(self, sr):
        print('---Guide Monitor 2---')
        sr.debug = False
        sr.master.winfo_toplevel().wm_resizable(True, True)
        self.guider_model = TUI.Models.getModel('guider')
        self.tcc_model = TUI.Models.getModel('tcc')

        time_range = 1800
        width = 8
        height = 6
        self.plot_widget = TUI.Base.StripChartWdg.StripChartWdg(
            master=sr.master, timeRange=time_range, numSubplots=2, width=width,
            height=height, cnvTimeFunc=TUI.Base.StripChartWdg.TimeConverter(
                useUTC=True))
        self.plot_widget.grid(row=0, column=0, sticky='nwes')
        self.plot_widget.grid_rowconfigure(0, weight=1)
        self.plot_widget.grid_columnconfigure(0, weight=1)
        
        self.plot_widget.xaxis.set_major_locator(mpl.dates.MinuteLocator(
            byminute=range(0,61,5)))

        # Callback

        # Focus Error"
        self.plot_widget.setYLimits(-150, 150, subplotInd=0)
        self.plot_widget.plotKeyVar(subplotInd=0, 
            keyVar=self.guider_model.focusError, keyInd=0, c='b')
        self.plot_widget.addConstantLine(60, subplotInd=0, color="red")
        self.plot_widget.addConstantLine(-60, subplotInd=0, color="red")
        self.plot_widget.addConstantLine(0, subplotInd=0, c='gray')
        self.plot_widget.subplotArr[0].yaxis.set_label_text('Focus Error')
        
        self.plot_widget.setYLimits(-60, 60, subplotInd=1)
        self.plot_widget.plotKeyVar(subplotInd=1, keyInd=0,
            func=self.scale_conv, keyVar=self.guider_model.scaleError, c='g')
        self.plot_widget.subplotArr[1].yaxis.set_label_text('Scale Error')
        self.plot_widget.addConstantLine(-30, subplotInd=1, c='r')
        self.plot_widget.addConstantLine(30, subplotInd=1, c='r')
        self.plot_widget.addConstantLine(0, subplotInd=1, c='gray')

    def scale_conv(self, val):
        """The -1 part is baked into the input value, but we still need the 1e6
        """
        v = val * 1.0e6
        return v

    def run(self, sr):
        pass

    def end(self, sr):
        pass

