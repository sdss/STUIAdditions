"""A combination of the scale error and focus error plots, based on the
    axisError script. It was inspired by the business of the guide monitor,
    which was too hard to read and borderline useless, as well as a discontent
    with how the scale monitor shows scale error, but the focus monitor shows
    net offset, which is inconsistent.

History:
2019-12-20  DG  Init
2020-03-16  DG  Many minor adjustments after testing. Notably that the flux
    monitor is an average over all fibers, and it's now in magnitudes
"""

import TUI.Base.StripChartWdg
import TUI.Models
import matplotlib as mpl
import numpy as np
import datetime

__version__ = '3.0.1'


class ScriptClass(object):
    def __init__(self, sr):
        print('===Guide Monitor 2 Version {}==='.format(__version__))
        sr.debug = False
        sr.master.winfo_toplevel().wm_resizable(True, True)
        self.guider_model = TUI.Models.getModel('guider')
        self.tcc_model = TUI.Models.getModel('tcc')

        time_range = 1800
        width = 8
        height = 9
        self.plot_widget = TUI.Base.StripChartWdg.StripChartWdg(
            master=sr.master, timeRange=time_range, numSubplots=4, width=width,
            height=height, cnvTimeFunc=TUI.Base.StripChartWdg.TimeConverter(
                useUTC=True))
        self.plot_widget.grid(row=0, column=0, sticky='nwes')
        self.plot_widget.grid_rowconfigure(0, weight=1)
        self.plot_widget.grid_columnconfigure(0, weight=1)

        self.plot_widget.xaxis.set_major_locator(mpl.dates.MinuteLocator(
            byminute=range(0, 61, 5)))

        # Callback

        # Focus Error"
        self.plot_widget.setYLimits(-150, 150, subplotInd=0)
        self.plot_widget.plotKeyVar(subplotInd=0,
                                    keyVar=self.guider_model.focusError,
                                    keyInd=0, c='b')
        self.plot_widget.addConstantLine(60, subplotInd=0, color="red")
        self.plot_widget.addConstantLine(-60, subplotInd=0, color="red")
        self.plot_widget.addConstantLine(0, subplotInd=0, c='gray')
        self.plot_widget.subplotArr[0].yaxis.set_label_text('Focus Error')

        self.plot_widget.setYLimits(-60, 60, subplotInd=1)
        self.plot_widget.plotKeyVar(subplotInd=1, keyInd=0,
                                    func=self.scaleConvert,
                                    keyVar=self.guider_model.scaleError, c='g')
        self.plot_widget.subplotArr[1].yaxis.set_label_text('Scale Error')
        self.plot_widget.addConstantLine(-30, subplotInd=1, c='r')
        self.plot_widget.addConstantLine(30, subplotInd=1, c='r')
        self.plot_widget.addConstantLine(0, subplotInd=1, c='gray')

        # Seeing
        self.plot_widget.setYLimits(0, 3, subplotInd=2)
        self.plot_widget.plotKeyVar(subplotInd=2, keyInd=0, color='orange',
                                    keyVar=self.guider_model.seeing,
                                    label='Seeing')
        self.plot_widget.subplotArr[2].yaxis.set_label_text('Seeing')
        self.plot_widget.addConstantLine(1, subplotInd=2, c='k')
        self.plot_widget.addConstantLine(1, subplotInd=2, c='k')

        # self.plot_widget.setYLimits(0, 0.15, subplotInd=3)
        self.plot_widget.plotKeyVar(subplotInd=3, keyInd=0,
                                    keyVar=self.guider_model.probe,
                                    func=self.mag_diff,
                                    c='g')
        # self.plot_widget.subplotArr[3].yaxis.set_label_text(r'$\Delta m$')
        self.plot_widget.subplotArr[3].yaxis.set_label_text('m')
        # self.plot_widget.addConstantLine(0, subplotInd=3, c='k')
        # self.plot_widget.addConstantLine(100, subplotInd=0, c='k')

        self.mag_times = []
        self.mags = []
        self.dt = datetime.timedelta(seconds=3)
        self.prev_mean = 0.0

    @staticmethod
    def scaleConvert(val):
        """The -1 part is baked into the input value, but we still need the 1e6
        """
        v = val * 1.0e6
        return v

    def model_ref_ratio(self, Var):
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
        # print(flux_ratio)
        return flux_ratio

    def mag_diff(self, Var):
        """This leaves relative brightness in units of magnitude, but it is
        intended as an alternative to self.model_ref_ratio
        """
        model = self.guider_model.probe[8]
        ref = self.guider_model.probe[9]
        print('Guider ref magnitude: {}'.format(ref))
        # diff = model - 2.5 * 10**ref
        diff = model
        now = datetime.datetime.now()
        # if (diff < 0) or (diff > 18):  # Used to be > 3
            # diff = np.nan
        if len(self.mag_times) == 0:
            self.mag_times.append(now)
            self.mags.append(diff)
            return self.prev_mean
        else:
            if (now - self.mag_times[0]) < self.dt:
                self.mag_times.append(now)
                self.mags.append(diff)
                return self.prev_mean
            else:
                ret = np.nanmean(self.mags)
                self.mag_times = []
                self.mags = []
                self.prev_mean = ret
                return ret

        # return diff

    def run(self, sr):
        pass

    def end(self, sr):
        pass
