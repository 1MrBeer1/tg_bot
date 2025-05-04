from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, CallbackQueryHandler, MessageHandler, filters
import requests

company_unique_id = 1


# Главное меню с текстовыми кнопками
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
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("☕ Кофе", callback_data='coffee'),
         InlineKeyboardButton("🍵 Чай", callback_data='tea')]
    ])


# Клавиатура с добавками
def additives_keyboard():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("Сахар 🧂", callback_data='sugar'),
            InlineKeyboardButton("Корица 🌰", callback_data='cinnamon')
        ],
        [
            InlineKeyboardButton("Сироп 🍯", callback_data='syrup'),
            InlineKeyboardButton("Без добавок ✖️", callback_data='no_additives')
        ]
    ])


# Клавиатура с видами сиропа
def syrup_types_keyboard():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("Ванильный", callback_data='vanilla'),
            InlineKeyboardButton("Карамельный", callback_data='caramel')
        ],
        [
            InlineKeyboardButton("Шоколадный", callback_data='chocolate'),
            InlineKeyboardButton("Кленовый", callback_data='maple')
        ]
    ])


async def hello(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        f'Привет, {update.effective_user.first_name}! 😊',
        reply_markup=main_menu_keyboard()
    )


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        res = requests.post(
            'http://192.168.56.1:8000/api/validate/check/checkUser',
            json={'telId': update.message.from_user.id}
        )

        greeting = "Привет! 👋" if res.status_code == 200 else "Добро пожаловать! 🎉"
        await update.message.reply_text(
            f'{greeting} {update.effective_user.first_name}!',
            reply_markup=main_menu_keyboard()
        )

    except Exception as e:
        await update.message.reply_text('⚠️ Ошибка запуска', reply_markup=main_menu_keyboard())


async def start_order(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        'Выберите напиток:',
        reply_markup=drink_keyboard()
    )


async def handle_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_data = context.user_data

    # Обработка выбора напитка
    if query.data in ['coffee', 'tea']:
        user_data['drink'] = query.data
        await query.edit_message_text(
            text="Выберите добавки:",
            reply_markup=additives_keyboard()
        )

    # Обработка выбора добавок
    elif query.data in ['sugar', 'cinnamon', 'no_additives']:
        await process_additives(query, user_data)

    # Обработка выбора сиропа
    elif query.data == 'syrup':
        user_data['need_syrup'] = True
        await query.edit_message_text(
            text="Выберите тип сиропа:",
            reply_markup=syrup_types_keyboard()
        )

    # Обработка выбора типа сиропа
    elif query.data in ['vanilla', 'caramel', 'chocolate', 'maple']:
        user_data['syrup'] = query.data
        await process_additives(query, user_data)


async def process_additives(query, user_data):
    drink = user_data.get('drink', 'напиток')
    additives = []

    if 'syrup' in user_data:
        additives.append(f"сироп {user_data['syrup']}")
    if 'sugar' in user_data:
        additives.append("сахар")
    if 'cinnamon' in user_data:
        additives.append("корица")

    additives_text = "без добавок" if not additives else "с " + ", ".join(additives)

    try:
        full_order = f"{drink} {additives_text}"
        requests.post(
            'http://192.168.56.1:8000/api/makeOrder',
            json={
                'tg_id': query.from_user.id,
                'company': company_unique_id,
                'order': full_order
            }
        )
        await query.edit_message_text(
            text=f"✅ Ваш заказ: {full_order.capitalize()}!\nПриготовим в течение 5 минут! ⏱️",
            reply_markup=None
        )
        await query.message.reply_text(
            "Хотите что-то ещё?",
            reply_markup=main_menu_keyboard()
        )
    except Exception as e:
        await query.edit_message_text("⚠️ Ошибка оформления заказа")

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
            "Используйте кнопки меню:",
            reply_markup=main_menu_keyboard()
        )
    ))

    app.run_polling()

if __name__ == '__main__':
    main()