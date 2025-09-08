from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

class Keyboard:
    def __init__(self, support_link: str, webapp_url: str):
        self.support_link = support_link
        self.webapp_url = webapp_url


    def main_keyboard(self, has_subs: bool, trial_used: bool) -> InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()

        builder.add(InlineKeyboardButton(text="🤖 Выбрать нейросеть", callback_data="select_ai"))
        builder.add(InlineKeyboardButton(text="🎭 Выбрать роль", callback_data="select_role"))

        if not has_subs:
            if trial_used:
                builder.add(InlineKeyboardButton(text='🔥 Купить подписку', callback_data="subs"))
            else:
                builder.add(InlineKeyboardButton(text='🔥 3 дня за 1 рубль',  callback_data="start_trial"))

        builder.adjust(1)
        # Эти две кнопки будут в одной строке
        builder.row(
            InlineKeyboardButton(text="👤 Профиль", callback_data="profile"),
            InlineKeyboardButton(text="Тех. поддержка", url=self.support_link)
        )

        return builder.as_markup()


    @staticmethod
    def select_ai_keyboard(
        ai_models_list: list[tuple[int, str, str]],
        allowed_classes: list[str],
        selected: int
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
            builder.add(
                InlineKeyboardButton(
                    text=btn_text,
                    callback_data=f"set_model:{mid}"
                )
            )
        # кнопка назад
        builder.add(InlineKeyboardButton(text='Назад', callback_data='main_menu'))
        # делим на строки по схеме: 2, 1, 2, 2, 2, 1
        builder.adjust(2, 1, 2, 2, 2, 1)
        return builder.as_markup()

    @staticmethod
    def get_role_keyboard(user_id: int, roles_list: list, selected_role_id: int, subtype: int):
        builder = InlineKeyboardBuilder()
        has_custom_roles = False
        for id, name, author_id, free_avaliable in roles_list:
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
            create_text = 'Редактировать роли'
            create_cb = 'edit_roles'
            if subtype == 0:
                create_text = f'✏️ {create_text}'
        else:
            create_text = 'Создать роль'
            create_cb = 'create_role'
            if subtype == 0:
                create_text = f'➕ {create_text}'

        builder.add(InlineKeyboardButton(text=create_text, callback_data=create_cb))

        # кнопка назад
        builder.add(InlineKeyboardButton(text='Назад', callback_data='main_menu'))
        builder.adjust(1)
        return builder.as_markup()

    @staticmethod
    def get_custom_roles_keyboard(user_id: int, roles_list: list, selected_role_id: int, subtype: int):
        builder = InlineKeyboardBuilder()
        for id, name, author_id, free_avaliable in roles_list:
            text = name
            builder.add(
                InlineKeyboardButton(
                    text=text,
                    callback_data=f"edit_role:{id}"
                )
            )
        create_text = 'Создать роль'
        create_cb = 'create_role'
        if subtype == 0:
            create_text = f'➕ {create_text}'
        builder.add(InlineKeyboardButton(text=create_text, callback_data=create_cb))

    @staticmethod
    def role_subs_keyboard(trial_used: bool):
        builder = InlineKeyboardBuilder()
        if trial_used:
            builder.add(InlineKeyboardButton(text='🔥 Купить подписку', callback_data='subs'))
        else:
            builder.add(InlineKeyboardButton(text='🔥 3 дня за 1 рубль', callback_data='start_trial'))
        builder.add(InlineKeyboardButton(text='Назад', callback_data='select_role'))
        builder.adjust(1)
        return builder.as_markup()

    @staticmethod
    def model_subs_keyboard(trial_used: bool):
        builder = InlineKeyboardBuilder()
        if trial_used:
            builder.add(InlineKeyboardButton(text='🔥 Купить подписку', callback_data='subs'))
        else:
            builder.add(InlineKeyboardButton(text='🔥 3 дня за 1 рубль', callback_data='start_trial'))
        builder.add(InlineKeyboardButton(text='Главное меню', callback_data='main_menu'))
        builder.adjust(1)
        return builder.as_markup()

    @staticmethod
    def profile_menu(has_subs: bool, trial_used: bool):
        builder = InlineKeyboardBuilder()
        if has_subs:
            builder.add(InlineKeyboardButton(text='⚙️ Управление подпиской', callback_data='settings_subs'))
        else:
            if trial_used:
                builder.add(InlineKeyboardButton(text='🔥 Купить подписку', callback_data='subs'))
            else:
                builder.add(InlineKeyboardButton(text='🔥 3 дня за 1 рубль', callback_data='start_trial'))

        builder.add(InlineKeyboardButton(text='💰️ Купить запросы', callback_data='buy_tokens'))
        builder.add(InlineKeyboardButton(text='🆓 Бесплатные запросы', callback_data='free_tokens'))
        builder.add(InlineKeyboardButton(text='Назад', callback_data='main_menu'))
        builder.adjust(1)
        return builder.as_markup()

    @staticmethod
    def subscribe_keyboard(packets: list):
        builder = InlineKeyboardBuilder()
        for packet in packets:
            text = f"{packet.name} — {packet.price}₽ "
            builder.add(InlineKeyboardButton(text=text, callback_data=f'buy_subs_id:{packet.id}'))
        builder.add(InlineKeyboardButton(text='Назад', callback_data='main_menu'))
        builder.adjust(1)
        return builder.as_markup()

    @staticmethod
    def cancel_keyboard():
        return ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="❌ Отмена")]
            ],
            resize_keyboard=True,
            one_time_keyboard=True
        )

    @staticmethod
    def payment_keyboard(amount: int,
                         stars_amount: int,
                         payment_link: str,
                         invoice_link: str,
                         oferta_link: str) -> InlineKeyboardMarkup:
        return InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text=f"TG Stars | {stars_amount} ⭐", url=invoice_link)],
                [InlineKeyboardButton(text=f"Картой | СБП | {amount}₽", url=payment_link)],
                [InlineKeyboardButton(text="Оферта", url=oferta_link)],
                [InlineKeyboardButton(text="Назад", callback_data="subs_list")],
            ]
        )

    @staticmethod
    def subs_keyboard(available_subs: list):
        builder = InlineKeyboardBuilder()
        for sub in available_subs:
            builder.add(InlineKeyboardButton(text=sub.name, callback_data=f'subs_id={sub.id}'))
        builder.add(InlineKeyboardButton(text='Назад', callback_data='main_menu'))
        builder.adjust(1)
        return builder.as_markup()

