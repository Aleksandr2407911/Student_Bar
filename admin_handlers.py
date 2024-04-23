from aiogram import Router
from aiogram.filters import Command, CommandStart
from aiogram.types import (InlineKeyboardButton, InlineKeyboardMarkup, Message,
                           KeyboardButton, ReplyKeyboardMarkup, CallbackQuery)
from filters import is_admin_filter
from aiogram import F
import push_pull_to_DB
import xlsx_parse
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.context import FSMContext

# Инициализируем роутер уровня модуля
router = Router()

# Ставим фильтр для роутера уровня модуля
router.message.filter(is_admin_filter)


# Создаем объекты кнопок главного меню
button_1 = KeyboardButton(text='Добавить меню 🍲')
button_2 = KeyboardButton(text='Подтверждение заказов 🕐')

# Создаем объект клавиатуры и добавляем кнопки главного меню
keyboard_main = ReplyKeyboardMarkup(
    keyboard=[[button_1], [button_2]], resize_keyboard=True)


'''#Создаем объекты кнопок списка заказов нужно взять из базы данных
list_buttons = []
for i in range():
    button = [KeyboardButton(text='НОМЕР ЗАКАЗА')] # нужно взять из базы номер заказа и вписать в название кнопки
    list_buttons.append(button)

# Создаем объект клавиатуры для списка заказов
keyboard_orders = ReplyKeyboardMarkup(keyboard=list_buttons)'''


# Этот хэндлер будет срабатывать на кнопку '/start'
# и отправлять в чат клавиатуру главного меню
@router.message(CommandStart())
async def process_start_command(message: Message):
    await message.answer(text='Hi!', reply_markup=keyboard_main)


# Этот хэндлер срабатывает на сообщение <Добавить меню 🍲>
# Обновляет БД (таблицу продуктов и категорий) при нажатии
@router.message(F.text == 'Добавить меню 🍲')
async def deny_accept_order(message: Message):
    actual_day_menu_F = xlsx_parse.find_daily_menu()
    push_pull_to_DB.for_update_menu_button(
        'product', 'categories', actual_day_menu_F)
    await message.answer('Меню добавлено')

def modify_string_to_correct_size(string):
    """
    Функция, которая принимает строку, проверяет ее размер,
    если он больше 64 байт, то сокращает ее и возвращает,
    если меньше, то просто возвращает
    """
    string = str(string)
    if len(string.encode("utf-8")) > 64:
        string = string[:27] + '...'
    return string

# Функция для создания словарей под категории для будущего использования в инлайн кнопках (на основе БД)
def compose_dc_for_orders():
    """
    Создает словарь, на основе БД таблицы orders, типа {ключ(callback): значение(text)}
    Цели создание словаря: удобство создавать кнопки и их callback, а также при нажатии кнопки быстро находит значение
    Впереди ключа ставлю o_ сокращено order_, для дальнейшего удобство при ловле в хендлер
    """
    list_for_dc = push_pull_to_DB.fetch_orders_from_table()
    dc_for_orders = {}
    count = 0
    print(list_for_dc)

    for i in list_for_dc:
        count += 1
        dc_for_orders[modify_string_to_correct_size(
            f"o_{count}")] = modify_string_to_correct_size(i['id'])
    print(dc_for_orders)
    return dc_for_orders


# Функция создает клавиатуру на основе словаря про orders
async def build_inline_keyboard_for_orders(buttons):
    """
    Сначала создает элемент клавиатуры keyboard_list
    Проходит по словарю с методом items()
    Добавляет в клавиатуру текст и callback
    Возвращает клавиатру.
    .adjust(2) - указывает, что кнопок будет 2 в ряд
    .as_markup() - обязательно писать в конце, иначе работать не будет
    """
    keyboard_list = InlineKeyboardBuilder()
    for callback, text in buttons.items():
        keyboard_list.add(InlineKeyboardButton(
            text=text, callback_data=callback))
    print('клавиатура создана')
    return keyboard_list.adjust(1).as_markup()


# Этот хэндлер срабатывает на сообщение <Подтверждение заказов 🕐>
@router.message(F.text == 'Подтверждение заказов 🕐')
async def deny_accept_order(message: Message):
    print('хэндлер сработал')
    await message.answer(text='Подтверждение заказов 🕐', reply_markup=await build_inline_keyboard_for_orders(compose_dc_for_orders()))


# Клавиатура подтверждения и удаления заказа
button_confirm_order = InlineKeyboardButton(text='Подтвердить заказ', callback_data='confirm')
button_deny_order = InlineKeyboardButton(text='Отклонить заказ', callback_data='deny')

keyboard_cd_order = InlineKeyboardMarkup(inline_keyboard=[[button_confirm_order], [button_deny_order]])

# Этот хэндлер срабатывает на нажатие кнопки заказа 
# И отображает все его информацию с двумя кнопками принять, отклонись с комментарием
@router.callback_query(lambda callback: callback.data.startswith('o_'))
async def reply_to_order(callback: CallbackQuery, state: FSMContext):
    await state.update_data(data_product=callback.data)
    await callback.answer()
    await callback.message.edit_text(text='Ответить на заказ', reply_markup=keyboard_cd_order)