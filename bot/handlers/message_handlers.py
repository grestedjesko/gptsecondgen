from aiogram import Router, F, Bot
from sqlalchemy.ext.asyncio import AsyncSession
from aiogram.types import Message, ContentType
from src.use_cases.usecases import UseCases
from aiogram.utils.chat_action import ChatActionSender

message_router = Router()


@message_router.message(F.content_type == ContentType.VOICE)
async def handle_voice(message: Message, bot: Bot, session: AsyncSession, usecases: UseCases):
    sended_message = await message.answer(text="🕓 Подождите немного, сейчас все будет готово")
    async with ChatActionSender.typing(bot=bot, chat_id=message.chat.id):
        await usecases.handle_voice_message.run(message=message,
                                                sended_message=sended_message,
                                                bot=bot,
                                                session=session)


@message_router.message(F.photo)
async def handle_photo(message: Message, bot: Bot, session: AsyncSession, usecases: UseCases):
    sended_message = await message.answer(text="🕓 Подождите немного, сейчас все будет готово")
    async with ChatActionSender.typing(bot=bot, chat_id=message.chat.id):
        await usecases.handle_photo_message.run(message=message,
                                                bot=bot,
                                                sended_message=sended_message,
                                                session=session)


@message_router.message(F.text)
async def handle_text(message: Message, bot: Bot, session: AsyncSession, usecases: UseCases):
    sended_message = await message.answer(text="🕓 Подождите немного, сейчас все будет готово")
    async with ChatActionSender.typing(bot=bot, chat_id=message.chat.id):
        await usecases.handle_text_message.run(message, bot, sended_message, session)


@message_router.message(F.document)
async def handle_document(message: Message, bot: Bot, session: AsyncSession, usecases: UseCases):
    sended_message = await message.answer(text="🕓 Подождите немного, сейчас все будет готово")
    async with ChatActionSender.typing(bot=bot, chat_id=message.chat.id):
        await usecases.handle_document_message.run(message=message,
                                                   bot=bot,
                                                   sended_message=sended_message,
                                                   session=session)