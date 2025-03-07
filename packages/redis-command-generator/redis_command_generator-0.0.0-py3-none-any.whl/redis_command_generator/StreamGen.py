import redis
import random
from simple_parsing import parse
from dataclasses import dataclass
from redis_command_generator.BaseGen import BaseGen

@dataclass
class StreamGen(BaseGen):
    MAX_SUBELEMENTS: int = 10
    SUBKEY_SIZE: int = 5
    SUBVAL_SIZE: int = 5
    
    def xadd(self, pipe: redis.client.Pipeline, key: str = None) -> None:
        # Classification: additive
        if key is None:
            key = self._randKey()
        
        fields = {self._randStr(self.SUBKEY_SIZE): self._randStr(self.SUBVAL_SIZE) for _ in range(random.randint(1, self.MAX_SUBELEMENTS))}
        pipe.xadd(key, fields)
    
    def xdel(self, pipe: redis.client.Pipeline, key: str = None, replaceNonexist: bool = True) -> None:
        # Classification: removal
        redisObj = self._pipeToRedis(pipe)
        
        if key is None or (replaceNonexist and not redisObj.exists(key)):
            key = self._scanRandKey(redisObj, "stream")
        if not key: return
        
        streamLen = random.randint(0, 10)
        if streamLen > 0:
            stream_id = f"{random.randint(1, 1000)}-0"
            pipe.xdel(key, stream_id)

if __name__ == "__main__":
    streamGen = parse(StreamGen)
    streamGen._runStandalone()
