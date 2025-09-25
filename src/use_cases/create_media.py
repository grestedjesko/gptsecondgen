from bot.keyboards.keyboards import Keyboard
from sqlalchemy.ext.asyncio import AsyncSession
from aiogram.types import User
from src.services.i18n_service import I18nService


class CreateMediaUseCase:
    def __init__(self, keyboard: Keyboard):
        self.keyboard = keyboard

    async def main_menu(self, session: AsyncSession, user: User):
        text = await I18nService.get_text("create_media_title", user, session)
        kbd = await self.keyboard.create_media_keyboard(user, session) 
        return text, kbd

    async def image_menu(self, session: AsyncSession, user: User):
        text = await I18nService.get_text("create_image_title", user, session)
        kbd = await self.keyboard.create_image_keyboard(user, session) 
        return text, kbd

    async def video_menu(self, session: AsyncSession, user: User):
        text = await I18nService.get_text("create_video_title", user, session)
        kbd = await self.keyboard.create_video_keyboard(user, session) 
        return text, kbd    