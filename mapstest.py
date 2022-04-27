import aiohttp
import urllib.parse
import asyncio

# x = requests.get("https://api.mapbox.com/geocoding/v5/mapbox.places/Los%20Angeles.json?access_token=pk.eyJ1IjoiZWdvcmtlZTk2IiwiYSI6ImNsMmc1cmFxdzAwcmYzYnFlbjZ4Y2NoaGkifQ.oWKr0o_oAp2QDbNAILJRVQ")

async def get_location(place: str):
    place = urllib.parse.quote(place)
    params = {'access_token': 'pk.eyJ1IjoiZWdvcmtlZTk2IiwiYSI6ImNsMmc1cmFxdzAwcmYzYnFlbjZ4Y2NoaGkifQ.oWKr0o_oAp2QDbNAILJRVQ'}
    async with aiohttp.request('GET', f"https://api.mapbox.com/geocoding/v5/mapbox.places/{str(place)}.json", params=params) as response:
        resp_city = await response.json()
    try:
        print(resp_city['features'][0])
    except IndexError:
        print("город не найден")

asyncio.run(get_location('Москва'))
print('\n')
asyncio.run(get_location('Moscow'))
print('\n')
asyncio.run(get_location('JDFhhjrgijerlvegheruiv'))
