

import RO.Wdg
import TUI.Base.StripChartWdg
import TUI.Models
import numpy as np
import matplotlib as mpl
import sys
sys.path.append('/Users/dylangatlin/python/')
import starcoder42 as s

class ScriptClass(object, ):
    def __init__(self, sr):
        sr.debug = False
        self.sr = sr
        print('Model Flux Test')
        self.guider_model = TUI.Models.getModel('guider')
        print('model flux')
        model_flux = self.guider_model.probe[7]
        s.describe(model_flux, print_it=True)
        
        print('model mag')
        model_mag = self.guider_model.probe[8]
        s.describe(model_mag, print_it=True)

        print('ref mag')
        ref_mag = self.guider_model.probe[9]
        s.describe(ref_mag, print_it=True)
    def run(self, sr):
        pass
    def end(self, sr):
        pass

