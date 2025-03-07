import redis
import random
from simple_parsing import parse
from dataclasses import dataclass
from redis_command_generator.BaseGen import BaseGen

@dataclass
class BitmapGen(BaseGen):
    MAX_SUBELEMENTS: int = 1000
    
    def setbit(self, pipe: redis.client.Pipeline, key: str = None) -> None:
        # Classification: additive
        if key is None:
            key = self._randKey()
        
        offset = random.randint(0, self.MAX_SUBELEMENTS)
        value = random.randint(0, 1)
        pipe.setbit(key, offset, value)
    
    def getbit(self, pipe: redis.client.Pipeline, key: str = None, replaceNonexist: bool = True) -> None:
        # Classification: removal
        redisObj = self._pipeToRedis(pipe)
        
        if key is None or (replaceNonexist and not redisObj.exists(key)):
            key = self._scanRandKey(redisObj, "bitmap")
        if not key: return
        
        offset = random.randint(0, self.MAX_SUBELEMENTS)
        pipe.getbit(key, offset)

if __name__ == "__main__":
    bitmapGen = parse(BitmapGen)
    bitmapGen._runStandalone()
