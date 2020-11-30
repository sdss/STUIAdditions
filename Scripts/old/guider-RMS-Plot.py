# import Tkinter
import matplotlib

import TUI


class ScriptClass(object):
    def __init__(self, sr):
        print "-----fluxPlot--- "
        #   sr.debug = True  # if True, run in debug-only mode
        sr.debug = False  # if False, real time run

        sr.master.winfo_toplevel().wm_resizable(True, True)

        self.guiderModel = TUI.Models.getModel("guider")

        #       timeRange=1800; width=8; height=2.4
        timeRange = 1800;
        width = 8;
        height = 5
        self.ppWdg = TUI.Base.StripChartWdg.StripChartWdg(
            master=sr.master, timeRange=timeRange,
            numSubplots=1, width=width, height=height,
            cnvTimeFunc=TUI.Base.StripChartWdg.TimeConverter(useUTC=True),
        )
        self.ppWdg.grid(row=0, column=0, sticky="nwes")
        self.ppWdg.grid_rowconfigure(0, weight=1)
        self.ppWdg.grid_columnconfigure(0, weight=1)

        self.ppWdg.xaxis.set_major_locator(
            matplotlib.dates.MinuteLocator(byminute=range(0, 61, 5)))

        self.ppWdg.plotKeyVar(
            label="RaRMS",
            subplotInd=0,
            keyVar=self.guiderModel.guideRMS,
            keyInd=10,
            color="blue"
        )

        self.ppWdg.plotKeyVar(
            label="DecRMS",
            subplotInd=0,
            keyVar=self.guiderModel.guideRMS,
            keyInd=11,
            color="green"
        )

        #     self.ppWdg.showY(0.0, 2.0, subplotInd=0)
        #     self.ppWdg.subplotArr[0].yaxis.set_label_text("fwhm")
        #     self.ppWdg.subplotArr[0].legend(loc=3, frameon=False)
        self.ppWdg.addConstantLine(0.1, subplotInd=0, color="red")
        self.ppWdg.addConstantLine(-0.1, subplotInd=0, color="red")

        #     self.seeing=self.guiderModel.seeing
        #     self.ppWdg.plotKeyVar(label="seeing", subplotInd=0, keyVar=self.seeing, keyInd=0, color="red")
        self.ppWdg.subplotArr[0].legend(loc=3, frameon=False)

    def run(self, sr):
        pass

    def end(self, sr):
        pass


'''
    Key("guideRMS",
        Int(name="expID",   help="gcamera exposure number"),
        Float(name="RMSerror", help="RMS of guide star offset from the fiber center",units="arcsec"),
        Int(name="nStars",  help="Number of (enabled) guide star used"),
        Float(name="AzRMS", help="Az component of RMS ", units="arcsec"),
        Float(name="AltRMS",help="Alt component of RMS ", units="arcsec"),
        Float(name="xRMS",  help="guide camera x axis component of RMS", units="arcsec"),
        Float(name="yRMS",  help="guide camera y axis component of RMS", units="arcsec"),
        Float(name="fitRMS", help="RMS of fit to guide star offsets", units="arcsec"),
        Int(name="nFit",    help="Number of guide stars used for fit"),
        Int(name="nFitReject", help="Number of guide stars rejected from fit"),
        Float(name="RaRMS", help="RA component of RMS", units="arcsec"),
        Float(name="DecRMS", help="Dec component of RMS", units="arcsec"),
'''
