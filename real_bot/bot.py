from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, CallbackQueryHandler, MessageHandler, filters
import requests
import logging
import asyncio

# Настройка логирования
logging.basicConfig(
    filename='bot.log',
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Константы
TELEGRAM_TOKEN = "7519915111:AAHVz5vBRDYiwaZrC22yMFHBqygUaBfV-JU"
COMPANY_UNIQUE_ID = 1
API_BASE_URL = 'http://192.168.56.1:8000'

# Гибкое меню
MENU = {
    'drinks': [
        {'id': 'coffee', 'label': '☕ Кофе', 'order_label': 'кофе'},
        {'id': 'tea', 'label': '🍵 Чай', 'order_label': 'чай'},
        {'id': 'season_menu', 'label': '🌟 Сезонное Меню', 'order_label': 'сезонное'}
    ],
    'drink_types': {
        'coffee': [
            {'id': 'americano', 'label': 'Американо', 'order_label': 'американо'},
            {'id': 'latte', 'label': 'Латте', 'order_label': 'латте'},
            {'id': 'cappuccino', 'label': 'Капучино', 'order_label': 'капучино'},
            {'id': 'mochaccino', 'label': 'Мокачино', 'order_label': 'мокачино'},
        ],
        'tea': [
            {'id': 'black', 'label': 'Чёрный', 'order_label': 'чёрный'},
            {'id': 'green', 'label': 'Зелёный', 'order_label': 'зелёный'},
        ],
        'season_menu': [
            {'id': 'gingerbread_coffee', 'label': 'Пряничный кофе', 'order_label': 'пряничный кофе'},
            {'id': 'yellow_snow', 'label': 'Жёлтый снег', 'order_label': 'жёлтый снег'},
            {'id': 'pistachio', 'label': 'Фисташковый', 'order_label': 'фисташковый'},
        ]
    },
    'additives': [
        {'id': 'sugar', 'label': 'Сахар 🧂', 'order_label': 'сахаром'},
        {'id': 'cinnamon', 'label': 'Корица 🌰', 'order_label': 'корицей'},
        {'id': 'vanilla_syrup', 'label': 'Ванильный сироп 🍯', 'order_label': 'ванильным сиропом'},
        {'id': 'caramel_syrup', 'label': 'Карамельный сироп', 'order_label': 'карамельным сиропом'},
        {'id': 'chocolate_syrup', 'label': 'Шоколадный сироп', 'order_label': 'шоколадным сиропом'},
        {'id': 'maple_syrup', 'label': 'Кленовый сироп', 'order_label': 'кленовым сиропом'},
    ],
    'volumes': [
        {'id': 'small', 'label': 'Маленький (200 мл)', 'order_label': 'маленький'},
        {'id': 'medium', 'label': 'Средний (300 мл)', 'order_label': 'средний'},
        {'id': 'large', 'label': 'Большой (400 мл)', 'order_label': 'большой'},
    ]
}

# Главное меню с кнопкой "Последний заказ"
def main_menu_keyboard():
    return ReplyKeyboardMarkup(
        [[KeyboardButton("Привет 😊"), KeyboardButton("Сделать заказ ☕")],[KeyboardButton("Последний заказ 📋")]],
        resize_keyboard=True,
        one_time_keyboard=True
    )

# Клавиатура с напитками
def drink_keyboard():
    buttons = [
        [InlineKeyboardButton(item['label'], callback_data=f"drink_{item['id']}") for item in MENU['drinks'][i:i + 2]]
        for i in range(0, len(MENU['drinks']), 2)
    ]
    buttons.append([InlineKeyboardButton("❌ Отмена", callback_data='cancel')])
    return InlineKeyboardMarkup(buttons)

# Клавиатура с видами напитка
def drink_type_keyboard(drink_id):
    buttons = [
        [InlineKeyboardButton(item['label'], callback_data=f"type_{item['id']}") for item in MENU['drink_types'][drink_id][i:i + 2]]
        for i in range(0, len(MENU['drink_types'][drink_id]), 2)
    ]
    buttons.append([
        InlineKeyboardButton("⬅️ Назад", callback_data='back_to_drink'),
        InlineKeyboardButton("❌ Отмена", callback_data='cancel')
    ])
    return InlineKeyboardMarkup(buttons)

# Клавиатура с объёмами
def volume_keyboard():
    buttons = [
        [InlineKeyboardButton(item['label'], callback_data=f"volume_{item['id']}") for item in MENU['volumes'][i:i + 2]]
        for i in range(0, len(MENU['volumes']), 2)
    ]
    buttons.append([
        InlineKeyboardButton("⬅️ Назад", callback_data='back_to_type'),
        InlineKeyboardButton("❌ Отмена", callback_data='cancel')
    ])
    return InlineKeyboardMarkup(buttons)

# Клавиатура с добавками
def additives_keyboard(selected_additives=None):
    selected_additives = selected_additives or []
    buttons = [
        [InlineKeyboardButton(f"{'✅ ' if item['id'] in selected_additives else ''}{item['label']}", callback_data=f"additive_{item['id']}") for item in MENU['additives'][i:i + 2]]
        for i in range(0, len(MENU['additives']), 2)
    ]
    buttons.append([
        InlineKeyboardButton("⬅️ Назад", callback_data='back_to_volume'),
        InlineKeyboardButton("❌ Отмена", callback_data='cancel')
    ])
    buttons.append([InlineKeyboardButton("Подтвердить ✅", callback_data='confirm_additives')])
    return InlineKeyboardMarkup(buttons)

# Обработчики
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        f'Привет, *{update.effective_user.first_name}*! 😊 Чем могу помочь?',
        reply_markup=main_menu_keyboard(),
        parse_mode='Markdown'
    )

async def start_order(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    context.user_data.clear()
    context.user_data['stage'] = 'drink'
    await update.message.reply_text('Выбери напиток:', reply_markup=drink_keyboard())

async def last_order(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id
    try:
        response = requests.get(f'{API_BASE_URL}/api/getLastOrder?tg_id={user_id}', timeout=5)
        response.raise_for_status()
        last_order_data = response.json()
        if last_order_data:
            order_text = last_order_data['order']
            await update.message.reply_text(
                f"Ваш последний заказ: {order_text}\nХотите повторить его?",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("Да, повторить", callback_data=f"repeat_{order_text}"),
                     InlineKeyboardButton("Нет, вернуться", callback_data="cancel")]
                ])
            )
        else:
            await update.message.reply_text("У вас нет предыдущих заказов.", reply_markup=main_menu_keyboard())
    except Exception as e:
        logger.error(f"Ошибка при получении последнего заказа: {str(e)}")
        await update.message.reply_text("😓 Не удалось получить последний заказ. Попробуйте позже.", reply_markup=main_menu_keyboard())

async def handle_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_data = context.user_data

    if query.data == 'cancel':
        user_data.clear()
        await query.edit_message_text("Действие отменено.")
        await query.message.reply_text("Выбери действие:", reply_markup=main_menu_keyboard())
        return

    if query.data.startswith("repeat_"):
        order_text = query.data.replace("repeat_", "")
        try:
            response = requests.post(
                f'{API_BASE_URL}/api/makeOrder',
                json={'tg_id': query.from_user.id, 'company': COMPANY_UNIQUE_ID, 'order': order_text},
                timeout=5
            )
            response.raise_for_status()
            await query.edit_message_text(f"✅ *Ваш заказ*: {order_text}!\nПриготовим в течение 5 минут! ⏱️", parse_mode='Markdown')
            await query.message.reply_text("Хочешь заказать ещё?", reply_markup=main_menu_keyboard())
        except Exception as e:
            logger.error(f"Ошибка при повторении заказа: {str(e)}")
            await query.edit_message_text(f"😓 Не удалось оформить заказ. Попробуйте позже!")
            await query.message.reply_text("Выбери действие:", reply_markup=main_menu_keyboard())
        return

    stage = user_data.get('stage', 'drink')

    # Выбор напитка
    if stage == 'drink' and query.data.startswith('drink_'):
        drink_id = query.data.replace('drink_', '')
        user_data['drink'] = drink_id
        user_data['stage'] = 'type'
        await query.edit_message_text(
            "Выбери вид напитка:" if drink_id != 'season_menu' else "Выбери сезонный напиток:",
            reply_markup=drink_type_keyboard(drink_id)
        )

    # Выбор типа напитка
    elif stage == 'type':
        if query.data.startswith('type_'):
            user_data['drink_type'] = query.data.replace('type_', '')
            if user_data['drink'] == 'season_menu':
                await process_order(query, user_data)  # Сразу подтверждаем для сезонного
            else:
                user_data['stage'] = 'volume'
                await query.edit_message_text("Выбери объём:", reply_markup=volume_keyboard())
        elif query.data == 'back_to_drink':
            user_data['stage'] = 'drink'
            user_data.pop('drink', None)
            await query.edit_message_text("Выбери напиток:", reply_markup=drink_keyboard())
    # Выбор объёма (только для кофе и чая)
    elif stage == 'volume':
        if query.data.startswith('volume_'):
            user_data['volume'] = query.data.replace('volume_', '')
            user_data['additives'] = []
            user_data['stage'] = 'additives'
            await query.edit_message_text("Выбери добавки:", reply_markup=additives_keyboard())
        elif query.data == 'back_to_type':
            user_data['stage'] = 'type'
            user_data.pop('volume', None)
            await query.edit_message_text(
                "Выбери вид напитка:",
                reply_markup=drink_type_keyboard(user_data['drink'])
            )

    # Выбор добавок (только для кофе и чая)
    elif stage == 'additives':
        if query.data.startswith('additive_'):
            additive = query.data.replace('additive_', '')
            if additive not in user_data['additives']:
                user_data['additives'].append(additive)
            else:
                user_data['additives'].remove(additive)
            await query.edit_message_text(
                "Выбери добавки (можно несколько):",
                reply_markup=additives_keyboard(user_data['additives'])
            )
        elif query.data == 'confirm_additives':
            await process_order(query, user_data)
        elif query.data == 'back_to_volume':
            user_data['stage'] = 'volume'
            user_data.pop('additives', None)
            await query.edit_message_text("Выбери объём:", reply_markup=volume_keyboard())

async def process_order(query, user_data):
    drink = user_data.get('drink', 'напиток')
    drink_type = user_data.get('drink_type', '')
    volume = user_data.get('volume', '')
    additives = user_data.get('additives', [])

    # Формирование текста заказа
    drink_label = next((item['order_label'] for item in MENU['drinks'] if item['id'] == drink), drink)
    type_label = next((item['order_label'] for item in MENU['drink_types'].get(drink, []) if item['id'] == drink_type), drink_type)
    volume_label = next((item['order_label'] for item in MENU['volumes'] if item['id'] == volume), '') if volume else ''
    additives_text = [next((item['order_label'] for item in MENU['additives'] if item['id'] == additive), additive) for additive in additives]

    additives_display = "без добавок" if not additives_text else "с " + ", ".join(additives_text)
    if drink == 'season_menu':
        full_order = f"{type_label}"
    else:
        full_order = f"{drink_label} {type_label} {volume_label} {additives_display}".strip()

    try:
        response = requests.post(
            f'{API_BASE_URL}/api/makeOrder',
            json={'tg_id': query.from_user.id, 'company': COMPANY_UNIQUE_ID, 'order': full_order},
            timeout=5
        )
        response.raise_for_status()
        await query.edit_message_text(
            f"✅ *Ваш заказ*: {full_order}!\nПриготовим в течение 5 минут! ⏱️",
            parse_mode='Markdown'
        )
        await query.message.reply_text("Хочешь заказать ещё?", reply_markup=main_menu_keyboard())
    except Exception as e:
        logger.error(f"Ошибка заказа: {str(e)}")
        await query.edit_message_text(f"😓 Не удалось оформить заказ. Попробуй позже!")
        await query.message.reply_text("Выбери действие:", reply_markup=main_menu_keyboard())

    user_data.clear()

def main():
    if not TELEGRAM_TOKEN:
        logger.error("TELEGRAM_TOKEN не задан.")
        print("Ошибка: TELEGRAM_TOKEN не задан.")
        return

    logger.info("Starting bot...")
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    # Добавляем обработчики
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.Regex(r'^Привет'), start))
    app.add_handler(MessageHandler(filters.Regex(r'^Сделать заказ'), start_order))
    app.add_handler(MessageHandler(filters.Regex(r'^Последний заказ'), last_order))
    app.add_handler(CallbackQueryHandler(handle_button))
    app.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND,
        lambda update, ctx: update.message.reply_text("Используй кнопки:", reply_markup=main_menu_keyboard())
    ))

    # Удаляем вебхук перед запуском
    loop = asyncio.get_event_loop()
    if loop.is_running():
        logger.warning("Event loop already running. Creating new loop.")
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    loop.run_until_complete(app.bot.delete_webhook(drop_pending_updates=True))

    # Запускаем поллинг
    logger.info("Polling started")
    app.run_polling(timeout=30, drop_pending_updates=True)

if __name__ == '__main__':
    main()