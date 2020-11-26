import TUI.Models
import matplotlib as mpl

import TUI


class ScriptClass(object):
    def __init__(self, sr):
        print "-----fluxPlot--- "
     #   sr.debug = True  # if True, run in debug-only mode 
        sr.debug = False # if False, real time run
        
        self.guiderModel = TUI.Models.getModel("guider")
        
        timeRange=3600; width=8; height=2.4
        self.ppWdg = TUI.Base.StripChartWdg.StripChartWdg(
            master = sr.master, timeRange = timeRange,
            numSubplots = 1,  width = width, height = height,
            cnvTimeFunc = TUI.Base.StripChartWdg.TimeConverter(useUTC=True),
        )
        self.ppWdg.grid(row=0, column=0, sticky="nwes")
        self.ppWdg.grid_rowconfigure(0, weight=1)
        self.ppWdg.grid_columnconfigure(0, weight=1)
        self.ppWdg.xaxis.set_major_locator(mpl.dates.MinuteLocator(byminute=range(0, 61, 10)))

        self.probe=self.guiderModel.probe       
        def fwhmFun (val):
            try: sr.getKeyVar(self.probe, ind=6)
            except:  self.focOff=0
            else: self.focOff=sr.getKeyVar(self.probe, ind=6)
            finally: pass
            if sefl.focOff == 0: val=val
            else: val=None
            return val   
            
        self.ppWdg.plotKeyVar(label="fwhm", subplotInd=0, keyVar=self.probe,
                  #  func=fwhmFun,
                    keyInd=5, color="blue")
        self.ppWdg.showY(0.0, 2.0, subplotInd=0)
        self.ppWdg.subplotArr[0].yaxis.set_label_text("fwhm")
        self.ppWdg.subplotArr[0].legend(loc=3, frameon=False)
        self.ppWdg.addConstantLine(1.0, subplotInd=0, color="grey")
        self.ppWdg.addConstantLine(2.0, subplotInd=0, color="grey")

        self.seeing=self.guiderModel.seeing
        self.ppWdg.plotKeyVar(label="seeing", subplotInd=0, keyVar=self.seeing, keyInd=0, color="red")
        self.ppWdg.subplotArr[0].legend(loc=3, frameon=False)
        
    def run(self, sr):
        pass
                        
    def end(self, sr):
        pass  

#    Key("probe",
#        Int(name="exposureID", help="gcamera exposure number"),
#        Int(name="probeID"),
#        Int(name="flags"),
#        Float(name="raError", help="measured RA error on the sky", units='arcsec'),
#        Float(name="decError", help="measured Dec error on the sky", units='arcsec'),
#        Float(name="FWHM", units='arcsec'),
#        Float(name="focusOffset", help="offset of probe tip from focalplane, with plus=away from sky/M2", units='um'),
#        Float(name="modelFlux", units='ADU'),
#        Float(name="modelMagnitude"),
#        Float(name="refMagnitude", help="known magnitude of guide star"),
#        Float(name="skyFlux", help="mean sky, per-pixel", units='ADU/pixel'),
#        Float(name="skyMagnitude", units="mags/square-arcsec"),
#        doCache = False,
#    ),
