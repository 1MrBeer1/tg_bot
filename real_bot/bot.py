from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, CallbackQueryHandler, MessageHandler, filters
import requests
import logging

# Настройка логирования
logging.basicConfig(
    filename='bot.log',
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Константы
TELEGRAM_TOKEN = "7519915111:AAHVz5vBRDYiwaZrC22yMFHBqygUaBfV-JU"  # Замени на свой токен
COMPANY_UNIQUE_ID = 1

# Гибкое меню
MENU = {
    'drinks': [
        {'id': 'coffee', 'label': '☕ Кофе', 'order_label': 'кофе'},
        {'id': 'tea', 'label': '🍵 Чай', 'order_label': 'чай'},
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
    },
    'additives': [
        {'id': 'sugar', 'label': 'Сахар 🧂', 'order_label': 'сахаром'},
        {'id': 'cinnamon', 'label': 'Корица 🌰', 'order_label': 'корицей'},
        {'id': 'vanilla_syrup', 'label': 'Ванильный сироп 🍯', 'order_label': 'ванильным сиропом'},
        {'id': 'caramel_syrup', 'label': 'Карамельный сироп', 'order_label': 'карамельным сиропом'},
        {'id': 'chocolate_syrup', 'label': 'Шоколадный сироп', 'order_label': 'шоколадным сиропом'},
        {'id': 'maple_syrup', 'label': 'Кленовый сироп', 'order_label': 'кленовым сиропом'},
    ],
}


# Главное меню
def main_menu_keyboard():
    return ReplyKeyboardMarkup(
        [
            [KeyboardButton("Привет 😊"), KeyboardButton("Сделать заказ ☕")]
        ],
        resize_keyboard=True,
        one_time_keyboard=False
    )


# Клавиатура с напитками
def drink_keyboard():
    buttons = [
        [InlineKeyboardButton(item['label'], callback_data=f"drink_{item['id']}") for item in MENU['drinks'][i:i + 2]]
        for i in range(0, len(MENU['drinks']), 2)
    ]
    buttons.append([
        InlineKeyboardButton("❌ Отмена", callback_data='cancel')
    ])
    return InlineKeyboardMarkup(buttons)


# Клавиатура с видами напитка
def drink_type_keyboard(drink_id):
    buttons = [
        [InlineKeyboardButton(item['label'], callback_data=f"type_{item['id']}") for item in
         MENU['drink_types'][drink_id][i:i + 2]]
        for i in range(0, len(MENU['drink_types'][drink_id]), 2)
    ]
    buttons.append([
        InlineKeyboardButton("⬅️ Назад", callback_data='back_to_drink'),
        InlineKeyboardButton("❌ Отмена", callback_data='cancel')
    ])
    return InlineKeyboardMarkup(buttons)


# Клавиатура с добавками (множественный выбор)
def additives_keyboard(selected_additives=None):
    selected_additives = selected_additives or []
    buttons = [
        [
            InlineKeyboardButton(
                f"{'✅ ' if item['id'] in selected_additives else ''}{item['label']}",
                callback_data=f"additive_{item['id']}"
            ) for item in MENU['additives'][i:i + 2]
        ] for i in range(0, len(MENU['additives']), 2)
    ]
    buttons.append([InlineKeyboardButton("Без добавок ✖️", callback_data='no_additives')])
    buttons.append([
        InlineKeyboardButton("⬅️ Назад", callback_data='back_to_type'),
        InlineKeyboardButton("Подтвердить ✅", callback_data='confirm_additives'),
        InlineKeyboardButton("❌ Отмена", callback_data='cancel')
    ])
    return InlineKeyboardMarkup(buttons)


async def hello(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        f'Привет, *{update.effective_user.first_name}*! 😊 Чем могу помочь?',
        reply_markup=main_menu_keyboard(),
        parse_mode='Markdown'
    )


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        res = requests.post(
            'http://192.168.56.1:8000/api/validate/check/checkUser',
            json={'telId': update.message.from_user.id},
            timeout=5
        )
        logger.info(f"API /validate/check/checkUser response: {res.status_code}")
        greeting = "Рад тебя видеть! 👋" if res.status_code == 200 else "Добро пожаловать! 🎉"
        await update.message.reply_text(
            f'{greeting} *{update.effective_user.first_name}*!',
            reply_markup=main_menu_keyboard(),
            parse_mode='Markdown'
        )
    except Exception as e:
        logger.error(f"Ошибка в /start: {str(e)}")
        await update.message.reply_text(
            '😓 Что-то пошло не так. Попробуй позже!',
            reply_markup=main_menu_keyboard()
        )


async def start_order(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    context.user_data.clear()
    context.user_data['stage'] = 'drink'
    await update.message.reply_text(
        'Выбери напиток:',
        reply_markup=drink_keyboard()
    )


async def handle_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_data = context.user_data

    # Отмена заказа
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

    # Обработка этапов
    stage = user_data.get('stage', 'drink')

    # Этап: выбор напитка
    if stage == 'drink' and query.data.startswith('drink_'):
        user_data['drink'] = query.data.replace('drink_', '')
        user_data['stage'] = 'type'
        await query.edit_message_text(
            text="Выбери вид напитка:",
            reply_markup=drink_type_keyboard(user_data['drink'])
        )

    # Этап: выбор вида напитка
    elif stage == 'type':
        if query.data.startswith('type_'):
            user_data['drink_type'] = query.data.replace('type_', '')
            user_data['additives'] = user_data.get('additives', [])
            user_data['stage'] = 'additives'
            await query.edit_message_text(
                text="Выбери добавки (можно несколько):",
                reply_markup=additives_keyboard(user_data['additives'])
            )
        elif query.data == 'back_to_drink':
            user_data['stage'] = 'drink'
            await query.edit_message_text(
                text="Выбери напиток:",
                reply_markup=drink_keyboard()
            )

    # Этап: выбор добавок
    elif stage == 'additives':
        if query.data.startswith('additive_'):
            additive = query.data.replace('additive_', '')
            if additive not in user_data['additives']:
                user_data['additives'].append(additive)
            else:
                user_data['additives'].remove(additive)
            await query.edit_message_text(
                text="Выбери добавки (можно несколько):",
                reply_markup=additives_keyboard(user_data['additives'])
            )
        elif query.data == 'back_to_type':
            user_data['stage'] = 'type'
            await query.edit_message_text(
                text="Выбери вид напитка:",
                reply_markup=drink_type_keyboard(user_data['drink'])
            )
        elif query.data == 'no_additives':
            user_data['additives'] = []
            await process_additives(query, user_data)
        elif query.data == 'confirm_additives':
            await process_additives(query, user_data)


async def process_additives(query, user_data):
    drink = user_data.get('drink', 'напиток')
    drink_type = user_data.get('drink_type', '')
    additives = user_data.get('additives', [])

    # Формирование текста заказа
    drink_label = next((item['order_label'] for item in MENU['drinks'] if item['id'] == drink), drink)
    type_label = next((item['order_label'] for item in MENU['drink_types'].get(drink, []) if item['id'] == drink_type),
                      drink_type)
    additives_text = []
    for additive in additives:
        additive_label = next((item['order_label'] for item in MENU['additives'] if item['id'] == additive), additive)
        additives_text.append(additive_label)

    additives_display = "без добавок" if not additives_text else "с " + ", ".join(additives_text)
    full_order = f"{drink_label} {type_label} {additives_display}"

    try:
        response = requests.post(
            'http://192.168.56.1:8000/api/makeOrder',
            json={
                'tg_id': query.from_user.id,
                'company': COMPANY_UNIQUE_ID,
                'order': full_order
            },
            timeout=5
        )
        response.raise_for_status()
        logger.info(f"API /makeOrder success: {full_order}, status: {response.status_code}")
        await query.edit_message_text(
            text=f"✅ *Ваш заказ*: {full_order.capitalize()}!\nПриготовим в течение 5 минут! ⏱️",
            reply_markup=None,
            parse_mode='Markdown'
        )
        await query.message.reply_text(
            "Хочешь заказать что-то ещё? 😊",
            reply_markup=main_menu_keyboard()
        )
    except Exception as e:
        logger.error(f"Ошибка при оформлении заказа: {str(e)}")
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
    if not TELEGRAM_TOKEN:
        logger.error("TELEGRAM_TOKEN не задан. Укажите TELEGRAM_TOKEN в коде.")
        print("Ошибка: TELEGRAM_TOKEN не задан. Укажите TELEGRAM_TOKEN в коде.")
        return

    # Настройка прокси (раскомментируй, если нужно)
    # proxy = {"https": "http://your_proxy:port"}
    # app = ApplicationBuilder().token(TELEGRAM_TOKEN).http_client_kwargs({"proxies": proxy}).build()

    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

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