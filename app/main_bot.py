from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import Update
from app.config import Settings
from app.di_setup import setup_di
from app.di import di
from app.db.base import Base
from bot.bot_loader import register_handlers
from fastapi import FastAPI
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends, Request
from typing import AsyncGenerator
from seed_data import seed_data

def get_di(request: Request):
    return request.app.state.di

def get_usecases(di = Depends(get_di)):
    return di.get("usecases")

async def get_session(di = Depends(get_di)) -> AsyncGenerator[AsyncSession, None]:
    session_factory = di.get("session_factory")
    async with session_factory() as session:
        yield session


async def init_models(engine):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


def create_app() -> FastAPI:
    config = Settings()

    setup_di(di, config=config)

    bot = Bot(token=config.tg_token)
    dp = Dispatcher(storage=MemoryStorage())
    session_factory = di.get('session_factory')
    register_handlers(dp, session_factory=session_factory)

    dp["config"] = config
    dp["redis"] = di.get("redis")
    dp["usecases"] = di.get("usecases")
    dp["whisper_service"] = di.get("whisper_service")
    dp["model_selection_service"] = di.get("model_selection_service")

    engine = di.get("engine")
    app = FastAPI()
    app.state.di = di

    @app.on_event("startup")
    async def on_startup():
        #await init_models(engine)
        #async with session_factory() as session:
        #    await seed_data(session=session)
        pass

    @app.post("/webhook")
    async def telegram_webhook(update: dict):
        #todo: remove try
        try:
            await dp.feed_update(bot, Update.model_validate(update))
        except Exception as e:
            print(e)
            return 200


    @app.post("/payconfirm")
    async def pay_confirm(request: Request,
                          usecases=Depends(get_usecases),
                          session: AsyncSession = Depends(get_session),):
        data = await request.json()
        await usecases.handle_payment.handle_payment(data=data, session=session)
        return {"status": "ok"}

    return app

app = create_app()