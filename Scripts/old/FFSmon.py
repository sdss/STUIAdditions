import RO.Wdg
import TUI.Models
import time
import RO.Astro.Tm
import sys,os, subprocess

def getTAITimeStr():
        currPythonSeconds = RO.Astro.Tm.getCurrPySec()
        currTAITuple= time.gmtime(currPythonSeconds - RO.Astro.Tm.getUTCMinusTAI())
        taiTimeStr = time.strftime("%H:%M:%S", currTAITuple)
        return taiTimeStr


class ScriptClass(object,):
    def __init__(self, sr, ):
        self.name="-- FFSmon--"
        width=35 ; height=15
        
        sr.master.winfo_toplevel().wm_resizable(True, True)
        
        self.labWdg = RO.Wdg.Label(master=sr.master, text = "MCP: FFs petals & wind speed & lamps", )
        self.labWdg.grid(row=0, column=0, sticky="w")

        self.checkWdg = RO.Wdg.Checkbutton(master=sr.master, 
            text = "sound", 
            defValue=False, 
            helpText ="Play sound",)
        self.checkWdg.grid(row=1, column=0, sticky="w")
        
        self.logWdg = RO.Wdg.LogWdg(master=sr.master, width=width, height =height,  
              helpText = "log window",)
        self.logWdg.grid(row=2, column=0, sticky="nsew")
        fs="12"   # font size
        ft="Monaco"
        self.logWdg.text.tag_config("b", foreground="darkblue")
        self.logWdg.text.tag_config("g", foreground="darkgreen")
        self.logWdg.text.tag_config("r", foreground="Sienna")

        self.logWdg.text.tag_config("nov", background="beige")
        self.logWdg.text.tag_config("cur", font=(ft,fs))

        sr.master.rowconfigure(2, weight=1)
        sr.master.columnconfigure(0, weight=1)

        self.mcpModel = TUI.Models.getModel("mcp")
        self.apoModel = TUI.Models.getModel("apo")
        
        self.logWdg.addMsg("init:", tags=["cur"])
        self.FFs="????-????"
        self.mcpModel.ffsStatus.addCallback(self.updateFFS,callNow=True)
        
        self.FFLamp="????"
        self.hgCdLamp="????" 
        self.neLamp ="????"
        self.mcpModel.ffLamp.addCallback(self.updateFFlamp,callNow=True)
        self.mcpModel.hgCdLamp.addCallback(self.updateHgCdLamp,callNow=True)
        self.mcpModel.neLamp.addCallback(self.updateNeLamp,callNow=True)
        self.logWdg.addMsg("monitor:", tags=["cur"])


#  Key("sp1Slithead", 
#        Enum("00", "01", "10", "11", labelHelp=("?", "Open", "Closed", "Invalid")),
#        Bool("0", "1", help="Latch extended"),
#        Bool("0", "1", help="Slithead in place")),
#    Key("sp2Slithead", 
#        Enum("00", "01", "10", "11", labelHelp=("?", "Open", "Closed", "Invalid")),
#        Bool("0", "1", help="Latch extended"),
#        Bool("0", "1", help="Slithead in place")),

    def updateFFlamp(self,keyVar):
       # if not keyVar.isGenuine: return
        ll="%s%s%s%s"% (str(keyVar[0]),str(keyVar[1]),str(keyVar[2]),str(keyVar[3]))
        if ll != self.FFLamp:
            ss="%s  mcp.ffl = %s" % (getTAITimeStr(),ll)
            print self.name, ss
            self.logWdg.addMsg("%s" % (ss), tags=["cur"])
            self.FFLamp=ll
            if self.checkWdg.getBool():        
                subprocess.Popen(['say',"flat"])

    def updateNeLamp(self,keyVar):
        #if not keyVar.isGenuine: return
        ll="%s%s%s%s"% (str(keyVar[0]),str(keyVar[1]),str(keyVar[2]),str(keyVar[3]))
        if ll !=self.neLamp:
            ss="%s  mcp.ne = %s"% (getTAITimeStr(),ll)
            print self.name, ss
            self.logWdg.addMsg("%s" % (ss), tags=["r","cur"])
            self.neLamp=ll
            if self.checkWdg.getBool():        
                subprocess.Popen(['say',"neon"])

    def updateHgCdLamp(self,keyVar):
       # if not keyVar.isGenuine: return
        ll="%s%s%s%s"% (str(keyVar[0]),str(keyVar[1]),str(keyVar[2]),str(keyVar[3]))
        if ll != self.hgCdLamp:
            ss="%s  mcp.hgcd = %s" % (getTAITimeStr(),ll)
            print self.name, ss
            self.logWdg.addMsg("%s" % (ss), tags=["b","cur"])
            self.hgCdLamp=ll
            if self.checkWdg.getBool():        
                subprocess.Popen(['say',"t-arc"])
                        
    def updateFFS(self,keyVar):
    #    if not keyVar.isGenuine: return
        ssp=self.getStr(keyVar)
        if ssp != self.FFs:
            wind25m=self.apoModel.winds25m[0]
            ss="%s  mcp.FFs=%s,  wind=%s" % (getTAITimeStr(), ssp, wind25m)
            print self.name, ss
            self.logWdg.addMsg("%s" % (ss), tags=["g","cur","nov"])
            self.FFs=ssp
            if self.checkWdg.getBool(): subprocess.Popen(['say',"petal"])
       
    def getStr(self, keyVar):
        ssp=""
        for i in range(0,8):
           p0=str(keyVar[i])[0];  p1=str(keyVar[i])[1]
           if p0=="0" and p1=="1": sp="0"
           elif p0=="1" and p1=="0": sp="1"
           else: sp="?"
           ssp=ssp+sp
        ssp='%s-%s' % (ssp[:4], ssp[4:])   
        return ssp
                            
    def run(self,sr):
        pass
       # self.logWdg.addMsg("%s" % ( self.getStat()), tags=["b","cur","nov"])
      
      
