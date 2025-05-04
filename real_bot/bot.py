from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, CallbackQueryHandler, MessageHandler, filters
import requests
import logging

# Настройка логирования для отладки API
logging.basicConfig(
    filename='bot.log',
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

company_unique_id = 1

# Гибкое меню (легко обновлять)
MENU = {
    'drinks': [
        {'id': 'кофе', 'label': '☕ Кофе'},
        {'id': 'чай', 'label': '🍵 Чай'},
    ],
    'types': {
        'кофе': [
            {'id': 'эспрессо', 'label': 'Эспрессо'},
            {'id': 'латте', 'label': 'Латте'},
        ],
        'чай': [
            {'id': 'чёрный', 'label': 'Чёрный'},
            {'id': 'зелёный', 'label': 'Зелёный'},
        ],
    },
    'additives': [
        {'id': 'сахар', 'label': 'Сахар 🧂', 'order_label': 'сахаром'},
        {'id': 'корица', 'label': 'Корица 🌰', 'order_label': 'корицей'},
    ],
    'syrups': [
        {'id': 'ванильный сироп', 'label': 'Ванильный сироп 🍯', 'order_label': 'ванильным сиропом'},
        {'id': 'карамельный сироп', 'label': 'Карамельный сироп', 'order_label': 'карамельным сиропом'},
        {'id': 'шоколадный сироп', 'label': 'Шоколадный сироп', 'order_label': 'шоколадным сиропом'},
        {'id': 'кленовый сироп', 'label': 'Кленовый сироп', 'order_label': 'кленовым сиропом'},
    ],
}

# Главное меню с текстовыми кнопками
def main_menu_keyboard():
    return ReplyKeyboardMarkup(
        [
            [KeyboardButton("Привет 😊"), KeyboardButton("Сделать заказ ☕")]
        ],
        resize_keyboard=True,
        one_time_keyboard=False
    )

# Клавиатура выбора заказа (генерируется из MENU)
def order_keyboard(user_data):
    drink = user_data.get('drink', None)
    drink_type = user_data.get('drink_type', None)
    additives = user_data.get('additives', [])

    keyboard = []

    # Секция 1: Напитки
    keyboard.append([InlineKeyboardButton("🍹 Напиток", callback_data='noop')])  # Заголовок
    drink_buttons = [
        InlineKeyboardButton(
            f"{'✅ ' if drink == item['id'] else ''}{item['label']}",
            callback_data=f"drink_{item['id']}"
        ) for item in MENU['drinks']
    ]
    keyboard.append(drink_buttons)
    keyboard.append([InlineKeyboardButton("────────────", callback_data='noop')])  # Разделитель

    # Секция 2: Виды напитка
    if drink and drink in MENU['types']:
        keyboard.append([InlineKeyboardButton("📋 Вид", callback_data='noop')])  # Заголовок
        type_buttons = [
            InlineKeyboardButton(
                f"{'✅ ' if drink_type == item['id'] else ''}{item['label']}",
                callback_data=f"type_{item['id']}"
            ) for item in MENU['types'][drink]
        ]
        keyboard.append(type_buttons)
        keyboard.append([InlineKeyboardButton("────────────", callback_data='noop')])  # Разделитель

    # Секция 3: Добавки и сиропы
    keyboard.append([InlineKeyboardButton("🧂 Добавки", callback_data='noop')])  # Заголовок
    additive_buttons = [
        InlineKeyboardButton(
            f"{'✅ ' if item['id'] in additives else ''}{item['label']}",
            callback_data=f"additive_{item['id']}"
        ) for item in MENU['additives']
    ]
    keyboard.append(additive_buttons)
    syrup_buttons = [
        [
            InlineKeyboardButton(
                f"{'✅ ' if item['id'] in additives else ''}{item['label']}",
                callback_data=f"additive_{item['id']}"
            ) for item in MENU['syrups'][i:i+2]
        ] for i in range(0, len(MENU['syrups']), 2)
    ]
    keyboard.extend(syrup_buttons)
    keyboard.append([InlineKeyboardButton("────────────", callback_data='noop')])  # Разделитель

    # Кнопки подтверждения и отмены
    keyboard.append([
        InlineKeyboardButton("Подтвердить ✅", callback_data='confirm'),
        InlineKeyboardButton("❌ Отмена", callback_data='cancel')
    ])

    return InlineKeyboardMarkup(keyboard)

async def hello(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        f'Привет, {update.effective_user.first_name}! 😊',
        reply_markup=main_menu_keyboard()
    )

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        res = requests.post(
            'http://192.168.56.1:8000/api/validate/check/checkUser',
            json={'telId': update.message.from_user.id},
            timeout=5
        )
        logger.info(f"API /validate/check/checkUser response: {res.status_code}")
        greeting = "Привет! 👋" if res.status_code == 200 else "Добро пожаловать! 🎉"
        await update.message.reply_text(
            f'{greeting} {update.effective_user.first_name}!',
            reply_markup=main_menu_keyboard()
        )
    except Exception as e:
        logger.error(f"Ошибка в /start: {str(e)}")
        await update.message.reply_text(
            '⚠️ Ошибка запуска. Попробуй позже!',
            reply_markup=main_menu_keyboard()
        )

async def start_order(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    context.user_data.clear()  # Очистка данных перед новым заказом
    await update.message.reply_text(
        'Собери свой заказ:',
        reply_markup=order_keyboard(context.user_data)
    )

async def handle_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_data = context.user_data

    # Игнорировать заголовки
    if query.data == 'noop':
        return

    # Обработка отмены
    if query.data == 'cancel':
        user_data.clear()
        await query.edit_message_text(
            text="Заказ отменён. Хочешь начать заново?",
            reply_markup=None
        )
        await query.message.reply_text(
            "Выбери действие:",
            reply_markup=main_menu_keyboard()
        )
        return

    # Обработка выбора напитка
    if query.data.startswith('drink_'):
        user_data['drink'] = query.data.split('_')[1]
        user_data.pop('drink_type', None)  # Сбрасываем вид напитка
        await query.edit_message_text(
            text="Собери свой заказ:",
            reply_markup=order_keyboard(user_data)
        )

    # Обработка выбора вида напитка
    elif query.data.startswith('type_'):
        user_data['drink_type'] = query.data.split('_')[1]
        await query.edit_message_text(
            text="Собери свой заказ:",
            reply_markup=order_keyboard(user_data)
        )

    # Обработка выбора добавок и сиропов
    elif query.data.startswith('additive_'):
        additive = query.data.replace('additive_', '')  # Убираем префикс
        user_data['additives'] = user_data.get('additives', [])
        if additive in user_data['additives']:
            user_data['additives'].remove(additive)
        else:
            user_data['additives'].append(additive)
        await query.edit_message_text(
            text="Собери свой заказ:",
            reply_markup=order_keyboard(user_data)
        )

    # Подтверждение заказа
    elif query.data == 'confirm':
        if not user_data.get('drink') or not user_data.get('drink_type'):
            await query.answer("Пожалуйста, выбери напиток и его вид!", show_alert=True)
            return
        await process_order(query, user_data)

async def process_order(query, user_data):
    drink = user_data.get('drink', 'напиток')
    drink_type = user_data.get('drink_type', '')
    additives = user_data.get('additives', [])

    # Формирование текста добавок
    additives_text = []
    for additive in additives:
        # Ищем order_label в additives или syrups
        for item in MENU['additives'] + MENU['syrups']:
            if item['id'] == additive:
                additives_text.append(item['order_label'])
                break

    additives_display = "без добавок" if not additives_text else "с " + ", ".join(additives_text)
    # Формат: "кофе эспрессо с сахаром, корицей, ванильным сиропом"
    full_order = f"{drink} {drink_type} {additives_display}"

    try:
        response = requests.post(
            'http://192.168.56.1:8000/api/makeOrder',
            json={
                'tg_id': query.from_user.id,
                'company': company_unique_id,
                'order': full_order
            },
            timeout=5
        )
        response.raise_for_status()
        logger.info(f"API /makeOrder success: {full_order}, status: {response.status_code}")
        await query.edit_message_text(
            text=f"✅ Ваш заказ: *{full_order.capitalize()}*!\nПриготовим в течение 5 минут! ⏱️",
            reply_markup=None,
            parse_mode='Markdown'
        )
        await query.message.reply_text(
            "Хочешь заказать что-то ещё? 😊",
            reply_markup=main_menu_keyboard()
        )
    except requests.exceptions.RequestException as e:
        logger.error(f"Ошибка API /makeOrder: {str(e)}")
        await query.edit_message_text(
            text=f"😓 Не удалось оформить заказ: {str(e)}. Попробуй позже!",
            reply_markup=None
        )
        await query.message.reply_text(
            "Выбери действие:",
            reply_markup=main_menu_keyboard()
        )

    user_data.clear()

def main():
    app = ApplicationBuilder().token("7519915111:AAHVz5vBRDYiwaZrC22yMFHBqygUaBfV-JU").build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.Regex(r'^Привет'), hello))
    app.add_handler(MessageHandler(filters.Regex(r'^Сделать заказ'), start_order))
    app.add_handler(CallbackQueryHandler(handle_button))

    app.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND,
        lambda update, ctx: update.message.reply_text(
            "Пожалуйста, используй кнопки меню:",
            reply_markup=main_menu_keyboard()
        )
    ))

    print("Бот запущен...")
    app.run_polling()

if __name__ == '__main__':
    main()