import aiohttp
import asyncio

async def main():
    client = aiohttp.ClientSession()

    response = await client.post(
        "http://127.0.0.1:8080/advertisements",
        json={"title": "advertisements_1", "description": "description_1", "owner": "user_1"},
        headers={"token": "123456"}
    )

    print(response.status)
    print(await response.text())

    await client.close()

asyncio.run(main())