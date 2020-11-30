# EM
# 03/22/2011 - increase time range to 1 hours to make possiboe to see trend

# import Tkinter
import matplotlib

import TUI


class ScriptClass(object):
    def __init__(self, sr):
        #   sr.debug = True  # if True, run in debug-only mode
        sr.debug = False  # if False, real time run
        print "APO weather"
        sr.master.winfo_toplevel().wm_resizable(True, True)

        self.apoModel = TUI.Models.getModel("apo")
        timeRange = 7200;
        width = 8;
        height = 4.6
        self.ppWdg = TUI.Base.StripChartWdg.StripChartWdg(
            master=sr.master,
            timeRange=timeRange,
            numSubplots=2, width=width, height=height,
            cnvTimeFunc=TUI.Base.StripChartWdg.TimeConverter(useUTC=True),
        )
        # make plot resizable
        self.ppWdg.grid(row=0, column=0, sticky="nwes")
        sr.master.rowconfigure(0, weight=1)
        sr.master.columnconfigure(0, weight=1)

        self.ppWdg.grid_rowconfigure(0, weight=1)
        self.ppWdg.grid_columnconfigure(0, weight=1)
        self.ppWdg.xaxis.set_major_locator(
            matplotlib.dates.MinuteLocator(byminute=range(0, 60, 15)))

        def diff(val):
            at = sr.getKeyVar(self.apoModel.airTempPT, ind=0)
            vv = at - val
            return vv

        airtemp = self.apoModel.airTempPT
        try:
            sr.getKeyVar(airtemp, ind=0)
        except:
            airtemp0 = 0.0
        else:
            airtemp0 = sr.getKeyVar(airtemp, ind=0)
        finally:
            pass

        dewpoint = self.apoModel.dpTempPT
        self.ppWdg.plotKeyVar(label="diff25m", subplotInd=0, keyVar=dewpoint,
                              func=diff, keyInd=0, color="red")
        self.ppWdg.plotKeyVar(label="airtemp", subplotInd=0, keyVar=airtemp,
                              keyInd=0, color="blue")
        self.ppWdg.plotKeyVar(label="dewpoint", subplotInd=0, keyVar=dewpoint,
                              keyInd=0, color="green")
        self.ppWdg.showY(0, 4, subplotInd=0)
        self.ppWdg.subplotArr[0].legend(loc=3, frameon=False)
        self.ppWdg.subplotArr[0].yaxis.set_label_text("Temperature, C")
        self.ppWdg.addConstantLine(0.0, subplotInd=0, color="grey")
        self.ppWdg.addConstantLine(2.5, subplotInd=0, color="grey")
        self.ppWdg.addConstantLine(5.0, subplotInd=0, color="grey")

        pl = 1
        winds25m = self.apoModel.winds25m
        try:
            sr.getKeyVar(winds25m, ind=0)
        except:
            winds25m0 = 0.0
        else:
            winds25m0 = sr.getKeyVar(winds25m, ind=0)
        finally:
            pass
        self.ppWdg.plotKeyVar(label="winds25m", subplotInd=pl, keyVar=winds25m,
                              keyInd=0, color="red")
        winds35m = self.apoModel.winds
        self.ppWdg.plotKeyVar(label="winds35m", subplotInd=pl, keyVar=winds35m,
                              keyInd=0, color="blue")
        gusts35m = self.apoModel.gusts
        self.ppWdg.plotKeyVar(label="gusts35m", subplotInd=pl, keyVar=gusts35m,
                              keyInd=0, color="green")
        self.ppWdg.showY(winds25m0 - 5, winds25m0 + 5, subplotInd=pl)
        self.ppWdg.subplotArr[pl].legend(loc=3, frameon=False)
        self.ppWdg.subplotArr[pl].yaxis.set_label_text("Wind, mph")
        self.ppWdg.addConstantLine(35, subplotInd=pl, color="grey")
        self.ppWdg.addConstantLine(30, subplotInd=pl, color="grey")

    def run(self, sr):
        pass

    def end(self, sr):
        pass
