"""A timer for all SDSS-V exposures

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
2020-11-15 DG A major, almost complete rewrite to work with SDSS-V
"""

import Tkinter as tk
import os.path

import numpy as np

import RO.Astro.Tm
import RO.Comm
import RO.OS
import RO.Wdg
import TUI.Models
import TUI.PlaySound

SoundsDir = RO.OS.getResourceDir(TUI, "Sounds")
SoundFileName = "Glass.wav"

__version__ = '3.0.0'


class ScriptClass(object):
    def __init__(self, sr, ):

        print('===timer Version {}==='.format(__version__))
        sr.master.winfo_toplevel().wm_resizable(True, True)
        self.fgList = ["DarkGrey", "ForestGreen", "Brown"]

        soundFilePath = os.path.join(SoundsDir, SoundFileName)
        self.soundPlayer = RO.Wdg.SoundPlayer(soundFilePath)

        sr.debug = False
        self.sr = sr
        frame = tk.Frame(sr.master)
        # gr = RO.Wdg.Gridder(frame)
        frame.grid(row=0, column=0, sticky="sn")

        self.label_wdg = RO.Wdg.Label(master=frame, text="      ",
                                      fg=self.fgList[0])
        self.label_wdg.grid(row=0, column=0, sticky="ns")
        self.checkWdg = RO.Wdg.Checkbutton(master=frame, text="", defValue=True,
                                           helpText="Play sound", )
        self.checkWdg.grid(row=0, column=1, sticky="we")

        self.timer_bar = RO.Wdg.ProgressBar(master=sr.master,
                                            valueFormat="%5.2f", label=None)
        self.timer_bar.grid(row=1, column=0, sticky="ew")

        sr.master.rowconfigure(0, weight=1)
        sr.master.rowconfigure(1, weight=1)
        sr.master.columnconfigure(0, weight=1)

        self.minAlert = 5.
        self.remaining_time = None
        self.total_time = None
        self.exp_t_passed = None
        self.alert = True
        self.call_func = 'Timer'
        self.callback = None
        self.timer = RO.Comm.Generic.Timer()
        self.wait = 1
        # self.fooTimer.start(self.wait, foo) # schedule self again
        self.set_timer()

        self.boss = TUI.Models.getModel('boss')
        self.sop = TUI.Models.getModel("sop")
        self.apogee = TUI.Models.getModel('apogee')

        self.sop.doApogeeScience_index.addCallback(
            self.calc_apogee_science_time, callNow=False
        )

        self.sop.doApogeeBossScience_nExposures.addCallback(
            self.calc_apogee_boss_science_time, callNow=False
        )

        self.apogee.utrReadState.addCallback(
            self.calc_apogee_science_time, callNow=False
        )

    def calc_apogee_science_time(self, keyVar):
        if self.sr.debug:
            print('timer survey: {}'.format(self.sop.survey[1]))
        self.callback = 'APOGEE utrRead'
        if 'APOGEE-2' in self.sop.survey[0]:
            remaining_pairs = (self.sop.doApogeeScience_index[1]
                               - self.sop.doApogeeScience_index[0])
            dither_count = self.sop.apogeeDitherSet[1]
            pair_time = np.sum(self.sop.doApogeeScience_expTime)
            self.exp_t_passed = (dither_count
                                 * self.sop.doApogeeScience_expTime[0]
                                 + self.apogee.utrReadState[2] *
                                 self.apogee.utrReadTime[0])
            self.remaining_time = (remaining_pairs * pair_time
                                   - self.exp_t_passed)
            self.total_time = self.sop.doApogeeScience_index[1] * pair_time
            self.call_func = self.sop.survey[1]
            if self.sr.debug:
                print('{} ({}) timer callback,'
                      ' Remaining pairs: {}'
                      ' Pair time: {}'
                      ' Progress: {} / {}'.format(self.call_func, self.callback,
                                                  remaining_pairs, pair_time,
                                                  self.remaining_time,
                                                  self.total_time))
        else:  # SDSS-V
            self.calc_apogee_boss_science_time(keyVar)

        self.timer_bar.setValue(newValue=self.remaining_time / 60, newMin=0,
                                newMax=self.total_time / 60)
        self.set_timer()

    def calc_apogee_boss_science_time(self, keyVar):
        remaining_exps = (self.sop.doApogeeBossScience_nExposures[1]
                          - self.sop.doApogeeBossScience_nExposures[0])
        total_exps = self.sop.doApogeeBossScience_nExposures[1]
        dither_count = self.sop.apogeeDitherSet[1]
        dither_time = np.max(self.sop.doApogeeScience_expTime)

        if 'BHM lead' in self.sop.survey[1]:
            # The fudge factor is for readout + time where APOGEE is still
            # exposing after BOSS is done. It has been tested and found to be
            # very accurate for long BHM sets.
            exp_time = np.max(self.sop.doBossScience_expTime) + 106.6

        elif 'MWM lead' in self.sop.survey[1]:

            exp_time = np.max(self.sop.doBossScience_expTime) + 124.5
        else:
            exp_time = np.nan

        self.exp_t_passed = (self.sop.doApogeeBossScience_nExposures[0]
                             * exp_time
                             + dither_count * dither_time
                             + self.apogee.utrReadState[2] *
                             self.apogee.utrReadTime[0])
        self.remaining_time = total_exps * exp_time - self.exp_t_passed
        self.total_time = (self.sop.doApogeeBossScience_nExposures[1]
                           * exp_time)

        self.call_func = self.sop.survey[1]
        if self.sr.debug:
            print('{} ({}) timer callback,'
                  ' Remaining exps: {}'
                  ' Exp time: {}'
                  ' Progress: {} / {}'.format(self.call_func, self.callback,
                                              remaining_exps, exp_time,
                                              self.remaining_time,
                                              self.total_time))

        self.timer_bar.setValue(newValue=self.remaining_time / 60, newMin=0,
                                newMax=self.total_time / 60)
        self.set_timer()

    def set_timer(self):
        """ Russel's timer"""
        self.timer.cancel()
        if self.remaining_time is None:
            self.label_wdg.set("Now is no time at all".format(self.call_func))
            self.label_wdg.config(fg=self.fgList[0])
        elif self.remaining_time < 0:
            self.remaining_time = None
            self.total_time = None
        else:
            min_left = self.remaining_time / 60.0
            self.label_wdg.set("{}: {:6.0f} min".format(
                self.call_func, self.total_time / 60))
            if min_left > self.minAlert:
                fgInd = 1
                self.alert = True
            elif min_left <= self.minAlert:
                fgInd = 2
                if self.alert:
                    if self.checkWdg.getBool():
                        self.soundPlayer.play()
                        self.soundPlayer.play()
                    self.alert = False
            else:
                fgInd = 0
            self.label_wdg.config(fg=self.fgList[fgInd])
            self.timer_bar.setValue(newValue=min_left)
            # schedule self again
            self.timer.start(self.wait, self.set_timer)
        self.callback = None

    def run(self, sr):
        pass

    def end(self, sr):
        self.timer.cancel()
