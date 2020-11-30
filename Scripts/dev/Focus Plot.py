"""A combination of the scale error and focus error plots, based on the
    axisError script. It was inspired by the business of the guide monitor,
    which was too hard to read and borderline useless, as well as a discontent
    with how the scale monitor shows scale error, but the focus monitor shows
    net offset, which is inconsistent.

History:
2020-07-27  DG  Init, based on the focusPlotWdg and a little guideMonitor2
"""

import Tkinter

# import datetime
# import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import sys
from matplotlib.backends.backend_tkagg import FigureCanvasTk

import RO.Constants
import RO.StringUtil
import TUI.Base.StripChartWdg
import TUI.Models
import TUI.TUIMenu.DownloadsWindow
from TUI.Inst.Guide import GuideImage

__version__ = '3.0.0'

_HelpURL = "Instruments/FocusPlotWin.html"


class ScriptClass(object, Tkinter.Frame):
    def __init__(self, sr, **kargs):
        Tkinter.Frame.__init__(self, sr.master, **kargs)
        print('---Focus Monitor, Version {}---'.format(__version__))
        self.sr = sr
        print(dir(sr))
        self.tk = sr.master
        self.sr.debug = False
        self.sr.master.winfo_toplevel().wm_resizable(True, True)
        self.guider_model = TUI.Models.getModel('guider')
        self.tcc_model = TUI.Models.getModel('tcc')
        self.tui_model = TUI.Models.getModel('tui')
        self.ftpSaveToPref = self.tui_model.prefs.getPrefVar("Save To")
        downloadTL = self.tui_model.tlSet.getToplevel(
            TUI.TUIMenu.DownloadsWindow.WindowName)
        self.downloadWdg = downloadTL and downloadTL.getWdg()

        # width = 2
        # height = 2
        self.fig = plt.figure()
        self.figCanvas = FigureCanvasTk(self.fig, self)
        self.figCanvas.show()
        self.plot_ax = self.fig.add_subplot(1, 1, 1)
        self.plot_ax.grid(axis='both')

        self.guider_model.file.addCallback(self.updatePlot)

    def updatePlot(self, keyVar):
        if not keyVar.isCurrent or not keyVar.isGenuine:
            return 0
        image_dir, image_name = keyVar.valueList[0:2]
        if image_dir[-1] != "/" and image_name[0] != "/":
            print("Warning: hacked around broken guider.files keyword")
            image_name = image_dir + "/" + image_name
        else:
            image_name = image_dir + image_name

        # create new object data
        localBaseDir = self.ftpSaveToPref.getValue()
        imObj = GuideImage.GuideImage(
            localBaseDir=localBaseDir,
            imageName=image_name,
            downloadWdg=self.downloadWdg,
            fetchCallFunc=self.plot,
        )
        self.plot(imObj)

    def getFITSObj(self, imObj):
        """Get pyfits fits object, or None if the file is not a usable version
        of a GPROC file
        """
        fitsObj = imObj.getFITSObj()
        try:
            sdss_fmt_str = fitsObj[0].header["SDSSFMT"]
        except Exception:
            self.sr.setMsg("No SDSSFMT header entry",
                           severity=RO.Constants.sevWarning, isTemp=True)
            return None

        try:
            formatName, versMajStr, versMinStr = sdss_fmt_str.split()
            int(versMajStr)
            int(versMinStr)
        except Exception:
            self.sr.setMsg("Could not parse SDSSFMT=%r" % (sdss_fmt_str,),
                           severity=RO.Constants.sevWarning, isTemp=True)
            return None

        if formatName.lower() != "gproc":
            self.sr.setMsg(
                "SDSSFMT = %s != gproc" % (formatName.lower(),),
                severity=RO.Constants.sevWarning, isTemp=True)
            return None

        self.sr.clearTempMsg()
        return fitsObj

    def plot(self, imObj):
        """Show plot for a new image; clear if imObj is None or has no plate
         info.
        """
        #        print "FocusPlotWdg.plot(imObj=%s)" % (imObj,)
        self.clear()
        if imObj is None:
            return

        try:
            fitsObj = self.getFITSObj(imObj)
            if fitsObj is None:
                return
        except Exception as e:
            sys.stderr.write("FocusPlotWdg: could not get FITS object: {}\n"
                             "".format(RO.StringUtil.strFromException(e)))
            return
        try:
            probeData = fitsObj[6].data
            numProbes = len(probeData)
            isGoodArr = probeData.field("exists") & probeData.field(
                "enabled") & np.isfinite(probeData.field("fwhm"))
            if len(isGoodArr) == 0:
                return
            focusOffsetArr = np.extract(isGoodArr,
                                        probeData.field("focusOffset"))
            fwhmArr = np.extract(isGoodArr, probeData.field("fwhm"))
            probeNumberArr = np.extract(isGoodArr,
                                        np.arange(1, numProbes + 1, dtype=int))
        except Exception as e:
            sys.stderr.write(
                "FocusPlotWdg could not parse data in image {}: {}\n"
                "".format(imObj.imageName, RO.StringUtil.strFromException(e)))
            return

        self.plot_ax.plot(focusOffsetArr, fwhmArr, color='black',
                          linestyle="", marker='o', label="probe")

        # add probe numbers
        for focusOffset, fwhm, probeNumber in zip(focusOffsetArr, fwhmArr,
                                                  probeNumberArr):
            self.plot_ax.annotate("%s" % (probeNumber,),
                                  (focusOffset, fwhm), xytext=(5, -5),
                                  textcoords="offset points")

        # add invisible 0,0 point to force autoscale to include origin
        self.plot_ax.plot([0.0], [0.0], linestyle="", marker="")

        # fit data and show the fit
        fitArrays = self.fitFocus(focusOffsetArr, fwhmArr, fitsObj)
        if fitArrays is not None:
            self.plot_ax.plot(fitArrays[0], fitArrays[1], color='blue',
                              linestyle="-", label="best fit")

        # add seeing
        try:
            seeingStr = fitsObj[0].header["SEEING"]
            seeing = float(seeingStr)
        except Exception:
            seeing = np.nan
        if np.isfinite(seeing):
            self.plot_ax.plot([0.0], [seeing], linestyle="", marker="x",
                              markersize=12,
                              color="green", markeredgewidth=1,
                              label="seeing")

        self.plot_ax.set_title(imObj.imageName)

        legend = self.plot_ax.legend(loc=4, numpoints=1)
        legend.draw_frame(False)

        # self.figCanvas.draw()

    def fitFocus(self, focusOffsetArr, fwhmArr, fitsObj, nPoints=50):
        """Fit a line to rms^2 - focus offset^2 vs. focus offset

        (after converting to suitable units)

        Inputs:
        - focusOffsetArr: array of focus offset values (um)
        - fwhmArr: array of FWHM values (arcsec)
        - nPoints: number of points desired in the returned fit arrays

        Returns [newFocusOffArr, fitFWHMArr] if the fit succeeds; None otherwise
        """
        if len(focusOffsetArr) < 2:
            self.sr.setMsg("Cannot fit data: too few data points",
                           severity=RO.Constants.sevWarning, isTemp=True)
            return None
        if min(focusOffsetArr) == max(focusOffsetArr):
            self.sr.setMsg("Cannot fit data: no focus offset range",
                           severity=RO.Constants.sevWarning, isTemp=True)
            return None
        try:
            plateScale = float(fitsObj[0].header["PLATSCAL"])

            focalRatio = 5.0
            C = 5.0 / (32.0 * focalRatio ** 2)

            # compute RMS in microns
            # RMS = FWHM / 2.35, but FWHM is in arcsec
            # plateScale is in mm/deg
            micronsPerArcsec = plateScale * 1.0e3 / 3600.0
            rmsArr = fwhmArr * (micronsPerArcsec / 2.35)  # in microns

            yArr = rmsArr ** 2 - (C * focusOffsetArr ** 2)

            fitCoeff = np.polyfit(focusOffsetArr, yArr, 1)

            fitFocusOffsetArr = np.linspace(min(focusOffsetArr),
                                            max(focusOffsetArr), nPoints)
            fitYArr = (fitFocusOffsetArr * fitCoeff[0]) + fitCoeff[1]
            fitRMSSqArr = fitYArr + (C * fitFocusOffsetArr ** 2)

            fitFWHM = np.sqrt(fitRMSSqArr) * (2.35 / micronsPerArcsec)

            return [fitFocusOffsetArr, fitFWHM]
        except Exception as e:
            self.sr.setMsg(
                "Cannot fit data: %s" % (RO.StringUtil.strFromException(e),),
                severity=RO.Constants.sevWarning, isTemp=True)
            return None

    def clear(self):
        self.plot_ax.clear()
        self.plot_ax.grid(True)
        # start with autoscale disabled due to bug in matplotlib
        self.plot_ax.set_autoscale_on(True)
        self.plot_ax.set_xlabel("Guide probe focus offset (um)")
        self.plot_ax.set_ylabel("Guide star FWHM (arcsec)")
        # self.figCanvas.draw()

    def run(self, sr):
        pass

    def end(self, sr):
        pass
