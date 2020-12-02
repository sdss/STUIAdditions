import Tkinter

import time

import RO.Wdg
import TUI.Models

nFile = ""


class ScriptClass(object):
    def __init__(self, sr):
        #  print "__guiderLog_____"
        self.name = "guiderLog:"

        sr.master.winfo_toplevel().wm_resizable(True, True)
        F1 = Tkinter.Frame(sr.master)
        gr1 = RO.Wdg.Gridder(F1)
        F1.grid(row=0, column=0, sticky="w")

        self.sr = sr
        self.fw = 9
        self.ttl = ''.join([s.rjust(self.fw, " ") for s in \
                            ('time', "secFoc", "expN", 'fiber', 'fwhm',
                             '  offset', 'modFlux', 'modMag', "refMag")])
        #  ll=RO.Wdg.Label(master=F1,text = self.ttl,).grid(row = 0, column=0, sticky="w")
        print self.name, self.ttl

        self.logWdg = RO.Wdg.LogWdg(master=sr.master, width=55, height=18, )
        self.logWdg.grid(row=1, column=0, sticky="nwes")

        sr.master.rowconfigure(1, weight=1)
        sr.master.columnconfigure(0, weight=1)

        fs = "12"  # font size
        ft = "Monaco"  # "Courier"  #"Menlo"  # font type
        self.logWdg.text.tag_config("cur", font=(ft, fs))

        self.guiderModel = TUI.Models.getModel("guider")
        self.tccModel = TUI.Models.getModel("tcc")
        self.guiderModel.probe.addCallback(self.updateProbe, callNow=True)

    def getTAITimeStr(self, ):
        return time.strftime("%H:%M:%S",
                             time.gmtime(
                                 time.time() - RO.Astro.Tm.getUTCMinusTAI()))

    def updateProbe(self, keyVar):
        if not keyVar.isGenuine:
            return
        timeStr = self.getTAITimeStr()
        global nFile

        if nFile != keyVar[0]:
            nFile = keyVar[0]
            self.logWdg.addMsg("-" * 82)
            self.logWdg.addMsg(self.ttl, tags=["cur"])

        sr = self.sr
        secFoc = sr.getKeyVar(self.tccModel.secFocus, ind=0, defVal=None)
        txt1 = ''.join([s.rjust(self.fw, " ") for s in \
                        (
                            timeStr,
                            str(secFoc),
                            str(keyVar[0]),
                            str("%2d" % keyVar[1]),
                            str("%5.3f" % keyVar[5]),
                            str("%5d" % keyVar[6]),
                            str("%7d" % keyVar[7]),
                            str("%6.2f" % keyVar[8]),
                            str("%6.2f" % keyVar[9]),
                        )])
        self.logWdg.addMsg("%s" % (txt1), tags=["cur"])

    #    print self.name, txt1

    def stopCalls(self, ):
        self.guiderModel.probe.removeCallback(self.updateProbe)
        self.logWdg.addMsg("    stopped")

    def run(self, sr):
        pass

    def end(self, sr):
        self.stopCalls()
        pass

    #    Key("probe",
#       0 Int(name="exposureID", help="gcamera exposure number"),
#       1 Int(name="probeID"),
#       2 Int(name="flags"),
#       3 Float(name="raError", help="measured RA error on the sky", units='arcsec'),
#       4 Float(name="decError", help="measured Dec error on the sky", units='arcsec'),
#       5 Float(name="FWHM", units='arcsec'),
#       6 Float(name="focusOffset", help="offset of probe tip from focalplane, with plus=away from sky/M2", units='um'),
#       7 Float(name="modelFlux", units='ADU'),
#       8 Float(name="modelMagnitude"),
#       9 Float(name="refMagnitude", help="known magnitude of guide star"),
#       10 Float(name="skyFlux", help="mean sky, per-pixel", units='ADU/pixel'),
#       11 Float(name="skyMagnitude", units="mags/square-arcsec"),
#        doCache = False,
#    ),
