#!/usr/bin/env python3
"""
Простой тест системы локализации
"""

from config.i18n import get_text, get_user_language, Language
from aiogram.types import User


def test_language_detection():
    """Тест определения языка"""
    print("=== Тест определения языка ===")
    
    # Создаем тестовых пользователей
    ru_user = User(id=1, is_bot=False, first_name="Test", language_code="ru")
    en_user = User(id=2, is_bot=False, first_name="Test", language_code="en")
    uk_user = User(id=3, is_bot=False, first_name="Test", language_code="uk")  # Украинский -> русский
    fr_user = User(id=4, is_bot=False, first_name="Test", language_code="fr")  # Французский -> английский
    unknown_user = User(id=5, is_bot=False, first_name="Test", language_code="zh")  # Китайский -> русский по умолчанию
    none_user = User(id=6, is_bot=False, first_name="Test", language_code=None)  # None -> русский по умолчанию
    
    # Тестируем определение языка
    assert get_user_language(ru_user) == Language.RU
    assert get_user_language(en_user) == Language.EN
    assert get_user_language(uk_user) == Language.RU  # Украинский -> русский
    assert get_user_language(fr_user) == Language.EN  # Французский -> английский
    assert get_user_language(unknown_user) == Language.RU  # Неизвестный -> русский
    assert get_user_language(none_user) == Language.RU  # None -> русский
    
    print("✅ Определение языка работает корректно")


def test_text_retrieval():
    """Тест получения текстов"""
    print("\n=== Тест получения текстов ===")
    
    # Создаем тестовых пользователей
    ru_user = User(id=1, is_bot=False, first_name="Test", language_code="ru")
    en_user = User(id=2, is_bot=False, first_name="Test", language_code="en")
    
    # Тест простых текстов
    ru_text = get_text("btn_select_ai", ru_user)
    en_text = get_text("btn_select_ai", en_user)
    
    assert "Выбрать нейросеть" in ru_text
    assert "Select AI" in en_text
    
    print(f"RU: {ru_text}")
    print(f"EN: {en_text}")
    
    # Тест с параметрами
    ru_text_with_params = get_text("btn_pay_card", ru_user, amount=100)
    en_text_with_params = get_text("btn_pay_card", en_user, amount=100)
    
    assert "100₽" in ru_text_with_params
    assert "100₽" in en_text_with_params
    
    print(f"RU with params: {ru_text_with_params}")
    print(f"EN with params: {en_text_with_params}")
    
    # Тест длинных текстов
    ru_long_text = get_text("subs_text", ru_user, model_name="GPT-4")
    en_long_text = get_text("subs_text", en_user, model_name="GPT-4")
    
    assert "GPT-4" in ru_long_text
    assert "GPT-4" in en_long_text
    
    print(f"RU long text: {ru_long_text[:50]}...")
    print(f"EN long text: {en_long_text[:50]}...")
    
    print("✅ Получение текстов работает корректно")


def test_all_buttons():
    """Тест всех кнопок"""
    print("\n=== Тест всех кнопок ===")
    
    ru_user = User(id=1, is_bot=False, first_name="Test", language_code="ru")
    en_user = User(id=2, is_bot=False, first_name="Test", language_code="en")
    
    button_keys = [
        "btn_select_ai", "btn_select_role", "btn_buy_subs", "btn_trial_3_days",
        "btn_profile", "btn_support", "btn_back", "btn_main_menu",
        "btn_edit_roles", "btn_create_role", "btn_delete_role", "btn_settings_subs",
        "btn_free_tokens", "btn_stop_renew", "btn_start_renew", "btn_extend_subs",
        "btn_cancel", "btn_pay_card", "btn_pay_stars", "btn_oferta", "btn_pay_1_rub"
    ]
    
    missing_keys = []
    
    for key in button_keys:
        try:
            ru_text = get_text(key, ru_user)
            en_text = get_text(key, en_user)
            
            if not ru_text or ru_text == key:
                missing_keys.append(f"RU: {key}")
            if not en_text or en_text == key:
                missing_keys.append(f"EN: {key}")
                
        except Exception as e:
            missing_keys.append(f"Error for {key}: {e}")
    
    if missing_keys:
        print("❌ Отсутствующие или некорректные тексты:")
        for key in missing_keys:
            print(f"  - {key}")
    else:
        print("✅ Все кнопки присутствуют и корректны")
    
    return len(missing_keys) == 0


if __name__ == "__main__":
    print("🚀 Запуск простого теста локализации...\n")
    
    try:
        test_language_detection()
        test_text_retrieval()
        all_buttons_ok = test_all_buttons()
        
        print(f"\n🎉 Тест {'пройден' if all_buttons_ok else 'завершен с ошибками'}!")
        
    except Exception as e:
        print(f"\n❌ Ошибка при выполнении теста: {e}")
        import traceback
        traceback.print_exc()
