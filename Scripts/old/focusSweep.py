# focusLoop
# run GUI
# 06/26/10 added file name of guider exposure 

import Tkinter

from datetime import datetime

import RO.Wdg
import TUI.Models


class ScriptClass(object):
    def __init__(self, sr):
        # if True, run in debug-only mode 
        # if False, real time run
        sr.debug = False
        sr.master.winfo_toplevel().wm_resizable(True, True)

        # Row 0
        F1 = Tkinter.Frame(sr.master)
        gr1 = RO.Wdg.Gridder(F1)
        F1.grid(row=0, column=0, sticky="w")

        # Center of loop  widget
        wdgR1a = Tkinter.Frame(F1)
        gr1a = RO.Wdg.Gridder(wdgR1a)
        wcenter = 250  # center
        self.centerWdg = RO.Wdg.IntEntry(master=wdgR1a, defValue=wcenter,
                                         minValue=-500, maxValue=800,
                                         helpText="Center of focus loop", )
        gr1a.gridWdg("Center", self.centerWdg, )
        wdgR1a.grid(row=0, column=0, sticky="w")

        # Number of points
        wdgR1b = Tkinter.Frame(F1)
        gr1b = RO.Wdg.Gridder(wdgR1b)
        np = 5  # center
        self.npWdg = RO.Wdg.IntEntry(master=wdgR1b, defValue=np,
                                     minValue=3, maxValue=20,
                                     helpText="Number of focus positions to mesure", )
        gr1b.gridWdg("    Number", self.npWdg, )
        wdgR1b.grid(row=0, column=1, sticky="w")

        # Step widget
        wdgR1c = Tkinter.Frame(F1)
        gr1c = RO.Wdg.Gridder(wdgR1c)
        st = 50  # center
        self.stepWdg = RO.Wdg.IntEntry(master=wdgR1c, defValue=st,
                                       minValue=10, maxValue=100,
                                       helpText="Step for focus changes", )
        gr1c.gridWdg("   Focus Step", self.stepWdg, )
        wdgR1c.grid(row=0, column=2, sticky="w")

        # Row 1
        F2 = Tkinter.Frame(sr.master)
        gr2 = RO.Wdg.Gridder(F2)
        F2.grid(row=1, column=0, sticky="w")
        # Guider integration time
        wdgR2a = Tkinter.Frame(F2)
        gr2a = RO.Wdg.Gridder(wdgR2a)
        gexp = 5  # center
        self.gexpWdg = RO.Wdg.IntEntry(master=wdgR2a, defValue=gexp,
                                       minValue=2, maxValue=30,
                                       helpText="gcamera integration time", )
        gr2a.gridWdg("Integration time", self.gexpWdg, )
        wdgR2a.grid(row=0, column=0, sticky="w")
        #
        wdgR2b = Tkinter.Frame(F2)
        gr2b = RO.Wdg.Gridder(wdgR2b)
        gn = 1  # number of exposures at the same foc position
        self.gnWdg = RO.Wdg.IntEntry(master=wdgR2b, defValue=gn,
                                     minValue=1, maxValue=5,
                                     helpText="Number of exposures at the same focus position")
        gr2b.gridWdg("   Exp. #", self.gnWdg, )
        wdgR2b.grid(row=0, column=1, sticky="w")

        # Row 2
        self.logWdg = RO.Wdg.LogWdg(master=sr.master, width=40, height=25, )
        self.logWdg.grid(row=2, column=0, sticky="news")
        sr.master.rowconfigure(2, weight=1)
        sr.master.columnconfigure(0, weight=1)

    def tm(self, sr):
        utc_datetime = datetime.utcnow()
        return utc_datetime.strftime("%Y-%m-%d %H:%M:%S")

    def run(self, sr):
        ssout = "--- focusSweep --" + self.tm(sr, )
        self.logWdg.addMsg(ssout)
        print ssout

        tccModel = TUI.Models.getModel("tcc")
        guiderModel = TUI.Models.getModel("guider")
        gcameraModel = TUI.Models.getModel("gcamera")

        curFoc = sr.getKeyVar(tccModel.secFocus, ind=0)
        self.logWdg.addMsg("current focus=" + str(curFoc))

        center = self.centerWdg.getNum()  # center=150 # center
        nPoints = self.npWdg.getNum()  # number of points
        step = self.stepWdg.getNum()  # step for focus
        iTime = self.gexpWdg.getNum()  # guider exposure time
        cmdG = "on oneExposure  time=" + str(iTime)  # guider command
        foc0 = center - step * (nPoints - 1) / 2
        gn = self.gnWdg.getNum()  # number of exposures

        yield sr.waitCmd(actor="guider", cmdStr="off", checkFail=False, )

        for it in range(0, nPoints):
            foc = foc0 + it * step
            cmdFoc = "set foc=" + str(foc)
            yield sr.waitCmd(actor="tcc", cmdStr=cmdFoc, checkFail=False, )
            sit = str(it)
            for n in range(0, gn):
                yield sr.waitCmd(actor="guider", cmdStr=cmdG, checkFail=False, )
                gfile = sr.getKeyVar(gcameraModel.filename, ind=0)
                #    ssout=sit+"  foc= "+str(foc)+"   "+gfile
                ssout = "%s foc=%1.0f  %s" % (sit, foc, gfile)
                self.logWdg.addMsg(ssout)
                print ssout
        #    sit="  "

        yield sr.waitCmd(actor="tcc", cmdStr="set foc=" + str(curFoc),
                         checkFail=False)
        self.logWdg.addMsg("set focus  %s" % (str(curFoc)))
        self.logWdg.addMsg("    done")
        self.logWdg.addMsg(' ')
        print "  end focusSweep "

    def end(self, sr):
        pass

#     yield sr.waitCmd(actor="guider",cmdStr=cmdG,checkFail = False,
#             keyVars=[guiderModel.guideProbe])
#     fwhm1 = sr.getKeyVar(guiderModel.guideProbe, ind=6)
#     fwhm=sr.value.getLastKeyVarData(guiderModel.guideProbe)[6]
