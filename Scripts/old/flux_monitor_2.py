#!/usr/bin/env python
"""Flux Monitor 2

History:
2019-12-22  DG  This code was started a few months ago, but I picked it up
    again when I learned more about plotting. The plotting libraries in RO
    are fairly rigid, and my attempts at bypassing it were futile, so I
    embraced the beast and found what I needed inside the guider keys

"""
import datetime
import TUI.Base.StripChartWdg
import TUI.Models
import matplotlib as mpl


class ScriptClass(object, ):
    def __init__(self, sr, ):
        sr.debug = False
        self.sr = sr
        self.sr.master.winfo_toplevel().wm_resizable(True, True)
        self.guider_model = TUI.Models.getModel("guider")
        print('---Flux Monitor 2---', datetime.datetime.now())
        timeRange = 3600
        width = 8
        height = 2.4

        self.plot_widget = TUI.Base.StripChartWdg.StripChartWdg(
            master=sr.master,
            timeRange=timeRange, numSubplots=1, width=width, height=height,
            cnvTimeFunc=TUI.Base.StripChartWdg.TimeConverter(useUTC=True), )

        self.plot_widget.grid(row=0, column=0, sticky='nwes')
        self.plot_widget.grid_rowconfigure(0, weight=1)
        self.plot_widget.grid_columnconfigure(0, weight=1)
        self.plot_widget.xaxis.set_major_locator(mpl.dates.MinuteLocator(
            byminute=range(0, 61, 10)))

        self.plot_widget.plotKeyVar(subplotInd=0, keyInd=0,
                                    keyVar=self.guider_model.probe,
                                    func=self.mag_diff,
                                    c='g')
        self.plot_widget.subplotArr[0].yaxis.set_label_text(r'$\Delta m$')
        self.plot_widget.addConstantLine(0, subplotInd=0, c='k')
        # self.plot_widget.addConstantLine(100, subplotInd=0, c='k')

    def model_ref_ratio(self, var):
        """The guider spits out probe[8] which is the modelled magnitude. It's
        called model because it uses a model to reduce the image, but that is
        the actual data. Meanwhile, probe[9] is the reference magnitude and
        should always be larger. Using the magnitude formula, I can use this
        to compute a flux ratio. Var is unfortunately useless because it
        refers to just model or just ref, so instead I pull it straight form
        the guider model dictionary which updates 17? times a guider image,
        each will result in a plotting callback that runs this function
        """
        model = self.guider_model.probe[8]
        ref = self.guider_model.probe[9]
        flux_ratio = 10 ** (2.5 * (ref - model))
        if flux_ratio > 1:
            flux_ratio = 1
        elif flux_ratio < 0:
            flux_ratio = 0
        return flux_ratio

    def clearCharts(self):
        """Clear all strip charts
        """
        self.plot_widget.clear()

    def run(self, sr):
        self.clearCharts()

    def end(self, sr):
        pass
