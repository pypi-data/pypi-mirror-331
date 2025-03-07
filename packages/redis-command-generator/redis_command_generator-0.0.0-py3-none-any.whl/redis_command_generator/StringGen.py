import redis
import random
from simple_parsing import parse
from dataclasses import dataclass
from redis_command_generator.BaseGen import BaseGen

@dataclass
class StringGen(BaseGen):
    SUBVAL_SIZE: int = 5
    INCRBY_MIN: int = -1000
    INCRBY_MAX: int = 1000
    
    def set(self, pipe: redis.client.Pipeline, key: str = None) -> None:
        # Classification: additive
        if key is None:
            key = self._randKey()
        
        pipe.set(key, self._randStr(self.SUBVAL_SIZE))
    
    def append(self, pipe: redis.client.Pipeline, key: str = None) -> None:
        # Classification: additive
        if key is None:
            key = self._randKey()
        
        pipe.append(key, self._randStr(self.SUBVAL_SIZE))
    
    def incrby(self, pipe: redis.client.Pipeline, key: str = None) -> None:
        # Classification: additive
        if key is None:
            key = self._randKey()
        
        pipe.incrby(key, random.randint(self.INCRBY_MIN, self.INCRBY_MAX))
    
    def delete(self, pipe: redis.client.Pipeline, key: str = None, replaceNonexist: bool = True) -> None:
        # Classification: removal
        redisObj = self._pipeToRedis(pipe)
        
        if key is None or (replaceNonexist and not redisObj.exists(key)):
            key = self._scanRandKey(redisObj, "string")
        if not key: return
        
        pipe.delete(key)

if __name__ == "__main__":
    stringGen = parse(StringGen)
    stringGen._runStandalone()

