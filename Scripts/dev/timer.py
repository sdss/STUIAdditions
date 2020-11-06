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
import Tkinter as tk
import RO.Astro.Tm
import RO.Comm
import RO.OS
import RO.Wdg
import TUI.Models
import TUI.PlaySound
import numpy as np

SoundsDir = RO.OS.getResourceDir(TUI, "Sounds")
SoundFileName = "Glass.wav"

__version__ = '2.7.0'


class ScriptClass(object):
    def __init__(self, sr, ):
        sr.master.winfo_toplevel().wm_resizable(True, True)
        self.fgList = ["DarkGrey", "ForestGreen", "Brown"]

        soundFilePath = os.path.join(SoundsDir, SoundFileName)
        self.soundPlayer = RO.Wdg.SoundPlayer(soundFilePath)

        self.sr = sr

        frame = tk.Frame(sr.master)
        # gr = RO.Wdg.Gridder(frame)
        frame.grid(row=0, column=0, sticky="sn")

        self.labWdg = RO.Wdg.Label(master=frame, text="      ",
                                   fg=self.fgList[0])
        self.labWdg.grid(row=0, column=0, sticky="ns")
        self.checkWdg = RO.Wdg.Checkbutton(master=frame, text="", defValue=True,
                                           helpText="Play sound", )
        self.checkWdg.grid(row=0, column=1, sticky="we")

        self.expTimer = RO.Wdg.ProgressBar(master=sr.master,
                                           valueFormat="%5.2f", label=None)
        self.expTimer.grid(row=1, column=0, sticky="ew")

        sr.master.rowconfigure(0, weight=1)
        sr.master.rowconfigure(1, weight=1)
        sr.master.columnconfigure(0, weight=1)

        self.minAlert = 300.0 / 60.0
        self.remaining_time = None
        self.total_time = None
        self.alert = True
        self.timer = RO.Comm.Generic.Timer()
        self.wait = 1
        # self.fooTimer.start(self.wait, foo) # schedule self again
        self.set_timer()

        self.boss = TUI.Models.getModel('boss')
        self.sopModel = TUI.Models.getModel("sop")

        self.sopModel.doApogeeScience_index.addCallback(
            self.calc_apogee_science_time, callNow=False
            )

        self.sopModel.doApogeeBossScience_nDither.addCallback(
            self.calc_apogee_boss_science_time, callNow=False
        )

    def calc_apogee_science_time(self, keyVar):
        remaining_pairs = keyVar[0] - keyVar[1]
        pair_time = np.sum(self.sopModel.doApogeeScience_expTime)
        self.remaining_time = remaining_pairs * pair_time
        self.total_time = keyVar[1] * pair_time
        self.expTimer.setValue(newValue=self.remaining_time, newMin=0,
                               newMax=self.total_time)
        print('APOGEE Science callback: {} / {}'.format(self.remaining_time,
                                                        self.total_time))
        self.set_timer()

    def calc_apogee_boss_science_time(self, keyVar):
        # TODO check these keywords during an Apogee Boss sequence
        remaining_pairs = keyVar[1] - keyVar[0]

    def set_timer(self):
        """ Russel's timer"""
        self.timer.cancel()
        if self.remaining_time is None:
            self.labWdg.set("Timer: None")
            self.labWdg.config(fg=self.fgList[0])
        else:
            min_left = self.remaining_time / 60.0
            self.labWdg.set("Timer: {:6.1f} min".format(min_left))
            if min_left > self.minAlert:
                fgInd = 1
                self.alert = True
            elif 0 < min_left <= self.minAlert:
                fgInd = 2
                if self.alert:
                    if self.checkWdg.getBool():
                        self.soundPlayer.play()
                        self.soundPlayer.play()
                        self.alert = False
            else:
                fgInd = 0
            self.labWdg.config(fg=self.fgList[fgInd])
            self.expTimer.setValue(newValue=min_left)
            # schedule self again
            self.timer.start(self.wait, self.set_timer)

    def run(self, sr):
        pass

    def end(self, sr):
        self.timer.cancel()
