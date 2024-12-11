import psycopg2
from tabulate import tabulate
import os
import pandas as pd


def Save_all_to_excel(cur):
    sql_query = "select * from books_list;"
    try:
        cur.execute(sql_query)
        # Получение данных из курсора
        res_data = cur.fetchall()
        # Преобразуем в DataFream
        data_to_excel = pd.DataFrame(res_data)
        # Сохраняем в файл
        data_to_excel.to_excel('Books/All_books.xlsx')

        print("Книги успешно сохранены!")
    except Exception as e:
        print("Error: ", e)


def Add_from_excel(cur):
    columns = ['name', 'author', 'year', 'bookcase', 'shelf', 'genre', 'publisher', 'note']

    # Считываем те книги, которые хотим добвить
    new_books = pd.read_excel('Books/new_books.xlsx')
    # Добавляем
    new_books = new_books[columns] # Убираем первый пусой столбец
    new_books_to_insert = list(new_books.itertuples(index=False, name=None))
    sql_query = """INSERT INTO books_list VALUES (%s, %s, %s, %s, %s, %s, %s, %s);"""
    try:
        cur.executemany(sql_query, new_books_to_insert)
        print(f"Новые книги добавлены!")

        # Очищаем данные в файле new_books.xlsx если не возникло ошибок во время их добавления
        empty_df = pd.DataFrame(columns=columns)
        empty_df.to_excel('Books/new_books.xlsx')
    except Exception as e:
        print(f"Error when try to add: {e}")
        cur.connection.rollback()

    

def Search_book(cur, mode):
    # Получение первого параметра для поиска
    filter = {}
    all_param = {1 : "Название", 2 : "Автор", 3 : "Год", 4 : "№ шкафа", 5 : "№ полки", 6 : "Жанр", 7 : "Издательство", 8 : "Заметка"}
    all_param_for_db = {1 : "name", 2 : "author", 3 : "year", 4 : "bookcase", 5 : "shelf", 6 : "genre", 7 : "publisher", 8 : "note"}
    have_param = []

    # Получение параметров и их значений
    while True:
        print("Выберите параметр для поиска:")
        for i in range(1, 9):
            # Пропускаем уже заданные параметры
            if i in have_param: continue

            print(f'[{i}] - {all_param[i]}')

        # Получаем номер и значение
        num_parameter = int(input())
        # Проверка на правильность введённого номера
        if num_parameter in have_param:
            print("Вы уже указывали этот параметр!")
            continue
        print("Введите значение: ")
        if num_parameter == 3 or num_parameter == 4 or num_parameter == 5:
            parameter = int(input())
        else:
            parameter = input()
        
        # Добавляем в фильтр
        filter[num_parameter] = parameter
        have_param.append(num_parameter)

        # Спрашиваем
        print("Вы хотите указать ещё параметр для поиска?")
        print("0 - Нет, 1 - Да : ")
        ans = int(input())
        
        # Очищаем консоль
        os.system('cls')
        
        if ans == 0: break
    
    try:
        # Составляем запрос
        sql_query = "SELECT * FROM books_list WHERE "
        for i in have_param:
            if i == 3 or i == 4 or i == 5:
                sql_query += f'{all_param_for_db[i]} = {filter[i]} and '
            else:
                sql_query += f'{all_param_for_db[i]} = \'{filter[i]}\' and '
        sql_query = sql_query[:-5] + ";"

        # Получение данных из таблицы books_list
        cur.execute(sql_query)

        print("Вот найденные результаты:")

        # Получение данных из курсора и вывод их на экран
        res_data = cur.fetchall()
        # Пронумеруем строки
        data_with_numbers = [(i + 1, *row) for i, row in enumerate(res_data)]
        # Иначе печатаем их
        headers  = ["#", "Название", "Автор", "Год", "№ шкафа", "№ полки", "Жанр", "Издательство", "Заметка"]
        print(tabulate(data_with_numbers, headers=headers, tablefmt="grid"))

        # Передаём данные о найденных книгах в Chenge_info() и выходим
        if mode == 1: return data_with_numbers

    except Exception as e:
        print("Error when search: ", e)

def Add_book(cur):
    book = ["" for i in range(8)]
    book[0] = input("Введите название книги: ")
    book[1] = input("Введите автора: ")
    book[2] = int(input("Введите год: "))
    book[3] = int(input("Введите номер шкафа: "))
    book[4] = int(input("Введите номер полки: "))
    book[5] = "'" + input("Введите жанр книги (\"0\" - не вводить): ") + "'"
    book[6] = "'" + input("Введите издательство (\"0\" - не вводить): ") + "'"
    book[7] = "'" + input("Введите заметку (\"0\" - не вводить): ") + "'"
    if book[5] == "'0'": book[5] = "NULL"
    if book[6] == "'0'": book[6] = "NULL"
    if book[7] == "'0'": book[7] = "NULL"

    try:
        sql_query = f'INSERT INTO books_list VALUES (\'{book[0]}\', \'{book[1]}\', {book[2]}, {book[3]}, {book[4]}, {book[5]}, {book[6]}, {book[7]});'
        cur.execute(sql_query)
        print("Книга добавлена!")
    except Exception as e:
        print("Error when try to add book: ", e)

def Chenge_info(cur):
    print("Давайте сначала найдём книгу")
    print("Введите те данные, которые помогут сузить поиск и найти книгу")

    all_param = {1 : "Название", 2 : "Автор", 3 : "Год", 4 : "№ шкафа", 5 : "№ полки", 6 : "Жанр", 7 : "Издательство", 8 : "Заметка"}
    all_param_for_db = {1 : "name", 2 : "author", 3 : "year", 4 : "bookcase", 5 : "shelf", 6 : "genre", 7 : "publisher", 8 : "note"}

    while True:
        data_with_numbers = Search_book(cur, 1)

        print("Введите 0 - чтобы уточнить параметры для поиска")
        print("Введите 1 - чтобы выбрать книгу")
        ans = int(input())
        if ans == 1: break
        else: # Очищаем консоль
            os.system('cls')
    
    index_of_book = int(input('Введите номер книги в таблице, чтобы её выбрать: '))

    # Очистим консоль
    os.system('cls')

    # Массив с значения выбранной книги
    choosen_book = list(data_with_numbers[index_of_book - 1])
    while True:
        # Уведомление о выбранной книге
        print("Вы выбрали вот эту книгу:")
        headers  = ["#", "Название", "Автор", "Год", "№ шкафа", "№ полки", "Жанр", "Издательство", "Заметка"]
        print(tabulate([choosen_book], headers=headers, tablefmt="grid"))

        # Выбираем изменяемое значение
        print("Какое значение вы хотите изменить? : ")
        for i in range(1, 9):
            print(f'[{i}] - {all_param[i]}')
        what_will_we_change = int(input())

        # Получаем новое значение
        if what_will_we_change == 6 or what_will_we_change == 7 or what_will_we_change == 8:
            print("Введите новое значение (' ' = пустое значение): ")
        else:
            print("Введите новое значение: ")
        if what_will_we_change == 3 or what_will_we_change == 4 or what_will_we_change == 5:
            new_info = int(input())
        else:
            new_info = "'" + input() + "'"
        if new_info == "' '": new_info = "NULL"
        
        # Составляем запрос
        sql_query = f'UPDATE books_list SET {all_param_for_db[what_will_we_change]} = {new_info} WHERE '

        for i in range(1, 9):
            # Пропускаем изменяемый параметр
            if i == what_will_we_change: continue
            # Добавляем значение, которое поможет индентифицировать книгу в запрос
            if choosen_book[i] == None:
                continue
            else:
                if i == 3 or i == 4 or i == 5:
                    value = choosen_book[i]
                else:
                    value = "'" + choosen_book[i] + "'"
            sql_query += f'{all_param_for_db[i]} = {value} AND '

        sql_query = sql_query[:-5] + ';'

        # Меняем старое на новое
        try:
            cur.execute(sql_query)
            print("Изменения сохранены!")

        except Exception as e:
            print("Error when try to change: ", e)
        
        # Обновляем значение в массиве choosen_book
        if what_will_we_change == 3 or what_will_we_change == 4 or what_will_we_change == 5:
            choosen_book[what_will_we_change] = int(new_info)
        else:
            choosen_book[what_will_we_change] = str(new_info)
        
        # Предлагаем изменить что-то ещё
        print("Вы хотите ещё что-то изменить в этой книге? 1 - Да, 0 - Нет: ")
        exit_or_no = int(input())
        if exit_or_no == 0: break

        # Очищаем консоль
        os.system('cls')

    

# В изменении инфы о книге может получиться проблема, когда найдутся две книги одинаковые. но мы рассчитываем на лучшее
# Сделать запускаемый файл, чтобы без ide запускать
# Добавить выгрузку всех книг в excel файл






# Импорт переменных из файла config.py
from config import host, db_name, db_password, db_user, port

try:
    # Подключение к базе данных
    db_conn = psycopg2.connect(
        host = host,
        database= db_name,  
        user= db_user,
        password = db_password,
        port = port
    )

    # Автоматическая фиксация изменений
    db_conn.autocommit = True

    # Создание курсора при помощи контекстного менеджера
    with db_conn.cursor() as cur:
        while True:
            print("Режими работы")
            print("[1] - Поиск")
            print("[2] - Добавление книги")
            print("[3] - Изменить данные о книге")
            print("[4] - Добавить книги из excel таблицы")
            print("[5] - Сохранение всех данных в файл")
            while True:
                try:
                    mode = int(input("Введите номер выбранного режима (или 0 - для Выхода): \n"))
                    break
                except:
                    print("Error: введите число от 1/2/3/4/5")
            
            # Очищаем консоль
            os.system('cls')

            while True:
                if mode == 1:
                    Search_book(cur, 0)
                    break
                elif mode == 2:
                    Add_book(cur)
                    break
                elif mode == 3:
                    Chenge_info(cur)
                    break
                elif mode == 4:
                    Add_from_excel(cur)
                    break
                elif mode == 5:
                    Save_all_to_excel(cur)
                    break
                else:
                    print("Неверно введено число! Попробуйте ещё раз (1/2/3/4/5) 0 - Выйти: ")
                    mode = int(input())
                    if mode == 0: break
            
            q = int(input("Вы хотите продолжить(1) или выйти(2)? : "))

            # Очищаем консоль
            os.system('cls')

            if q == 2:
                break

except Exception as e:

    # Отмена внесённых изменений
    db_conn.rollback()

    # Обработка ошибок
    print("[INFO] Ошибка при работе с PostgreSQL:", e)

finally:
    # Закрытие соединения с базой данных
    if db_conn:
        db_conn.close()
        print(f"[INFO] Соединение с базой данных '{db_name}' закрыто.")