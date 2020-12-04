# готовим данные для создания employee
# data =      {"clientUserId": client_user_id,
#             "legalEntityId": legal_entity_id,
#             "departmentId": department_id,
#             "positionId": position_id,
#             "roleIds": []}
import json

import requests

from src.classes.add_employee import AddEmployee
from src.convert import get_snils, data2class
from src.methods.create_client_user import create_client_user
from src.methods.get_for_employee import get_external_id, get_department, get_role_ids, get_position
from src.methods.data_from_server import get_external_id_lst


def prepare_data_for_employee(token, client_id, client_user_id, legal_entity_dict,
                              legal_entity_excel,
                              position_excel, positions_dict, department_excel, root_department_id,
                              departments_dict,
                              head_manager_excel,
                              hr_manager_excel, head_manager_id, hr_manager_id, external_id_excel):
    legal_entity_id = ''
    for id_name, name in legal_entity_dict.items():
        if name == legal_entity_excel:
            legal_entity_id = id_name

    external_id_lst = get_external_id_lst(token, client_id, legal_entity_id)
    external_id = get_external_id(external_id_excel, external_id_lst)
    position_id = get_position(token, client_id, position_excel, positions_dict)
    department_id = get_department(token, client_id, department_excel, root_department_id, departments_dict)
    role_ids = get_role_ids(head_manager_excel, hr_manager_excel, head_manager_id, hr_manager_id)

    # data = {"clientUserId": client_user_id,
    #         "legalEntityId": legal_entity_id,
    #         "departmentId": department_id,
    #         "positionId": position_id,
    #         "roleIds": role_ids,
    #         "externalId": external_id}
    add_employee = AddEmployee(client_user_id)
    add_employee.legalEntityId = legal_entity_id
    add_employee.departmentId = department_id
    add_employee.positionId = position_id
    add_employee.roleIds = role_ids
    add_employee.externalId = external_id

    data = json.loads(add_employee.toJSON())

    return data


# создаем сотрудника
# возвращается его employeeId
def create_employee_from_client_user(token, client_id, data_for_creating_employee):
    create_employee_response = requests.post('https://app-test1.hr-link.ru/api/v1/clients/' + client_id + '/employees',
                                             headers={'User-Api-Token': token},
                                             json=data_for_creating_employee)
    response_dict = json.loads(create_employee_response.text)

    if response_dict.get('result'):
        created_employee = response_dict.get('employee')
        created_employee_id = created_employee.get('id')
        print('Сотрудник создан.')
        return created_employee_id
    else:
        print('Сотрудник не создан.')


# полное создание одного сотрудника:
# создаем client_user
# вызываем функцию, которая приготовит данные для создания employee
# создаем employee
def create_employee_full(data):
    data_for_creating_user = json.loads(data.user.toJSON())
    legal_entity_excel = data.employee.legalEntity
    position_excel = data.employee.position
    department_excel = data.employee.department

    head_manager_excel = data.employee.headManager
    hr_manager_excel = data.employee.hrManager

    external_id_excel = data.employee.externalId
    try:
        client_user_id = create_client_user(data.token, data.client_id, data_for_creating_user)
        if client_user_id:
            data_em = prepare_data_for_employee(data.token, data.client_id, client_user_id,
                                                data.checked_legal_entity_dict,
                                                legal_entity_excel,
                                                position_excel, data.positions_dict, department_excel,
                                                data.root_department_id,
                                                data.departments_dict,
                                                head_manager_excel,
                                                hr_manager_excel, data.head_manager_id, data.hr_manager_id,
                                                external_id_excel)
            create_employee_from_client_user(data.token, data.client_id, data_em)
            print('!!!')
        else:
            print('...')
    except:
        print('Произошла ошибка при добавлении сотрудника.')


# создаем employees
def create_employees(data, df):
    if data.checked_legal_entity_dict:
        for i, row in df.iterrows():
            print('creating employee #: ' + str(i))
            snils = get_snils(row)

            if snils and not (snils in data.lst_person_snils):
                user, employee = data2class(row)
                if user and employee:
                    data.user = user
                    data.employee = employee

                    create_employee_full(data)
                    data.lst_person_snils.append(snils)
            else:
                print('Пользователь с таким СНИЛСом уже существует в сервисе. Или введен некорректный СНИЛС.')