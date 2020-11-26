# 06/09/2010 EM, set variable for arc warming, add time stamps when command started,
#  checked if command failed so to quit with message
#  06/26/10  added exposureId - keyword output 
#  02/24/2013 EM:  tai time,  set all checks for false after any run; resized window
#      tried to sticky RO.Wdg.Checkbutton to left, but could not  ?? 

import RO.Wdg
import Tkinter
import TUI.Models
from datetime import datetime
import time

class ScriptClass(object):
    def __init__(self, sr):

        # if True, run in debug-only mode (which doesn't DO anything, it just pretends)
        # if False, real time run
        sr.debug = False
        self.name="bossCalibs"
        sr.master.winfo_toplevel().wm_resizable(True, True)

        gr = RO.Wdg.Gridder(sr.master)
        self.testWdg = Tkinter.Frame(master = sr.master,borderwidth = 1,  relief = "solid",)
        gr.gridWdg(False, self.testWdg, sticky="ew", )
        th="Check to run";
 
        txt="boss exposure bias"
        self.biasCheckWdg = RO.Wdg.Checkbutton(self.testWdg, 
             text = txt,defValue = False, helpText =th,)
    #    self.biasCheckWdg.grid(row=0, column=0, sticky="e")
        gr.gridWdg(self.biasCheckWdg,sticky="ew")  # it does not do anything ?? 

        txt="boss exposure dark"
        self.darkCheckWdg = RO.Wdg.Checkbutton(self.testWdg, text =txt, 
              defValue = False, helpText=th,)
        gr.gridWdg(self.darkCheckWdg,sticky="w")

        self.gcamDarkWdg = RO.Wdg.Checkbutton(self.testWdg, 
            text ="gcamera dark", defValue = False, helpText =th,)
        gr.gridWdg(self.gcamDarkWdg,sticky="w")

        self.calibFCheckWdg = RO.Wdg.Checkbutton(self.testWdg, 
            text = "boss exposure flat  ", defValue = False, helpText =th,)
        gr.gridWdg(self.calibFCheckWdg,sticky="w")

        self.guiderCheckWdg = RO.Wdg.Checkbutton(self.testWdg, 
            text = "guider flat", defValue = False, helpText =th,)
        gr.gridWdg(self.guiderCheckWdg,sticky="w")

        self.calibACheckWdg = RO.Wdg.Checkbutton(self.testWdg, 
            text ="boss exposure  arc ", defValue = False, helpText =th,)
        gr.gridWdg(self.calibACheckWdg,sticky="w")

        self.hartCheckWdg = RO.Wdg.Checkbutton(self.testWdg, 
            text ="boss hartmann", defValue = False, helpText =th,)
        gr.gridWdg(self.hartCheckWdg,sticky="w")

        self.logWdg = RO.Wdg.LogWdg(master=sr.master, width=20,  height =16,)
        self.logWdg.grid(row=10, column=0, sticky="news")
        sr.master.rowconfigure(10, weight=1)
        sr.master.columnconfigure(0, weight=1)
        self.logWdg.text.tag_config("a", foreground="magenta")
        
        self.mcpModel = TUI.Models.getModel("mcp")
        
    def getTAITimeStr(self,):
        currPythonSeconds = RO.Astro.Tm.getCurrPySec()
        self.currTAITuple= time.gmtime(currPythonSeconds - RO.Astro.Tm.getUTCMinusTAI())
        self.taiTimeStr = time.strftime("%H:%M:%S", self.currTAITuple) 
        self.taiDateStr = time.strftime("%Y-%m-%d", self.currTAITuple) 
        return self.taiTimeStr, self.taiDateStr,self.currTAITuple

    def runAct(self,sr,act,cmd):
        tm, dt, seconds = self.getTAITimeStr()
        self.logWdg.addMsg(tm+"  "+act+" "+cmd)
        yield sr.waitCmd(actor=act, cmdStr=cmd, abortCmdStr="abort", checkFail=False)
        cmdVar = sr.value
        if cmdVar.didFail:
            self.logWdg.addMsg("*** FAILED ***" ) 
            raise sr.ScriptError("something wrong") 

    def runMCP(self,sr,cmd):
        tm, dt, seconds = self.getTAITimeStr() 
        self.logWdg.addMsg(tm+"  "+"mcp"+" "+cmd)
        yield sr.waitCmd(actor="mcp", cmdStr=cmd, checkFail=False)
        cmdVar = sr.value
        if cmdVar.didFail:
             self.logWdg.addMsg("*** FAILED ***")
             raise sr.ScriptError("something wrong") 

    def setMCP(self,sr,ffs,ff,ne,hgcd):
        ffsStatus=self.mcpModel.ffsStatus[:]
        FFlamp=self.mcpModel.ffLamp[:]
        hgCdLamp=self.mcpModel.hgCdLamp[:]
        neLamp=self.mcpModel.neLamp[:]    
        print ffsStatus
        print FFlamp
        print hgCdLamp
        print neLamp

    def run(self, sr):
        tm, dt, seconds = self.getTAITimeStr() 
        self.logWdg.addMsg("-- %s, %s " % (self.name, tm), tags=["a"])
        
        self.setMCP(sr,False, False, False, False)

        yield self.runMCP(sr,"ffs.close")
        yield self.runMCP(sr,"ff.off")
        yield self.runMCP(sr,"ne.off")
        yield self.runMCP(sr,"hgcd.off")
  
        bossModel = TUI.Models.getModel("boss")

        if self.biasCheckWdg.getBool():
            yield self.runAct(sr,"boss","exposure bias")
            exposureId = int(sr.getKeyVar(bossModel.exposureId, ind=0))+1
            self.logWdg.addMsg("       ok, file=%s " % (exposureId))
        if self.darkCheckWdg.getBool():
            yield self.runAct(sr,"boss","exposure dark itime=20")
            exposureId = int(sr.getKeyVar(bossModel.exposureId, ind=0))+1
            self.logWdg.addMsg("       ok, file=%s " % (exposureId))
        if self.gcamDarkWdg.getBool():
            yield self.runAct(sr,"gcamera","dark time=20")
  
        if self.calibFCheckWdg.getBool() or self.guiderCheckWdg.getBool():
            yield self.runMCP(sr,"ff.on")
            if self.calibFCheckWdg.getBool():
               yield self.runAct(sr,"boss","exposure flat itime=30")
               exposureId = int(sr.getKeyVar(bossModel.exposureId, ind=0))+1
               self.logWdg.addMsg("       ok, file=%s " % (exposureId))
            if self.guiderCheckWdg.getBool():
	           yield self.runAct(sr,"guider","flat time=0.5") #  cartridge="+str(gc))
            yield self.runMCP(sr,"ff.off")

        if self.calibACheckWdg.getBool() or self.hartCheckWdg.getBool():
            yield self.runMCP(sr,"ne.on")
            yield self.runMCP(sr,"hgcd.on")
            if self.calibACheckWdg.getBool():
                warmTime=3  # min
                self.logWdg.addMsg('warming lamps for %s min' %(warmTime))
                yield sr.waitMS(warmTime*60*1000)
                yield self.runAct(sr,"boss","exposure arc itime=4")
                exposureId = int(sr.getKeyVar(bossModel.exposureId, ind=0))+1
                self.logWdg.addMsg("       ok, file=%s " % (exposureId))
            if self.hartCheckWdg.getBool():
                self.logWdg.addMsg('no lamps warmimg :-))')
                yield self.runAct(sr,"boss","exposure arc itime=4 hartmann=left")
                exposureId = int(sr.getKeyVar(bossModel.exposureId, ind=0))+1
                self.logWdg.addMsg("       ok, file=%s " % (exposureId))
                yield self.runAct(sr,"boss","exposure arc itime=4 hartmann=right")
                exposureId = int(sr.getKeyVar(bossModel.exposureId, ind=0))+1
                self.logWdg.addMsg("       ok, file=%s " % (exposureId))
            yield self.runMCP(sr,"ne.off")
            yield self.runMCP(sr,"hgcd.off")
                        
        if self.biasCheckWdg.getBool():  self.biasCheckWdg.setBool(False)
        if self.darkCheckWdg.getBool():  self.darkCheckWdg.setBool(False)
        if self.gcamDarkWdg.getBool():  self.gcamDarkWdg.setBool(False) 
        if self.hartCheckWdg.getBool():  self.hartCheckWdg.setBool(False)
        if self.calibFCheckWdg.getBool(): self.calibFCheckWdg.setBool(False)
        if self.guiderCheckWdg.getBool(): self.guiderCheckWdg.setBool(False)
        if self.calibACheckWdg.getBool():  self.calibACheckWdg.setBool(False)

        tm, dt, seconds = self.getTAITimeStr() 
        self.logWdg.addMsg("-- done, %s --" % tm, tags=["a"]) 
        self.logWdg.addMsg(" ")
