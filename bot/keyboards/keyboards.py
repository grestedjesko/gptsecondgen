from typing import Optional

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton, User
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.db.models import AiRoles
from config.i18n import get_text


class Keyboard:
    def __init__(self, support_link: str, webapp_url: str):
        self.support_link = support_link
        self.webapp_url = webapp_url


    def main_keyboard(self, has_subs: bool, trial_used: bool, user: User) -> InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()

        builder.add(InlineKeyboardButton(
            text=get_text("btn_select_ai", user), 
            callback_data="select_ai"
        ))
        builder.add(InlineKeyboardButton(
            text=get_text("btn_select_role", user), 
            callback_data="select_role"
        ))

        if not has_subs:
            if trial_used:
                builder.add(InlineKeyboardButton(
                    text=get_text("btn_buy_subs", user), 
                    callback_data="subs"
                ))
            else:
                builder.add(InlineKeyboardButton(
                    text=get_text("btn_trial_3_days", user), 
                    callback_data="start_trial"
                ))

        builder.adjust(1)
        # Эти две кнопки будут в одной строке
        builder.row(
            InlineKeyboardButton(
                text=get_text("btn_profile", user), 
                callback_data="profile"
            ),
            InlineKeyboardButton(
                text=get_text("btn_support", user), 
                url=self.support_link
            )
        )

        return builder.as_markup()


    @staticmethod
    def select_ai_keyboard(
        ai_models_list: list[tuple[int, str, str]],
        allowed_classes: list[str],
        selected: int,
        user: User
    ) -> InlineKeyboardMarkup:
        """
        ai_models_list: [(id, name, ai_class), ...]
        allowed_classes: ['gpt-3.5', 'gpt-4', ...]
        """
        builder = InlineKeyboardBuilder()

        for mid, name, ai_class in ai_models_list:
            if ai_class in allowed_classes:
                btn_text = name
                if mid == selected:
                    btn_text = '✅ ' + btn_text
            else:
                btn_text = f"🔒 {name}"
            builder.add(InlineKeyboardButton(text=btn_text, callback_data=f"set_model:{mid}"))

        builder.add(InlineKeyboardButton(
            text=get_text("btn_back", user), 
            callback_data='main_menu'
        ))
        builder.adjust(1, 2, 1, 2, 2, 2, 1)
        return builder.as_markup()

    @staticmethod
    def role_keyboard(user_id: int, roles_list: list, selected_role_id: int, subtype: int, user: User, page: int = 0, per_page: int = 5):
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
            create_text = get_text("btn_edit_roles", user)
            create_cb = 'custom_roles'
            if subtype == 0:
                create_text = f'✏️ {create_text}'
        else:
            create_text = get_text("btn_create_role", user)
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
            text=get_text("btn_back", user), 
            callback_data='main_menu'
        ))
        return builder.as_markup()

    @staticmethod
    def custom_role_keyboard(roles: Optional[list[AiRoles]], user: User):
        builder = InlineKeyboardBuilder()
        for role in roles:
            builder.add(InlineKeyboardButton(text=role.name, callback_data=f'settings_role_id={role.id}'))

        if len(roles) < 5:
            builder.add(InlineKeyboardButton(
                text=get_text("btn_create_role", user), 
                callback_data='create_role'
            ))
        builder.add(InlineKeyboardButton(
            text=get_text("btn_back", user), 
            callback_data='select_role'
        ))
        builder.adjust(1)
        return builder.as_markup()

    @staticmethod
    def role_settings_keyboard(role_id: int, user: User):
        builder = InlineKeyboardBuilder()
        builder.add(InlineKeyboardButton(
            text=get_text("btn_delete_role", user), 
            callback_data=f'delete_role_id={role_id}'
        ))
        builder.add(InlineKeyboardButton(
            text=get_text("btn_back", user), 
            callback_data='custom_roles'
        ))
        builder.adjust(1)
        return builder.as_markup()

    @staticmethod
    def role_subs_keyboard(trial_used: bool, user: User):
        builder = InlineKeyboardBuilder()
        if trial_used:
            builder.add(InlineKeyboardButton(
                text=get_text("btn_buy_subs", user), 
                callback_data='subs'
            ))
        else:
            builder.add(InlineKeyboardButton(
                text=get_text("btn_trial_3_days", user), 
                callback_data='start_trial'
            ))
        builder.add(InlineKeyboardButton(
            text=get_text("btn_back", user), 
            callback_data='select_role'
        ))
        builder.adjust(1)
        return builder.as_markup()

    @staticmethod
    def model_subs_keyboard(trial_used: bool, user: User):
        builder = InlineKeyboardBuilder()
        if trial_used:
            builder.add(InlineKeyboardButton(
                text=get_text("btn_buy_subs", user), 
                callback_data='subs'
            ))
        else:
            builder.add(InlineKeyboardButton(
                text=get_text("btn_trial_3_days", user), 
                callback_data='start_trial'
            ))
        builder.add(InlineKeyboardButton(
            text=get_text("btn_main_menu", user), 
            callback_data='main_menu'
        ))
        builder.adjust(1)
        return builder.as_markup()

    @staticmethod
    def profile_menu(has_subs: bool, trial_used: bool, user: User):
        builder = InlineKeyboardBuilder()
        if has_subs:
            builder.add(InlineKeyboardButton(
                text=get_text("btn_settings_subs", user), 
                callback_data='settings_subs'
            ))
        else:
            if trial_used:
                builder.add(InlineKeyboardButton(
                    text=get_text("btn_buy_subs", user), 
                    callback_data='subs'
                ))
            else:
                builder.add(InlineKeyboardButton(
                    text=get_text("btn_trial_3_days", user), 
                    callback_data='start_trial'
                ))

        #builder.add(InlineKeyboardButton(text='💰️ Купить запросы', callback_data='buy_tokens'))
        builder.add(InlineKeyboardButton(
            text=get_text("btn_free_tokens", user), 
            callback_data='free_tokens'
        ))
        builder.add(InlineKeyboardButton(
            text=get_text("btn_back", user), 
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

    @staticmethod
    def cancel_keyboard(user: User):
        return ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text=get_text("btn_cancel", user))]
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

