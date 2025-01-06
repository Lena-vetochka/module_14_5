# -*- coding: utf-8 -*-
from distutils.command.check import check

from  aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.dispatcher import FSMContext
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
import asyncio

from crud_functions import get_all_products, is_included, add_user


api = ''
bot = Bot(token = api)
dp = Dispatcher(bot, storage = MemoryStorage())


kb = ReplyKeyboardMarkup(resize_keyboard=True)
button_ = KeyboardButton(text = 'Рассчитать')
button1_ = KeyboardButton(text = 'Информация')
button2_ = KeyboardButton(text = 'Купить')
button3_= KeyboardButton(text = 'Регистрация')
kb.row(button_, button1_)
kb.row(button3_, button2_)

kb2 = InlineKeyboardMarkup(resize_keyboard = True)
button = InlineKeyboardButton(text = 'Рассчитать норму калорий', callback_data= 'calories')
button2 = InlineKeyboardButton(text = 'Формулы расчёта', callback_data= 'formulas')
kb2.row(button, button2)

kb3 = InlineKeyboardMarkup(
    inline_keyboard= [
        [InlineKeyboardButton(text= 'Продукт 1', callback_data= 'product_buying'),
        InlineKeyboardButton(text= 'Продукт 2', callback_data= 'product_buying'),
        InlineKeyboardButton(text= 'Продукт 3', callback_data= 'product_buying'),
        InlineKeyboardButton(text= 'Продукт 4', callback_data= 'product_buying')]
    ], resize_keyboard = True
)


class UserState(StatesGroup):  #собираем данные
    age = State()
    growth = State()
    weight = State()


class RegistrationState(StatesGroup):
    username = State()
    email = State()
    age = State()
    balance = 1000


@dp.message_handler(commands= ['start'])
async def start_message(message):
    await message.answer('Привет! Я бот помогающий здоровью.', reply_markup = kb )


@dp.message_handler(text = 'Рассчитать')
async def main_menu(message):
    await message.answer('Выберите опцию:', reply_markup = kb2)


@dp.message_handler(text = 'Регистрация')
async def sing_up(message):
    await message.answer('Введите имя пользователя (только латинский алфавит):')
    await RegistrationState.username.set()


@dp.message_handler(state = RegistrationState.username)
async def set_username(message, state):
    if is_included(message.text):
        await state.update_data(username = message.text)
        await message.answer('Введите свой e-mail:')
        await RegistrationState.email.set()
    else:
        await message.answer('Пользователь существует, введите другое имя')
        await RegistrationState.username.set()


@dp.message_handler(state = RegistrationState.email)
async def set_email(message, state):
    if ('@' in message.text) and ('.' in message.text): # проверим на наличие @ и точки:
        await state.update_data(email = message.text)
        await message.answer('Введите свой возраст:')
        await RegistrationState.age.set()
    else:
        await message.answer('Неверный адрес эл.почты, введите другой:')
        await RegistrationState.email.set()


@dp.message_handler(state = RegistrationState.age)
async def set_age(message, state):
    try:
        age = int(message.text)
    except:
        await message.answer(f'Введите число, свой возраст:')
        await RegistrationState.age.set()
        return set_age
    await state.update_data(age = message.text)
    data = await state.get_data()
    add_user(data['username'], data['email'], data['age'])   # добавляем в БД
    await message.answer('Регистрация прошла успешно!', reply_markup = kb )
    await state.finish()


@dp.message_handler(text = 'Купить')
async def get_buying_list(message):
    for product in get_all_products():
        await message.answer(f'Название: {product[1]} | Описание: {product[2]} | Цена: {product[3]}')
        with open(f'bot_selling_games/{product[0]}.jpg', 'rb') as img:
            await message.answer_photo(img)
    await message.answer('Выберите продукт для покупки:', reply_markup= kb3)


@dp.callback_query_handler(text = 'product_buying')
async def send_confirm_message(call):
    await call.message.answer('Вы успешно приобрели продукт!')
    await call.answer()


@dp.callback_query_handler(text= 'formulas')
async def get_formulas(call):
    await call.message.answer('10 x вес (кг) + 6,25 x рост (см) – 5 x возраст (г) – 161')
    await call.answer()


@dp.callback_query_handler(text = 'calories')
async def set_age(call):
    await call.message.answer('Введите свой возраст:')
    await UserState.age.set()   #запись возраста


@dp.message_handler()
async def all_message(message):
    await message.answer('Введите команду /start, чтобы начать общение.')


@dp.message_handler(state = UserState.age)
async def set_growth(message, state):
    try:
        await state.update_data(age = float(message.text))
    except:
        await message.answer('Введите число, свой возраст')
        return set_age()
    await message.answer('Введите свой рост в см:', )
    await UserState.growth.set()


@dp.message_handler(state = UserState.growth)
async def set_weight(message, state):
    try:
        await state.update_data(growth = float(message.text))
    except:
        await message.answer('Введите число, свой рост')
        return set_growth()
    await message.answer('Введите свой вес:')
    await UserState.weight.set()


@dp.message_handler(state = UserState.weight)
async def send_calories(message, state):
    try:
        await state.update_data(weight =float(message.text))
    except:
        await message.answer('Введите число, свой вес')
        return send_calories()
    data = await state.get_data()
    calories = (10 * data['weight'] + 6.25 * data['growth'] -
                5 * data['age'] - 161)
    await message.answer(f'Ваша норма калорий {calories}/сутки')
    await state.finish()


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates= True)
