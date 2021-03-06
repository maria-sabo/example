# -*- coding: utf-8 -*-

import sys
import requests

from src.classes.data_for_creating_employee import DataCreateEmployee
from src.config import sub_domain
from src.convert import xlsx2df

from src.methods.check_legal_entities import check_legal_entities_excel
from src.methods.create_client_user import get_client_id_by_token
from src.methods.data_from_server import get_root_department_id, get_employee_role_ids, get_departments_dict, \
    get_positions_dict, get_lst_about_users
from src.methods.create_employee import create_employees

ARGS_COUNT = 3


def main():
    """
    Если при запуске программы введены все требуемые аргументы
        Считывается переданный токен, путь к excel-файлу
        С помощью токена берется идентификатор клиента
        Если идентфиикатор клиента получен успешно, то
            excel-таблица переводится в DataFrame
            Если таблица успешно перевелась, то
                Проверяется список переданных юрлиц
                Если все юрлица переданы корректно, то
                    Берутся данные о пользователях с сервера
                    Берется идентификатор корневого отдела
                    Берутся идентификаторы роли "Руководитель", "Кадровик"
                    Берутся словари должностей, отделов
                    На основании взятых значений вызывается функция create_employees(data, data_users, df),
                    которая создает всех сотрудников

    sys.argv[0]: Аргумент командной строки, по умолчанию путь к скрипту main.py
    sys.argv[1]: Аргумент командной строки, путь к excel-файлу, из которого будем загружать сотрудников
    sys.argv[2]: Аргумент командной строки, строковое значение api-токена клиента
    :return:
    """
    print('Welcome: ' + requests.get('https://' + sub_domain + '.hr-link.ru/api/v1/version').text + '\n')

    if sys.argv.__len__() == ARGS_COUNT:
        data = DataCreateEmployee

        excel_name = sys.argv[1]
        data.token = sys.argv[2]

        data.client_id = get_client_id_by_token(data.token)

        if data.client_id:
            df = xlsx2df(excel_name)
            if df is not False:
                data.checked_legal_entity_dict = check_legal_entities_excel(data.token, data.client_id,
                                                                            df['Юрлицо'].values)
                if not data.checked_legal_entity_dict:
                    return False
                else:
                    data_users = get_lst_about_users(data.token, data.client_id)
                    data.root_department_id = get_root_department_id(data.token, data.client_id)
                    data.head_manager_id, data.hr_manager_id = get_employee_role_ids(data.token)
                    data.positions_dict = get_positions_dict(data.token, data.client_id)
                    data.departments_dict = get_departments_dict(data.token, data.client_id)

                    create_employees(data, data_users, df)
            else:
                print('Переданный файл ' + excel_name + ' не найден.')
        else:
            print('Клиент не найден.')
    else:
        print(
            'Введите три аргумента: \n - путь к запускаемому файлу (main.py) \n - путь к xlsx файлу, из которого будут '
            'выгружаться сотрудники \n - токен клиента')


if __name__ == main():
    main()
