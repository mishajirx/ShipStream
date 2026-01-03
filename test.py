import datetime
import argparse
import requests

# HOST = '0.0.0.0'
HOST = '127.0.0.1'
PORT = 5000
URL = f'http://{HOST}:{PORT}'
parser = argparse.ArgumentParser(  # object processing arguments (like in a function)
    description="convert integers to decimal system")
parser.add_argument('--clear', default='0', type=str, help='need to delete all data?(yes(1)/no(0))')


def check_assign_time(j1: dict, j2: dict):
    t1 = j1['assign_time']
    t2 = j2['assign_time']
    u = datetime.datetime.fromisoformat(t1.split('.')[0])
    v = datetime.datetime.fromisoformat(t2.split('.')[0])
    if (u - v).total_seconds() <= 1:
        return True
    return False


# methods for comfortable testing
def add_couriers(data) -> requests.models.Response:
    url = f'{URL}/api/couriers'
    response = requests.post(url, json=data)
    # print(response, response.json())
    return response


def add_orders(data) -> requests.models.Response:
    url = f'{URL}/api/orders'
    response = requests.post(url, json=data)
    # print(response, response.json())
    return response


def edit_courier(courier_id, data) -> requests.models.Response:
    url = f'{URL}/api/couriers/' + str(courier_id)
    response = requests.patch(url, json=data)
    # if not response:
    #     print(response)
    # else:
    #     print(response, response.json())
    return response


def get_courier(courier_id) -> requests.models.Response:
    url = f'{URL}/api/couriers/' + str(courier_id)
    response = requests.get(url)
    # if not response:
    #     print(response)
    # else:
    #     print(response, response.json())
    return response


def assign_orders(courier_id) -> requests.models.Response:
    url = f'{URL}/api/orders/assign'
    data = {'courier_id': courier_id}
    response = requests.post(url, json=data)
    # if not response:
    #     print(response)
    # else:
    #     print(response, response.json())
    return response


def complete_orders(data) -> requests.models.Response:
    url = f'{URL}/api/orders/complete'
    response = requests.post(url, json=data)
    # if not response:
    #     print(response)
    # else:
    #     print(response, response.json())
    return response


def clear_db(data):
    url = f'{URL}/api/clear'
    response = requests.post(url, json=data)
    # print(response, response.json())


"""Connection Test"""


def test_connection():
    print('Attention, Testing will trigger database cleanup')
    ans = 'y'
    # ans = input('Continue?(y/n)')
    assert ans == 'y'
    test_url = f'{URL}/api/test'
    response = requests.get(test_url)
    # print('Something went wrong: Connection Error')
    # print('Try to rerun service')
    if response:
        print(response.json())
    else:
        print(response)
    clear_db({'code': 'zhern0206eskiy'})


""" Main Tests"""


def test_post_couriers_normal_data():
    res = add_couriers({
        "data": [
            {
                "courier_id": 1,
                "courier_type": "foot",
                "regions": [1, 12, 22],
                "working_hours": ["11:35-14:05", "09:00-11:00"]
            },
            {
                "courier_id": 2,
                "courier_type": "bike",
                "regions": [22],
                "working_hours": ["09:00-18:00"]
            },
            {
                "courier_id": 3,
                "courier_type": "car",
                "regions": [12, 22, 23, 33],
                "working_hours": ['22:00-22:30']
            }
        ]
    })  # adding couriers (normal data)
    assert res.status_code == 201 and res.json() == {'couriers': [{'id': 1}, {'id': 2}, {'id': 3}]}
    # {'couriers': [{'id': 1}, {'id': 2}, {'id': 3}]}


def test_post_couriers_repeating_id():
    res = add_couriers({
        "data": [
            {
                "courier_id": 1,
                "courier_type": "foot",
                "regions": [1, 12, 22],
                "working_hours": ["11:35-14:05", "09:00-11:00"]
            },
            {
                "courier_id": 2,
                "courier_type": "bike",
                "regions": [22],
                "working_hours": ["09:00-18:00"]
            },
            {
                "courier_id": 3,
                "courier_type": "car",
                "regions": [12, 22, 23, 33],
                "working_hours": []
            }
        ]
    })  # repeating ids (error)
    assert res.status_code == 400 and res.json() == \
           {'validation_error': [{'errors': [{'loc': ['id'],
                                              'msg': 'Invalid id: There is a courier with '
                                                     'the same id',
                                              'type': 'value_error'}],
                                  'id': 1},
                                 {'errors': [{'loc': ['id'],
                                              'msg': 'Invalid id: There is a courier with '
                                                     'the same id',
                                              'type': 'value_error'}],
                                  'id': 2},
                                 {'errors': [{'loc': ['id'],
                                              'msg': 'Invalid id: There is a courier with '
                                                     'the same id',
                                              'type': 'value_error'}],
                                  'id': 3}]}
    # {'validation_error': [{'id': 1}, {'id': 2}, {'id': 3}]}


def test_post_couriers_wrong_field():
    res = add_couriers({
        "data": [
            {
                "courier_id": 5,
                "courier_type": "foot",
                "regions": [1, 12, 22],
                "working_hours": ["11:35-14:05", "09:00-11:00"]
            },
            {
                "courier_id": 7,
                "courier_type": "bike",
                "regions": [22],
                "working_hours": ["09:00-18:00"]
            },
            {
                "courier_id": 9,
                "courier_type": "car",
                "regions": [12, 22, 23, 33],
                "working_hours": [],
                "foo": 2
            }
        ]
    })  # non-existent field (error)
    assert res.status_code == 400 and res.json() == \
           {'validation_error': [{'errors': [{'loc': ['foo'],
                                              'msg': 'extra fields not permitted',
                                              'type': 'value_error.extra'}],
                                  'id': 9}]}
    # {'validation_error': [{'id': 9}]}


def test_post_couriers_wrong_value():
    res = add_couriers({
        "data": [
            {
                "courier_id": 5,
                "courier_type": "foot",
                "regions": [1, 12, 22],
                "working_hours": ["11:35-14:05", "09:00-11:00"]
            },
            {
                "courier_id": 7,
                "courier_type": "bike",
                "regions": [22],
                "working_hours": ["09:00-18:00"]
            },
            {
                "courier_id": 9,
                "courier_type": "car",
                "regions": [12, 'f2', 23, 33],
                "working_hours": [],
            }
        ]
    })  # non-existent field (error)
    assert res.status_code == 400 and res.json() == \
           {'validation_error': [{'errors': [{'loc': ['regions', 1],
                                              'msg': 'value is not a valid integer',
                                              'type': 'type_error.integer'}],
                                  'id': 9}]}
    # {'validation_error': [{'id': 9}]}


def test_post_couriers_wrong_wh_format():
    res = add_couriers({
        "data": [
            {
                "courier_id": 43,
                "courier_type": "car",
                "regions": [12, 22, 23, 33],
                "working_hours": ['uyfyjcyjtc'],
            }
        ]
    })  # invalid working hours format
    assert res.status_code == 400 and res.json() == \
           {'validation_error': [{'errors': [{'loc': ['working_hours'],
                                              'msg': 'invalid working hours format',
                                              'type': 'value_error'}],
                                  'id': 43}]}


def test_post_couriers_wrong_wh_numbers():
    res = add_couriers({
        "data": [
            {
                "courier_id": 43,
                "courier_type": "car",
                "regions": [12, 22, 23, 33],
                "working_hours": ['16:0h-1g:01'],
            }
        ]
    })  # invalid working hours format
    assert res.status_code == 400 and res.json() == \
           {'validation_error': [{'errors': [{'loc': ['working_hours'],
                                              'msg': 'invalid literal for int() with base '
                                                     "10: '0h'",
                                              'type': 'value_error'}],
                                  'id': 43}]}


def test_patch_couriers_all_params():
    res = edit_courier(1, {
        "regions": [11, 33, 2],
        "working_hours": ['12:00-12:30'],
        'courier_type': 'car'
    })  # changing all parameters (normal data)
    assert res.status_code == 200 and res.json() == {'courier_id': '1', 'courier_type': 'car',
                                                     'regions': [11, 33, 2],
                                                     'working_hours': ['12:00-12:30']}


def test_patch_couriers_any_params():
    res = edit_courier(1, {
        "regions": [11, 2],
        "working_hours": ['11:00-15:30'],
    })  # changing not all parameters (normal data)
    assert res.status_code == 200 and res.json() == {'courier_id': '1', 'courier_type': 'car',
                                                     'regions': [11, 2],
                                                     'working_hours': ['11:00-15:30']}


def test_patch_couriers_wrong_params():
    res = edit_courier(1, {
        'bar': 123
    })  # changing a non-existent parameter (error)
    assert res.status_code == 400 and res.json() == \
           {'errors': [
               {'loc': ['bar'], 'msg': 'extra fields not permitted', 'type': 'value_error.extra'}]}


def test_patch_couriers_wrong_id():
    res = edit_courier(10, {
        'regions': [1, 2, 3]
    })  # changing a non-existent courier (error)
    assert res.status_code == 404 and res.json() == {'message': 'no courier with this id'}


def test_post_orders_normal_data():
    res = add_orders({
        "data": [
            {
                "order_id": 1,
                "weight": 0.23,
                "region": 12,
                "delivery_hours": ["09:00-18:00"]
            },
            {
                "order_id": 2,
                "weight": 15,
                "region": 1,
                "delivery_hours": ["09:00-18:00"]
            },
            {
                "order_id": 3,
                "weight": 0.01,
                "region": 22,
                "delivery_hours": ["09:00-12:00", "16:00-21:30"]
            }
        ]
    })  # adding orders (normal data)
    assert res.status_code == 201 and res.json() == {'orders': [{'id': 1}, {'id': 2}, {'id': 3}]}


def test_post_orders_repeating_id():
    res = add_orders({
        "data": [
            {
                "order_id": 5,
                "weight": 0.23,
                "region": 12,
                "delivery_hours": ["09:00-18:00"]
            },
            {
                "order_id": 8,
                "weight": 15,
                "region": 1,
                "delivery_hours": ["09:00-18:00"]
            },
            {
                "order_id": 3,
                "weight": 0.01,
                "region": 22,
                "delivery_hours": ["09:00-12:00", "16:00-21:30"]
            }
        ]
    })  # repeating id (error)
    assert res.status_code == 400 and res.json() == \
           {'validation_error': [{'errors': [{'loc': ['id'],
                                              'msg': 'Invalid id: There is a order with '
                                                     'the same id',
                                              'type': 'value_error'}],
                                  'id': 3}]}


def test_post_orders_odd_field():
    res = add_orders({
        "data": [
            {
                "order_id": 1,
                "weight": 0.23,
                "region": 12,
                "delivery_hours": ["09:00-18:00"],
                "fjhfbgudrgbdiu": 123
            },
            {
                "order_id": 2,
                "weight": 15,
                "region": 1,
                "delivery_hours": ["09:00-18:00"]
            },
            {
                "order_id": 3,
                "weight": 0.01,
                "region": 22,
                "delivery_hours": ["09:00-12:00", "16:00-21:30"]
            }
        ]
    })  # non-existent field (error)
    assert res.status_code == 400 and res.json() == \
           {'validation_error': [{'errors': [{'loc': ['fjhfbgudrgbdiu'],
                                              'msg': 'extra fields not permitted',
                                              'type': 'value_error.extra'},
                                             {'loc': ['id'],
                                              'msg': 'Invalid id: There is a order with '
                                                     'the same id',
                                              'type': 'value_error'}],
                                  'id': 1},
                                 {'errors': [{'loc': ['id'],
                                              'msg': 'Invalid id: There is a order with '
                                                     'the same id',
                                              'type': 'value_error'}],
                                  'id': 2},
                                 {'errors': [{'loc': ['id'],
                                              'msg': 'Invalid id: There is a order with '
                                                     'the same id',
                                              'type': 'value_error'}],
                                  'id': 3}]}


def test_post_orders_too_big_weight():
    res = add_orders({
        "data": [
            {
                "order_id": 10,
                "weight": 100,
                "region": 12,
                "delivery_hours": ["09:00-18:00"]
            },
            {
                "order_id": 11,
                "weight": 15,
                "region": 1,
                "delivery_hours": ["09:00-18:00"]
            },
            {
                "order_id": 12,
                "weight": 0.01,
                "region": 22,
                "delivery_hours": ["09:00-12:00", "16:00-21:30"]
            }
        ]
    })  # weight too big (error)
    assert res.status_code == 400 and res.json() == \
           {'validation_error': [{'errors': [{'loc': ['weight'],
                                              'msg': 'weight should be between 0.01 and '
                                                     '50',
                                              'type': 'value_error'}],
                                  'id': 10}]}


def test_post_orders_too_small_weight():
    res = add_orders({
        "data": [
            {
                "order_id": 10,
                "weight": 0.00001,
                "region": 12,
                "delivery_hours": ["09:00-18:00"]
            },
            {
                "order_id": 11,
                "weight": 15,
                "region": 1,
                "delivery_hours": ["09:00-18:00"]
            },
            {
                "order_id": 12,
                "weight": 0.01,
                "region": 22,
                "delivery_hours": ["09:00-12:00", "16:00-21:30"]
            }
        ]
    })  # weight too small (error)
    assert res.status_code == 400 and res.json() == {
        'validation_error': [{'errors': [{'loc': ['weight'],
                                          'msg': 'weight should be between 0.01 and '
                                                 '50',
                                          'type': 'value_error'}],
                              'id': 10}]}


def test_assign_orders_courier_with_some_orders():
    res = assign_orders(1)  # assigning orders to courier 1 (normal data)
    assert res.status_code == 200 and res.json() == {'orders': []}


def test_assign_orders_courier_without_orders():
    res = assign_orders(2)  # assigning orders to courier 2 (normal data)
    t = str(datetime.datetime.utcnow()).replace(' ', 'T') + 'Z'
    assert res.status_code == 200 and check_assign_time(res.json(),
                                                        {'assign_time': t, 'orders': [{'id': 3}]})


def test_assign_orders_wrong_courier():
    res = assign_orders(4)  # assigning orders to courier 3 (error)
    assert res.status_code == 400


def test_assign_orders_idempotent_proof():
    res1 = assign_orders(2)  # assigning orders to courier 2 (normal data)
    res2 = assign_orders(2)
    t = str(datetime.datetime.utcnow()).replace(' ', 'T') + 'Z'
    assert res1.status_code == res2.status_code == 201 and \
           check_assign_time(res1.json(), res2.json()) and \
           check_assign_time(res1.json(), {'assign_time': t, 'orders': [{'id': 3}]}) and \
           check_assign_time(res2.json(), {'assign_time': t, 'orders': [{'id': 3}]})


def test_complete_orders_right_order_and_courier():
    res = complete_orders({
        "courier_id": 2,
        "order_id": 3,
        "complete_time": str(datetime.datetime.utcnow()).replace(' ', 'T') + 'Z'
    })  # completion by courier 2 of order 3 (normal data)
    assert res.status_code == 200 and res.json() == {'order_id': 3}


def test_complete_orders_right_data_idempotent_proof():
    res1 = complete_orders({
        "courier_id": 2,
        "order_id": 3,
        "complete_time": str(datetime.datetime.utcnow()).replace(' ', 'T') + 'Z'
    })  # completion by courier 2 of order 3 (normal data) proving idempotency
    res2 = complete_orders({
        "courier_id": 2,
        "order_id": 3,
        "complete_time": str(datetime.datetime.utcnow()).replace(' ', 'T') + 'Z'
    })
    assert res2.status_code == res1.status_code == 200 and res2.json() == res1.json() == {
        'order_id': 3}


def test_complete_orders_courier_and_order_dont_match():
    res = complete_orders({
        "courier_id": 1,
        "order_id": 3,
        "complete_time": str(datetime.datetime.utcnow()).replace(' ', 'T') + 'Z'
    })  # completion by courier 1 of order 3 (error)
    assert res.status_code == 400 and res.json() == {'message': 'courier and order don\'t match'}


def test_complete_orders_wrong_order():
    res = complete_orders({
        "courier_id": 2,
        "order_id": 10,
        "complete_time": str(datetime.datetime.utcnow()).replace(' ', 'T') + 'Z'
    })  # completion by courier 2 of order 1 (error)
    assert res.status_code == 400 and res.json() == {'message': 'no order with this id'}


def test_complete_orders_wrong_courier():
    res = complete_orders({
        "courier_id": 4,
        "order_id": 5,
        "complete_time": str(datetime.datetime.utcnow()).replace(' ', 'T') + 'Z'
    })  # completion by courier 4 of order 5 (error)
    assert res.status_code == 400 and res.json() == {'message': 'no courier with this id'}


def test_get_courier_with_some_orders():
    res = get_courier(3)  # information about courier 3 (normal data)
    assert res.status_code == 200 and \
           res.json() == {'courier_id': '3', 'courier_type': 'car', 'earnings': 0,
                          'regions': [12, 22, 23, 33],
                          'working_hours': ['22:00-22:30']}


def test_get_courier_without_any_orders():
    res = get_courier(2)  # information about courier 2 (normal data)
    assert res.status_code == 200 and res.json() == {'courier_id': '2', 'courier_type': 'bike',
                                                     'earnings': 2500,
                                                     'rating': 5.0, 'regions': [22],
                                                     'working_hours': ['09:00-18:00']}


def test_get_courier_wrong_id():
    res = get_courier(4)  # information about courier 4 (error)
    assert res.status_code == 404


""" Test that when changing courier data, the order can become free """


def test_orders_untying_weight():
    add_orders({
        "data": [
            {
                "order_id": 4,
                "weight": 40,
                "region": 22,
                "delivery_hours": ["22:00-22:15"]
            }
        ]
    })  # added order with weight 40 (ok)
    assign_orders(3)  # assigned it to a car courier (ok)
    edit_courier(3, {'courier_type': 'foot'})  # he changed type (ok)
    res = complete_orders({
        "courier_id": 3,
        "order_id": 4,
        "complete_time": str(datetime.datetime.utcnow()).replace(' ', 'T') + 'Z'
    })  # order is no longer his (error)
    edit_courier(3, {'courier_type': 'car'})  # change back (ok)
    assert res.status_code == 400


def test_orders_untying_time():
    assign_orders(3)  # assigned it to a courier with suitable time (ok)
    edit_courier(3, {'working_hours': ['12:00-13:00']})  # he changed working hours (ok)
    res = complete_orders({
        "courier_id": 3,
        "order_id": 4,
        "complete_time": str(datetime.datetime.utcnow()).replace(' ', 'T') + 'Z'
    })  # order is no longer his (error)
    edit_courier(3, {'working_hours': ['22:00-22:30']})  # change back (ok)
    assert res.status_code == 400


def test_orders_untying_region():
    assign_orders(3)  # assigned it to a courier with suitable region (ok)
    edit_courier(3, {'regions': [1]})  # he changed regions (ok)
    res = complete_orders({
        "courier_id": 3,
        "order_id": 4,
        "complete_time": str(datetime.datetime.utcnow()).replace(' ', 'T') + 'Z'
    })  # order is no longer his (error)
    assert res.status_code == 400


"""Test that you cannot take an already assigned order"""


def test_orders_are_not_for_many_couriers():
    add_couriers({
        "data": [
            {
                "courier_id": 6,
                "courier_type": "bike",
                "regions": [40],
                "working_hours": ["13:00-13:50"]
            },
            {
                "courier_id": 7,
                "courier_type": "bike",
                "regions": [40],
                "working_hours": ["13:00-13:50"]
            }
        ]
    })  # create two almost identical couriers
    add_orders({
        "data": [
            {
                "order_id": 8,
                "weight": 10,
                "region": 40,
                "delivery_hours": ["13:30-13:41"]
            }
        ]
    })  # add suitable order for them
    assign_orders(6)  # one will receive it
    res1 = assign_orders(7)  # the second one won't
    complete_orders({
        "courier_id": 6,
        "order_id": 8,
        "complete_time": str(datetime.datetime.utcnow()).replace(' ', 'T') + 'Z'
    })  # completes order
    res2 = assign_orders(7)  # the second one also cannot receive it
    assert res1.status_code == res2.status_code == 200 and res1.json() == res2.json() == {
        'orders': []}
    # print(res1.json(), res2.json())


"""Test for precise order distribution"""


def test_assign_orders_right_orders_distributing():
    add_couriers({
        "data": [
            {
                "courier_id": 100,
                "courier_type": "car",
                "regions": [34],
                "working_hours": ["11:35-14:05", "09:00-11:00"]
            },
        ]
    })  # adding couriers (normal data)
    add_orders({
        "data": [
            {
                "order_id": 101,
                "weight": 49,
                "region": 34,
                "delivery_hours": ["09:00-18:00"]
            },
            {
                "order_id": 102,
                "weight": 25.5,
                "region": 34,
                "delivery_hours": ["09:00-18:00"]
            },
            {
                "order_id": 103,
                "weight": 24.5,
                "region": 34,
                "delivery_hours": ["09:00-18:00"]
            }
        ]
    })  # adding orders (normal data)
    res = assign_orders(100)
    clear_db({'code': 'zhern0206eskiy'})
    assert res.status_code == 200 and res.json()['orders'] == [{'id': 102}, {'id': 103}]
