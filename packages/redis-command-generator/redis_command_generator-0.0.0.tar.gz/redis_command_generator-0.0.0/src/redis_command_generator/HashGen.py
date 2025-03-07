import redis
import random
from simple_parsing import parse
from dataclasses import dataclass
from redis_command_generator.BaseGen import BaseGen

@dataclass
class HashGen(BaseGen):
    MAX_SUBELEMENTS: int = 10
    SUBKEY_SIZE: int = 5
    SUBVAL_SIZE: int = 5
    INCRBY_MIN: int = -1000
    INCRBY_MAX: int = 1000
    
    def hset(self, pipe: redis.client.Pipeline, key: str = None) -> None:
        # Classification: additive
        if key is None:
            key = self._randKey()
        
        fields = {self._randStr(self.SUBKEY_SIZE): self._randStr(self.SUBVAL_SIZE) for _ in range(random.randint(1, self.MAX_SUBELEMENTS))}
        pipe.hset(key, mapping=fields)
    
    def hincrby(self, pipe: redis.client.Pipeline, key: str = None) -> None:
        # Classification: additive
        if key is None:
            key = self._randKey()
        
        field = self._randStr(self.defKeySize)
        increment = random.randint(self.INCRBY_MIN, self.INCRBY_MAX)
        pipe.hincrby(key, field, increment)
    
    def hdel(self, pipe: redis.client.Pipeline, key: str = None, replaceNonexist: bool = True) -> None:
        # Classification: removal
        redisObj = self._pipeToRedis(pipe)
        
        if key is None or (replaceNonexist and not redisObj.exists(key)):
            key = self._scanRandKey(redisObj, "hash")
        if not key: return
        
        fields = [self._randStr(self.SUBKEY_SIZE) for _ in range(random.randint(1, self.MAX_SUBELEMENTS))]
        pipe.hdel(key, *fields)

if __name__ == "__main__":
    hashGen = parse(HashGen)
    hashGen._runStandalone()
