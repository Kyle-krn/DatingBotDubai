from datetime import datetime, date
import aiohttp
import urllib.parse
import asyncio
from pprint import PrettyPrinter
# x = requests.get("https://api.mapbox.com/geocoding/v5/mapbox.places/Los%20Angeles.json?access_token=pk.eyJ1IjoiZWdvcmtlZTk2IiwiYSI6ImNsMmc1cmFxdzAwcmYzYnFlbjZ4Y2NoaGkifQ.oWKr0o_oAp2QDbNAILJRVQ")

from timezonefinder import TimezoneFinder
from pytz import timezone, utc

tf = TimezoneFinder()
# latitude, longitude = 52.5061, 13.358

# pp = PrettyPrinter(indent=4)

async def get_location_by_city(place: str):
    place = urllib.parse.quote(place)
    params = {'access_token': 'pk.eyJ1IjoiZWdvcmtlZTk2IiwiYSI6ImNsMmc1cmFxdzAwcmYzYnFlbjZ4Y2NoaGkifQ.oWKr0o_oAp2QDbNAILJRVQ', 'proximity': 'ip',
              'types': ','.join(['country', 'place'])}
    async with aiohttp.request('GET', f"https://api.mapbox.com/geocoding/v5/mapbox.places/{str(place)}.json", params=params) as response:
        resp_city = await response.json()
        # pp.pprint(resp_city)
    try:
        center_city = resp_city['features'][0]['center']
        tmz = timezone(tf.timezone_at(lng=center_city[0], lat=center_city[1]))
        tmz = int(tmz.utcoffset(datetime.now()).total_seconds() / 60 / 60)
        return resp_city['features'][0]['place_name'], center_city, tmz 
    except IndexError:
        return None, None, None


async def get_location_by_lat_long(lat: float, long: float):
    # place = urllib.parse.quote(place)
    params = {'access_token': 'pk.eyJ1IjoiZWdvcmtlZTk2IiwiYSI6ImNsMmc1cmFxdzAwcmYzYnFlbjZ4Y2NoaGkifQ.oWKr0o_oAp2QDbNAILJRVQ', 
              }
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



        
# x, geo, tmz = asyncio.run(get_location_by_city("Дубаи"))
# x, geo, tmz = asyncio.run(get_location_by_lat_long(55.2962, 25.2684))
# print(geo)
# tz = timezone('America/New_York')
# x = int(tz.utcoffset(datetime.now()).total_seconds() / 60 / 60)
# print(x)
# x = asyncio.run(get_location_by_city("Dubai"))
# print(x)
# print(date.today())