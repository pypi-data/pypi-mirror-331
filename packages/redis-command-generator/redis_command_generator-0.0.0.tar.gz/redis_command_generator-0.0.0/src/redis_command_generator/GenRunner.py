import threading
import copy
import sys
from simple_parsing import parse
from dataclasses import dataclass
from redis_command_generator.BaseGen import MemoryCapReachedException
from redis_command_generator.AllDTGen import *

def createTypeGen(baseClasses):
    return type('TypeGen', baseClasses, {})

def instTypeGen(objWithArgs, classType):
    classObj = copy.deepcopy(objWithArgs)
    classObj.__class__ = classType
    return classObj

def stringsToClasses(classnames):
    classes = []
    for name in classnames:
        classes.append(getattr(sys.modules[__name__], name))
    
    return classes

# Append thread number to logfile name
def renameLog(logfile, threadNum):
    if logfile is None:
        return None
    
    logfile = logfile.split(".")
    return f"{logfile[0]}_t{threadNum}.{logfile[1]}"

@dataclass
class allDTGenT(AllDTGen):
    numThreads: int = 3
    includeGens: tuple = ("SetGen", "ZSetGen", "StringGen", "StreamGen", "ListGen", "HyperLogLogGen", "HashGen", "GeoGen", "BitmapGen")
    excludeGens: tuple = ()

class GenRunner():
    def __init__(self):
        self.threads = []
        self.events = []
    
    def __enter__(self):
        return self
    
    def start(self, args):
        genNames = [gen for gen in args.includeGens if gen not in args.excludeGens]
        genTypes = stringsToClasses(genNames)
        TypeGen = createTypeGen(tuple(genTypes))
        
        genList = []
        for i in range(args.numThreads):
            # Create a new instance of the generated class with cmd line args
            genInst = instTypeGen(args, TypeGen)
            genInst.logfile = renameLog(args.logfile, i)
            genList.append(genInst)
            
            self.events.append(threading.Event())
            t = threading.Thread(target=(genInst._runStandalone), args=(self.events[i],))
            self.threads.append(t)
            
            try:
                t.start()
            except MemoryCapReachedException:
                pass

    def join(self):
        for t in self.threads:
            t.join()

    def __exit__(self, exc_type, exc_value, traceback):
        for e in self.events:
            e.set()
        self.join()

if __name__ == "__main__":
    args = parse(allDTGenT)
    
    genRunner = GenRunner()
    genRunner.start(args)