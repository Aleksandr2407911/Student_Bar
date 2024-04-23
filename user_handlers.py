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
import asyncio
import datetime

# инициализируем роутер уровня модуля
router = Router()



class register_commands(StatesGroup):
    category_name = State()


# Создаем объект кнопок главного меню
button_1 = KeyboardButton(text='Меню 🍲')
button_2 = KeyboardButton(text='Корзина 🧺')
button_3 = KeyboardButton(text='Мои заказы 🕐')

# Создаем объект клавиатуры и добавляем кнопки главного меню
Keyboard = ReplyKeyboardMarkup(
    keyboard=[[button_1], [button_2], [button_3]], resize_keyboard=True)


button_add = InlineKeyboardButton(text='Добавить в корзину', callback_data='add_to_the_bin')
button_go_products = InlineKeyboardButton(text='Назад', callback_data='back_p')

keyboard_add_products = InlineKeyboardMarkup(inline_keyboard=[[button_add, button_go_products]])


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
            modify_string_to_correct_size(i['name']), i['price'], i['weight'], i['picture'])
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
    string = f"Название блюда: {product_info[0]}\nСтоимость: {product_info[1]}руб.\nКоличество\\Вес: {product_info[2]}"

    await state.update_data(category=dc_for_categ, data_product={'name': product_info[0],
                                                                 'cost': product_info[1]})
    await callback.answer()
    # отправляет новое сообщение с фоткой и характеристиками продукта
    await callback.message.answer_photo(photo=product_info[3], caption=string, reply_markup=keyboard_add_products)


# реагирует на кнопку назад в продуктах
@router.callback_query(F.data == "back_p")
async def return_to_products(callback: CallbackQuery):
    """
    При нажатии кнопки назад удаляет сообщение с фоткой и характеристиками продукта
    """
    await callback.answer()
    await callback.message.delete()





# Временное хранилице корзины пользователей {id1: [{}, {}], id2: […]}
#{544595768: [{'name': 'Салат «Цезарь» с курицей', 'cost': 182}, {'name': 'Салат «Метелка»', 'cost': 65}]}
temp_bin = {}

@router.callback_query(F.data == "add_to_the_bin")
async def add_to_the_bin(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    # Получаем сохраненное имя категории из состояния
    data_product = data.get('data_product')
    await callback.answer('Продукт добавлен в корзину')
    temp_bin.setdefault(callback.from_user.id, []).append(data_product)
    print(temp_bin)


# USER BIN
button_change_prod = InlineKeyboardButton(text='Изменить продукты 🍲', callback_data='change_products')
button_to_order = InlineKeyboardButton(text='Отправить заказ 🧺', callback_data='to_order')

keyboard_bin = InlineKeyboardMarkup(inline_keyboard=[[button_change_prod], [button_to_order]])


@router.message(F.text == 'Корзина 🧺')
async def return_to_bin(message: Message):
    await message.answer(text='Корзина 🧺', reply_markup= keyboard_bin)


# Функция создает клавиатуру для корзины на основе словаря (временного хранилища)
async def build_inline_keyboard_for_bin(temp_bin, id):
    """
    Сначала создает элемент клавиатуры keyboard_list
    Проходит по словарю с методом items()
    Добавляет в клавиатуру текст и callback
    Возвращает клавиатру.
    .adjust(2) - указывает, что кнопок будет 2 в ряд
    .as_markup() - обязательно писать в конце, иначе работать не будет
    """
    keyboard_list = InlineKeyboardBuilder()
    for product in temp_bin[id]:
        keyboard_list.add(InlineKeyboardButton(text=f"{product['name']}/{product['cost']}", callback_data=f"_bin{product['name']}"))
    back_button = InlineKeyboardButton(text="Назад", callback_data="back_to_bin_menu")
    keyboard_list.row(back_button)
    return keyboard_list.adjust(2).as_markup()



# Функция будет считать сумму покупки, принимает на вход id пользователя и временную корзину
# Возвтращает сумму заказа
async def amount_bin(temp_bin, id):
    amount = 0
    for product in temp_bin[id]:
        amount += product['cost']
    return amount


@router.callback_query(F.data == "change_products")
async def change_prosucts(callback: CallbackQuery, state: FSMContext):
    if callback.from_user.id in temp_bin:
        temp_amount = amount_bin(temp_bin, callback.from_user.id)
        await callback.answer()  # Убирает мигание инлайн кнопки
        await callback.message.edit_text(text=f'Общая стоимость: {await temp_amount}',
                                        reply_markup=await build_inline_keyboard_for_bin(temp_bin, callback.from_user.id))
    else:
        await callback.answer(text='В корзине ничего нет', show_alert=True)



@router.callback_query(F.data == "back_to_bin_menu")
async def return_to_bin_menu(callback: CallbackQuery, state: FSMContext):
    #data = await state.get_data()
    # Получаем сохраненное имя категории из состояния
    #category = data.get('category')
    await callback.answer()
    await callback.message.edit_text(text='Корзина 🧺', reply_markup= keyboard_bin)




# Клавиатура для удаления и go_back корзины
button_delete_prod = InlineKeyboardButton(text='Удалить из корзины', callback_data='delete_products')
button_go_back_to_products_bin = InlineKeyboardButton(text='Назад', callback_data='go_back_to_products_bin')

keyboard_delete_product = InlineKeyboardMarkup(inline_keyboard=[[button_delete_prod], [button_go_back_to_products_bin]])


@router.callback_query(lambda callback: callback.data.startswith('_bin'))
async def delete_product_from_bin_menu(callback: CallbackQuery, state: FSMContext):
    await state.update_data(data_product= callback.data)
    await callback.answer()
    await callback.message.edit_text(text='Удалить продукт', reply_markup= keyboard_delete_product)

# Функция для удаления продукта при нажатии на кнопку 'удалить продукт'
# Удаляет продукт по названию
async def delete_product(name, user_id):
    count = -1
    for product in temp_bin[user_id]:
        count += 1
        if name == f"_bin{product.get('name', 'no')}":
            temp_bin[user_id].pop(count)
            print(f"продукт {product['name']} удален")
            break
    print("Ничего не удалилось")



@router.callback_query(F.data == "delete_products")
async def delete_product_from_bin(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    # Получаем сохраненное имя продукта из состояния
    name = data.get('data_product')
    await delete_product(name, callback.from_user.id)
    print(temp_bin) #{544595768: [{'name': 'Шаурма с курицей', 'cost': 196}]}
    print(name) #_binШаурма с курицей
    temp_amount = amount_bin(temp_bin, callback.from_user.id) # не нужно await
    await callback.answer(text="Продукт удален из корзины")
    await callback.message.edit_text(text=f'Общая стоимость: {await temp_amount}',
                                     reply_markup=await build_inline_keyboard_for_bin(temp_bin, callback.from_user.id))




@router.callback_query(F.data == "go_back_to_products_bin")
async def return_to_bin_menu(callback: CallbackQuery, state: FSMContext):
    #data = await state.get_data()
    # Получаем сохраненное имя категории из состояния
    #category = data.get('category')
    # Получаем сохраненное имя продукта из состояния
    temp_amount = amount_bin(temp_bin, callback.from_user.id) # не нужно await
    await callback.answer('Назад')
    await callback.message.edit_text(text=f'Общая стоимость: {await temp_amount}',
                                     reply_markup=await build_inline_keyboard_for_bin(temp_bin, callback.from_user.id))
    

@router.callback_query(F.data == 'to_order')
async def send_products_to_order(callback: CallbackQuery, state: FSMContext):
    now_datetime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    push_pull_to_DB.insert_order_to_table(temp_bin, callback.from_user.id, now_datetime)
    del temp_bin[callback.from_user.id]