#!/usr/bin/env python
"""Seeing monitor

History:
2012-04-23 Elena Malanushenko, converted from a script to a window by Russell Owen
2012-06-04 ROwen    Fix clear button.
2015-11-03 ROwen    Replace "== None" with "is None" and "!= None" with "is not None" to modernize 
    the code.
"""
import Tkinter
import datetime
import sys
import os
import RO.Wdg
import TUI.Base.StripChartWdg
import TUI.Models
import numpy as np
import matplotlib as mpl


WindowName = "---Flux Monitor 2---"
class Data:
    def __init__(self):
        pass


class HidePrints:
    '''Hides print statements of other functions when called using with. This is very useful when
    you're using an RO backend that has tons of handled errors that are printed.
    
    Usage:
        with HiddenPrints():
            buggy_function()
            print('This will not print')
        
        print('This will still print')
    
    '''
    def __enter__(self):
        self._original_stdout = sys.stdout
        sys.stdout = open(os.devnull, 'w')

    def __exit__(self, exc_type, exc_val, exc_tb):
        sys.stdout.close()
        sys.stdout = self._original_stdout


class ScriptClass(object, ):
    def __init__(self, sr, ):
        sr.debug = False
        self.sr = sr
        self.name = WindowName
        print self.name, datetime.datetime.now()
        timeRange = 3600
        width = 8
        height = 2.4
        self.data = Data()
        self.data.t = [mpl.dates.date2num(datetime.datetime.now())]
        self.data.f = [[0]*17]
        # A possibly futile attempt to prevent this plot from spewing the world
        # with unwanted prints of errors that don't matter.
        # TclError: bad window path name
        with HidePrints():
            self.plot_widget = TUI.Base.StripChartWdg.StripChartWdg(master=sr.master,
                    timeRange=timeRange, numSubplots=1, width=width, height=height,
                    cnvTimeFunc=TUI.Base.StripChartWdg.TimeConverter(useUTC=True),)
        
        self.plot_widget.grid(row=0, column=0, sticky='nwes')
        self.plot_widget.grid_rowconfigure(0, weight=1)
        self.plot_widget.grid_columnconfigure(0, weight=1)
        self.plot_widget.xaxis.set_major_locator(mpl.dates.MinuteLocator(
            byminute=range(0, 61, 10)))
        self.ax = self.plot_widget.figure.gca()
        # self.sr.master.winfo_toplevel().wm_resizable(True, True)
        
        self.guiderModel = TUI.Models.getModel("guider")
        # print('guiderModel probe')
        # print(self.guiderModel.probe[7])
        # print(dir(self.guiderModel.probe))
        self.guiderModel.probe.addCallback(self.append_data, callNow=True)
        self.guiderModel.probe.addCallback(self.plot_data, callNow=True)
        # the default ticks are not nice, so be explicit
        # print(dir(self.plot_widget))

    def fluxFun(self, modelFlux):
        focOff = self.guiderModel.probe[6]
        if focOff == None:
            # ignore out-of-focus probes
            return np.nan
        # print('modelFlux')
        # print(modelFlux)
        expTime = self.guiderModel.expTime[0]
        if expTime == None:
            return np.nan
        return modelFlux/expTime

        # self.plot_widget.plotKeyVar(
        #     label = "Model Flux",
        #     subplotInd = 0,
        #     keyVar = self.guiderModel.probe,
        #     keyInd = 7,
        #     func = fluxFun,
        #     color = "green",
        # )
        # self.plot_widget.showY(0.0, 1.0, subplotInd=0)
        # self.plot_widget.subplotArr[0].yaxis.set_label_text("Model Flux (ADU/sec)")

        # self.clearWdg = RO.Wdg.Button(master = self, text = "C", callFunc = self.clearCharts)
        # self.clearWdg.grid(row=0, column=0, sticky = "sw")
 
    def append_data(self, keyVar):
        if not keyVar.isGenuine:
            return
        if len(self.data.f[-1]) == 17:
            self.data.f.append([])
            self.data.t.append(mpl.dates.date2num(datetime.datetime.now()))
            print 'appending', keyVar[7]
            self.data.f[-1].append(self.fluxFun(keyVar[7]))

    def plot_data(self, keyVar):
        '''Plots TimexN datasets where the data is in self.data.{x,y}'''
        if len(self.data.f[-1]) == 17:
            print('plotting')
            x = np.array(self.data.t)
            y = np.array(self.data.f)
            print(x)
            print(y)
            print(x.shape)
            self.ax.plot_date(x, y)
        else:
            print('not plotting')

    def clearCharts(self, wdg=None):
        """Clear all strip charts
        """
        self.plot_widget.clear()

    def run(self, sr):
        pass
    def end(self, sr):
        pass



# def addWindow(tlSet):
#     """Create the window for TUI.
#     """
#     tlSet.createToplevel(
#         name = WindowName,
#         defGeom = "+412+44",
#         visible = False,
#         resizable = True,
#         wdgFunc = FluxMonitorWdg,
#     )
# 
# class FluxMonitorWdg(Tkinter.Frame):
#     def __init__(self, master, timeRange=3600, width=8, height=2.4):
#         """Create a FluxMonitorWdg
#         
#         Inputs:
#         - master: parent Tk widget
#         - timeRange: range of time displayed (seconds)
#         - width: width of plot (inches)
#         - height: height of plot (inches)
#         """
#         Tkinter.Frame.__init__(self, master)
#         self.guiderModel = TUI.Models.getModel("guider")
#         
#         self.stripChartWdg = TUI.Base.StripChartWdg.StripChartWdg(
#             master = self,
#             timeRange = timeRange,
#             numSubplots = 1, 
#             width = width,
#             height = height,
#             cnvTimeFunc = TUI.Base.StripChartWdg.TimeConverter(useUTC=True),
#         )
#         self.stripChartWdg.grid(row=0, column=0, sticky="nwes")
#         self.grid_rowconfigure(0, weight=1)
#         self.grid_columnconfigure(0, weight=1)
# 
#         # the default ticks are not nice, so be explicit
#         self.stripChartWdg.xaxis.set_major_locator(matplotlib.dates.MinuteLocator(byminute=range(0, 61, 10)))
# 
#         subplotInd = 0
# 
#         def fluxFun(modelFlux):
#             focOff = self.guiderModel.probe[6]
#             if focOff == None:
#                 # ignore out-of-focus probes
#                 return None
# 
#             expTime = self.guiderModel.expTime[0]
#             if expTime == None:
#                 return None
#             return modelFlux/expTime
# 
#         self.stripChartWdg.plotKeyVar(
#             label = "Model Flux",
#             subplotInd = subplotInd,
#             keyVar = self.guiderModel.probe,
#             keyInd = 7,
#             func = fluxFun,
#             color = "green",
#         )
#         self.stripChartWdg.showY(0.0, 1.0, subplotInd=0)
#         self.stripChartWdg.subplotArr[0].yaxis.set_label_text("Model Flux (ADU/sec)")
# 
#         self.clearWdg = RO.Wdg.Button(master = self, text = "C", callFunc = self.clearCharts)
#         self.clearWdg.grid(row=0, column=0, sticky = "sw")
#     
#     def clearCharts(self, wdg=None):
#         """Clear all strip charts
#         """
#         self.stripChartWdg.clear()
# 
# 
# if __name__ == "__main__":
#     import TestData
# 
#     addWindow(TestData.tuiModel.tlSet)
#     TestData.tuiModel.tlSet.makeVisible(WindowName)
# 
#     # there isn't any flux data yet    
# #    TestData.runTest()
#     
#     TestData.tuiModel.reactor.run()
