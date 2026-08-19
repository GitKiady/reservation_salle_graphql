
from datetime import datetime

from utils.cache.redis_config import Redis


r = Redis()

# KEYS[1]: bkrm:{room_id}
# ARGV[1]: start date en timestamp
# ARGV[2]: expiration time en seconde
SCRIPT_LUA = """
if redis.call('EXISTS', KEYS[1]) == 1 then
    return 0
else
    redis.call('SET', 'KEYS[1]', '1', 'EX', 'ARGV[2]')
    return 1
end
"""

attemp_booking = r.register_script(SCRIPT_LUA)

def cle_booking(room_id: int, start: datetime) -> str:
    # bkrm: Booking Room
    return f"bkrm:{room_id}:{start}" 

async def try_to_book(room_id: int, start: datetime, end: datetime) -> bool:
    expiration = (end.timestamp - start.timestamp)
    return await attemp_booking(
        keys=[cle_booking(room_id, start)],
        args=[start.timestamp, expiration]
    )

async def get_booking(room_id: int) -> dict:
    return await r.get(cle_booking(room_id))
