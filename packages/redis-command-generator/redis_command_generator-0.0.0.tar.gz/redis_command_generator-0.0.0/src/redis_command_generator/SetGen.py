import redis
import random
from simple_parsing import parse
from dataclasses import dataclass
from redis_command_generator.BaseGen import BaseGen

@dataclass
class SetGen(BaseGen):
    MAX_SUBELEMENTS: int = 10
    SUBVAL_SIZE: int = 5
    
    def sadd(self, pipe: redis.client.Pipeline, key: str = None) -> None:
        # Classification: additive
        if key is None:
            key = self._randKey()
        
        members = [self._randStr(self.SUBVAL_SIZE) for _ in range(random.randint(1, self.MAX_SUBELEMENTS))]
        pipe.sadd(key, *members)
    
    def srem(self, pipe: redis.client.Pipeline, key: str = None, replaceNonexist: bool = True) -> None:
        # Classification: removal
        redisObj = self._pipeToRedis(pipe)
        
        if key is None or (replaceNonexist and not redisObj.exists(key)):
            key = self._scanRandKey(redisObj, "set")
        if not key: return
        
        member = redisObj.srandmember(key)
        if not member: return
        
        pipe.srem(key, member)

if __name__ == "__main__":
    setGen = parse(SetGen)
    setGen._runStandalone()