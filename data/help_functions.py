import datetime
from math import sqrt

from data import db_session
from data.couriers import Courier
from data.deliveryhours import DH
from data.orders import Order

import requests

from data.users import User

API_KEY = 'c5f0691a-e271-43b3-a4c6-7fd7b6d0533a'
STATIC_API_KEY = "AIzaSyCR21Jo0yYeIdZmOgsY_7wD4OUQRoFfE3s"


def is_t_ok(l1, l2) -> bool:
    # format HH:MM - HH:MM
    time = [0] * 1441
    # print(list(l1) + list(l2))
    for h in list(l1) + list(l2):
        t = h.hours
        b1, b2 = t.split('-')
        a = b1.split(':')
        a = int(a[0]) * 60 + int(a[1])
        b = b2.split(':')
        b = int(b[0]) * 60 + int(b[1])
        time[a] += 1
        time[b + 1] -= 1
        # print(t, b1, b2, a, b, time[a], time[b + 1])
    # print('---------------------------')
    balance = 0
    for i in time:
        balance += i
        if balance >= 2:
            return True
    return False


def get_coordinates(address: str) -> (int, int):
    address.replace(',', ',+')
    coords = f"http://geocode-maps.yandex.ru/v1/?apikey={API_KEY}" \
             f"&geocode={address}&format=json"

    print(coords)
    response = requests.get(coords)

    json_response = response.json()
    xy = json_response["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]['Point']['pos']
    # xy = f'{xy.replace(" ", ",")}'
    xy = ','.join(xy.split()[::-1])
    return xy


def check_address(address: str):
    symbols = ['&', "=", "$", ";", "?"]
    for s in symbols:
        if s in address:
            return False
    try:
        get_coordinates(address)
    except:
        return False
    return True


def choose_orders(ords: list[Order], max_weight: int) -> list[Order]:
    answer = []
    current_weight = 0
    ords.sort(key=lambda order: order.weight)
    for order in ords:
        if order.weight + current_weight <= max_weight:
            answer.append(order)
            current_weight += order.weight
        print(current_weight, max_weight)

    return answer


def from_few_fields_to_json(t, rs, whs):
    d = {
        'courier_type': t,
        'regions': list(map(int, rs.split(','))),
        'working_hours': whs.split(',')
    }
    return d


def parse_time(raw_time: datetime.time) -> str:
    h = raw_time.hour
    m = raw_time.minute
    return ('0' if (h < 10) else '') + str(h) + ":" + ('0' if (m < 10) else '') + str(m)


def parse_to_about(type_of_courier: str, region: int, start_time: datetime.time, end_time: datetime.time) -> str:
    return type_of_courier + ';' + str(region) + ';' + parse_time(start_time) + '-' + parse_time(end_time)


def parse_from_about(about: str) -> (str, int, datetime.time, datetime.time):
    if about == "":
        return None
    data = about.split(";")
    type_of_courier = data[0]
    region = int(data[1])
    start_time, end_time = data[2].split('-')
    h1, m1 = map(int, start_time.split(':'))
    start_time = datetime.time(h1, m1)
    h2, m2 = map(int, end_time.split(':'))
    end_time = datetime.time(h2, m2)
    return type_of_courier, region, start_time, end_time


def count_distance(c1: str, c2: str) -> float:
    x1, y1 = map(float, c1.split(','))
    x2, y2 = map(float, c2.split(','))
    dx = x1 - x2
    dy = y1 - y2
    return sqrt(dx ** 2 + dy ** 2) * 111


def collect_info_about_orders(orders: list[Order], db_sess: db_session.Session, flag) \
        -> list[tuple[Order, str, str, str]]:
    orders = list(filter(lambda item: item.complete_time == "" or flag, orders))
    delivery_hours = [db_sess.query(DH).filter(DH.order_id == order.id).all()[0] for order in orders]
    courier_names = []
    client_names = []
    for order in orders:
        list_of_couriers = db_sess.query(User).filter(User.c_id == order.orders_courier).all()
        if list_of_couriers:
            courier_names.append(f"{list_of_couriers[0].name}, Phone: {list_of_couriers[0].phone_number}")
        else:
            courier_names.append("")
        client = db_sess.query(User).filter(User.id == order.user_id).first()
        client_names.append(client.name + ", " + client.phone_number)

    items = list(zip(orders, delivery_hours, courier_names, client_names))

    return items


def form_couriers_json(id_list: list, db_sess):
    try:
        ans = []
        for i in id_list:
            candidate = db_sess.query(User).filter(User.id == i).first()
            t, rs, whs = candidate.about.split(';')
            new_id = max([j.id for j in db_sess.query(Courier).all()] + [0]) + 1
            ans.append({
                'courier_id': new_id,
                'courier_type': t,
                'regions': list(map(int, rs.split(','))),
                'working_hours': whs.split(','),
                'user_id': i
            })
        # print(ans)
        return {'data': ans}
    except Exception:
        return {'data': False}
