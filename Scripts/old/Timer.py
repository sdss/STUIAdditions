"""A timer for APOGEE exposures

History:
2013-08-20: EM: moved to STUI
2013-03-11: EM: changed voice to mac system Glass.wav
2013-04-20: EM: multiple refinement,  added format and colors,
    changed time left for None if no exposures left in sop sequence.
2013-04-22: EM:
    changed colors to self.fgList=["black", "ForestGreen","OrangeRed"]
    changed name from Timer to apogeeTimer
    added check button for sound on / off, default on.
2012-05-17 EM: change label text to just "apogeeTimer"
2015-02-04 EM: timer updated for new sop keywords
2019-12-02 EM removed any prints to STUI log
"""
import Tkinter

import os

import RO.OS
import RO.Wdg
import TUI
import TUI.Models

SoundsDir = RO.OS.getResourceDir(TUI, "Sounds")
SoundFileName = "Glass.wav"


class ScriptClass(object):
    def __init__(self, sr, ):
        self.sr = sr
        self.fgList = ["DarkGrey", "ForestGreen", "Brown"]
        self.name = " APOGEE Timer: "
        # print "-----" + self.name + "-------"

        soundFilePath = os.path.join(SoundsDir, SoundFileName)
        self.soundPlayer = RO.Wdg.SoundPlayer(soundFilePath)

        self.sopModel = TUI.Models.getModel("sop")
        self.apogeeModel = TUI.Models.getModel("apogee")

        sr.master.winfo_toplevel().wm_resizable(True, True)
        F1 = Tkinter.Frame(sr.master)
        gr = RO.Wdg.Gridder(F1)
        F1.grid(row=0, column=0, sticky="ns")
        self.labWdg = RO.Wdg.Label(master=F1, text=self.name, fg=self.fgList[0])
        self.labWdg.grid(row=0, column=0, sticky="ew")
        self.checkWdg = RO.Wdg.Checkbutton(master=F1, text="sound",
                                           defValue=True,
                                           helpText="Play sound", )
        self.checkWdg.grid(row=0, column=1, sticky="ew")
        self.expTimer = RO.Wdg.ProgressBar(master=sr.master,
                                           valueFormat="%4.1f", label=None, )
        self.expTimer.grid(row=1, column=0, sticky="ew")
        sr.master.rowconfigure(0, weight=1)
        sr.master.rowconfigure(1, weight=1)
        sr.master.columnconfigure(0, weight=1)

        self.alertTime = 5.0  # min
        self.alert = True

        self.sopModel.doApogeeScienceState.addCallback(
            self.doApogeeScienceState, callNow=True)
        self.sopModel.doApogeeScience_index.addCallback(
            self.doApogeeScience_index, callNow=True)
        self.index, nPairs = self.sopModel.doApogeeScience_index[0:2]
        self.index_in_pair = 0
        self.apogeeModel.utrReadState.addCallback(self.utrState, callNow=True)

    def doApogeeScienceState(self, keyVar):
        if not keyVar.isGenuine: return
        self.record()

    def doApogeeScience_index(self, keyVar):
        if not keyVar.isGenuine: return
        indexC, nPairs = self.sopModel.doApogeeScience_index[0:2]
        # print self.sopModel.doApogeeScience_index
        if indexC != self.index:
            self.index_in_pair = 0
            self.index = indexC
        self.record()

    def utrState(self, keyVar):
        if not keyVar.isGenuine: return
        # print self.apogeeModel.utrReadState
        if keyVar[2] == keyVar[3]:
            self.index_in_pair = 1
        self.record()

    def record(self, ):
        if self.sopModel.doApogeeScienceState[0] != 'running':
            self.setNone()
            return
        index, nPairs = self.sopModel.doApogeeScience_index[
                        0:2]  # running and requested dither pairs
        expTime = self.sopModel.doApogeeScience_expTime[
            0]  # "exposure time" in  sec

        # total time for exposure
        totalTime = nPairs * 2.0 * expTime / 60.0  # sop total time in min

        # pairs over 
        sopOver = index * 2.0 * expTime / 60.0

        # exposure in pair over self.index_in_pair

        pairOver = self.index_in_pair * expTime / 60.0

        # apogee
        # KeyVar('apogee', utrReadState=(String('apRaw-14880058'), Enum('Done'), Int(10), Int(10)))
        #  String('apRaw-14880058')  "name of exposure"
        #  Enum('Done')  "state of UTR read"
        #  Int(10)  "number of current UTR read, starting from 1"
        #  Int(10)  "total number of UTR reads requested"
        utr2 = self.apogeeModel.utrReadState[2]  # number of current UTR reads
        utrExp = self.apogeeModel.utrReadTime[0] / 60.
        utrOver = utr2 * utrExp

        newVal = totalTime - sopOver - pairOver - utrOver

        # print "--", "pair=",index, "index_in_pair=", self.index_in_pair , utr2
        # print "------", "full pair over=",sopOver, "half-pair-over=",pairOver, "utr-over=", utrOver
        over = sopOver + pairOver + utrOver
        left = totalTime - over
        # print "----------", "over =", over, "  left=", left
        self.setTimer(newVal=left, newMin=0, newMax=totalTime)

    def setTimer(self, newVal, newMin, newMax):
        state = self.sopModel.doApogeeScienceState[0]
        self.labWdg.set("%s %5.1f (of %5.1f) min" % (self.name, newVal, newMax))
        self.expTimer.setValue(newValue=newVal, newMin=newMin, newMax=newMax)
        self.labWdg.config(fg=self.fgList[0])
        return

    def setNone(self):
        state = self.sopModel.doApogeeScienceState[0]
        self.labWdg.set("%s  %s " % (self.name, state))
        self.expTimer.setValue(newValue=0.0, newMin=0.0, newMax=0.0001)
        self.labWdg.config(fg=self.fgList[0])
        return

    def run(self, sr):
        self.record()


'''
    def setTimer(self,):
        npairs=self.sopModel.doApogeeScience_index[1]
        requested_utr_reads=self.apogeeModel.utrReadState[3]
        try:
            apExpTime= self.apogeeModel.utrReadTime[0]
            self.totalTime=npairs *2.0 * requested_utr_reads * apExpTime 
            self.timeLeft=self.totalTime
            self.alert = True
        except:
            self.totalTime=None
            self.timeLeft=None
            self.alert = False
        print "self.totalTime=",self.totalTime
        print "self.timeLeft=",self.timeLeft
            
    def sopState (self, keyVar):
        print "sop state=", self.state
        if not keyVar.isGenuine: 
            return
        if self.state == keyVar[0]:
            return
        self.state=keyVar[0]
        if self.state == 'running':
            self.setTimer()
            maxT=self.totalTime/60.0
            val=self.timeLeft/60.0
            self.expTimer.setValue(newValue=val, newMin=0, newMax=maxT)
        else:
            self.setNone(self.state)

    def utrState(self, keyVar):
        if not keyVar.isGenuine: 
            return
        if self.utrRead == keyVar[2]:
            return

        self.utrRead=self.apogeeModel.utrReadState[2]
        self.timeLeft=self.timeLeft-self.apogeeModel.utrReadTime[0]
        
        timeLeftMin=self.timeLeft/60.0
        totalTimeMin=self.totalTime/60.0
        if timeLeftMin > 5.0: 
            self.labWdg.config(fg=self.fgList[1])
            self.labWdg.set("%s %5.1f min " % (self.name,self.timeLeft))
            self.expTimer.setValue(newValue=timeLeftMin, newMin=0, newMax=totalTimeMin)            
        elif 0 < timeLeftMin <= self.alertTime:
            if self.alert and  self.checkWdg.getBool():
                self.soundPlayer.play()
                self.alert = False
            self.labWdg.config(fg=self.fgList[2])
            self.labWdg.set("%s %5.1f min " % (self.name,self.timeLeft))
            self.expTimer.setValue(newValue=timeLeftMin, newMin=0, newMax=totalTimeMin)
        else: 
            pass
#            self.setNone(self.state)
        return
'''

#    def end(self, sr):
#        pass
#  self.sopModel.doApogeeScience_sequenceState.removeCallback(self.seqState)
#  self.apogeeModel.utrReadState.removeCallback(self.utrState)
#  print "-- call removed,  done --"

#    Key("doApogeeScience_expTime", Float(help="exposure time", units="sec"), Float(help="default", units="sec")),
#    Key("doApogeeScience_sequenceState", String(help="full exposure sequence. Basically ditherSeq * seqCount"),
#        Int(help="index of running exposure")),

if __name__ == "__main__":
    import TUI.Base.TestDispatcher

    TestDispatcher = TUI.Base.TestDispatcher.TestDispatcher("sop")
    sopTester = TestDispatcher(actor="sop", delay=0.5)
    tuiModel = testDispatcher.tuiModel
    testData = ('doApogeeScienceState="running"',)
    sopTester.dispatch(testData)
