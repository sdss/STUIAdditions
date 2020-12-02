# TEST THE hartEnd LINES TO ADD THE '[MaNGA] hartmanns: ' INFO.

import time

import RO.Astro.Tm
import RO.Wdg
import TUI.Models


class ScriptClass(object):
    def __init__(self, sr):
        sr.debug = False  # If True, run in debug-only mode. If False, run in real time.
        self.sr = sr
        self.name = "-ExpForLog-"
        width = 80
        height = 5

        # Create resizeable window 1.
        sr.master.winfo_toplevel().wm_resizable(True, True)

        # Create three log windows: one each for eBOSS, MaNGA, APOGEE.
        self.logWdg1 = RO.Wdg.LogWdg(master=sr.master, width=width,
                                     height=height,
                                     helpText="eBOSS")
        self.logWdg1.grid(row=0, column=0, sticky="news")

        self.logWdg2 = RO.Wdg.LogWdg(master=sr.master, width=width,
                                     height=height,
                                     helpText="MaNGA", relief="sunken", bd=2)
        self.logWdg2.grid(row=1, column=0, sticky="news")

        self.logWdg3 = RO.Wdg.LogWdg(master=sr.master, width=width,
                                     height=height,
                                     helpText="APOGEE", relief="sunken", bd=2)
        self.logWdg3.grid(row=2, column=0, sticky="news")

        # Format the three log windows into three equally-sized rows within the window.
        sr.master.rowconfigure(0, weight=1)
        sr.master.rowconfigure(1, weight=1)
        sr.master.rowconfigure(2, weight=1)
        sr.master.columnconfigure(0, weight=1)

        # Set font size and type, and then specify text color.
        fs = "12"
        ft = "Monaco"
        self.logWdg1.text.tag_config("cur", font=(ft, fs))
        self.logWdg2.text.tag_config("cur", font=(ft, fs))
        self.logWdg3.text.tag_config("cur", font=(ft, fs))
        self.logWdg1.text.tag_config("b", foreground="darkblue")
        self.logWdg2.text.tag_config("g", foreground="darkgreen")
        self.logWdg3.text.tag_config("c", foreground="brown")

        # Titles of the logs.
        self.logWdg1.addMsg("--- eBOSS ---\n", tags=["b", "cur"])
        self.logWdg2.addMsg("--- MaNGA-led ---\n", tags=["g", "cur"])
        self.logWdg3.addMsg("--- APOGEE-led ---\n", tags=["c", "cur"])

        # Connect to actors in order to get keywords.
        self.guiderModel = TUI.Models.getModel("guider")
        self.sopModel = TUI.Models.getModel("sop")
        self.hartmannModel = TUI.Models.getModel("hartmann")
        self.bossModel = TUI.Models.getModel("boss")
        self.apogeeModel = TUI.Models.getModel("apogee")
        self.cmdsModel = TUI.Models.getModel("cmds")
        self.mcpModel = TUI.Models.getModel("mcp")

        # Initialize some variables.
        self.survey = ''
        self.surveyLead = ''
        self.loadCart = ''
        self.expState = ''
        self.apogeeState = ''
        self.gotoFieldState = ''

        # Specify desired guider keywords and set survey variables before the call for the survey keyword.
        self.guiderModel.cartridgeLoaded.addCallback(self.updateLoadCart,
                                                     callNow=True)
        self.guiderModel.survey.addCallback(self.guideSurveyFun, callNow=True)

        # sop
        self.sopModel.gotoFieldState.addCallback(self.updateGotoField,
                                                 callNow=False)
        #  self.sopModel.gotoFieldStages.addCallback(self.updateGtfStagesFun,callNow=True)
        #  self.sopModel.doCalibsState.addCallback(self.updateCalStateFun,callNow=True)
        #  self.sopModel.doScienceState.addCallback(self.updateSciStateFun,callNow=True)

        # Specify desired boss keywords.
        self.bossModel.exposureState.addCallback(self.updateBossState,
                                                 callNow=True)

        # Add APOGEE callback for exposureWroteSummary.
        self.apogeeModel.exposureWroteSummary.addCallback(
            self.updateApogeeExpos, callNow=True)
        #        self.apogeeModel.exposureState.addCallback(self.updateApogeeExpos, callNow = True)

        # Collimator motor positions.
        self.motPos = [
            sr.getKeyVar(self.bossModel.motorPosition, ind=i, defVal=None)
            for i in range(0, 6)]
        self.bossModel.motorPosition.addCallback(self.motorPosition,
                                                 callNow=True)

        # For hartmann info, need cmdsModel.
        self.startHartmannCollimate = None
        self.cmdsModel.CmdQueued.addCallback(self.hartStart, callNow=False)
        self.cmdsModel.CmdDone.addCallback(self.hartEnd, callNow=False)

        # dict() is a type of variable - looks like array but instead of calling by index you call by name.
        self.resid = dict()
        self.avrMove = dict()
        self.rPistonMove = dict()
        self.bRingMove = dict()
        self.rMeanOffset = dict()
        self.bMeanOffset = dict()

        self.spNumList = ("1", "2")
        for spNum in self.spNumList:
            residKey = getattr(self.hartmannModel, "sp%sResiduals" % (spNum))

            def residProxy(residKey, spNum=spNum):
                self.residCallback(spNum, residKey)

            residKey.addCallback(residProxy, callNow=False)

            moveKey = getattr(self.hartmannModel, "sp%sAverageMove" % (spNum))

            def moveProxy(moveKey, spNum=spNum):
                self.moveCallback(spNum, moveKey)

            moveKey.addCallback(moveProxy, callNow=False)

            rPiston = getattr(self.hartmannModel, "r%sPistonMove" % (spNum))

            def rProxy(rPiston, spNum=spNum):
                self.rPistonCallback(spNum, rPiston)

            rPiston.addCallback(rProxy, callNow=False)

            bRing = getattr(self.hartmannModel, "b%sRingMove" % (spNum))

            def bProxy(bRing, spNum=spNum):
                self.bRingCallback(spNum, bRing)

            bRing.addCallback(bProxy, callNow=False)

            rOffset = getattr(self.hartmannModel, "r%sMeanOffset" % (spNum))

            def rOffsetProxy(rOffset, spNum=spNum):
                self.rOffsetCallback(spNum, rOffset)

            rOffset.addCallback(rOffsetProxy, callNow=False)

            bOffset = getattr(self.hartmannModel, "b%sMeanOffset" % (spNum))

            def bOffsetProxy(bOffset, spNum=spNum):
                self.bOffsetCallback(spNum, bOffset)

            bOffset.addCallback(bOffsetProxy, callNow=False)

    def residCallback(self, spNum, keyVar):
        # Callback for <spName>Residuals keyword.
        if not keyVar.isGenuine: return
        self.resid[spNum] = keyVar[0:3]

    def moveCallback(self, spNum, keyVar):
        # Callback for hartmann.sp%sAverageMove keyword.
        if not keyVar.isGenuine: return
        self.avrMove[spNum] = keyVar[0]

    def rPistonCallback(self, spNum, keyVar):
        if not keyVar.isGenuine: return
        self.rPistonMove[spNum] = keyVar[0]

    def bRingCallback(self, spNum, keyVar):
        if not keyVar.isGenuine: return
        self.bRingMove[spNum] = keyVar[0]

    def rOffsetCallback(self, spNum, keyVar):
        if not keyVar.isGenuine: return
        self.rMeanOffset[spNum] = keyVar[1]

    def bOffsetCallback(self, spNum, keyVar):
        if not keyVar.isGenuine: return
        self.bMeanOffset[spNum] = keyVar[1]

    def hartStart(self, keyVar):
        if not keyVar.isGenuine: return
        self.q1 = (keyVar[4] == "hartmann") and ("collimate" in keyVar[6])
        self.q2 = (keyVar[4] == "sop") and (keyVar[6] == "collimateBoss")
        if self.q1 or self.q2:
            self.startHartmannCollimate = keyVar[0]
            self.resid["1"] = self.resid["2"] = ["?", "?", "?"]
            self.avrMove["1"] = self.avrMove["2"] = "?"
            self.rPistonMove["1"] = self.rPistonMove["2"] = "?"
            self.bRingMove["1"] = self.bRingMove["2"] = "?"
            self.rMeanOffset["1"] = self.rMeanOffset["2"] = "?"
            self.bMeanOffset["1"] = self.bMeanOffset["2"] = "?"
        return

        # Look for cmdsModel.CmdDone keyword and compare the index of cmd with previously saved index for hartmann.

    def hartEnd(self, keyVar):
        if not keyVar.isGenuine: return
        if keyVar[0] == self.startHartmannCollimate:  # Right command number.
            self.startHartmannCollimate = None  # Remove flag, index=None.
            ssTime = "%s" % (self.getTAITimeStr())
            cart = self.guiderModel.cartridgeLoaded[0]
            survey = self.guiderModel.survey[0]
            surveyLead = self.guiderModel.survey[1]
            #            ss0 = "[MaNGA] hartmanns:"
            ss = "  %s Hartmann analysis for cartridge %s:" % (ssTime, cart)
            if "MaNGA" in survey:
                #                self.logWdg2.addMsg(ss0, tags = "c")
                #                self.logWdg2.addMsg("%s" % (95*""))
                self.logWdg2.addMsg(ss, tags="c")
                for spNum in self.spNumList:
                    rPiston = self.rPistonMove[spNum]
                    rStr = self.rMeanOffset[spNum]
                    bRing = self.bRingMove[spNum]
                    bStr = self.bMeanOffset[spNum]
                    self.logWdg2.addMsg(
                        "    sp%s offset: r = %s steps (%s);  b = %s deg (%s) " % \
                        (spNum, rPiston, rStr, bRing, bStr), tags="c")
                for spNum in self.spNumList:
                    self.logWdg2.addMsg(
                        "    sp%s pred. move: spAverageMove = %s steps" % \
                        (spNum, self.avrMove[spNum]), tags="c")
                for spNum in self.spNumList:
                    spRes = self.resid[spNum]
                    spTemp = getattr(self.bossModel, "sp%sTemp" % (spNum))
                    ss = "pred. residual: r = %s steps, b = %s deg, spTemp = %s C" % \
                         (spRes[0], spRes[1], spTemp[0])
                    self.logWdg2.addMsg("    sp%s %s" % (spNum, ss), tags="c")
            else:
                self.logWdg1.addMsg(ss, tags="c")
                for spNum in self.spNumList:
                    rPiston = self.rPistonMove[spNum]
                    rStr = self.rMeanOffset[spNum]
                    bRing = self.bRingMove[spNum]
                    bStr = self.bMeanOffset[spNum]
                    self.logWdg1.addMsg(
                        "    sp%s offset: r = %s steps (%s);  b = %s deg (%s) " % \
                        (spNum, rPiston, rStr, bRing, bStr), tags="c")
                for spNum in self.spNumList:
                    self.logWdg1.addMsg(
                        "    sp%s pred. move: spAverageMove = %s steps" % \
                        (spNum, self.avrMove[spNum]), tags="c")
                for spNum in self.spNumList:
                    spRes = self.resid[spNum]
                    spTemp = getattr(self.bossModel, "sp%sTemp" % (spNum))
                    ss = "pred. residual: r = %s steps, b = %s deg, spTemp = %s C" % \
                         (spRes[0], spRes[1], spTemp[0])
                    self.logWdg1.addMsg("    sp%s %s" % (spNum, ss), tags="c")
            if (keyVar[1] != ":") and (
                    "MaNGA" in survey):  # If command finished with status of fail.
                self.logWdg2.addMsg("  Hartmann failed.", severity=self.redWarn)
            if (keyVar[1] != ":") and (
                    "eBOSS" in survey):  # If command finished with status of fail.
                self.logWdg1.addMsg("  Hartmann failed.", severity=self.redWarn)
            return

    def motorPosition(self, keyVar):
        if not keyVar.isGenuine: return
        if keyVar == self.motPos:
            return
        sr = self.sr
        timeStr = self.getTAITimeStr()
        sname = "  %s,  %s" % (self.name, timeStr)
        survey = self.guiderModel.survey[0]
        surveyLead = self.guiderModel.survey[1]
        mv = [0] * 6
        for i in range(0, 6):
            try:
                mv[i] = keyVar[i] - self.motPos[i]
            except Exception:
                mv[i] = None
        if mv[0:3] != [0] * 3:
            ss = "  %s  sp1.motor.move= %s, %s, %s" % (
            timeStr, mv[0], mv[1], mv[2])
            if "MaNGA" in survey:
                self.logWdg2.addMsg("%s" % ss, tags="c")
            else:
                self.logWdg1.addMsg("%s" % ss, tags="c")
        if mv[3:6] != [0] * 3:
            ss = "  %s  sp2.motor.move= %s, %s, %s" % (
            timeStr, mv[3], mv[4], mv[5])
            if "MaNGA" in survey:
                self.logWdg2.addMsg("%s" % ss, tags="c")
            else:
                self.logWdg1.addMsg("%s" % ss, tags="c")
        self.motPos = list(self.bossModel.motorPosition[0:6])

    def getTAITimeStr(self):
        currPythonSeconds = RO.Astro.Tm.getCurrPySec()
        currTAITuple = time.gmtime(
            currPythonSeconds - RO.Astro.Tm.getUTCMinusTAI())
        self.taiTimeStr = time.strftime("%H:%M:%S", currTAITuple)
        return self.taiTimeStr

    def getTAITimeStrDate(self):
        currPythonSeconds = RO.Astro.Tm.getCurrPySec()
        currTAITuple = time.gmtime(
            currPythonSeconds - RO.Astro.Tm.getUTCMinusTAI())
        self.taiTimeStr = time.strftime("%M:%D:%Y,  %H:%M:%S", currTAITuple)
        return self.taiTimeStr

    # Update APOGEE exposure and print exposure info to the APOGEE-led log window.
    def updateApogeeExpos(self, keyVar):
        if not keyVar.isGenuine: return
        if keyVar[0] != self.apogeeState:
            timeStr = self.getTAITimeStr()
            self.apogeeState = keyVar[0]
            #            if self.apogeeState == "Exposing":
            dd0 = self.apogeeModel.utrReadState[0]
            #                dd3 = self.apogeeModel.exposureState[2]
            dd3 = self.apogeeModel.utrReadState[3]
            dth = self.apogeeModel.ditherPosition[1]
            exptp = self.apogeeModel.exposureState[1]
            ss = "  %s  apogee exposure %s, expName=%s, nReads=%s, dither=%s" % (
            timeStr, exptp, dd0, dd3, dth)
            self.logWdg3.addMsg("%s" % (ss), tags="c")

    # Update BOSS exposure and print appropriate info to the appropriate log window.
    def updateBossState(self,
                        keyVar):  # keyVar is equal to the bossModel.exposureState keyword.
        if not keyVar.isGenuine: return  # Exclude stale keyword value.
        timeStr = self.getTAITimeStr()
        if keyVar[
            0] != self.expState:  # If keyword is different (something has changed) then proceed.
            self.expState = keyVar[0]
            expTime = keyVar[1]
            expId = int(self.bossModel.exposureId[0]) + 2
            if self.expState == "INTEGRATING":  # This is valid for biases, too: exposureState=INTEGRATING,0.0,0.0
                survey = self.guiderModel.survey[0]
                surveyLead = self.guiderModel.survey[1]
                if "MaNGA" in survey:
                    mangaDith = self.guiderModel.mangaDither[0]
                    if self.mcpModel.ffLamp[0] == 1:
                        ss = "  %s  boss exposure flat, expNum=%i, expTime=%s" % (
                        timeStr, expId, expTime)
                        self.logWdg2.addMsg("%s " % (ss), tags="g")
                    elif self.mcpModel.hgCdLamp[0] == 1:
                        ss = "  %s  boss exposure  arc, expNum=%i, expTime=%s" % (
                        timeStr, expId, expTime)
                        self.logWdg2.addMsg("%s " % (ss), tags="g")
                    elif expTime == 900.0:
                        ss = "  %s  boss exposure science, expNum=%i, expTime=%s" % (
                        timeStr, expId, expTime)
                        self.logWdg2.addMsg("%s, %s" % (ss, mangaDith),
                                            tags="g")
                    elif expTime == 0.:
                        ss = "  %s  boss exposure bias, expNum=%i, expTime=%s" % (
                        timeStr, expId, expTime)
                        self.logWdg2.addMsg("%s " % (ss), tags="g")
                    else:
                        ss = "  %s  boss exposure dark, expNum=%i, expTime=%s" % (
                        timeStr, expId, expTime)
                        self.logWdg2.addMsg("%s " % (ss), tags="g")

                else:
                    if self.mcpModel.ffLamp[0] == 1:
                        ss = "  %s  boss exposure flat, expNum=%i, expTime=%s" % (
                        timeStr, expId, expTime)
                        self.logWdg1.addMsg("%s " % (ss), tags="b")
                    elif self.mcpModel.hgCdLamp[0] == 1:
                        ss = "  %s  boss exposure  arc, expNum=%i, expTime=%s" % (
                        timeStr, expId, expTime)
                        self.logWdg1.addMsg("%s " % (ss), tags="b")
                    elif expTime == 900.0:
                        ss = "  %s  boss exposure science, expNum=%i, expTime=%s" % (
                        timeStr, expId, expTime)
                        self.logWdg1.addMsg("%s " % (ss), tags="b")
                    elif expTime == 0.:
                        ss = "  %s  boss exposure bias, expNum=%i, expTime=%s" % (
                        timeStr, expId, expTime)
                        self.logWdg2.addMsg("%s " % (ss), tags="b")
                    else:
                        ss = "  %s  boss exposure dark, expNum=%i, expTime=%s" % (
                        timeStr, expId, expTime)
                        self.logWdg2.addMsg("%s " % (ss), tags="b")
        return None

    # Update cartridge and plate based on loadCartridge.
    def updateLoadCart(self, keyVar):
        if not keyVar.isGenuine: return
        ct = keyVar[0]  # Parse the cartridge number from keyVar.
        pl = keyVar[1]  # Parse the plate number from keyVar.
        sd = keyVar[
            2]  # Parse the side ('A' or 'B'; obsolete - MARVELS) from keyVar.
        if [ct, pl, sd] != self.loadCart:
            self.updateLoadCartOutput()
            self.loadCart = [ct, pl,
                             sd]  # Update self.loadCart with new cartridge, plate, side.
            self.survey = ''
            self.surveyLead = ''
        else:  # If cartridge, plate, side is same as keyVar, no update needed and just move on.
            pass

    # Print new cartridge and plate info into the appropriate log window.
    def updateLoadCartOutput(self):
        ll = self.guiderModel.cartridgeLoaded
        ct = ll[0]
        pl = ll[1]
        timeStr = self.getTAITimeStr()
        ss = "Cartridge: %s Plate: %s" % (str(ct), str(pl))
        if ct > 9:
            self.logWdg1.addMsg("%s" % (95 * "*"))
            self.logWdg1.addMsg("%s" % ss)
        else:
            self.logWdg2.addMsg("%s" % (95 * "*"))
            self.logWdg2.addMsg("%s" % ss)
            self.logWdg3.addMsg("%s" % (95 * "*"))
            self.logWdg3.addMsg("%s" % ss)

    def guideSurveyFun(self, keyVar):
        if not keyVar.isGenuine: return
        if (self.survey != keyVar[0]) or (self.surveyLead != keyVar[1]):
            self.survey = keyVar[0]
            self.surveyLead = keyVar[1]
            self.guideSurveyPrint()
        else:
            pass

    def guideSurveyPrint(self):
        timeStr = self.getTAITimeStr()
        ss = "Survey: %s Survey Lead: %s" % (self.survey, self.surveyLead)
        if "MaNGA" in self.survey:
            self.logWdg2.addMsg("%s" % ss)
            self.logWdg2.addMsg("%s" % (95 * ""))
        if "APOGEE" in self.survey:
            self.logWdg3.addMsg("%s" % ss)
            self.logWdg3.addMsg("%s" % (95 * ""))
        else:
            self.logWdg1.addMsg("%s" % ss)
            self.logWdg1.addMsg("%s" % (95 * ""))

    def updateGotoField(self, keyVar):
        if not keyVar.isGenuine: return
        if keyVar[0] != self.gotoFieldState:
            timeStr = self.getTAITimeStr()
            if keyVar[0] == 'running':
                if "MaNGA" in self.survey:
                    self.logWdg2.addMsg(
                        "%sZ - gotoField. noGSOGTF. Clear. Seeing:  FWHM" % (
                            timeStr))
                    self.logWdg2.addMsg("%s" % (95 * ""))
                if "APOGEE" in self.survey:
                    self.logWdg3.addMsg(
                        "%sZ - gotoField. noGSOGTF. Clear. Seeing:  FWHM" % (
                            timeStr))
                    self.logWdg3.addMsg("%s" % (95 * ""))
                else:
                    self.logWdg1.addMsg(
                        "%sZ - gotoField. noGSOGTF. Clear. Seeing:  FWHM" % (
                            timeStr))
                    self.logWdg1.addMsg("%s" % (95 * ""))
            #            if keyVar[0] == 'failed':
            #                if "MaNGA" in self.survey:
            #                    self.logWdg2.addMsg("%s - gotoField FAILED." % (timeStr))
            #                    self.logWdg2.addMsg("%s" % (95*""))
            #                if "APOGEE" in self.survey:
            #                    self.logWdg3.addMsg("%s - gotoField FAILED." % (timeStr))
            #                    self.logWdg3.addMsg("%s" % (95*""))
            #                else:
            #                    self.logWdg1.addMsg("%s - gotoField FAILED." % (timeStr))
            #                    self.logWdg1.addMsg("%s" % (95*""))
            self.gotoFieldState = keyVar[0]

    def run(self, sr):
        self.updateLoadCartOutput()
        self.guideSurveyPrint()
