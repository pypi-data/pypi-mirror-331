import redis
import random
from simple_parsing import parse
from dataclasses import dataclass
from redis_command_generator.BaseGen import BaseGen

GEO_LONG_MIN: float = -180
GEO_LONG_MAX: float = 180
GEO_LAT_MIN : float = -85.05112878
GEO_LAT_MAX : float = 85.05112878

@dataclass
class GeoGen(BaseGen):
    MAX_SUBELEMENTS: int = 10
    SUBVAL_SIZE: int = 5
    
    def geoadd(self, pipe: redis.client.Pipeline, key: str = None) -> None:
        # Classification: additive
        if key is None:
            key = self._randKey()
        
        members = [(random.uniform(GEO_LONG_MIN, GEO_LONG_MAX), random.uniform(GEO_LAT_MIN, GEO_LAT_MAX), self._randStr(self.SUBVAL_SIZE)) for _ in range(random.randint(1, self.MAX_SUBELEMENTS))]
        for lng, lat, member in members:
            pipe.geoadd(key, (lng, lat, member))
    
    def geodel(self, pipe: redis.client.Pipeline, key: str = None, replaceNonexist: bool = True) -> None:
        # Classification: removal
        redisObj = self._pipeToRedis(pipe)
        
        if key is None or (replaceNonexist and not redisObj.exists(key)):
            key = self._scanRandKey(redisObj, "geo")
        if not key: return
        
        members = [self._randStr(self.SUBVAL_SIZE) for _ in range(random.randint(1, self.MAX_SUBELEMENTS))]
        pipe.zrem(key, *members)

if __name__ == "__main__":
    geoGen = parse(GeoGen)
    geoGen._runStandalone()
