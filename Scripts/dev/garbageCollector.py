import gc
import pprint


class ScriptClass(object, ):
    def __init__(self, sr):
        print('Garbage:')
        pprint.pprint(gc.garbage)

    @staticmethod
    def run(sr):
        gc.collect()
        pprint.pprint(gc.garbage)
