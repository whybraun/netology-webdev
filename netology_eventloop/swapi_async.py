import datetime
import aiohttp
import asyncio
from more_itertools import chunked
from models import init_db, SwapiPeople, Session, engine


MAX_CHUNK = 10

async def fetch_and_join_data(client, urls, key):
    tasks = [fetch_data(client, url, key) for url in urls]
    results = await asyncio.gather(*tasks) 
    return ', '.join(results)


async def fetch_data(client, url, key):
    response = await client.get(url)
    data = await response.json()
    return data.get(key, '')


async def get_person(client, person_id):
    http_response = await client.get(f"https://swapi.dev/api/people/{person_id}")
    json_result = await http_response.json()

    tasks = []

    if 'homeworld' in json_result:
        tasks.append(fetch_data(client, json_result['homeworld'], 'name'))
    
    for i in ['films', 'vehicles', 'starships', 'species']:
        if i in json_result:
            tasks.append(fetch_and_join_data(client, json_result[i], 'title' if i == 'films' else 'name'))
    results = await asyncio.gather(*tasks)

    for key, result in zip(['homeworld', 'films', 'vehicles','starships','species'], results):
        if key in json_result:
            json_result[key] = result

    return json_result


async def insert_to_db(list_of_jsons):
    async with Session() as session:
        for json_item in list_of_jsons:
            person = SwapiPeople(
                birth_year=json_item.get('birth_year', ''),
                eye_color=json_item.get('eye_color', ''),
                films=json_item.get('films', ''),
                gender=json_item.get('gender', ''),
                hair_color=json_item.get('hair_color', ''),
                height=json_item.get('height', ''),
                homeworld=json_item.get('homeworld', ''),
                mass=json_item.get('mass', ''),
                name=json_item.get('name', ''),
                skin_color=json_item.get('skin_color', ''),
                species=json_item.get('species', ''),
                starships=json_item.get('starships', ''),
                vehicles=json_item.get('vehicles', '')
            )
            session.add(person)
        await session.commit()
        

async def main():
    await init_db()
    client = aiohttp.ClientSession()
    
    for chunk in chunked(range(1, 100), MAX_CHUNK):
        coros = [get_person(client, person_id) for person_id in chunk]
        result = await asyncio.gather(*coros)
        asyncio.create_task(insert_to_db(result))

    tasks_set = asyncio.all_tasks() - {asyncio.current_task()}
    await asyncio.gather(*tasks_set)
    
    await client.close()
    await engine.dispose()


if __name__ == '__main__':
    start = datetime.datetime.now()
    asyncio.run(main())
    print(datetime.datetime.now() - start)
