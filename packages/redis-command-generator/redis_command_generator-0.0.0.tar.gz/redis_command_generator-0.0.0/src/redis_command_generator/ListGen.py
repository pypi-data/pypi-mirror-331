import redis
import random
from simple_parsing import parse
from dataclasses import dataclass
from redis_command_generator.BaseGen import BaseGen

@dataclass
class ListGen(BaseGen):
    MAX_SUBELEMENTS: int = 10
    SUBVAL_SIZE: int = 5
    
    def lpush(self, pipe: redis.client.Pipeline, key: str = None) -> None:
        # Classification: additive
        if key is None:
            key = self._randKey()
        
        items = [self._randStr(self.SUBVAL_SIZE) for _ in range(random.randint(1, self.MAX_SUBELEMENTS))]
        pipe.lpush(key, *items)
    
    def rpush(self, pipe: redis.client.Pipeline, key: str = None) -> None:
        # Classification: additive
        if key is None:
            key = self._randKey()
        
        items = [self._randStr(self.SUBVAL_SIZE) for _ in range(random.randint(1, self.MAX_SUBELEMENTS))]
        pipe.rpush(key, *items)
    
    def lpop(self, pipe: redis.client.Pipeline, key: str = None, replaceNonexist: bool = True) -> None:
        # Classification: removal
        redisObj = self._pipeToRedis(pipe)
        
        if key is None or (replaceNonexist and not redisObj.exists(key)):
            key = self._scanRandKey(redisObj, "list")
        if not key: return
        
        pipe.lpop(key)
    
    def rpop(self, pipe: redis.client.Pipeline, key: str = None, replaceNonexist: bool = True) -> None:
        # Classification: removal
        redisObj = self._pipeToRedis(pipe)
        
        if key is None or (replaceNonexist and not redisObj.exists(key)):
            key = self._scanRandKey(redisObj, "list")
        if not key: return
        
        pipe.rpop(key)
    
    def lrem(self, pipe: redis.client.Pipeline, key: str = None, replaceNonexist: bool = True) -> None:
        # Classification: removal
        redisObj = self._pipeToRedis(pipe)
        
        if key is None or (replaceNonexist and not redisObj.exists(key)):
            key = self._scanRandKey(redisObj, "list")
        if not key: return
        
        listLength = redisObj.llen(key)
        if not listLength: return
        
        randIndex = random.randint(0, listLength - 1)
        item = redisObj.lindex(key, randIndex)
        if not item: return
        
        pipe.lrem(key, 0, item)

if __name__ == "__main__":
    listGen = parse(ListGen)
    listGen._runStandalone()
