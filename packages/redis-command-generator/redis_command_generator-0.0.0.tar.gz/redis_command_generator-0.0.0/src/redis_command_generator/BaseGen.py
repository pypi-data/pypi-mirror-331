import redis
import random
import string
import threading
from typing import Callable, List
from simple_parsing import parse
from dataclasses import dataclass, field
from contextlib import contextmanager

class MemoryCapReachedException(Exception):
    pass

@contextmanager
def exception_wrapper():
    try:
        yield
    except redis.exceptions.ResponseError as e:
        if ("WRONGTYPE" not in str(e)) and (not ("INCRBY" in str(e) and "value is not an integer or out of range" in str(e))):
            raise e

class RedisObj():
    def __init__(self, *args, **kwargs):
        self._client = redis.Redis(*args, **kwargs)

    def __getattr__(self, name):
        original_attr = getattr(self._client, name)

        if callable(original_attr):
            def wrapper(*args, **kwargs):
                with exception_wrapper():
                    return original_attr(*args, **kwargs)
            return wrapper
        else:
            return original_attr

@dataclass
class BaseGen():
    verbose: bool = False  # Print debug information (sent commands)
    quite: bool = False  # Suppress response-related exception prints
    hosts: tuple = ("localhost:6379",)  # Redis hosts to connect to (when running as standalone)
    flush: bool = False  # Flush all hosts on connection (when running as standalone)
    maxCmdCnt: int = 1000  # Maximum number of commands to execute, may be interuppted by exceeding memory cap
    memCap: float = 70  # Memory cap percentage
    pipeEveryX: int = 500  # Execute pipeline every X commands
    defKeySize: int = 3  # Default key size
    defKeyPref: str = '' # Default key prefix
    excludeCmds: tuple = ()  # Commands to exclude from random selection
    logfile: str = None  # Optional log file path to write debug information to
    MAXMEMORY: int = None
    PRINT_PREFIX: str = "COMMAND GENERATOR: "
    
    TTL_LOW: int = 15
    TTL_HIGH: int = 300

    def __post_init__(self):
        self.scanCursors = {}

    def _randStr(self, strSize: int) -> str:
        return "".join(random.choices(string.ascii_letters + string.digits, k = strSize))
    
    def _randKey(self) -> str:
        return self.defKeyPref + self._randStr(self.defKeySize)
    
    def _scanRandKey(self, redisObj: redis.Redis, type: str) -> str | None:
        conn = self._getConnInfo(redisObj)
        if conn not in self.scanCursors:
            self.scanCursors[conn] = {}
        
        if type not in self.scanCursors[conn]:
            self.scanCursors[conn][type] = 0
        
        oldCursor = self.scanCursors[conn][type]
        cursor, keys = redisObj.scan(self.scanCursors[conn][type], _type=type)
        self.scanCursors[conn][type] = cursor
        ret = random.choice(keys) if keys else None
        self._print(f"type: {type}, ret: {ret}")
        self._print(f"old cursor: {oldCursor}, new cursor: {self.scanCursors[conn][type]}")
        
        return ret
    
    def _getRandCmd(self) -> Callable[[redis.client.Pipeline, str], None]:
        methodNames = [name for name in dir(self) if callable(getattr(self, name)) and not name.startswith('_') and name not in self.excludeCmds]
        name = random.choice(methodNames)
        return getattr(self, name)
    
    def _checkMemCap(self, redisObj: redis.Redis):
        info = redisObj.info()
        
        if self.MAXMEMORY:
            maxMem = self.MAXMEMORY
        else:
            maxMem = info['maxmemory'] if ('maxmemory' in info) else None
        
        currMem = info['used_memory']
        
        if maxMem and currMem >= (self.memCap / 100) * maxMem:
            eStr = f"Memory cap for {self._getConnInfo(redisObj)} reached, with {currMem} bytes used out of {maxMem * (self.memCap / 100)} available"
            raise MemoryCapReachedException(eStr)
    
    def _getConnInfo(self, redisObj: redis.Redis) -> str:
        return f"{redisObj.connection_pool.connection_kwargs['host']}:{redisObj.connection_pool.connection_kwargs['port']}"
    
    def _pipeToRedis(self, pipe: redis.client.Pipeline) -> RedisObj:
        redobj = redis.Redis(connection_pool=pipe.connection_pool)
        rcobj = RedisObj(connection_pool=pipe.connection_pool)
        return rcobj
    
    def _print(self, msg: str) -> None:
        if self.file:
            self.file.write(f"{msg}\n")
        
        if self.verbose:
            print(self.PRINT_PREFIX + msg)

    def _printPipelineCommands(self, pipe: redis.client.Pipeline) -> None:
        for command in pipe.command_stack:
            self._print(f"Command: {command[0]}")
    
    def _runStandalone(self, stopEvent: threading.Event = None) -> None:
        self.file = open(self.logfile, 'w') if self.logfile else None
        
        rl = []
        try:
            for host in self.hosts:
                (hostname, port) = host.split(':')
                rl.append(redis.Redis(host=hostname, port=port))
                rl[-1].ping()
                self._print("INFO: " + str(rl[-1].info()))
                if self.flush:
                    rl[-1].flushall()
            
            redisPipes = [r.pipeline(transaction=False) for r in rl]
            
            for i in range(1, self.maxCmdCnt + 1):
                self._print(f"i = {i}")
                if stopEvent and stopEvent.is_set():
                    break
                
                key = self._randKey()
                cmd = self._getRandCmd()
                
                for pipe in redisPipes:
                    cmd(pipe, key)

                if i % self.pipeEveryX == 0:
                    for (pipe, r) in zip(redisPipes, rl):
                        self._print(f"Executing pipeline for {self._getConnInfo(r)}")
                        self._printPipelineCommands(pipe)
                        
                        with exception_wrapper():
                            pipe.execute()
                        
                        self._checkMemCap(r)
        except Exception as e:
            self._print(f"Exception: {e}")
            raise e
        finally:
            for r in rl:
                self._print("Connection: " + self._getConnInfo(r))
                self._print("Memmory usage: " + str(r.info()['used_memory']))
                self._print("DB size: " + str(r.dbsize()))
                r.close()
            self.file.close() if self.file else None
    
    def expire(self, pipe: redis.client.Pipeline, key: str = None, replaceNonexist: bool = True) -> None:
        redisObj = self._pipeToRedis(pipe)
        
        if (key is None) or (replaceNonexist and not redisObj.exists(key)):
            key = redisObj.randomkey()
        if not key: return
        
        pipe.expire(key, random.randrange(self.TTL_LOW, self.TTL_HIGH))
    
    def persist(self, pipe: redis.client.Pipeline, key: str = None, replaceNonexist: bool = True) -> None:
        redisObj = self._pipeToRedis(pipe)
        
        if (key is None) or (replaceNonexist and not redisObj.exists(key)):
            key = redisObj.randomkey()
        if not key: return
        
        pipe.persist(key)

if __name__ == "__main__":
    baseGen = parse(BaseGen)
    baseGen._runStandalone()