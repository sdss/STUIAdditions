import RO.Wdg
import TUI.Models
import time
#import subprocess

class ScriptClass(object):
    def __init__(self, sr, ):

       self.sr=sr 
       sr.master.winfo_toplevel().wm_resizable(True, True)

       self.tccModel = TUI.Models.getModel("tcc")
       self.mcpModel = TUI.Models.getModel("mcp")
       self.sopModel = TUI.Models.getModel("sop")
       self.apogeeModel = TUI.Models.getModel("apogee")
       self.bossModel = TUI.Models.getModel("boss")

       row=0 
       self.labWdg0 = RO.Wdg.Label(master=sr.master, text ="0: Apogee exposure time left")
       self.labWdg0.grid(row=row, column=0, sticky="nsw")

       row=row+1   #1
       self.labWdg1 = RO.Wdg.Label(master=sr.master, text ="1: mcp.gang=")
       self.labWdg1.grid(row=row, column=0, sticky="nsw")
       self.mcpgang="?"
       
       row=row+1   #2
       self.labWdg2 = RO.Wdg.Label(master=sr.master, text ="sop.doApogeeScience_sequenceState=")
       self.labWdg2.grid(row=row, column=0, sticky="nsw")
       self.seqStateVar=sr.getKeyVar(self.sopModel.doApogeeScience_sequenceState, ind=0, defVal=None)

       row=row+1  #3
       self.labWdg3 = RO.Wdg.Label(master=sr.master, text ="doApogeeScience_seqCount= ")
       self.labWdg3.grid(row=row, column=0, sticky="nsw")
   #    self.doApogeeScience_seqCount=self.sopModel.doApogeeScience_seqCount[0]       
       self.doApScience_seqCount=sr.getKeyVar(self.sopModel.doApogeeScience_seqCount,ind=0, defVal=None)       
                    
       row=row+1
       self.labWdg4 = RO.Wdg.Label(master=sr.master, text ="sop.doApogeeScience_ditherSeq =")
       self.labWdg4.grid(row=row, column=0, sticky="nsw")
       self.seqStateVar=sr.getKeyVar(self.sopModel.doApogeeScience_ditherSeq, ind=0, defVal=None)

       row=row+1   #5
       self.labWdg5 = RO.Wdg.Label(master=sr.master, text ="utrState = ")
       self.labWdg5.grid(row=row, column=0, sticky="nsw")
       self.utrStateVar=self.apogeeModel.utrReadState[0]
              
       row=row+1   #6
       self.labWdg6 = RO.Wdg.Label(master=sr.master, text ="doApogeeScience_expTime= ")
       self.labWdg6.grid(row=row, column=0, sticky="nsw")
       self.doApogeeScience_expTime=self.sopModel.doApogeeScience_expTime[0]   

       row=row+1   #7
       self.labWdg7 = RO.Wdg.Label(master=sr.master, text ="doApogeeScienceStages= ")
       self.labWdg7.grid(row=row, column=0, sticky="nsw")
       self.doApogeeScienceStages=self.sopModel.doApogeeScienceStages[0]   

       row=row+1   #8
       self.labWdg8 = RO.Wdg.Label(master=sr.master, text ="doApogeeScienceState= ")
       self.labWdg8.grid(row=row, column=0, sticky="nsw")
       self.doApogeeScienceState=self.sopModel.doApogeeScienceState[0]   
       
       row=row+1   #9
       self.labWdg9 = RO.Wdg.Label(master=sr.master, text ="apogeeModel.utrReadTime = ")
       self.labWdg9.grid(row=row, column=0, sticky="nsw")
       self.utrExp=self.apogeeModel.utrReadTime[0]   
       
       for rowI in range(0,row+1):
           sr.master.rowconfigure(rowI, weight=1)
       sr.master.columnconfigure(0, weight=1)
       
# ------------------
       self.warnTimeA=5;  self.warn5A=False    # Apogee

       self.record(sr)   # #0
       self.mcpModel.apogeeGang.addCallback(self.getGang,callNow=True)  #1  
       self.sopModel.doApogeeScience_sequenceState.addCallback(self.doApogeeScience_sequenceState,callNow=True) #2
       self.sopModel.doApogeeScience_seqCount.addCallback(self.doApogeeScience_seqCount, callNow=True)   #3
       self.sopModel.doApogeeScience_ditherSeq.addCallback(self.doApogee_dither, callNow=True)  #4
       self.apogeeModel.utrReadState.addCallback(self.utrState,callNow=True)  #5
       self.sopModel.doApogeeScience_expTime.addCallback(self.doApogeeScience_expT,callNow=True)  #6
       self.sopModel.doApogeeScienceStages.addCallback(self.apSatges,callNow=True)  #7
       self.sopModel.doApogeeScienceState.addCallback(self.apState,callNow=True)  #8         
       self.apogeeModel.utrReadTime.addCallback(self.utrExpTime,callNow=True)  #9
  
#--9---
    def utrExpTime(self, keyVar):
        self.labWdg9.set("9: apogeeModel.utrReadTime = %s" % (keyVar[0]))
        self.record()

#--8---
    def apState(self, keyVar):
        self.labWdg8.set("8: sop.doApogeeScienceState = %s" % (keyVar[0]))
        self.doApogeeScienceState=keyVar[0]
        self.record()
#--7---
    def apSatges(self, keyVar):
        self.labWdg7.set("7: sop.doApogeeScienceStages = %s" % (keyVar[0]))
        self.record()

# --6---
    def doApogeeScience_expT(self, keyVar):
        self.labWdg6.set("6: sop.doApogeeScience_expTime = %s" % (keyVar[0]))
        self.record()
# --5---
    def utrState(self, keyVar):
        self.labWdg5.set("5: apogee.utrState = %s, %s, %s, %s" % (keyVar[0],keyVar[1],keyVar[2],keyVar[3]))
        self.record()
#--4---
    def doApogee_dither (self, keyVar):
        self.labWdg4.set("4: doApogeeScience_ditherSeq[0]= %s" % (keyVar[0]))
        self.record()
#--3----
    def doApogeeScience_seqCount(self, keyVar): 
        self.labWdg3.set("3: sop.doApogeeScience_seqCount[0] = %s" % (keyVar[0]))  
        self.record() 
#--2------
    def doApogeeScience_sequenceState(self, keyVar): 
        self.labWdg2.set("2: sop.doApogeeScience_sequenceState = %s, %s" % (keyVar[0],keyVar[1]))
        self.record()
#-1 -------                                
    def getGang(self, keyVar): 
        self.mcpgang=keyVar[0]
        hlp=self.mcpModel.apogeeGangLabelDict.get(self.mcpgang, "?")
        self.labWdg1.set("1: mcp.gang = %s  (%s)" % (self.mcpgang, hlp))
        self.record()
#--------                                                  
    def record(self,sr):
         if self.doApogeeScienceState != 'running':
               timeLeft=None
               self.labWdg0.set("Apogee exposure time left  = %s " % (timeLeft))
               return
         sr=self.sr
         sq=self.sopModel.doApogeeScience_sequenceState[0]
         expTime=self.sopModel.doApogeeScience_expTime[0]
         indState=self.sopModel.doApogeeScience_sequenceState[1]
         t1=len(sq)*expTime  # total exposure time         
         t2=indState*expTime  #  full number of exposures completed 
         utr2=self.apogeeModel.utrReadState[2]
         expState=self.apogeeModel.exposureState[0]
         if expState=="Done":
               utr2=0         
         tm=self.apogeeModel.utrReadTime[0]
         tover=t2+utr2*tm
         timeLeft=(t1-tover)/60
         if timeLeft <= 0:
             timeLeft=None
             self.labWdg0.set("Apogee exposure time left  = %s " % (timeLeft))
             return         
         self.labWdg0.set("Apogee exposure time left  = %5.1f min" % (timeLeft))
         if (timeLeft > self.warnTimeA):
              self.warn5A = False
         elif (0 < timeLeft <= self.warnTimeA):
              if  self.warn5A == False:
                    self.warn5A = True
                #    subprocess.Popen(['say'," five minuts warning"])
         elif timeLeft <= 0:
             pass
#--------  
    def getTAITimeStr(self,):
        return time.strftime("%H:%M",
              time.gmtime(time.time() -  - RO.Astro.Tm.getUTCMinusTAI()))
            
    def run(self, sr):
        self.record()
                
    def end(self, sr): 
       pass
     #   self.mcpModel.apogeeGang.removeCallback(self.getGang)  #1
     #   self.sopModel.doApogeeScience_sequenceState.removeCallback(self.seqState) #2
     #   self.apogeeModel.utrReadState.removeCallback(self.utrState)  #3
         

'''
   Key("doApogeeScienceStages", String()*(1,6), help="names of the doApogeeScience stages"),
    Key("doApogeeScienceState",
       Enum('idle',                'running','done','failed','aborted',
            help="state of the entire command"),
       String("text", help="perhaps useful text to be displayed"),
       Enum('idle','off','pending','running','done','failed','aborted',
            help="state of all the individual stages of this command, " + \
                 "as identified by the commandStages keyword.")*(1,6)),
    
    Key("doApogeeScience_ditherSeq", String(help="dither positions in a sequence"), String(help="default dither sequence")),
    Key("doApogeeScience_seqCount", Int(help="number of times to run ditherSeq"), Int(help="default")),
    Key("doApogeeScience_expTime", Float(help="exposure time", units="sec"), Float(help="default", units="sec")),
    Key("doApogeeScience_sequenceState", String(help="full exposure sequence. Basically ditherSeq * seqCount"),
        Int(help="index of running exposure")),
    Key("doApogeeScience_comment", String(help="For some FITS headers"), String(help="default value")),
    
    Key("doApogeeSkyFlatsStages", String()*(1,6), help="names of the doApogeeSkyFlats stages"),
    Key("doApogeeSkyFlatsState",
       Enum('idle',                'running','done','failed','aborted',
            help="state of the entire command"),
       String("text", help="perhaps useful text to be displayed"),
       Enum('idle','off','pending','running','done','failed','aborted',
            help="state of all the individual stages of this command, " + \
                 "as identified by the commandStages keyword.")*(1,6)),
    
    Key("doApogeeSkyFlats_ditherSeq", String(help="dither positions in a sequence"), String(help="default dither sequence")),
    Key("doApogeeSkyFlats_expTime", Float(help="exposure time", units="sec"), Float(help="default", units="sec")),
    Key("doApogeeSkyFlats_sequenceState", String(help="full exposure sequence. Basically ditherSeq * seqCount"),
        Int(help="index of running exposure")),

'''
