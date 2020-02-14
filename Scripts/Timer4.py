"""A timer for BOSS exposures

History:
2013-04-20 EM: bossTimer.py
2013-04-20 EM: added color and sound
2013-04-22 EM: added check button on/off sound, default on.
2012-04-24 EM: added ProgressBar
2012-05-17 EM: cut label text to just "bossTimer"
2013-08-20 EM: moved to STUI
2014-03-05  changed keyword name sopModel.doScience to sopModel.doBossScience
    for new sop
2014-11-05 EM fixed bug with initial keyword value before connection.
2019-12-02 EM removed any prints to STUI log;  added try to get len() of 
   sopModel.doApogeeMangaSequence_ditherSeq[0]  in init section
"""

import os.path
import time
import Tkinter
import RO.Astro.Tm
import RO.Comm
import RO.OS
import RO.Wdg
import TUI.Models
import TUI.PlaySound

SoundsDir = RO.OS.getResourceDir(TUI, "Sounds")
SoundFileName = "Glass.wav"


class ScriptClass(object):
    def __init__(self, sr, ):
        sr.master.winfo_toplevel().wm_resizable(True, True)
        self.fgList = ["DarkGrey", "ForestGreen", "Brown"]

        soundFilePath = os.path.join(SoundsDir, SoundFileName)
        self.soundPlayer = RO.Wdg.SoundPlayer(soundFilePath)

        self.sr = sr

        frame = Tkinter.Frame(sr.master)
        # gr = RO.Wdg.Gridder(frame)
        frame.grid(row=0, column=0, sticky="sn")

        self.labWdg = RO.Wdg.Label(master=frame, text="      ",
                                   fg=self.fgList[0])
        self.labWdg.grid(row=0, column=0, sticky="ns")
        self.checkWdg = RO.Wdg.Checkbutton(master=frame, text="", defValue=True,
                                           helpText="Play sound",)
        self.checkWdg.grid(row=0, column=1, sticky="we")

        self.expTimer = RO.Wdg.ProgressBar(master=sr.master,
                                           valueFormat="%5.2f",  label=None)
        self.expTimer.grid(row=1, column=0, sticky="ew")

        sr.master.rowconfigure(0, weight=1)
        sr.master.rowconfigure(1, weight=1)
        sr.master.columnconfigure(0, weight=1)

        self.minAlert = 300.0/60.0
        self.secEnd = None
        self.alert = True
        self.fooTimer = RO.Comm.Generic.Timer()
        self.wait = 1
        # self.fooTimer.start(self.wait, foo) # schedule self again
        self.set_timer()

        self.boss = TUI.Models.getModel('boss')
        self.sopModel = TUI.Models.getModel("sop")
        # self.nExp0, self.nExp1 = self.sopModel.doBossScience_nExp[0:2]
        self.SnExp1, self.nExp0 = self.sopModel.doApogeeMangaSequence_ditherSeq[
                                  0:2]
        try:
            self.nExp1 = len(self.SnExp1)
        except: 
            self.nExp1 = 0

        if sr.getKeyVar(self.boss.exposureState, 0) == 'INTEGRATING':
            # This conditional loop prevents the timer from being reset every
            # readout to n_exp_remaining * readout_time
            self.expTotal = sr.getKeyVar(self.boss.exposureState, 1, defVal=900)
        else:
            self.expTotal = 900.

        # I evaluated the time of reading out as 69.7 sec
        self.expTotal = self.expTotal + 69.7
        self.sopModel.doApogeeMangaSequence_ditherSeq.addCallback(
            self.update_rtime, callNow=True)
        # self.sopModel.doApogeeScienceState.addCallback(
        #    self.update_rtime, callNow=True)
        
    def get_time_str(self, ):
        """ get timestamp"""
        self.currPythonSeconds = RO.Astro.Tm.getCurrPySec()
        self.currTAITuple = time.gmtime(self.currPythonSeconds
                                        - RO.Astro.Tm.getUTCMinusTAI())
        self.taiTimeStr = time.strftime("%H:%M:%S", self.currTAITuple)
        return self.taiTimeStr, self.currPythonSeconds

    def update_rtime(self, keyVar):
        """Callback to update the exposure values, but this is actually a
        wrapper function for calc_manga_length and calc_apog_length
        """
        self.survey = self.sr.getKeyVar(self.sopModel.survey, 0)
        if 'MaNGA' in self.survey:
            self.calc_manga_length(keyVar)
        else:
            self.calc_apog_length(keyVar)

    def calc_manga_length(self, keyVar):
        if sr.getKeyVar(self.boss.exposureState, 0) == 'INTEGRATING':
            # This conditional loop prevents the timer from being reset every
            # readout to n_exp_remaining * readout_time
            self.expTotal = sr.getKeyVar(self.boss.exposureState, 1, defVal=900)
        else:
            self.expTotal = 900.
        self.SnExp1, self.nExp0 = keyVar[0:2]
        self.nExp1 = len(self.SnExp1)
        
        if keyVar[0] == keyVar[1]:   # end seq
            self.secEnd = None
        elif keyVar[0] != self.nExp0:   # begin seq, or next exposure
            tai, sec = self.get_time_str()
            self.secEnd = sec + (self.nExp1 - self.nExp0) * self.expTotal
            minleft = (self.nExp1 - self.nExp0) * self.expTotal / 60.0
        elif keyVar[1] != self.nExp1:  # modification in progress
            self.secEnd = self.secEnd + (keyVar[1] - self.nExp1) * self.expTotal
        else:
            tai, sec = self.get_time_str()
            self.secEnd = sec + (self.nExp1 - self.nExp0) * self.expTotal

        try:
            new_value = (self.nExp1 - self.nExp0) * self.expTotal / 60.
            new_max = self.nExp1 * self.expTotal / 60.
        except:
            new_value = 0
            new_max = 900
        else:
            self.expTimer.setValue(newValue=new_value, newMin=0, newMax=new_max)
            self.set_timer()

    def calc_apog_length(self, keyVar):
        self.expTotal = self.sr.getKeyVar(self.sopModel.doApogeeScience_expTime,
                                          ind=0, defVal=500)
        self.expTotal = self.expTotal
        # print self.SnExp1, self.nExp0

        self.SnExp1, self.nExp0 = keyVar[0:2]
        self.nExp1 = len(self.SnExp1)

        if keyVar[0] == keyVar[1]:  # end seq
            self.secEnd = None
        elif keyVar[0] != self.nExp0:  # begin seq, or next exposure
            tai, sec = self.get_time_str()
            self.secEnd = sec + (self.nExp1 - self.nExp0) * self.expTotal
            minleft = (self.nExp1 - self.nExp0) * self.expTotal / 60.0
        elif keyVar[1] != self.nExp1:  # modification in progress
            self.secEnd = self.secEnd + (keyVar[1] - self.nExp1) * self.expTotal
        else:
            tai, sec = self.get_time_str()
            self.secEnd = sec + (self.nExp1 - self.nExp0) * self.expTotal

        try:
            new_value = (self.nExp1 - self.nExp0) * self.expTotal / 60.
            new_max = self.nExp1 * self.expTotal / 60.
        except:
            new_value = 0
            new_max = 900
        else:
            self.expTimer.setValue(newValue=new_value, newMin=0, newMax=new_max)
            self.set_timer()

    def set_timer(self):
        """ Russel's timer"""
        self.fooTimer.cancel()
        lab = " A & M Timer: "
        if self.secEnd is None:
            self.labWdg.set("%s None   " % lab)
            self.labWdg.config(fg=self.fgList[0])
        else:
            tai, sec = self.get_time_str()
            min_left = (self.secEnd - sec) / 60.0
            self.labWdg.set("%s %6.2f min   " % (lab, min_left))
            if min_left > self.minAlert:
                fgInd = 1
                self.alert = True
            elif 0 < min_left <= self.minAlert:
                fgInd = 2
                if self.alert:
                    self.alert = False
                    if self.checkWdg.getBool():
                        self.soundPlayer.play()
                        self.soundPlayer.play()
            else:
                fgInd = 0
            self.labWdg.config(fg=self.fgList[fgInd])
            self.expTimer.setValue(newValue=min_left)
            # schedule self again
            self.fooTimer.start(self.wait, self.set_timer)

    def run(self, sr):
        pass

    def end(self, sr):
        self.fooTimer.cancel()
