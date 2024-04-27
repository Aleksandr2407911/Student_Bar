import pymysql
import queries_function
import xlsx_parse
from config import load_config


config = load_config(r'/Users/aleksandrrabinskij/Desktop/Student_Bar/.env')

# выдает список меню актуального дня
actual_day_menu = xlsx_parse.find_daily_menu()


# заполняет таблицу категорий в БД на основе экселя
def fill_categories_table(actual_day_menu):
    with connection.cursor() as cursor:
        for line in actual_day_menu:
            queries_function.insert_categories(cursor, line[3])
    connection.commit()
    connection.close()


# очищает любую таблицу, которую передашь в функцию
def clear_table(table_name):
    with connection.cursor() as cursor:
        queries_function.delete_data_from_tables(cursor, table_name)
    connection.commit()
    connection.close()


# достает информацию из любой таблицу в БД в виде списка словарей
def fetch_data_from_table(table_name):
    with connection.cursor() as cursor:
        queries_function.get_rows_from_table(cursor, table_name)
    data = cursor.fetchall()
    return data


# заполняет таблицу продуктов
def fill_product_table(actual_day_menu):
    with connection.cursor() as cursor:
        for i in actual_day_menu:
            queries_function.insert_product(cursor, i)
    connection.commit()
    connection.close()


# достает информацию из таблицы продуктов на основе категории
def fetch_productlist_based_on_category(category_name):
    with connection.cursor() as cursor:
        queries_function.fetch_product_based_on_category(cursor, category_name)
    data = cursor.fetchall()
    return data


def for_update_menu_button(table_name1, table_name2, actual_day_menu):
    with connection.cursor() as cursor:
        queries_function.delete_data_from_tables(cursor, table_name1)
    connection.commit()

    with connection.cursor() as cursor:
        queries_function.delete_data_from_tables(cursor, table_name2)
    connection.commit()

    with connection.cursor() as cursor:
        for line in actual_day_menu:
            queries_function.insert_categories(cursor, line[3])
    connection.commit()

    with connection.cursor() as cursor:
        for i in actual_day_menu:
            queries_function.insert_product(cursor, i)
    connection.commit()
    connection.close()


# добавляет в таблиицу orders заказ
def insert_order_to_table(temp_bin, id, time):
    with connection.cursor() as cursor:
        queries_function.insert_order(cursor, temp_bin, id, time)
    connection.commit()
    connection.close()

# Извлекает сегодняшнии заказы из таблицы со статусом FALSE
def fetch_orders_from_table(status):
    with connection.cursor() as cursor:
        queries_function.fetch_orders(cursor, status)
    data = cursor.fetchall()
    return data

# добавляет в таблиицу users address пользователя
def insert_address_to_table(user_tg_id, address):
    with connection.cursor() as cursor:
        queries_function.delete_address(cursor, user_tg_id)
    connection.commit()
    with connection.cursor() as cursor:
        queries_function.insert_address(cursor, user_tg_id, address)
    connection.commit()
    connection.close()


try:
    # Подключение к БД MySQL
    connection = pymysql.connect(
        host='localhost',
        port=3306,
        user='root',
        password=config.db.password,
        database=config.db.database,
        cursorclass=pymysql.cursors.DictCursor
    )

    # print(fetch_data_from_table('categories'))

    # clear_table('product')
    #fill_categories_table(actual_day_menu)
    #fill_product_table(actual_day_menu)
    #clear_table('orders')
    # clear_table('categories')
    # print(fetch_productlist_based_on_category('Горячее'))
    #for_update_menu_button('product', 'categories', actual_day_menu)
    #insert_order_to_table({544595768: [{'name': 'Чизкейк-брауни', 'cost': 165}]}, 544595768, '2023-03-08 15:42:18')
    #insert_address_to_table(544345534, "Вилиса Лациса 18")
    #print(fetch_orders_from_table())


except Exception as e:
    print('Error3:', e)
