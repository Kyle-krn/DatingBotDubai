from datetime import datetime
from typing import Tuple
import aiohttp
import urllib.parse
from timezonefinder import TimezoneFinder
from pytz import timezone
from data import config


tf = TimezoneFinder()


async def get_location_by_city(place: str) -> Tuple[str, list, int]:
    """Поиск лоакции по названию города, отдает - полное название локации, координаты центра города и разница в часах с UTC0"""
    place = urllib.parse.quote(place)
    params = {'access_token': config.MAPBOX_TOKEN, 
              'proximity': 'ip',
              'types': ','.join(['country', 'place'])}
    async with aiohttp.request('GET', f"https://api.mapbox.com/geocoding/v5/mapbox.places/{str(place)}.json", params=params) as response:
        resp_city = await response.json()
    try:
        center_city = resp_city['features'][0]['center']
        tmz = timezone(tf.timezone_at(lng=center_city[0], lat=center_city[1]))
        tmz = int(tmz.utcoffset(datetime.now()).total_seconds() / 60 / 60)
        return resp_city['features'][0]['place_name'], center_city, tmz 
    except IndexError:
        return None, None, None


async def get_location_by_lat_long(lat: float, long: float) -> Tuple[str, list, int]:
    """Поиск лоакции по названию геолокации, отдает - полное название локации, координаты центра города и разница в часах с UTC0"""
    params = {'access_token': config.MAPBOX_TOKEN}
    async with aiohttp.request('GET', f"https://api.mapbox.com/geocoding/v5/mapbox.places/{long},{lat}.json", params=params) as response:
        resp_city = await response.json()
    try:
        place = ", ".join([i['text'] for i in resp_city['features'][0]['context'] if not i['text'].isdigit()])
        center_city = resp_city['features'][0]['center']
        tmz = timezone(tf.timezone_at(lng=center_city[0], lat=center_city[1]))
        tmz = int(tmz.utcoffset(datetime.now()).total_seconds() / 60 / 60)
        return place, center_city, tmz 
    except IndexError:
        return None, None, None



    