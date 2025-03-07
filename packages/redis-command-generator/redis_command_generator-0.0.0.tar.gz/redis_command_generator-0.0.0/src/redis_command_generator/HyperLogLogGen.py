import redis
import random
from simple_parsing import parse
from dataclasses import dataclass
from redis_command_generator.BaseGen import BaseGen

@dataclass
class HyperLogLogGen(BaseGen):
    MAX_SUBELEMENTS: int = 10
    
    def pfadd(self, pipe: redis.client.Pipeline, key: str = None) -> None:
        # Classification: additive
        if key is None:
            key = self._randKey()
        
        elements = [self._randStr(self.defKeySize) for _ in range(random.randint(1, self.MAX_SUBELEMENTS))]
        pipe.pfadd(key, *elements)
    
    def pfmerge(self, pipe: redis.client.Pipeline, key: str = None, replaceNonexist: bool = True) -> None:
        # Classification: removal
        redisObj = self._pipeToRedis(pipe)
        
        if key is None or (replaceNonexist and not redisObj.exists(key)):
            key = self._scanRandKey(redisObj, "hyperloglog")
        if not key: return
        
        sourceKeys = [self._randKey() for _ in range(random.randint(1, self.MAX_SUBELEMENTS))]
        pipe.pfmerge(key, *sourceKeys)

if __name__ == "__main__":
    hyperLogLogGen = parse(HyperLogLogGen)
    hyperLogLogGen._runStandalone()
