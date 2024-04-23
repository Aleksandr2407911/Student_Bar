from datetime import date
def delete_data_from_tables(cursor, table_name):
    """
    Удаление данных из любой таблицы
    На вход подается имя таблицы
    1 запрос - удаляет данные
    2 запрос - сбрасывает значение первичного ключа
    """
    try:
        # Удаление всех данных из таблицы
        delete_query = f"""DELETE FROM {table_name}
                            WHERE id > 0;"""
        cursor.execute(delete_query)

        # Сброс автоинкрементного (первичного ключа) значения до 1
        reset_auto_increment_query = f"""ALTER TABLE {table_name}
                                        AUTO_INCREMENT = 1;"""
        cursor.execute(reset_auto_increment_query)

        return f"Таблица {table_name} очищена"
    except Exception as e:
        return f"Error2: {e}"


def get_rows_from_table(cursor, table_name):
    """
    Запрос достает все записи в таблице
    """
    try:
        fetch_query = f"""SELECT *
                         FROM {table_name}"""
        cursor.execute(fetch_query)

        return 'Все строки таблицы выведены'
    except Exception as e:
        return f"Error4: {e}"


def insert_categories(cursor, category):
    """
    Функция для таблицы categories
    При записи данных, проверяет есть ли запись в таблице,
    Если запись есть, то ничего не происходит
    Если записи нет, то запись будет добавлена
    """
    try:
        # Проверка существует ли запись в таблице
        check_query = """SELECT COUNT(*) AS count
                       FROM categories
                       WHERE category = %s"""
        cursor.execute(check_query, category)
        result = cursor.fetchone()

        # Проверка существует ли запись в таблице
        if result['count'] > 0:
            return "Запись уже существует"
        else:
            # Если записи нет, добавление записи
            insert_to_table_categories = """INSERT INTO categories (category)
                                            VALUES (%s)"""
            cursor.execute(insert_to_table_categories, category)
            return "Запись добавлена"
    except Exception as e:
        return f"Error1: {e}"


# Использовать для счетчика количесва продуктов в заказе 

def insert_product(cursor, daily_data):
    """
    Вставляет продукты в БД
    Первый запрос проверяет наличие продукта, если он есть, он не будет добавляться
    Второй запрос добавляет продукт в таблицу product
    """
    try:
        # Проверка существует ли запись в таблице
        check_query = """SELECT COUNT(*) AS count
                       FROM product
                       WHERE name = %s"""
        cursor.execute(check_query, daily_data[0])
        result = cursor.fetchone()

        # Проверка существует ли запись в таблице
        if result['count'] > 0:
            return "Запись уже существует"
        else:
            # Если записи нет, добавление записи
            insert_to_table_product = """INSERT INTO product (name, price, weight, picture, category_id)
                                            VALUES (%s, %s, %s, %s,
                                            (SELECT id
                                            FROM categories
                                            WHERE category = %s)
                                            )"""
            cursor.execute(insert_to_table_product,
                           (daily_data[0], daily_data[2], daily_data[1], daily_data[4], daily_data[3]))
            return 'ok'
    except Exception as e:
        return f"Error5: {e}"


def fetch_product_based_on_category(cursor, category):
    """
    Достает все продукты по определенной категории
    """
    try:
        category_products = """SELECT *
                            FROM product
                            WHERE category_id = (SELECT id
					                            FROM categories
                                                WHERE category = %s)"""
        cursor.execute(category_products, category)
    except Exception as e:
        return f"Error6: {e}"
    
# Функция будет считать сумму покупки, принимает на вход id пользователя и временную корзину
# Возвтращает сумму заказа
def amount_bin(temp_bin, id):
    amount = 0
    for product in temp_bin[id]:
        amount += product['cost']
    return amount

def insert_order(cursor, temp_bin, id, time):
    """
    Вставляет заказ в таблицу order, принимает временное хранилище, id пользователя и текущее время
    """
    try:
        insert_to_table_order = """INSERT INTO Orders (user_tg_id, total_price, time, status)
                                        VALUES (%s, %s, %s, 0)"""
        amount = amount_bin(temp_bin, id)
        cursor.execute(insert_to_table_order,
                        (id, amount, time))
        return 'ok'
    except Exception as e:
        return f"Error5: {e}"
    
def fetch_orders(cursor):
    """
    Достает все данные из таблицы orders опираясь на сегодняшнюю дату и статуса заказа FALSE
    """
    try:
        fetch_orders_from_table = """SELECT *
                                     FROM orders
                                     WHERE DATE(time) = %s AND status = FALSE"""
        cursor.execute(fetch_orders_from_table, (date.today().strftime("%Y-%m-%d")))
        return 'Данных о заказах извлечены'
    except Exception as e:
        return f"Error5: {e}"
    
