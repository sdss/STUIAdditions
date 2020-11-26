"""
History:
2010-06-09 EM added check of fail for guider cartridge
2011-05-16 EM resizable window, added three apogee actors 
2012-06-01 RO use asynchronous calls
2012-08-28 EM design - output actor + cmd 
2013-02-06 EM added version as date; removed  "check to fail"
2015-10-27 GF added apogee short dark
"""
import RO.Constants
import RO.Wdg
import TUI.Models
from datetime import datetime

#import time
#import RO.Astro.Tm


class ScriptClass(object):
    def __init__(self, sr):
        # if True, run in debug-only mode (which doesn't DO anything)
        # if False, real time run
        sr.name="--afternoon sets"
        sr.debug = False
        self.sr=sr
        sr.master.winfo_toplevel().wm_resizable(True, True)
        self.logWdg = RO.Wdg.LogWdg(master=sr.master, width=30, height=22)
        self.logWdg.grid(row=0, column=0, sticky="news")
        sr.master.rowconfigure(0, weight=1)
        sr.master.columnconfigure(0, weight=1)
        self.logWdg.text.tag_config("a", foreground="magenta") 
        self.logWdg.text.tag_config("g", foreground="grey")
        self.redWarn=RO.Constants.sevError
        
        self.actorCmdVarList = []
        self.startTimeStr = None
                
        self.cmdList=[
            "tcc track 121,30 mount",
            "tcc set scale=1.0",
            "tcc set focus=0.0",
            "sop doBossCalibs nbias=1 ndark=1 darktime=20",
            "guider dark stack=9 time=15",
        #    "test to fail",
        ]        
        self.logWdg.addMsg("-- %s -" % (sr.name),  tags=["a"] )
        self.logWdg.addMsg("Short Apogee Darks", tags=["g"] )
        for ll in self.cmdList: 
            self.logWdg.addMsg("%s" % ll, tags=["g"] )
                       
    def cmdCallback(self, dum=None):
        """Command callback: redisplay all information
        
        Note: redisplaying everything keeps the actors in the desired order.
        """
        sr=self.sr
        self.logWdg.clearOutput()
        self.logWdg.addMsg("%s, %s" % (sr.name, self.startTimeStr), tags=["a"])
        self.logWdg.addMsg("Apogee Short Darks")
        
        for actor, cmd, cmdVar in self.actorCmdVarList:
            if not cmdVar.isDone:
                 self.logWdg.addMsg("%s %s - ?" % (actor, cmd,), severity=RO.Constants.sevWarning)
            elif cmdVar.didFail:
                 self.logWdg.addMsg("%s %s - **FAILED**" % (actor,cmd), severity=RO.Constants.sevError)
            else:
                 self.logWdg.addMsg("%s  %s  - ok" % (actor, cmd))
 
    def getTAITimeStr(self,):
      currPythonSeconds = RO.Astro.Tm.getCurrPySec()
      currTAITuple= time.gmtime(currPythonSeconds - RO.Astro.Tm.getUTCMinusTAI())
      self.taiTimeStr = time.strftime("%H:%M:%S", currTAITuple) 
      return self.taiTimeStr
 
    def checkGangPodium(self, sr):   
        self.mcpModel = TUI.Models.getModel("mcp")
        ngang=sr.getKeyVar(self.mcpModel.apogeeGang, ind=0, defVal=0)
        hlp=self.mcpModel.apogeeGangLabelDict.get(ngang, "?")
        self.logWdg.addMsg("mcp.gang=%s  (%s)" % (ngang, hlp))
        if ngang != '12':         
            self.logWdg.addMsg(" Error: mcp.gang must be = 12 (podium dense) \n",    
                  severity=RO.Constants.sevError)
            subprocess.Popen(['say','error']) 
            return False 
        else:
           return True
           
    def run(self, sr):
        utc_datetime = datetime.utcnow()
     #   self.startTimeStr = utc_datetime.strftime("%Y-%m-%d %H:%M:%S")
        self.startTimeStr = utc_datetime.strftime("%H:%M:%S")
        self.actorCmdVarList = []
        cmdVarList = [] 
        
        ########
        if not self.checkGangPodium(sr):
           raise sr.ScriptError("") 
           
        for actorCmd in [
            "apogeecal allOff",
            "apogee shutter close",
            "apogeecal shutterOpen",
            "apogee expose nreads=3; object=Dark",
            "apogeecal shutterClose",
            "apogeecal allOff",          
         ]:
         actor, cmd = actorCmd.split(None, 1)
         self.logWdg.addMsg("%s .... " % (actorCmd,))
         yield sr.waitCmd(actor=actor, cmdStr=cmd, checkFail=True)
         cmdVar = sr.value
         if cmdVar.didFail:      
             self.logWdg.addMsg("   ** FAILED **" % (actorCmd),severity=RO.Constants.sevError)
             raise sr.ScriptError("")
        ###########      
           
               
 #       for actorCmd in  self.cmdList:
        for actorCmd in  [
            "tcc track 121,30 mount",
            "tcc set scale=1.0",
            "tcc set focus=0.0",
            "sop doBossCalibs nbias=1 ndark=1 darktime=20",
            "guider dark stack=9 time=15",
        #    "test to fail",
        ]:
            actor, cmd = actorCmd.split(None, 1)
            cmdVar = sr.startCmd(
                actor = actor,
                cmdStr = cmd,
                callFunc = self.cmdCallback,
                checkFail = False,
            )
            cmdVarList.append(cmdVar)
            self.actorCmdVarList.append((actor,cmd, cmdVar))

        
        self.cmdCallback()

        yield sr.waitCmdVars(cmdVarList, checkFail=False) 
          
        self.logWdg.addMsg("-- done --", tags=["a"])
		

