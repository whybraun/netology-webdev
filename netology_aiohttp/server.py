import json
from sqlalchemy.exc import IntegrityError
from aiohttp import web
from models import Session, Advertisements, engine, init_orm

app = web.Application()

@web.middleware
async def session_middleware(request, handler):
    async with Session() as session:
        request.session = session
        response = await handler(request)
        return response

async def orm_context(app):
    print("START")
    await init_orm()
    yield
    print("FINISH")
    await engine.dispose()

app.cleanup_ctx.append(orm_context)
app.middlewares.append(session_middleware)

def get_error(error_class, message):
    return error_class(
        text=json.dumps(
            {"error": message}
        ),
        content_type="application/json"
    )

async def get_advertisements_by_id(session, advertisements_id):
    advertisements = await session.get(Advertisements, advertisements_id)
    if advertisements is None:
        raise get_error(web.HTTPNotFound, message=f"User with id {advertisements_id} not found")
    return advertisements

async def add_advertisements(session, advertisements):
    try:
        await session.add(advertisements)
        await session.commit()
    except IntegrityError:
        raise get_error(web.HTTPConflict, message=f"Advertisement with id {advertisements.id} already exists")

class AdvertisementsView(web.View):

    @property
    def advertisements_id(self):
        return int(self.request.match_info['advertisements_id'])
    
    def session_id(self) -> Session:
        return self.request.session
    
    async def get_advertisements(self):
        advertisements = await get_advertisements_by_id(self.session, self.advertisements_id)
        return advertisements
    
    async def get(self):
        advertisements = await self.get_advertisements()
        return web.json_response(advertisements.dict)

    async def post(self):
        advertisements_data = await self.request.json()
        advertisements = Advertisements(**advertisements_data)
        await add_advertisements(self.session, advertisements)
        return web.json_response({'id': advertisements.id})

    async def patch(self):
        advertisements_data = await self.request.json()
        advertisements = await self.get_advertisements()

        for key, value in advertisements_data.items():
            setattr(advertisements, key, value)
        await add_advertisements(self.session, advertisements)
        return web.json_response(advertisements.dict)
            
    async def delete(self):
        advertisements = await self.get_advertisements()
        await self.session.delete(advertisements)
        await self.session.commit()
        return web.json_response({'status': 'deleted'})

app.add_routes(
    [
        web.get('/advertisements/{advertisements_id:\d+}', AdvertisementsView),
        web.patch('/advertisements/{advertisements_id:\d+}', AdvertisementsView),
        web.delete('/advertisements/{advertisements_id:\d+}', AdvertisementsView),
        web.post('/advertisements/', AdvertisementsView),
    ]
)

web.run_app(app, port=8080)