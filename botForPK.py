import os
import telebot
import pyautogui
from telebot import types
import platform

TOKEN = 'СЮДА ТОКЕН ВАШЕГО БОТА'
ADMIN_ID =  0 #ВАШ АЙДИ В ТГ

bot = telebot.TeleBot(TOKEN)

try:
    bot.set_my_commands([
        types.BotCommand("start", "Запустить бота"),
        types.BotCommand("menu", "Открыть главное меню")
    ])
except Exception:
    pass

# КНОПКИ
def get_main_menu():
    markup = types.InlineKeyboardMarkup(row_width=1)
    btn_screen = types.InlineKeyboardButton("Сделать скриншот", callback_data='screen')
    btn_stats = types.InlineKeyboardButton("Статус дисков", callback_data='stats')
    btn_apps = types.InlineKeyboardButton("Игры и Программы", callback_data='apps_menu')
    btn_restart = types.InlineKeyboardButton("Перезагрузить ПК", callback_data='restart')
    btn_shutdown = types.InlineKeyboardButton("Выключить ПК", callback_data='shutdown')
    
    markup.add(btn_screen, btn_stats, btn_apps, btn_restart, btn_shutdown)
    return markup
# ТУТ ПРИМЕР НА КС И ДОТЕ
def get_apps_menu():
    markup = types.InlineKeyboardMarkup(row_width=1)
    btn_cs = types.InlineKeyboardButton("Запустить название вашей игры или программы", callback_data='run_cs')
    btn_dota = types.InlineKeyboardButton("Запустить название вашей игры или программы", callback_data='run_dota')
    # ТАКЖЕ МОЖНО ДОБАВИТЬ БОЛЬШЕ

    btn_back = types.InlineKeyboardButton("Назад", callback_data='main_menu')
    
    markup.add(btn_cs, btn_dota, btn_back)
    return markup

def get_back_menu():
    markup = types.InlineKeyboardMarkup()
    btn_back = types.InlineKeyboardButton("Назад", callback_data='main_menu')
    markup.add(btn_back)
    return markup

@bot.message_handler(commands=['start', 'menu'])
def send_welcome(message):
    if message.chat.id != ADMIN_ID: #ПРОВЕРКА, ЧТОБЫ ПОЛЬЗОВАЛИСЬ ТОЛЬКО ВЫ
        bot.reply_to(message, "Доступ запрещен!")
        return
        
    bot.send_message(
        message.chat.id, 
        "Управления ПК:", 
        reply_markup=get_main_menu()
    )

# ОБРАБАТЫВАЕМ НАЖАТИЕ КНОПКИ
@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    if call.message.chat.id != ADMIN_ID:
        bot.answer_callback_query(call.id, "Доступ запрещен!")
        return

    # ВОЗВРАТ
    if call.data == 'main_menu':
        bot.answer_callback_query(call.id)
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text="Управления ПК:",
            reply_markup=get_main_menu()
        )

    # МЕНЮ
    elif call.data == 'apps_menu':
        bot.answer_callback_query(call.id)
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text="Выберите игру или программу для запуска:",
            reply_markup=get_apps_menu()
        )
    # ЗАПУСК ВАШИХ ИГР
    elif call.data == 'run_cs':
        bot.answer_callback_query(call.id, "Запускаю игру...")
        os.system("start steam://rungameid/АЙДИ ИГРЫ")
        bot.send_message(call.message.chat.id, "Команда на запуск Counter-Strike 2 отправлена.", reply_markup=get_back_menu())

    elif call.data == 'run_dota':
        bot.answer_callback_query(call.id, "Запускаю игру...")
        os.system("start steam://rungameid/АЙДИ ИГРЫ")
        bot.send_message(call.message.chat.id, "Команда на запуск Dota 2 отправлена.", reply_markup=get_back_menu())
        #ДЛЯ ЗАПУСКА ПРОГРАММ НЕ ИЗ СТИМА УКАЗЫВАЕМ ПОЛНЫЙ ПУТЬ


    # СКРИН
    elif call.data == 'screen':
        bot.answer_callback_query(call.id, "Делаю скриншот...")
        screen_name = "screen_bot.png"
        try:
            screenshot = pyautogui.screenshot()
            screenshot.save(screen_name)
            with open(screen_name, 'rb') as photo:
                bot.send_photo(call.message.chat.id, photo)
            bot.send_message(call.message.chat.id, "Действие выполнено.", reply_markup=get_back_menu())
        finally:
            if os.path.exists(screen_name):
                os.remove(screen_name)
                
    # СТАТУС ДИСКОВ
    elif call.data == 'stats':
        bot.answer_callback_query(call.id, "Собираю данные...")
        os_info = platform.system() + " " + platform.release()
        
        # Запрашиваем информацию о дисках через PowerShell напрямую из Python
        powershell_cmd = "Get-CimInstance Win32_LogicalDisk | Select-Object DeviceID, @{Name='FreeGB';Expression={[math]::Round($_.FreeSpace/1GB,2)}}, @{Name='SizeGB';Expression={[math]::Round($_.Size/1GB,2)}} | Out-String"
        disk_info = os.popen(f'powershell "{powershell_cmd}"').read()
        
        response = f"Статус ПК:\nОС: {os_info}\n\nДиски:\n{disk_info}"
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=response,
            reply_markup=get_back_menu()
        )
        
    # РЕСТАРТ КОМПА
    elif call.data == 'restart':
        bot.answer_callback_query(call.id, "Перезагрузка...")
        bot.send_message(call.message.chat.id, "Компьютер перезагружается. Связь разорвана.")
        os.system('shutdown /r /t 1')
        
    # ВЫКЛЮЧАЕМ
    elif call.data == 'shutdown':
        bot.answer_callback_query(call.id, "Выключение...")
        bot.send_message(call.message.chat.id, "Компьютер выключается. Связь разорвана.")
        os.system('shutdown /s /t 1')

print("Бот успешно запущен")
bot.infinity_polling()