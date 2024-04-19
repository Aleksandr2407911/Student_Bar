from aiogram import Router
from aiogram.filters import Command, CommandStart
from aiogram.types import (InlineKeyboardButton, InlineKeyboardMarkup, Message,
                           KeyboardButton, ReplyKeyboardMarkup, CallbackQuery)
import xlsx_parse
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
import push_pull_to_DB
from aiogram import F
from aiogram.utils.keyboard import InlineKeyboardBuilder

# инициализируем роутер уровня модуля
router = Router()

# Класс для использования FSMContext, помогает запомнить категорию продукта


class register_commands(StatesGroup):
    category_name = State()


# Создаем объект кнопок главного меню
button_1 = KeyboardButton(text='Меню 🍲')
button_2 = KeyboardButton(text='Корзина 🧺')
button_3 = KeyboardButton(text='Мои заказы 🕐')

# Создаем объект клавиатуры и добавляем кнопки главного меню
Keyboard = ReplyKeyboardMarkup(
    keyboard=[[button_1], [button_2], [button_3]], resize_keyboard=True)

# Клавиатура под кнопки, которые внутри каждого продукта
button_add = InlineKeyboardButton(
    text='Добавить в корзину', callback_data='add_to_thebin')
button_go_products = InlineKeyboardButton(text='Назад', callback_data='back_p')
keyboard_add_products = InlineKeyboardMarkup(
    inline_keyboard=[[button_add, button_go_products]])


def modify_string_to_correct_size(string):
    """
    Функция, которая принимает строку, проверяет ее размер, 
    если он больше 64 байт, то сокращает ее и возвращает,
    если меньше, то просто возвращает
    """
    if len(string.encode("utf-8")) > 64:
        string = string[:27] + '...'
    return string


# Функция для создания словарей под категории для будущего использования в инлайн кнопках (на основе БД)
def compose_dc_for_categories():
    """
    Создает слоаварь, на основе БД таблица категорий, типа {ключ(callback): значение(text)}
    Цели создание словаря: удобство создавать кнопки и их callback, а также при нажатии кнопки быстро находит значение
    Впереди ключа ставлю c_ сокращено categories_, для дальнейшего удобство при ловле в хендлер
    """
    list_for_dc = push_pull_to_DB.fetch_data_from_table('categories')
    dc_for_categories = {}
    count = 0

    for i in list_for_dc:
        count += 1
        dc_for_categories[modify_string_to_correct_size(
            f"c_{count}")] = modify_string_to_correct_size(i['category'])

    return dc_for_categories


# Функция для создания словарей под продукты для будущего использования в инлайн кнопках (на основе БД)
def compose_dc_products_in_exact_category(category_name):
    """
    Создает слоаварь, на основе БД таблица категорий, типа {ключ(callback): значение(text)}
    Цели создание словаря: удобство создавать кнопки и их callback, а также при нажатии кнопки быстро находит значение
    Впереди ключа ставлю p_ сокращено products_, для дальнейшего удобство при ловле в хендлер
    """
    list_for_dc = push_pull_to_DB.fetch_productlist_based_on_category(
        category_name)
    dc_for_products = {}

    for k, v in compose_dc_for_categories().items():
        if v == category_name:
            name_of_certain_category = k

    for i in list_for_dc:
        info_about_certain_product = (
            modify_string_to_correct_size(i['name']), i['price'], i['weight'])
        key = "p " + f"{name_of_certain_category} " + i['name']
        dc_for_products[modify_string_to_correct_size(
            key)] = info_about_certain_product

    return dc_for_products


# Функция создает клавиатуру на словаря про категории
async def build_inline_keyboard_for_categories(buttons):
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
    return keyboard_list.adjust(2).as_markup()


# Функция создает клавиатуру на основе словаря про продукты
async def build_inline_keyboard_for_products(buttons):
    """
    Сначала создает элемент клавиатуры keyboard_list
    Проходит по словарю с методом items() 
    Добавляет в клавиатуру текст и callback
    После for добавляет кнопку назад
    Возвращает клавиатру. 
    .adjust(2) - указывает, что кнопок будет 2 в ряд 
    .as_markup() - обязательно писать в конце, иначе работать не будет
    """
    keyboard_list = InlineKeyboardBuilder()
    for callback, text in buttons.items():
        keyboard_list.add(InlineKeyboardButton(
            text=text[0], callback_data=callback))
    back_button = InlineKeyboardButton(text="Назад", callback_data="back_c")
    keyboard_list.row(back_button)
    return keyboard_list.adjust(1).as_markup()


# Этот хэндлер будет срабатывать на кнопку '/start'
# и отправлять в чат клавиатуру главного меню
@router.message(CommandStart())
async def process_start_command(message: Message):
    await message.answer(text='Hi', reply_markup=Keyboard)


# этот хэндлер будет срабатывать на кнопку Меню 🍲
@router.message(F.text == 'Меню 🍲')
async def process_menu_command(message: Message):
    await message.answer(text='Меню 🍲', reply_markup=await build_inline_keyboard_for_categories(compose_dc_for_categories()))


# хэндлер обрабатывает все кнопки category и выводит, что находится в категории
@router.callback_query(lambda callback: callback.data.startswith('c_'))
async def get_back_from_category(callback: CallbackQuery):
    temp = compose_dc_for_categories()
    callback_data = temp[callback.data]
    await callback.answer()  # Убирает мигание инлайн кнопки
    await callback.message.edit_text(text=callback_data, reply_markup=await build_inline_keyboard_for_products(compose_dc_products_in_exact_category(callback_data)))


# хэндлер реагирует на кнопку назад
@router.callback_query(F.data == "back_c")
async def return_to_category(callback: CallbackQuery):
    await callback.answer()  # Убирает мигание инлайн кнопки
    await callback.message.edit_text(text='Меню 🍲', reply_markup=await build_inline_keyboard_for_categories(compose_dc_for_categories()))


# хэндлер реагирует на все кнопки product, выдает информацию о продукте
@router.callback_query(lambda callback: callback.data.startswith('p '))
async def get_back_data_aboutproduct(callback: CallbackQuery, state: FSMContext):
    """
    Следующие 4 строки находят название категории. Зачем?
    При нажатии категории мы теряем ее название, так как переходит вглубь по уровню, в продукты
    Чтобы достать определенную информацию о продукте, нам надо обратиться к словарю продуктов (compose_dc_products_in_exact_category)
    Этот словарь в свою очередь внутри оттакивается от категории, то есть мы не сможем физически ничего найти, не зная категорию
    Для этого я переработал словарь категорий. Его вид {c_1: 'Салаты'}
    Далее в название callback-а продукта я засовываю ключ из словаря выше. Словарь продуктов {p c_1 название продукта: 'название продукта'}
    Ловлю callback, вытаскиваю из него c_1 и на основе списка, нахожу название категории, далее уже просто создаю словарь продуктов (compose_dc_products_in_exact_category)
    """
    distinguish_category_index = callback.data.split()[1]
    dc_for_categ = compose_dc_for_categories()[distinguish_category_index]
    product = compose_dc_products_in_exact_category(dc_for_categ)
    product_info = product[callback.data]
    string = f"Название блюда: {product_info[0]}\nСтоимость: {
        product_info[1]}руб.\nКоличество\\Вес: {product_info[2]}"

    # запоминает название категории, чтобы от продукта заново вернуться к продуктам по данной категории
    await state.update_data(category=dc_for_categ)
    await callback.message.edit_text(text=string, reply_markup=keyboard_add_products)


# реагирует на кнопку назад в продуктах
@router.callback_query(F.data == "back_p")
async def return_to_products(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    # Получаем сохраненное имя категории из состояния
    category = data.get('category')
    await callback.answer()
    await callback.message.edit_text(text='Меню 🍲', reply_markup=await build_inline_keyboard_for_products(compose_dc_products_in_exact_category(category)))
