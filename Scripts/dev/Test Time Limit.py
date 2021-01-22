#!/usr/bin/env python

from TUI import Models


class ScriptClass:
    def __init__(self, sr):
        self.sr = sr
        self.tcc_model = Models.getModel('tcc')

    def run(self, sr):
        yield self.sr.waitCmd(actor="tcc", cmdStr="axis status",
                              keyVars=[self.tccModel.altStat,
                                       self.tccModel.axePos],
                              timeLim=2)

    def end(self):
        pass