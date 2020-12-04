"""History
2017-04-10 created by EM
2017-05-15 DO:  scale and window size update
"""
import matplotlib

import TUI


class ScriptClass(object):
    def __init__(self, sr):
        # sr.debug = True  # if True, run in debug-only mode
        sr.debug = False  # if False, real time run

        sr.master.winfo_toplevel().wm_resizable(True, True)
        self.guiderModel = TUI.Models.getModel("guider")
        self.tccModel = TUI.Models.getModel("tcc")

        timeRange = 3600  # testing 100
        width = 5
        height = 5
        self.ppWdg = TUI.Base.StripChartWdg.StripChartWdg(
            master=sr.master, timeRange=timeRange,
            numSubplots=2, width=width, height=height,
            cnvTimeFunc=TUI.Base.StripChartWdg.TimeConverter(useUTC=True),
        )
        self.ppWdg.grid(row=0, column=0, sticky="nwes")
        self.ppWdg.grid_rowconfigure(0, weight=1)
        self.ppWdg.grid_columnconfigure(0, weight=1)

        self.ppWdg.xaxis.set_major_locator(
            matplotlib.dates.MinuteLocator(byminute=range(0, 61, 15)))

        self.NumAvr = 5
        self.avrRaErr = []
        self.avrDecErr = []
        self.guiderModel.axisError.addCallback(self.axisErrorCallback)

        self.cartridgeID = self.guiderModel.cartridgeLoaded[0]
        # self.guiderModel.cartridgeLoaded.addCallback(self.cartridgeIDCallback)

        # "axisError:RA"
        self.ppWdg.setYLimits(-0.5, 0.5, subplotInd=0)
        self.ppWdg.plotKeyVar(label="axisError:RA", subplotInd=0,
                              keyVar=self.guiderModel.axisError, keyInd=0,
                              color="blue",
                              linewidth=0.5, marker=".")
        self.ppWdg.addConstantLine(0.2, subplotInd=0, color="red")
        self.ppWdg.addConstantLine(-0.2, subplotInd=0, color="red")
        # self.ppWdg.subplotArr[0].yaxis.set_label_text("axisError:RA")
        self.ppWdg.subplotArr[0].legend(loc=3, frameon=False)

        def avrRaErrorFun(val):
            if len(self.avrRaErr) == 0:
                return 0
            else:
                return sum(self.avrRaErr) / len(self.avrRaErr)

        self.avrRaLine = self.ppWdg.plotKeyVar(subplotInd=0,
                                               keyVar=self.guiderModel.axisError,
                                               func=avrRaErrorFun, keyInd=0,
                                               color="blue", linewidth=1.5)

        # "axisError:Dec"
        self.ppWdg.setYLimits(-0.5, 0.5, subplotInd=1)
        self.ppWdg.plotKeyVar(label="axisError:Dec", subplotInd=1,
                              keyVar=self.guiderModel.axisError, keyInd=1,
                              color="green",
                              linewidth=0.5, marker=".")
        self.ppWdg.addConstantLine(0.2, subplotInd=1, color="red")
        self.ppWdg.addConstantLine(-0.2, subplotInd=1, color="red")
        # self.ppWdg.subplotArr[1].yaxis.set_label_text("axisError:Dec")
        self.ppWdg.subplotArr[1].legend(loc=3, frameon=False)

        def avrDecErrorFun(val):
            if len(self.avrDecErr) == 0:
                return 0
            else:
                return sum(self.avrDecErr) / len(self.avrDecErr)

        self.avrDecLine = self.ppWdg.plotKeyVar(subplotInd=1,
                                                keyVar=self.guiderModel.axisError,
                                                func=avrDecErrorFun, keyInd=1,
                                                color="green", linewidth=1.5)

        # "axePos:alt"
        # self.ppWdg.setYLimits(0, 90, subplotInd=2)
        # self.ppWdg.showY(30, 60, subplotInd=2)
        # self.ppWdg.plotKeyVar(label="axePos:alt", subplotInd=2,
        #    keyVar=self.tccModel.axePos,  keyInd=1,  color="green")
        # self.ppWdg.addConstantLine(30, subplotInd=2, color="grey")
        # self.ppWdg.addConstantLine(60, subplotInd=2, color="grey")
        # self.ppWdg.subplotArr[2].yaxis.set_label_text("axePos:alt")
        # self.ppWdg.subplotArr[2].legend(loc=3, frameon=False)

    def axisErrorCallback(self, keyVar):
        if not keyVar.isGenuine:
            return
        self.avrRaErr.append(keyVar[0])
        if len(self.avrRaErr) > self.NumAvr:
            self.avrRaErr = self.avrRaErr[-self.NumAvr:]
        self.avrDecErr.append(keyVar[1])
        if len(self.avrDecErr) > self.NumAvr:
            self.avrDecErr = self.avrDecErr[-self.NumAvr:]

    def cartridgeIDCallback(self, keyVar):
        if not keyVar.isGenuine:
            return
        if keyVar[0] == self.cartridgeID:
            return
        self.cartridgeID = keyVar[0]
        self.avrRaLine.addPoint(None)
        self.avrDecLine.addPoint(None)
        self.avrRaErr = list()
        self.avrDecErr = list()

    def run(self, sr):
        pass

    def end(self, sr):
        pass
