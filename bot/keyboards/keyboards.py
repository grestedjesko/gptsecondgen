from typing import Optional
import asyncio
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton, User
from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models import AiRoles
from app.db.models.packets import Packet, PacketType
from config.i18n import get_text
from src.services.i18n_service import I18nService



class Keyboard:
    def __init__(self, support_link: str, webapp_url: str):
        self.support_link = support_link
        self.webapp_url = webapp_url

    async def _get_text(self, key: str, user: User, session: AsyncSession = None, **kwargs) -> str:
        """Вспомогательная функция для получения текста с учетом сохраненного языка"""
        if session:
            return await I18nService.get_text(key, user, session, **kwargs)
        else:
            return get_text(key, user, **kwargs)


    async def main_keyboard(self, has_subs: bool, trial_used: bool, user: User, session: AsyncSession = None) -> InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()
        trial_used = True
        if not has_subs:
            if trial_used:
                builder.add(InlineKeyboardButton(
                    text=await self._get_text("btn_buy_subs", user, session), 
                    callback_data="subs_list"
                ))
            else:
                builder.add(InlineKeyboardButton(
                    text=await self._get_text("btn_trial_3_days", user, session), 
                    callback_data="start_trial"
                ))

        builder.add(InlineKeyboardButton(
            text=await self._get_text("btn_select_ai", user, session), 
            callback_data="select_ai"
        ))

        builder.add(InlineKeyboardButton(
            text=await self._get_text("btn_select_role", user, session), 
            callback_data="select_role"
        ))

        builder.add(InlineKeyboardButton(
            text=await self._get_text("btn_create", user, session), 
            callback_data="create_media"
        ))

        builder.add(
            InlineKeyboardButton(
                text=await self._get_text("btn_profile", user, session), 
                callback_data="profile"
            )
        )

        builder.add(
            InlineKeyboardButton(
                text=await self._get_text("btn_settings", user, session), 
                callback_data="settings"
            )
        )

        builder.adjust(1,2,1,2)
        return builder.as_markup()


    async def select_ai_keyboard(
        self,
        ai_models_list: list[tuple[int, str, str]],
        neiro_packet_models: list[int],
        premium_models: list[int],
        selected: int,
        user: User,
        session: AsyncSession = None
    ) -> InlineKeyboardMarkup:
        """
        ai_models_list: [(id, name, ai_class), ...]
        allowed_classes: ['gpt-3.5', 'gpt-4', ...]
        """
        builder = InlineKeyboardBuilder()

        for mid, name in ai_models_list:
            if mid in premium_models:
                btn_text = f'⭐️ {name}'
            elif mid in neiro_packet_models:
                btn_text = f'📂 {name}'
            
            else:
                btn_text = name
            if mid == selected:
                btn_text = '✅ ' + btn_text
            builder.add(InlineKeyboardButton(text=btn_text, callback_data=f"set_model:{mid}"))

        builder.add(InlineKeyboardButton(
            text=await self._get_text("btn_back", user, session), 
            callback_data='main_menu'
        ))
        builder.adjust(1, 1, 2)
        return builder.as_markup()

    async def role_keyboard(self, user_id: int, roles_list: list, selected_role_id: int, subtype: int, user: User, page: int = 0, per_page: int = 5, session: AsyncSession = None):
        builder = InlineKeyboardBuilder()
        has_custom_roles = False

        total = len(roles_list)
        start = max(page, 0) * per_page
        end = start + per_page
        page_roles = roles_list[start:end]

        for id, name, author_id, free_avaliable in page_roles:
            if author_id == user_id:
                has_custom_roles = True

            if id == selected_role_id:
                text = f'✅ {name}'
            else:
                if author_id == user_id:
                    if subtype == 0:
                        text = f'🔒 {name}'
                    else:
                        text = f'⭐️ {name}'
                else:
                    if free_avaliable:
                        text = name
                    else:
                        if subtype == 0:
                            text = f'🔒 {name}'
                        else:
                            text = name

            builder.add(
                InlineKeyboardButton(
                    text=text,
                    callback_data=f"set_role:{id}"
                )
            )
        if has_custom_roles:
            create_text = await self._get_text("btn_edit_roles", user, session)
            create_cb = 'custom_roles'
            if subtype == 0:
                create_text = f'✏️ {create_text}'
        else:
            create_text = await self._get_text("btn_create_role", user, session)
            create_cb = 'create_role'
            if subtype == 0:
                create_text = f'➕ {create_text}'

        builder.add(InlineKeyboardButton(text=create_text, callback_data=create_cb))
        builder.adjust(1)

        if total > per_page:
            last_page = (total - 1) // per_page
            prev_page = max(page - 1, 0)
            next_page = min(page + 1, last_page)

            prev_btn = InlineKeyboardButton(
                text=' ' if page == 0 else '«',
                callback_data='noop' if page == 0 else f'roles_page:{prev_page}'
            )
            next_btn = InlineKeyboardButton(
                text=' ' if page == last_page else '»',
                callback_data='noop' if page == last_page else f'roles_page:{next_page}'
            )

            builder.row(
                prev_btn,
                InlineKeyboardButton(text=f'{page + 1}/{last_page + 1}', callback_data='noop'),
                next_btn,
            )

        builder.row(InlineKeyboardButton(
            text=await self._get_text("btn_back", user, session), 
            callback_data='main_menu'
        ))
        return builder.as_markup()

    async def custom_role_keyboard(self, roles: Optional[list[AiRoles]], user: User, session: AsyncSession = None):
        builder = InlineKeyboardBuilder()
        for role in roles:
            builder.add(InlineKeyboardButton(text=role.name, callback_data=f'settings_role_id={role.id}'))

        if len(roles) < 5:
            builder.add(InlineKeyboardButton(
                text=await self._get_text("btn_create_role", user, session), 
                callback_data='create_role'
            ))
        builder.add(InlineKeyboardButton(
            text=await self._get_text("btn_back", user, session), 
            callback_data='select_role'
        ))
        builder.adjust(1)
        return builder.as_markup()

    async def role_settings_keyboard(self, role_id: int, user: User, session: AsyncSession = None):
        builder = InlineKeyboardBuilder()
        builder.add(InlineKeyboardButton(
            text=await self._get_text("btn_delete_role", user, session), 
            callback_data=f'delete_role_id={role_id}'
        ))
        builder.add(InlineKeyboardButton(
            text=await self._get_text("btn_back", user, session), 
            callback_data='custom_roles'
        ))
        builder.adjust(1)
        return builder.as_markup()

    async def role_subs_keyboard(self, trial_used: bool, user: User, session: AsyncSession = None):
        builder = InlineKeyboardBuilder()
        if trial_used:
            builder.add(InlineKeyboardButton(
                text=await self._get_text("btn_buy_subs", user, session), 
                callback_data='subs'
            ))
        else:
            builder.add(InlineKeyboardButton(
                text=await self._get_text("btn_trial_3_days", user, session), 
                callback_data='start_trial'
            ))
        builder.add(InlineKeyboardButton(
            text=await self._get_text("btn_back", user, session), 
            callback_data='select_role'
        ))
        builder.adjust(1)
        return builder.as_markup()

    async def model_subs_keyboard(self, trial_used: bool, user: User, session: AsyncSession = None):
        builder = InlineKeyboardBuilder()
        if trial_used:
            builder.add(InlineKeyboardButton(
                text=await self._get_text("btn_buy_subs", user, session), 
                callback_data='subs'
            ))
        else:
            builder.add(InlineKeyboardButton(
                text=await self._get_text("btn_trial_3_days", user, session), 
                callback_data='start_trial'
            ))
        builder.add(InlineKeyboardButton(
            text=await self._get_text("btn_main_menu", user, session), 
            callback_data='main_menu'
        ))
        builder.adjust(1)
        return builder.as_markup()

    async def profile_menu(self, has_subs: bool, trial_used: bool, user: User, session: AsyncSession = None):
        builder = InlineKeyboardBuilder()
        if has_subs:
            builder.add(InlineKeyboardButton(
                text=await self._get_text("btn_settings_subs", user, session), 
                callback_data='settings_subs'
            ))
        else:
            if trial_used:
                builder.add(InlineKeyboardButton(
                    text=await self._get_text("btn_buy_subs", user, session), 
                    callback_data='subs'
                ))
            else:
                builder.add(InlineKeyboardButton(
                    text=await self._get_text("btn_trial_3_days", user, session), 
                    callback_data='start_trial'
                ))

        #builder.add(InlineKeyboardButton(text='💰️ Купить запросы', callback_data='buy_tokens'))
        builder.add(InlineKeyboardButton(
            text=await self._get_text("btn_free_tokens", user, session), 
            callback_data='free_tokens'
        ))
        builder.add(InlineKeyboardButton(
            text=await self._get_text("btn_back", user, session), 
            callback_data='main_menu'
        ))
        builder.adjust(1)
        return builder.as_markup()

    @staticmethod
    def subscribe_keyboard(packets: list, user: User):
        builder = InlineKeyboardBuilder()
        for packet in packets:
            text = f"{packet.name} — {packet.price}₽ "
            builder.add(InlineKeyboardButton(text=text, callback_data=f'buy_subs_id:{packet.id}'))
        builder.add(InlineKeyboardButton(
            text=get_text("btn_back", user), 
            callback_data='main_menu'
        ))
        builder.adjust(1)
        return builder.as_markup()

    @staticmethod
    def subs_settings_keyboard(will_renew: bool, user: User):
        builder = InlineKeyboardBuilder()
        if will_renew:
            builder.add(InlineKeyboardButton(
                text=get_text("btn_stop_renew", user), 
                callback_data='subs_stop_renew'
            ))
        else:
            builder.add(InlineKeyboardButton(
                text=get_text("btn_start_renew", user), 
                callback_data='rebind_payment_method'
            ))
        
        builder.add(InlineKeyboardButton(
            text=get_text("btn_extend_subs", user), 
            callback_data='extend_subs'
        ))
        
        builder.add(InlineKeyboardButton(
            text=get_text("btn_back", user), 
            callback_data='profile'
        ))
        builder.adjust(1)
        return builder.as_markup()

    async def cancel_keyboard(self, user: User, session: AsyncSession = None):
        return ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text=await self._get_text("btn_cancel", user, session))]
            ],
            resize_keyboard=True,
            one_time_keyboard=True
        )

    @staticmethod
    def payment_keyboard(amount: int,
                         stars_amount: int,
                         payment_link: str,
                         invoice_link: str,
                         oferta_link: str,
                         user: User) -> InlineKeyboardMarkup:
        return InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(
                    text=get_text("btn_pay_stars", user, stars=stars_amount), 
                    url=invoice_link
                )],
                [InlineKeyboardButton(
                    text=get_text("btn_pay_card", user, amount=amount), 
                    url=payment_link
                )],
                [InlineKeyboardButton(
                    text=get_text("btn_oferta", user), 
                    url=oferta_link
                )],
                [InlineKeyboardButton(
                    text=get_text("btn_back", user), 
                    callback_data="subs_list"
                )],
            ]
        )

    @staticmethod
    def subs_keyboard(available_subs: list, user: User):
        builder = InlineKeyboardBuilder()
        for sub in available_subs:
            builder.add(InlineKeyboardButton(text=sub.name, callback_data=f'subs_id={sub.id}'))
        builder.add(InlineKeyboardButton(
            text=get_text("btn_back", user), 
            callback_data='main_menu'
        ))
        builder.adjust(1)
        return builder.as_markup()

    @staticmethod
    def subs_extend_keyboard(available_subs: list, user: User):
        builder = InlineKeyboardBuilder()
        for sub in available_subs:
            builder.add(InlineKeyboardButton(text=sub.name, callback_data=f'subs_id={sub.id}'))
        builder.add(InlineKeyboardButton(
            text=get_text("btn_back", user), 
            callback_data='profile'
        ))
        builder.adjust(1)
        return builder.as_markup()

    @staticmethod
    def payment_rebind_keyboard(link: str, user: User):
        builder = InlineKeyboardBuilder()
        builder.add(InlineKeyboardButton(
            text=get_text("btn_pay_1_rub", user), 
            url=link
        ))
        builder.add(InlineKeyboardButton(
            text=get_text("btn_back", user), 
            callback_data='settings_subs'
        ))
        builder.adjust(1)
        return builder.as_markup()

    @staticmethod
    def settings_keyboard(user: User, saved_language: str = None):
        """Клавиатура главного меню настроек"""
        builder = InlineKeyboardBuilder()
        builder.add(InlineKeyboardButton(
            text=get_text("btn_select_ai", user, saved_language), 
            callback_data='select_ai'
        ))

        builder.add(InlineKeyboardButton(
            text=get_text("btn_select_role", user, saved_language), 
            callback_data='select_role'
        ))  

        builder.add(InlineKeyboardButton(
            text=get_text("btn_settings_context", user, saved_language), 
            callback_data='settings_context'
        ))

        builder.add(InlineKeyboardButton(
            text=get_text("btn_settings_voice", user, saved_language), 
            callback_data='settings_voice'
        ))

        builder.add(InlineKeyboardButton(
            text=get_text("btn_settings_language", user, saved_language), 
            callback_data='settings_language'
        ))
        builder.add(InlineKeyboardButton(
            text=get_text("btn_back", user, saved_language), 
            callback_data='main_menu'
        ))
        builder.adjust(2, 1, 1, 1, 1)
        return builder.as_markup()

    @staticmethod
    def language_selection_keyboard(user: User, saved_language: str = None):
        """Клавиатура выбора языка"""
        builder = InlineKeyboardBuilder()
        builder.add(InlineKeyboardButton(
            text=get_text("language_russian", user, saved_language), 
            callback_data='set_language:ru'
        ))
        builder.add(InlineKeyboardButton(
            text=get_text("language_english", user, saved_language), 
            callback_data='set_language:en'
        ))
        builder.add(InlineKeyboardButton(
            text=get_text("btn_back_to_settings", user, saved_language), 
            callback_data='settings'
        ))
        builder.adjust(1)
        return builder.as_markup()


    @staticmethod
    async def create_media_keyboard(user: User, saved_language: str = None):
        builder = InlineKeyboardBuilder()
        builder.add(InlineKeyboardButton(
            text=get_text("btn_create_picture", user, saved_language), 
            callback_data='create_image', 
        ))
        builder.add(InlineKeyboardButton(
            text=get_text("btn_create_video", user, saved_language), 
            callback_data='create_video', 
        ))
        builder.add(InlineKeyboardButton(
            text=get_text("btn_create_music", user, saved_language), 
            callback_data='create_music', 
        ))  
        builder.add(InlineKeyboardButton(
            text=get_text("btn_back", user, saved_language), 
            callback_data='main_menu', 
        ))
        builder.adjust(1)
        return builder.as_markup()

    @staticmethod
    async def create_image_keyboard(user: User, saved_language: str = None):
        builder = InlineKeyboardBuilder()
        builder.add(InlineKeyboardButton(
            text=get_text("btn_replace_face", user, saved_language), 
            callback_data='replace_face', 
        ))
        builder.add(InlineKeyboardButton(
            text=get_text("btn_remove_background", user, saved_language), 
            callback_data='remove_background', 
        ))
        builder.add(InlineKeyboardButton(
            text=get_text("btn_enhance_image", user, saved_language), 
            callback_data='enhance_image', 
        ))
        builder.add(InlineKeyboardButton(
            text=get_text("btn_back", user, saved_language), 
            callback_data='create_media', 
        ))

        builder.adjust(1)
        return builder.as_markup()

    @staticmethod
    async def create_video_keyboard(user: User, saved_language: str = None):
        builder = InlineKeyboardBuilder()
        builder.add(InlineKeyboardButton(
            text=get_text("btn_veo", user, saved_language), 
            callback_data='video_veo', 
        ))
        builder.add(InlineKeyboardButton(
            text=get_text("btn_video_hailuo", user, saved_language), 
            callback_data='video_hailuo', 
        ))
        builder.add(InlineKeyboardButton(
            text=get_text("btn_video_kiling", user, saved_language), 
            callback_data='video_kiling', 
        ))
        builder.add(InlineKeyboardButton(
            text=get_text("btn_video_pika", user, saved_language), 
            callback_data='video_pika', 
        ))
        builder.add(InlineKeyboardButton(
            text=get_text("btn_back", user, saved_language), 
            callback_data='create_media', 
        ))
        builder.adjust(2,2,1)
        return builder.as_markup()

    @staticmethod
    async def subs_main_menu(user: User, packet_types: list[PacketType]):
        builder = InlineKeyboardBuilder()

        builder.row(InlineKeyboardButton(
            text=get_text("btn_premium", user), 
            callback_data='premium'
        )) 

        # Packet buttons arranged in rows of 2
        packets_builder = InlineKeyboardBuilder()
        for packet_type in packet_types:
            packets_builder.add(InlineKeyboardButton(
                text=packet_type.name, 
                callback_data=f'buy_packet_id={packet_type.id}'
            ))
        packets_builder.adjust(2)
        builder.attach(packets_builder)
        
        # Single-button row at the bottom
        builder.row(InlineKeyboardButton(
            text=get_text("btn_back", user), 
            callback_data='main_menu'
        ))

        return builder.as_markup()