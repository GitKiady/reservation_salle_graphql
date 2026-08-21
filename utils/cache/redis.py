
from datetime import datetime, timedelta
from typing import List

from utils.cache.redis_config import Redis


r = Redis()

# KEYS[1]: bkrm:{room_id}
# ARGV[1]: start_booking
# ARGV[2]: end_booking
SCRIPT_LUA = """
local start_bk = tonumber(ARGV[1])
local end_bk = tonumber(ARGV[2])

local reservation = redis.call('LRANGE', KEYS[1], 0, -1)
for i = 1, #reservation - 1, 2 do
    local start = tonumber(reservation[i])
    local finish = tonumber(reservation[i+1])

    if start == start_bk and end == end_bk then
        return "Créneau déjà réservé."
    end
    if start < start_bk and start_bk < end_bk or  then
        return "La date de début est en conflit avec d'autre réservations."
    end
    if start < end_bk and end_bk < finish then
        return "La date de fin est en conflit avec d'autre réservations."
    end
    if start == start_bk and end <= end_bk then
        return "La date de début est en conflit avec d'autre réservations."
    end
    if start <= start_bk and end == end_bk then
        return "La date de fin est en conflit avec d'autre réservations."
    end
end

redis.call('RPUSH', KEYS[1], start_bk)
redis.call('RPUSH', KEYS[1], end_bk)

return "OK"
"""

attemp_booking = r.register_script(SCRIPT_LUA)

def cle_booking(room_id: int) -> str:
    # bkrm: Booking Room
    return f"bkrm:{room_id}" 

async def try_to_book(room_id: int, start: datetime, end: datetime) -> str:
    return await attemp_booking(
        keys=[cle_booking(room_id, start)],
        args=[start.timestamp(), end.timestamp()]
    )

async def get_booking(room_id: int) -> dict:
    return await r.get(cle_booking(room_id))


async def del_booking(room_id: int, start_date: datetime, end_date: datetime) -> bool:
    # Appeler par cancel si le booking n'est pas confirmé ou après que la date est dépassé
    cle = cle_booking(room_id)
    rm_start = await r.lrem(cle, 1, start_date.timestamp())
    rm_end = await r.lrem(cle, 1, end_date.timestamp())

    if rm_start and rm_end:
        return 1

    return 0
