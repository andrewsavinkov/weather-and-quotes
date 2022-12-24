from telegram import Update, Bot, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters, \
    CallbackQueryHandler, CallbackContext
from credits import bot_token
from bs4 import BeautifulSoup as bs
from random import randint
import requests

app = ApplicationBuilder().token(bot_token).build()


async def hello(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f'Hello {update.effective_user.first_name}')


async def start(update, context):
    await context.bot.send_message(update.effective_chat.id, "Привет")


async def message(update, context):
    if update.message.text == 'Bob':
        await update.message.reply_text(f'{update.effective_chat.id}, Привет, bob, I was waiting for you')
    else:
        await update.message.reply_text(
            f'{update.effective_chat.id}, Привет, though you''re not bob, anyway I was waiting for you')


async def unknown(update, context):
    await update.message.reply_text("Unknown command!")


async def choose_action(update: Update, context: CallbackContext):
    keyboard = [
        [InlineKeyboardButton("Погода в Перми сейчас", callback_data='1')],
        [InlineKeyboardButton("Цитаты", callback_data='2')],
        [InlineKeyboardButton("Анекдоты", callback_data='3')],
    ]
    await update.message.reply_text('Что вам вывести на экран?', reply_markup=InlineKeyboardMarkup(keyboard))


def random_quote(update, context):
    url = 'https://finewords.ru/'
    response = requests.get(url).text
    soup = bs(response, 'html.parser')
    citate = soup.find_all('div', class_='cit')[randint(0, 249)].find('p').text
    return citate


def random_joke(update, context):
    url = 'https://anekdot.ru'
    response = requests.get(url).text
    soup = bs(response, 'html.parser')
    anekdot = soup.find_all('div', class_='text')[randint(0, 25)].text
    return anekdot


def weather(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # msg=update.message.text
    # items=msg.split()
    API_key = '4321a3d417b53045aa1b6617c529c910'
    city_name = 'Perm'
    response = requests.get(
        f"http://api.openweathermap.org/data/2.5/weather?q={city_name}&appid={API_key}&units=metric&lang=ru")
    temp = response.json()['main']
    answer = f"{temp['temp']}"
    return answer


async def button(update, context):
    global weather
    quer = update.callback_query
    await quer.answer()
    if quer.data == '1':
        weather = weather(update=Update, context=ContextTypes.DEFAULT_TYPE)
        await context.bot.send_message(update.effective_chat.id, f"Сейчас в Перми:\n{weather} °С")
    elif quer.data == '2':
        quote = random_quote(update=Update, context=ContextTypes.DEFAULT_TYPE)
        await context.bot.send_message(update.effective_chat.id, f"Цитата:\n{quote}")
    elif quer.data == '3':
        anekdot = random_joke(update=Update, context=ContextTypes.DEFAULT_TYPE)
        await context.bot.send_message(update.effective_chat.id, f"Анекдот:\n{anekdot}")


app.add_handler(CallbackQueryHandler(button))
app.add_handler(CommandHandler('hello', hello))
app.add_handler(CommandHandler('start', start))
app.add_handler(CommandHandler('action', choose_action))

app.add_handler(MessageHandler(filters.Command(), unknown))
app.add_handler(MessageHandler(filters.Text(), message))

app.run_polling()
