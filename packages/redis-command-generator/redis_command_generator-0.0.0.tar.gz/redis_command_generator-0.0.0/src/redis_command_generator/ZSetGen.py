import redis
import random
from simple_parsing import parse
from dataclasses import dataclass
from redis_command_generator.BaseGen import BaseGen

@dataclass
class ZSetGen(BaseGen):
    MAX_SUBELEMENTS: int = 10
    SUBVAL_SIZE: int = 5
    
    def zadd(self, pipe: redis.client.Pipeline, key: str = None) -> None:
        # Classification: additive
        if key is None:
            key = self._randKey()
        
        members = {self._randStr(self.SUBVAL_SIZE): random.random() for _ in range(random.randint(1, self.MAX_SUBELEMENTS))}
        pipe.zadd(key, mapping=members)
    
    def zincrby(self, pipe: redis.client.Pipeline, key: str = None) -> None:
        # Classification: additive
        if key is None:
            key = self._randKey()
        
        member = self._randStr(self.SUBVAL_SIZE)
        increment = random.random()
        pipe.zincrby(key, increment, member)
    
    def zrem(self, pipe: redis.client.Pipeline, key: str = None, replaceNonexist: bool = True) -> None:
        # Classification: removal
        redisObj = self._pipeToRedis(pipe)
        
        if key is None or (replaceNonexist and not redisObj.exists(key)):
            key = self._scanRandKey(redisObj, "zset")
        if not key: return
        
        members = [self._randStr(self.SUBVAL_SIZE) for _ in range(random.randint(1, self.MAX_SUBELEMENTS))]
        pipe.zrem(key, *members)

if __name__ == "__main__":
    zsetGen = parse(ZSetGen)
    zsetGen._runStandalone()
