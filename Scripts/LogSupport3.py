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
"""

import RO.Wdg
import TUI.Models
import time


# noinspection PyPep8Naming
class ScriptClass(object, ):
    def __init__(self, sr, ):
        # if True, run in debug-only mode 
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
        s = " "
        dashes = "%s" % (width * "-")

        self.logWdg1.addMsg("--- Offsets --- (arcsec) ", tags=["b", "cur"])
        self.logWdg1.addMsg('{:<5} {:<9} {:<6} {:<6} {:<6} {:<9}'
                            ' {:<4} {:<10} {:<5} {:<6}'.format(
                                'Time', 'Cart', 'Az', 'Alt', 'Rot', 'objOff',
                                'guideRot', 'calibOff', 'guideRMS', 'mission'),
                            tags=["b", "cur"])
        self.logWdg1.addMsg("%s" % dashes, tags=["b", "cur"])

        self.logWdg2.addMsg("--- Focus ---", tags=["g", "cur"])

        self.logWdg2.addMsg('{:<5} {:<9} {:<5} {:<4} {:<4} {:<5} {:<6} {:<6}'
                            '{:<5} {:<4} {:<3} {:<4}'.format('Time', 'Cart',
                                                             'Scale', 'M1',
                                                             'M2', 'Focus',
                                                             'Az', 'Alt',
                                                             'Temp', 'Wind',
                                                             'Dir', 'FWHM'),
                            tags=["g", "cur"])
        self.logWdg2.addMsg("%s" % dashes, tags=["g", "cur"])

        self.logWdg3.addMsg("--- Weather ---", tags=["cur"])
        ss = "Time %s Inst    Temp   DP   Dif  Humid Wind Dir Dust,1um IRSC  " \
             "IRSCm FWHM" % (2 * s,)
        self.logWdg3.addMsg("%s" % (ss,), tags=["cur"])
        self.logWdg3.addMsg("%s" % dashes, tags=["cur"])

        self.logWdg4.addMsg("--- Hartmann ---", tags=["cur", "c"])
        ss = "Time    Inst         r1   b1  move1 b1pred Tsp1      r2   b2  " \
             "move2 b2pred Tsp2"
        self.logWdg4.addMsg("%s" % ss, tags=["cur", "c"])
        sline = "%s     %s    %s" % (14 * '-', 28 * "-", 28 * "-")
        self.logWdg4.addMsg("%s" % sline, tags=["cur", "c"])

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
            self.hartInfo = ["?"] * 8

    def hartEnd(self, keyVar):
        if not keyVar.isGenuine:
            return
        if keyVar[0] == self.startHartmannCollimate:
            self.startHartmannCollimate = None
            self.print_hartmann_to_log()

    def print_hartmann_to_log(self):
        tm = self.getTAITimeStr()
        ss1 = "%s %s   " % (tm, self.getCart(self.sr))

        rPiston = self.hartInfo[0]
        bRing = self.hartInfo[2]
        spAvMove = self.hartInfo[4]
        spRes = self.hartInfo[6]
        spTemp = self.bossModel.sp1Temp[0]
        try:
            ss2 = "%5i %5.1f %5i %5.1f %4.1f" % (rPiston, bRing, spAvMove,
                                                 spRes, spTemp)
        except ValueError:
            ss2 = "%5s %5s %5s %5s %4s" % (rPiston, bRing, spAvMove, spRes,
                                           spTemp)

        rPiston = self.hartInfo[1]
        bRing = self.hartInfo[3]
        spAvMove = self.hartInfo[5]
        spRes = self.hartInfo[7]
        spTemp = self.bossModel.sp2Temp[0]
        try:
            ss3 = "%5i %5.1f %5i %5.1f %4.1f" % (rPiston, bRing, spAvMove,
                                                 spRes, spTemp)
        except ValueError:
            ss3 = "%5s %5s %5s %5s %4s" % (rPiston, bRing, spAvMove, spRes,
                                           spTemp)

        self.logWdg4.addMsg("%s  %s    %s" % (ss1, ss2, ss3), tags=["c", "cur"])

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
            self.record(sr, "MaStars")
            self.manga_seq_i = keyVar[1]

    def updateApogeeMangaState(self, keyVar):
        if not keyVar.isGenuine:
            return
        if keyVar[1] != self.ap_manga_seq_i:
            sr = self.sr
            self.record(sr, "MaNGA")
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
        scale = sr.getKeyVar(self.tccModel.scaleFac, ind=0, defVal=1.0)

        az = sr.getKeyVar(self.tccModel.axePos, ind=0, defVal=999)
        alt = sr.getKeyVar(self.tccModel.axePos, ind=1, defVal=99)
        rot = sr.getKeyVar(self.tccModel.axePos, ind=2, defVal=999)
        cart = self.getCart(sr, )

        primOr = self.fInt(sr.getKeyVar(self.tccModel.primOrient, ind=0,
                                        defVal=9999), 5)
        secOr = self.fInt(sr.getKeyVar(self.tccModel.secOrient, ind=0,
                                       defVal=9999), 5)
        secFoc = self.fInt(sr.getKeyVar(self.tccModel.secFocus, ind=0,
                                        defVal=9999), 4)

        def ffsec(n):
            if n is None:
                return "%5s" % "n/a"  # 999.9"
            else:
                return "%5.1f" % (n * 3600)

        def ffsecS(n):
            if n is None:
                return "%4s" % "n/a"
            else:
                return "%4.1f" % (n * 3600)
        # All offsets *3600
        objOff0 = ffsec(RO.CnvUtil.posFromPVT(self.tccModel.objArcOff[0]))
        objOff1 = ffsec(RO.CnvUtil.posFromPVT(self.tccModel.objArcOff[1]))

        guideOff0 = ffsec(RO.CnvUtil.posFromPVT(self.tccModel.guideOff[0]))
        guideOff1 = ffsec(RO.CnvUtil.posFromPVT(self.tccModel.guideOff[1]))
        guideOff2 = ffsec(RO.CnvUtil.posFromPVT(self.tccModel.guideOff[2]))

        calibOff0 = ffsec(RO.CnvUtil.posFromPVT(self.tccModel.calibOff[0]))
        calibOff1 = ffsec(RO.CnvUtil.posFromPVT(self.tccModel.calibOff[1]))
        calibOff2 = ffsecS(RO.CnvUtil.posFromPVT(self.tccModel.calibOff[2]))

        # rotOff = RO.CnvUtil.posFromPVT(self.tccModel.guideOff[2])

        fwhm = sr.getKeyVar(self.guiderModel.seeing, ind=0, defVal=99.9)
        guideRMS = sr.getKeyVar(self.guiderModel.guideRMS, ind=1, defVal=99.999)

        airT = sr.getKeyVar(self.apoModel.airTempPT, ind=0, defVal=-99)
        dir = self.fInt(sr.getKeyVar(self.apoModel.windd, ind=0, defVal=-99), 3)
        wind = self.fInt(sr.getKeyVar(self.apoModel.winds, ind=0, defVal=99), 2)
        dp = sr.getKeyVar(self.apoModel.dpTempPT, ind=0, defVal=-99)
        humid = self.fInt(sr.getKeyVar(self.apoModel.humidPT, ind=0,
                                       defVal=999), 3)
        dustb = self.fInt(sr.getKeyVar(self.apoModel.dustb, ind=0,
                                       defVal=9999), 5)
        #   dustb="%5s" % (sr.getKeyVar(self.apoModel.dustb, ind=0,
        #   defVal="n/a"))

        irsc = sr.getKeyVar(self.apoModel.irscsd, ind=0, defVal=999)
        irscmean = sr.getKeyVar(self.apoModel.irscmean, ind=0, defVal=999)

        at = sr.getKeyVar(self.apoModel.airTempPT, ind=0, defVal=999)
        val = sr.getKeyVar(self.apoModel.dpTempPT, ind=0, defVal=999)
        diff = at - val

        objOffs = "(%3.0f,%3.0f) " % (float(objOff0), float(objOff1))
        calibOffs = "(%2.0f,%2.0f,%2.0f) " % (float(calibOff0),
                                              float(calibOff1),
                                              float(calibOff2))
        self.logWdg1.addMsg('{:<5} {:<9} {:<+6.1f} {:<+6.1f} {:<+6.1f} {:<9}'
                            ' {:<4} {:<10} {:<5} {:<6}'.format(
                                tm, cart, az, alt, rot, objOffs,
                                float(guideOff2), calibOffs, float(guideRMS),
                                atm),
                            tags=["b", "cur"])

        # focus
        self.logWdg2.addMsg('{:<5} {:<9} {:<+5.1f} {:<+4.0f} {:<+4.0f}'
                            ' {:<+5.0f} {:<+6.1f} {:<+6.1f} {:<+5.1f} {:<4.0f}'
                            ' {:<3.0f}'
                            ' {:<4.1f}'.format(tm, cart, (scale-1)*1e6, primOr,
                                               secOr, secFoc, az, alt, airT,
                                               wind, dir, fwhm),
                            tags=["g", "cur"])

        # weather
        ss1 = "%s %s %5.1f %5.1f %5.1f  %s" % (tm, cart, airT, dp, diff, humid,)
        ss2 = "   %s  %s  %s  %5.1f  %4i  %3.1f %s" % (wind, dir, dustb, irsc,
                                                       irscmean, fwhm, atm)
        ss = ss1 + ss2
        self.logWdg3.addMsg("%s " % ss, tags=["cur"])

    def run(self, sr):
        self.record(sr, "")
        self.print_hartmann_to_log()
