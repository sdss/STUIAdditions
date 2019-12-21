""" Elena Malanushenko  01/30/2011
script to gather information for night log

History: 
05/16/2011  removed scale from 1st block 
.. 
09/09/2013 EM: changed format of calibOffset to 4 digits to fit 80 chars line  
    size. 
some day in the past:  added 4th window for hartmann output.
03/25/2015 EM:  formated hartmann output to fit 80 chars width in night log;
    removed all print to stui error log
03/30/2015 EM: format hartmann block;  fixed  bug with cart number
2015-11-05 ROwen    Stop using dangerous bare "except:"
2016-02-03 EM  Added  callback functions for hartmann values;  print values 
    only specific for the last hartmann;  if failed, no old values output in the
    table but '?'.
2017-06-12 EM Updated hartStart with cmd call for function with option. 
2018-04-28 DO Updated fwhm --> with new seeing keyword, follow up of Jose's 
   of guider changes
2018-10-27 EM Added   guiderActor.guideRMS[1] value to logWdg1 table;  
    formatted offsets to shrink the line  
2019-10-5 DG&EM: Replaced updateBossState with updateMangaState that correctly
   tracks whether or not the exposure is a new manga exposure and writes to log
2019-10-6 DG: Rolled back previous changes by commenting the necessary lines
2019-12-1 DG: Added a callback
2019-12-19 DG: Made a number of formatting changes for more stable results
"""

import RO.Wdg
import TUI.Models
import time
import numpy as np


# noinspection PyPep8Naming
class ScriptClass(object, ):
    def __init__(self, sr, ):
        # if True, run in debug-only mode _
        # if False, real time run
        sr.debug = False
        self.sr = sr
        self.name = "-logSupport-3-"
        print(self.name)
        width = 80
        height = 5

        # resizeable window-1
        sr.master.winfo_toplevel().wm_resizable(True, True)

        # log1  - offset
        self.logWdg1 = RO.Wdg.LogWdg(master=sr.master, width=width,
                                     height=height, helpText="Offset", )
        self.logWdg1.grid(row=0, column=0, sticky="news")

        # log2  - focus
        self.logWdg2 = RO.Wdg.LogWdg(master=sr.master, width=width,
                                     height=height, helpText="Focus",
                                     relief="sunken", bd=2, )
        self.logWdg2.grid(row=1, column=0, sticky="nsew")

        # log3  -- weather
        self.logWdg3 = RO.Wdg.LogWdg(master=sr.master, width=width,
                                     height=height, helpText="Weather",
                                     relief="sunken", bd=2)
        self.logWdg3.grid(row=2, column=0, sticky="nsew")

        # log4  -- hartmann
        self.logWdg4 = RO.Wdg.LogWdg(master=sr.master, width=width,
                                     height=height, helpText="Hartman",
                                     relief="sunken", bd=2)
        self.logWdg4.grid(row=3, column=0, sticky="nsew")

        # resizeable window-2
        sr.master.rowconfigure(0, weight=1)
        sr.master.rowconfigure(1, weight=1)
        sr.master.rowconfigure(2, weight=1)
        sr.master.rowconfigure(3, weight=1)
        sr.master.columnconfigure(0, weight=1)

        # stui models
        self.tccModel = TUI.Models.getModel("tcc")
        self.guiderModel = TUI.Models.getModel("guider")
        self.apoModel = TUI.Models.getModel("apo")
        self.apogeeModel = TUI.Models.getModel("apogee")
        self.cmdsModel = TUI.Models.getModel("cmds")
        self.hartmannModel = TUI.Models.getModel("hartmann")
        self.sopModel = TUI.Models.getModel("sop")

        fs = "12"  # font size
        ft = "Monaco"  # "Courier"  #"Menlo"  # font type
        self.logWdg1.text.tag_config("cur", font=(ft, fs))
        self.logWdg2.text.tag_config("cur", font=(ft, fs))
        self.logWdg3.text.tag_config("cur", font=(ft, fs))
        self.logWdg4.text.tag_config("cur", font=(ft, fs))

        self.logWdg1.text.tag_config("b", foreground="darkblue")
        self.logWdg2.text.tag_config("g", foreground="darkgreen")
        self.logWdg3.text.tag_config("c", foreground="Brown")
        self.logWdg4.text.tag_config("r", foreground="red")

        # title lines
        dashes = "%s" % (width * "=")

        self.logWdg1.addMsg("--- Offsets --- (arcsec) ", tags=["b", "cur"])
        self.logWdg1.addMsg('{:<5} {:<9} {:<6} {:<4} {:<6} {:<11}'
                            ' {:<9} {:<10} {:<8}'
                            ''.format('Time', 'Cart', 'Az', 'Alt', 'Rot',
                                      'objOff', 'guideRot', 'calibOff',
                                      'guideRMS'),
                            tags=["b", "cur"])
        self.logWdg1.addMsg("%s" % dashes, tags=["b", "cur"])

        self.logWdg2.addMsg("--- Focus ---", tags=["g", "cur"])

        self.logWdg2.addMsg('{:<5} {:<9} {:<6} {:<5} {:<5} {:<5} {:<6} {:<5}'
                            ' {:<5} {:<4} {:<3}'
                            ' {:<4}'.format('Time', 'Cart', 'Scale', 'M1', 'M2',
                                            'Focus', 'Az', 'Alt', 'Temp',
                                            'Wind', 'Dir', 'FWHM'),
                            tags=["g", "cur"])
        self.logWdg2.addMsg("%s" % dashes, tags=["g", "cur"])

        self.logWdg3.addMsg("--- Weather ---", tags=["cur"])
        self.logWdg3.addMsg('{:<5} {:<9} {:<5} {:<5} {:<4} {:<5} {:<4} {:<3}'
                            ' {:<6} {:<7} {:<5}'
                            ''.format('Time', 'Cart', 'Temp', 'DP', 'Diff',
                                      'Humid', 'Wind', 'Dir', '1umDst',
                                      'IRSCSig', 'IRSCm'),
                            tags=["cur"])
        self.logWdg3.addMsg("%s" % dashes, tags=["cur"])

        self.logWdg4.addMsg("--- Hartmann ---", tags=["cur", "c"])
        self.logWdg4.addMsg('{:<5} {:<9} {:<5} {:<5} {:<5} {:<7} {:<4} {:<5}'
                            ' {:<5} {:<5} {:<7} {:<4}'
                            ''.format('Time', 'Cart', 'R1', 'B1', 'Move1',
                                      'B1Resid', 'TSP1', 'R2', 'B2', 'Move2',
                                      'B2Resid', 'TSP2'),
                            tags=["cur", "c"])
        # sline = "%s     %s    %s" % (14 * '-', 28 * "-", 28 * "-")

        self.logWdg4.addMsg("%s" % dashes, tags=["cur", "c"])

        self.bossModel = TUI.Models.getModel("boss")
        self.expState = self.bossModel.exposureState[0]
        # self.bossModel.exposureState.addCallback(self.updateBossState,
        #                                          callNow=True)
        self.apogeeState = self.apogeeModel.exposureWroteSummary[0]
        self.apogeeModel.exposureWroteSummary.addCallback(
            self.updateApogeeExpos, callNow=True)

        self.startHartmannCollimate = None
        self.cmdsModel.CmdQueued.addCallback(self.hartStart, callNow=False)
        self.cmdsModel.CmdDone.addCallback(self.hartEnd, callNow=False)
        self.cartHart = " x-xxxxA"

        self.hartInfo = [0] * 8

        self.hartmannModel.r1PistonMove.addCallback(self.r1PistonMoveFun,
                                                    callNow=False)
        self.hartmannModel.r2PistonMove.addCallback(self.r2PistonMoveFun,
                                                    callNow=False)

        self.hartmannModel.b1RingMove.addCallback(self.b1RingMoveFun,
                                                  callNow=False)
        self.hartmannModel.b2RingMove.addCallback(self.b2RingMoveFun,
                                                  callNow=False)
        self.hartmannModel.sp1AverageMove.addCallback(self.sp1AverageMoveFun,
                                                      callNow=False)
        self.hartmannModel.sp2AverageMove.addCallback(self.sp2AverageMoveFun,
                                                      callNow=False)
        self.hartmannModel.sp1Residuals.addCallback(self.sp1ResidualsFun,
                                                    callNow=False)
        self.hartmannModel.sp2Residuals.addCallback(self.sp2ResidualsFun,
                                                    callNow=False)

        self.sopModel = TUI.Models.getModel('sop')
        # Inits a variable used later
        self.manga_seq_i = self.sopModel.doMangaSequence_ditherSeq[1]
        self.ap_manga_seq_i = self.sopModel.doApogeeMangaSequence_ditherSeq[1]
        # If MaNGA is leading, this will be called
        self.sopModel.doMangaSequence_ditherSeq.addCallback(
            self.updateMangaState, callNow=True)
        # If MaNGA is not leading, this will be called
        self.sopModel.doApogeeMangaSequence_ditherSeq.addCallback(
            self.updateApogeeMangaState, callNow=True)

    def r1PistonMoveFun(self, keyVar):
        if not keyVar.isGenuine:
            return
        self.hartInfo[0] = keyVar[0]

    def r2PistonMoveFun(self, keyVar):
        if not keyVar.isGenuine:
            return
        self.hartInfo[1] = keyVar[0]

    def b1RingMoveFun(self, keyVar):
        if not keyVar.isGenuine:
            return
        self.hartInfo[2] = keyVar[0]

    def b2RingMoveFun(self, keyVar):
        if not keyVar.isGenuine:
            return
        self.hartInfo[3] = keyVar[0]

    def sp1AverageMoveFun(self, keyVar):
        if not keyVar.isGenuine:
            return
        self.hartInfo[4] = keyVar[0]

    def sp2AverageMoveFun(self, keyVar):
        if not keyVar.isGenuine:
            return
        self.hartInfo[5] = keyVar[0]

    def sp1ResidualsFun(self, keyVar):
        if not keyVar.isGenuine:
            return
        self.hartInfo[6] = keyVar[1]

    def sp2ResidualsFun(self, keyVar):
        if not keyVar.isGenuine:
            return
        self.hartInfo[7] = keyVar[1]

    def hartStart(self, keyVar):
        if not keyVar.isGenuine:
            return
            # q1=(keyVar[4]=="hartmann")
            # and (keyVar[6]=="collimate ignoreResiduals")
        q1 = (keyVar[4] == "hartmann") and ("collimate" in keyVar[6])
        q2 = (keyVar[4] == "sop") and (keyVar[6] == "collimateBoss")
        if q1 or q2:
            self.startHartmannCollimate = keyVar[0]  # setup flag
            self.hartInfo = [np.nan] * 8

    def hartEnd(self, keyVar):
        if not keyVar.isGenuine:
            return
        if keyVar[0] == self.startHartmannCollimate:
            self.startHartmannCollimate = None
            self.print_hartmann_to_log()

    def print_hartmann_to_log(self):
        tm = self.getTAITimeStr()
        cart = self.getCart(self.sr)

        # rPiston = self.hartInfo[0]
        # bRing = self.hartInfo[2]
        # spAvMove = self.hartInfo[4]
        # spRes = self.hartInfo[6]
        # spTemp = self.bossModel.sp1Temp[0]
        # try:
        #     ss2 = "%5i %5.1f %5i %5.1f %4.1f" % (rPiston, bRing, spAvMove,
        #                                          spRes, spTemp)
        # except ValueError:
        #     ss2 = "%5s %5s %5s %5s %4s" % (rPiston, bRing, spAvMove, spRes,
        #                                    spTemp)

        # rPiston = self.hartInfo[1]
        # bRing = self.hartInfo[3]
        # spAvMove = self.hartInfo[5]
        # spRes = self.hartInfo[7]
        # spTemp = self.bossModel.sp2Temp[0]
        # try:
        #    ss3 = "%5i %5.1f %5i %5.1f %4.1f" % (rPiston, bRing, spAvMove,
        #                                         spRes, spTemp)
        # except ValueError:
        #    ss3 = "%5s %5s %5s %5s %4s" % (rPiston, bRing, spAvMove, spRes,
        #                                   spTemp)
        try:
            hart_data = np.array(self.hartInfo).astype(float)
            # self.logWdg4.addMsg("%s  %s    %s" % (ss1, ss2, ss3),
            # tags=["c", "cur"])
            self.logWdg4.addMsg('{:<5} {:<9} {:<5.0f} {:<+5.1f} {:<5.0f}'
                                ' {:<7.1f}'.format(tm, cart, *hart_data[0::2])
                                + (' {:<4.1f}'.format(float(
                                    self.bossModel.sp1Temp[0])))
                                + (' {:<5.0f} {:<5.1f} {:<5.0f}'
                                   ' {:<7.1f}'.format(*hart_data[1::2]))
                                + (' {:<4.1f}'.format(float(
                                    self.bossModel.sp2Temp[0]))),
                                tags=["cur", "c"])
        except ValueError:
            hart_data = np.array(self.hartInfo).astype(str)
            self.logWdg4.addMsg('{:<5} {:<9} {:<5} {:<5} {:<5} {:<7}'
                                ''.format(tm, cart, *hart_data[0::2])
                                + (' {:<4}'.fomrat(float(
                                    self.bossModel.sp1Temp[0])))
                                + (' {:<5} {:<5} {:<5} {:<7}'.format(
                                    *hart_data[1::2]))
                                + (' {:<4}'.format(float(
                                    self.bossmodel.sp2Temp[0]))),
                                tags=["cur", "c"])

    def updateApogeeExpos(self, keyVar):
        if not keyVar.isGenuine:
            return
        if keyVar[0] != self.apogeeState:
            sr = self.sr
            dd3 = self.apogeeModel.utrReadState[3]
            if (dd3 == 47) or (dd3 == 94):
                self.record(sr, "APOGEE")
                self.apogeeState = keyVar[0]

    # Some old code we do not need
    # def updateBossState(self, keyVar):
    #     if not keyVar.isGenuine:
    #         return
    #     if keyVar[0] != self.expState:
    #         if keyVar[0] == "INTEGRATING" and keyVar[1] == 900.00:
    #             sr = self.sr
    #             self.record(sr, "BOSS")
    #         self.expState = keyVar[0]

    def updateMangaState(self, keyVar):
        if not keyVar.isGenuine:
            return
        if keyVar[1] != self.manga_seq_i:
            sr = self.sr
            self.record(sr, "MaNGA")
            self.manga_seq_i = keyVar[1]

    def updateApogeeMangaState(self, keyVar):
        if not keyVar.isGenuine:
            return
        if keyVar[1] != self.ap_manga_seq_i:
            sr = self.sr
            self.record(sr, "MaStar")
            self.ap_manga_seq_i = keyVar[1]

    def getTAITimeStr(self, ):
        #        return time.strftime("%H:%M:%S",
        #              time.gmtime(time.time() -
        #              - RO.Astro.Tm.getUTCMinusTAI()))
        return time.strftime("%H:%M",
                             time.gmtime(time.time()
                                         - - RO.Astro.Tm.getUTCMinusTAI()))

    def getCart(self, sr, ):
        ctLoad = self.guiderModel.cartridgeLoaded
        gc = sr.getKeyVar(ctLoad, ind=0, defVal=99)
        gp = sr.getKeyVar(ctLoad, ind=1, defVal=9999)
        gs = sr.getKeyVar(ctLoad, ind=2, defVal="Z")
        ss = "%2i-%s%s" % (gc, str(gp), str(gs))
        return ss

    def fInt(self, val, num):
        return str(int(val)).rjust(num, " ")

    def record(self, sr, atm):
        tm = self.getTAITimeStr()
        scale = float(sr.getKeyVar(self.tccModel.scaleFac, ind=0, defVal=1.0))

        az = float(sr.getKeyVar(self.tccModel.axePos, ind=0, defVal=999))
        alt = float(sr.getKeyVar(self.tccModel.axePos, ind=1, defVal=99))
        rot = float(sr.getKeyVar(self.tccModel.axePos, ind=2, defVal=999))
        cart = self.getCart(sr, )

        primOr = int(sr.getKeyVar(self.tccModel.primOrient, ind=0, defVal=9999))
        secOr = int(sr.getKeyVar(self.tccModel.secOrient, ind=0, defVal=9999))
        secFoc = int(sr.getKeyVar(self.tccModel.secFocus, ind=0, defVal=9999))

        # def float(n):
        #     if n is None:
        #         return "%5s" % "n/a"  # 999.9"
        #     else:
        #         return "%5.1f" % (n * 3600)

        # def ffsecS(n):
        #     if n is None:
        #         return "%4s" % "n/a"
        #     else:
        #         return "%4.1f" % (n * 3600)
        # All offsets *3600
        objOff0 = float(
            RO.CnvUtil.posFromPVT(self.tccModel.objArcOff[0])) * 3600
        objOff1 = float(
            RO.CnvUtil.posFromPVT(self.tccModel.objArcOff[1])) * 3600

        guideOff0 = float(
            RO.CnvUtil.posFromPVT(self.tccModel.guideOff[0])) * 3600
        guideOff1 = float(
            RO.CnvUtil.posFromPVT(self.tccModel.guideOff[1])) * 3600
        guideOff2 = float(
            RO.CnvUtil.posFromPVT(self.tccModel.guideOff[2])) * 3600

        calibOff0 = float(
            RO.CnvUtil.posFromPVT(self.tccModel.calibOff[0])) * 3600
        calibOff1 = float(
            RO.CnvUtil.posFromPVT(self.tccModel.calibOff[1])) * 3600
        calibOff2 = float(
            RO.CnvUtil.posFromPVT(self.tccModel.calibOff[2])) * 3600

        # rotOff = RO.CnvUtil.posFromPVT(self.tccModel.guideOff[2])

        fwhm = float(sr.getKeyVar(self.guiderModel.seeing, ind=0, defVal=99.9))
        guideRMS = float(sr.getKeyVar(self.guiderModel.guideRMS, ind=1,
                                      defVal=99.999))

        airT = float(sr.getKeyVar(self.apoModel.airTempPT, ind=0, defVal=-99))
        direc = int(sr.getKeyVar(self.apoModel.windd, ind=0, defVal=-99))
        wind = int(sr.getKeyVar(self.apoModel.winds, ind=0, defVal=99))
        dp = sr.getKeyVar(self.apoModel.dpTempPT, ind=0, defVal=-99)
        humid = int(sr.getKeyVar(self.apoModel.humidPT, ind=0, defVal=999))
        dustb = int(sr.getKeyVar(self.apoModel.dustb, ind=0, defVal=9999))
        #   dustb="%5s" % (sr.getKeyVar(self.apoModel.dustb, ind=0,
        #   defVal="n/a"))

        irsc = sr.getKeyVar(self.apoModel.irscsd, ind=0, defVal=999)
        irscmean = sr.getKeyVar(self.apoModel.irscmean, ind=0, defVal=999)

        at = sr.getKeyVar(self.apoModel.airTempPT, ind=0, defVal=999)
        val = sr.getKeyVar(self.apoModel.dpTempPT, ind=0, defVal=999)
        diff = at - val

        objOffs = "(%3.1f,%3.1f) " % (float(objOff0), float(objOff1))
        calibOffs = "(%2.0f,%2.0f,%2.0f)" % (float(calibOff0),
                                             float(calibOff1),
                                             float(calibOff2))
        self.logWdg1.addMsg('{:<5} {:<9} {:<+6.1f} {:<4.1f} {:<+6.1f} {:<11}'
                            ' {:<+8.1f} {:<10} {:<8.3f}'
                            ''.format(tm, cart, az, alt, rot, objOffs,
                                      guideOff2, calibOffs, guideRMS
                                      ), tags=["b", "cur"])

        # focus
        self.logWdg2.addMsg('{:<5} {:<9} {:<+6.1f} {:<+5.0f} {:<+5.0f}'
                            ' {:<+5.0f} {:<+6.1f} {:<5.1f} {:<+5.1f} {:<4.0f}'
                            ' {:<3.0f}'
                            ' {:<4.1f}'.format(tm, cart, (scale - 1) * 1e6,
                                               primOr,
                                               secOr, secFoc, az, alt, airT,
                                               wind, direc, fwhm),
                            tags=["g", "cur"])

        # weather
        self.logWdg3.addMsg('{:<5} {:<9} {:<+5.1f} {:<+5.1f} {:<4.1f} {:<5.0f}'
                            ' {:<4.0f} {:<3.0f} {:<6.0f} {:<7.1f} {:<5.1f}'
                            ''.format(tm, cart, airT, dp, diff, humid,
                                      wind, direc, dustb, irsc, irscmean),
                            tags=["cur"])
        print(atm, )

    def run(self, sr):
        self.record(sr, "")
        self.print_hartmann_to_log()
