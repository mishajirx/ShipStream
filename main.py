from flask import Flask
import re

import pydantic
from flask import jsonify, request, render_template, redirect
from flask_login import LoginManager, login_user, current_user, login_required, logout_user
from typing import List, Optional
import json
from forms.new_order import MakeOrderForm
from pydantic import validator
from data import shop_api
from forms.registration import RegisterForm
from data import db_session
from data.couriers import Courier
from data.orders import Order
from data.regions import Region
from data.workinghours import WH
from data.deliveryhours import DH
from data.users import User
from data.records import Record
from forms.login import LoginForm
from forms.what_couriers import NewCourierForm
from forms.homa_page import HomeForm
from forms.user_edit import EditAboutForm
from data.help_functions import *
from data.variables import *

app = Flask(__name__)
app.config['SECRET_KEY'] = 'misha_secret_key'
login_manager = LoginManager()
login_manager.init_app(app)


class CourierModel(pydantic.BaseModel):
    base: List[int]
    courier_id: int
    courier_type: str
    regions: List[int]
    working_hours: List[str]
    user_id: Optional[int]

    @validator('courier_type')
    def courier_type_should_be(cls, courier_type: str):
        if courier_type not in c_type:
            raise ValueError('courier_type should be "foot", "car" or "bike"')
        return courier_type

    @validator('working_hours')
    def wh_should_be(cls, working_hours: list):
        for wh in working_hours:
            if not PATTERN.match(wh) or len(wh) != 11:
                raise ValueError('invalid working hours format')
            if wh[2] != ':' or wh[5] != '-' or wh[8] != ':':
                raise ValueError('invalid separators')
            if not all(map(lambda x: x.isnumeric,
                           [wh[0], wh[1], wh[3], wh[4], wh[6], wh[7], wh[9], wh[10]])):
                raise ValueError('Hours/minutes should be integer')
            else:
                f1 = not 0 <= int(wh[0:2]) <= 23
                f2 = not 0 <= int(wh[3:5]) <= 59
                f3 = not 0 <= int(wh[6:8]) <= 23
                f4 = not 0 <= int(wh[9:11]) <= 59
                if f1 or f3:
                    raise ValueError('Hours should be between 0 and 23')
                if f2 or f4:
                    raise ValueError('Minutes should be between 0 and 59')
        return working_hours

    class Config:
        extra = 'forbid'


class EditCourierModel(pydantic.BaseModel):
    courier_id: Optional[int]
    courier_type: Optional[str]
    regions: Optional[List[int]]
    working_hours: Optional[List[str]]

    @validator('courier_type')
    def courier_type_should_be(cls, courier_type: str):
        if courier_type not in c_type:
            raise ValueError('courier_type should be "foot", "car" or "bike"')
        return courier_type

    @validator('working_hours')
    def wh_should_be(cls, working_hours: list):
        for wh in working_hours:
            if not PATTERN.match(wh) or len(wh) != 11:
                raise ValueError('invalid working hours format')
            if wh[2] != ':' or wh[5] != '-' or wh[8] != ':':
                raise ValueError('invalid separators')
            if not all(map(lambda x: x.isnumeric,
                           [wh[0], wh[1], wh[3], wh[4], wh[6], wh[7], wh[9], wh[10]])):
                raise ValueError('Hours/minutes should be integer')
            else:
                f1 = not 0 <= int(wh[0:2]) <= 23
                f2 = not 0 <= int(wh[3:5]) <= 59
                f3 = not 0 <= int(wh[6:8]) <= 23
                f4 = not 0 <= int(wh[9:11]) <= 59
                if f1 or f3:
                    raise ValueError('Hours should be between 0 and 23')
                if f2 or f4:
                    raise ValueError('Minutes should be between 0 and 59')
        return working_hours

    class Config:
        extra = 'forbid'


class OrderModel(pydantic.BaseModel):
    base: List[int]
    order_id: int
    weight: float
    region: int
    delivery_hours: List[str]

    class Config:
        extra = 'forbid'

    @validator('weight')
    def weight_should_be(cls, w: float):
        if not 0.01 <= w <= 50:
            raise ValueError('weight should be between 0.01 and 50')
        return w

    @validator('delivery_hours')
    def dh_should_be(cls, delivery_hours: list):
        for dh in delivery_hours:
            if not PATTERN.match(dh) or len(dh) != 11:
                raise ValueError('invalid working hours format')
            try:
                map(int, [dh[0], dh[1], dh[3], dh[4], dh[6], dh[7], dh[9], dh[10]])
            except ValueError:
                raise ValueError('Hours/minutes should be integer')
            if dh[2] != ':' or dh[5] != '-' or dh[8] != ':':
                raise ValueError('invalid separators')
            f1 = not 0 <= int(dh[0:2]) <= 23
            f2 = not 0 <= int(dh[3:5]) <= 59
            f3 = not 0 <= int(dh[6:8]) <= 23
            f4 = not 0 <= int(dh[9:11]) <= 59
            if f1 or f3:
                raise ValueError('Hours should be between 0 and 23')
            if f2 or f4:
                raise ValueError('Minutes should be between 0 and 59')
        return delivery_hours


def log_event(event: str, db_sess: db_session.Session):
    record = Record(
        event=event
    )
    db_sess.add(record)
    db_sess.commit()


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route('/', methods=['GET', 'POST'])
def start():
    form = HomeForm()

    return render_template('homepage.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        raw_phone_number = str(form.phone_number.data)
        print(raw_phone_number)
        user = db_sess.query(User).filter(User.phone_number == raw_phone_number).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html',
                               message="Invalid login or password",
                               form=form)
    return render_template('login.html', title='Login', form=form)


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Registration',
                                   form=form,
                                   message="Passwords do not match")
        db_sess = db_session.create_session()
        raw_number = str(form.phone_number.data)
        print(raw_number)
        if db_sess.query(User).filter(User.phone_number == raw_number).first():
            return render_template('register.html', title='Registration',
                                   form=form,
                                   message="User with this phone already exists")
        user = User(
            name=form.name.data,
            phone_number=raw_number,
            about="",
            user_type=0
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        log_event(f"User {user.name} registered on the platform", db_sess)
        db_sess.commit()

        return redirect('/login')
    return render_template('register.html', title='Registration', form=form)


@app.route('/admins', methods=['GET', "POST"])
@login_required
def make_admins():
    if current_user.user_type < 3:
        return redirect('/')
    db_sess = db_session.create_session()
    users = db_sess.query(User).all()
    return render_template('existing_users.html', title='Existing Users',
                           items=users)


@app.route('/admins/<user_id>', methods=['GET', "POST"])
@login_required
def make_admin(user_id):
    if current_user.user_type < 3:
        return redirect('/')
    db_sess = db_session.create_session()
    user = db_sess.query(User).get(user_id)
    if db_sess.query(User).get(user.c_id):
        courier_id = user.c_id
        courier = db_sess.query(Courier).filter(Courier.id == courier_id).first()
        # return jsonify({'message': 'no courier with this id'}), 400
        user = db_sess.query(User).filter(User.c_id == courier_id).first()
        user.c_id = None
        ords = db_sess.query(Order).filter(Order.orders_courier == courier_id,
                                           Order.complete_time != '').all()
        for i in ords:
            i.orders_courier = 0
        regions = db_sess.query(Region).filter(Region.courier_id == courier_id).all()
        for i in regions:
            db_sess.delete(i)
        whs = db_sess.query(WH).filter(WH.courier_id == courier_id).all()
        for i in whs:
            db_sess.delete(i)
        db_sess.delete(courier)
    user.user_type = 3
    log_event(f"User {user.name} assigned as admin", db_sess)
    db_sess.commit()

    return render_template('result.html', u=str({"Status": 'Ok, now user is admin'}))


@app.route("/history", methods=["GET"])
@login_required
def view_history():
    if current_user.user_type != 3:
        return redirect('/')
    db_sess = db_session.create_session()
    events = db_sess.query(Record).all()
    return render_template("history.html", items=events)


@app.route('/couriers', methods=['GET', "POST"])
@login_required
def add_couriers():
    if current_user.user_type != 3:
        return redirect('/')
    form = NewCourierForm()
    db_sess = db_session.create_session()
    candidates = db_sess.query(User).filter(User.user_type == 1).all()
    form.couriers.choices = [(i.id, i.name) for i in candidates]
    if form.validate_on_submit():
        req_json = form_couriers_json(form.couriers.data, db_sess)['data']
        already_in_base = [i.id for i in db_sess.query(Courier).all()]
        res = []
        bad_id = []
        is_ok = True
        if not req_json:
            return render_template('result.html', u='Incorrect courier information')
        for courier_info in req_json:
            flag = False
            error_ans = []
            try:
                CourierModel(**courier_info, base=already_in_base)
            except pydantic.ValidationError as e:
                error_ans += json.loads(e.json())
                flag = True
            if courier_info['courier_id'] in already_in_base:
                error_ans += [
                    {"loc": ["id"], "msg": "Invalid id: There is a courier with the same id",
                     "type": "value_error"}
                ]
            if flag or courier_info['courier_id'] in already_in_base:
                is_ok = False
                bad_id.append({"id": int(courier_info['courier_id']), 'errors': error_ans})
            if not is_ok:
                continue
            courier = Courier()
            courier.id = courier_info['courier_id']
            user = db_sess.query(User).filter(User.id == int(courier_info['user_id'])).first()
            user.c_id = courier.id
            user.user_type = 2
            # print(user)
            courier.maxw = c_type[courier_info['courier_type']]
            for i in list((courier_info['regions'])):
                reg = Region()
                reg.courier_id = courier.id
                reg.region = i
                db_sess.add(reg)
            for i in list(courier_info['working_hours']):
                wh = WH()
                wh.courier_id = courier.id
                wh.hours = i
                db_sess.add(wh)
            db_sess.add(courier)
            log_event(f"User {user.name} assigned as courier", db_sess)
            res.append({"id": courier_info['courier_id']})

        if is_ok:
            db_sess.commit()

            return render_template('result.html', u=str("Courier added"))
            # return jsonify({"couriers": res}), 201
        # pprint({"validation_error": bad_id})
        # print('-------------------------------------------------------------------------')
        return render_template('result.html', u=str({"validation_error": bad_id}))
        # return jsonify({"validation_error": bad_id}), 400
    return render_template('available_couriers.html', title='New Courier', form=form)


@app.route('/couriers/delete', methods=["POST", 'GET'])
@login_required
def list_couriers():
    if current_user.user_type < 3:
        return redirect('/')
    db_sess = db_session.create_session()
    users = db_sess.query(User).filter(User.user_type == 2).all()
    return render_template('existing_couriers.html', title='Existing Couriers', items=users)


@app.route('/couriers/delete/<user_id>', methods=["POST", 'GET'])
@login_required
def delete_couriers(user_id):
    # courier_id = request.json['courier_id']
    if current_user.user_type < 3:
        return redirect('/')
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.id == user_id).first()
    courier_id = user.c_id
    courier = db_sess.query(Courier).filter(Courier.id == courier_id).first()
    if not courier:
        return render_template('result.html', u=str({'message': 'no courier with this id'}))
        # return jsonify({'message': 'no courier with this id'}), 400
    user = db_sess.query(User).filter(User.c_id == courier_id).first()
    user.c_id = None
    user.user_type = 1
    ords = db_sess.query(Order).filter(Order.orders_courier == courier_id,
                                       Order.complete_time != '').all()
    for i in ords:
        i.orders_courier = 0
    regions = db_sess.query(Region).filter(Region.courier_id == courier_id).all()
    for i in regions:
        db_sess.delete(i)
    whs = db_sess.query(WH).filter(WH.courier_id == courier_id).all()
    for i in whs:
        db_sess.delete(i)
    db_sess.delete(courier)

    db_sess.commit()
    return render_template('result.html', u=f"Courier {courier_id} deleted")
    # return jsonify({"courier_id": courier_id}), 200


@app.route('/orders', methods=["POST", 'GET'])
@login_required
def add_orders():
    form = MakeOrderForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        res = []
        bad_id = []
        is_ok = True
        already_in_base = [i.id for i in db_sess.query(Order).all()]

        order_info = {'order_id': max(already_in_base + [0]) + 1, 'weight': form.weight.data,
                      'region': form.region.data,
                      'delivery_hours': [parse_time(form.workhours_start.data) + '-' + parse_time(
                          form.workhours_end.data)], }
        # print(req_json[0]['delivery_hours'])
        order_id = -1

        flag = False
        error_ans = []
        try:
            OrderModel(**order_info, base=already_in_base)
        except pydantic.ValidationError as e:
            error_ans += json.loads(e.json())
            flag = True
        if order_info['order_id'] in already_in_base:
            error_ans += [
                {"loc": ["id"], "msg": "Invalid id: There is a order with the same id",
                 "type": "value_error"}
            ]
        if flag or order_info['order_id'] in already_in_base:
            is_ok = False
            bad_id.append({"id": int(order_info['order_id']), 'errors': error_ans})

        order = Order()
        order.id = order_info['order_id']
        order.weight = order_info['weight']
        order.region = order_info['region']
        order.orders_courier = 0
        order.user_id = current_user.id
        order.address = regions_table[order.region] + ' '
        city_written = ("c." in form.address.data) or ("city" in form.address.data)
        if not city_written and order.region == 61:
            order.address += PRESENTATION_CITY
        order.address += form.address.data
        print(order.address)
        print(check_address(order.address))
        if not check_address(order.address):
            return render_template('result.html', u=str("Invalid order address, order rejected"))

        for i in list(order_info['delivery_hours']):
            dh = DH()
            dh.order_id = order.id
            dh.hours = i
            db_sess.add(dh)
        db_sess.add(order)
        log_event(f"User {current_user.name} ordered for time {order_info['delivery_hours']}", db_sess)
        res.append({"id": int(order_info['order_id'])})

        if is_ok:
            db_sess.commit()
            return render_template('result.html', u=str(
                f"Order number {order.id} created. Order is available for viewing in \"My Orders\" section!"))
        return render_template('result.html', u=str("Data is incorrect"))

    return render_template('new_order.html', title='New Order', form=form)


@app.route('/couriers/edit', methods=["POST", 'GET'])
@login_required
def edit_courier():
    courier_id = current_user.c_id
    db_sess = db_session.create_session()
    courier = db_sess.query(Courier).filter(Courier.id == courier_id).first()
    if not courier:
        return jsonify({'message': 'no courier with this id'}), 404
    user = db_sess.query(User).filter(User.id == current_user.id).first()
    try:
        req_json = from_few_fields_to_json(*list(user.about.split(";")))
    except Exception as e:
        return render_template('result.html', u=str({'errors': e}))
    # req_json = request.json
    # print(req_json)
    try:
        EditCourierModel(**req_json)
    except pydantic.ValidationError as e:
        # print({'errors': json.loads(e.json())})
        return render_template('result.html', u=str({'errors': json.loads(e.json())}))
        # return jsonify({'errors': json.loads(e.json())}), 400
    for k, v in dict(req_json).items():
        if k == 'courier_type':
            courier.maxw = c_type[v]
        elif k == 'regions':
            v = set(v)
            regions = db_sess.query(Region).filter(Region.courier_id == courier.id).all()
            for reg in regions:
                if reg.region not in v:
                    db_sess.delete(reg)
                else:
                    v.discard(reg.region)
            for i in v:
                reg = Region()
                reg.courier_id = courier.id
                reg.region = i
                db_sess.add(reg)
        elif k == 'working_hours':
            db_sess.query(WH).filter(WH.courier_id == courier.id).delete()
            for i in v:
                wh = WH()
                wh.courier_id = courier.id
                wh.hours = i
                db_sess.add(wh)
    db_sess.commit()
    res = {'courier_id': courier_id, 'courier_type': rev_c_type[courier.maxw]}
    a = db_sess.query(WH).filter(WH.courier_id == courier.id).all()
    res['working_hours'] = [i.hours for i in a]
    b = [i.region for i in db_sess.query(Region).filter(Region.courier_id == courier.id).all()]
    res['regions'] = b
    for i in db_sess.query(Order).filter(Order.orders_courier == courier_id).all():
        dh = db_sess.query(DH).filter(DH.order_id == i.id).all()
        if i.complete_time:
            continue
        if i.region not in res['regions'] or not is_t_ok(dh, a):
            i.orders_courier = 0
    db_sess.commit()
    ords = list(db_sess.query(Order).filter(Order.orders_courier == courier_id,
                                            Order.complete_time == '').all())
    for i in ords:
        i.orders_courier = 0
    db_sess.commit()
    courier.currentw = 0
    orders = choose_orders(list(ords), courier.maxw)
    for order in orders:
        courier.currentw += order.weight
        order.orders_courier = courier_id
    db_sess.commit()
    return render_template('result.html', u="Data changed")


@app.route('/couriers/get', methods=["GET"])
@login_required
def get_courier():
    if current_user.user_type != 2:
        return redirect('/')
    courier_id = current_user.c_id
    db_sess = db_session.create_session()
    courier = db_sess.query(Courier).filter(Courier.id == courier_id).first()
    if request.method == 'GET':
        res = {'courier_id': courier_id, 'courier_type': rev_c_type[courier.maxw]}
        a = [i.hours for i in db_sess.query(WH).filter(WH.courier_id == courier.id).all()]
        res['working_hours'] = a
        b = [i.region for i in db_sess.query(Region).filter(Region.courier_id == courier.id).all()]
        res['regions'] = b
        if not db_sess.query(Order).filter(Order.orders_courier == courier_id,
                                           Order.complete_time == '').all():
            courier.earnings += courier.last_pack_cost
            courier.last_pack_cost = 0
        res['earnings'] = courier.earnings
        if not courier.earnings:
            # return jsonify(res), 200
            return render_template('courier_info.html',
                                   t=translate_to_russian[res['courier_type']],
                                   wh=','.join(list(map(str, res['working_hours']))),
                                   rs=str(res['regions']),
                                   earnings='-',
                                   rating='-'
                                   )
        try:
            t = min([i.summa / i.q
                     for i in db_sess.query(Region).filter(Region.courier_id == courier.id).all() if
                     i.q != 0])
        except ValueError:
            t = 60 * 60
        res['rating'] = round((60 * 60 - min(t, 60 * 60)) / (60 * 60) * 5, 2)
        # return jsonify(res), 200
        return render_template('courier_info.html',
                               t=translate_to_russian[res['courier_type']],
                               wh=','.join(list(map(str, res['working_hours']))),
                               rs=str(res['regions']),
                               earnings=str(res['earnings']),
                               rating=str(res['rating'])
                               )


@app.route('/admins/orders', methods=['POST', 'GET'])
@login_required
def orders_on_map_for_admin():
    if current_user.user_type != 3:
        return redirect('/')
    db_sess = db_session.create_session()
    points = []

    max_distance = 0

    for order in db_sess.query(Order).all():

        if order.complete_time != "" or current_user.show_completed:
            coordinates = get_coordinates(order.address)
            points.append(coordinates + ",pm2rdl" + str(order.id))
            max_distance = max(max_distance, count_distance(coordinates, COURIER_COORDINATES))
    points_str = "|".join(points)

    map_request = f"https://maps.googleapis.com/maps/api/staticmap?" \
                  f"size=650x450&markers=color:blue%7Clabel:S%7C{points_str}&" \
                  f"markers=color:red%7Clabel:C%7C{COURIER_COORDINATES}&" \
                  f"key={STATIC_API_KEY}"

    print(map_request)

    print(map_request)
    response = requests.get(map_request)
    map_file = f"map_{current_user.id}_admin.png"
    with open("static/" + map_file, "wb") as file:
        file.write(response.content)

    return render_template('show_map.html', title="All orders on map", file=map_file, backlink="/")


@app.route('/orders/assign', methods=["POST", 'GET'])
@login_required
def assign_orders():
    if current_user.user_type != 2:
        return redirect('/')
    courier_id = current_user.c_id
    # courier_id = request.json['courier_id']
    db_sess = db_session.create_session()
    courier = db_sess.query(Courier).filter(Courier.id == courier_id).first()
    if not courier:
        return jsonify({'message': 'no courier with this id'}), 400
    ords = db_sess.query(Order).filter(Order.orders_courier == courier_id,
                                       Order.complete_time == '').all()
    if ords:
        # print('didnt all task')
        res = [{'id': i.id} for i in ords]
        # return jsonify({'orders': res, 'assign_time': courier.last_assign_time}), 201
        return render_template('result.html',
                               u=f"You already have {len(res)} orders")
    courier_regions = [i.region for i in
                       db_sess.query(Region).filter(Region.courier_id == courier_id).all()]
    courier_wh = db_sess.query(WH).filter(WH.courier_id == courier_id).all()
    ords = db_sess.query(Order).filter((Order.orders_courier == 0),
                                       Order.region.in_(courier_regions)).all()
    ords = list(
        filter(lambda u: is_t_ok(db_sess.query(DH).filter(DH.order_id == u.id).all(), courier_wh),
               ords))
    orders = choose_orders(list(ords), courier.maxw)
    for order in orders:
        courier.currentw += order.weight
        order.orders_courier = courier_id

    db_sess.commit()

    res = [{'id': order.id} for order in
           db_sess.query(Order).filter(Order.orders_courier == courier_id,
                                       '' == Order.complete_time)]
    if not res:
        return render_template('result.html', u="No orders matching your schedule yet")
        # return jsonify({"orders": []}), 200
    courier.last_pack_cost = kd[courier.maxw] * 500
    # t = str(datetime.datetime.utcnow()).replace(' ', 'T') + 'Z'
    t = str(datetime.datetime.utcnow().isoformat()) + 'Z'
    courier.last_assign_time = t
    assign_time = t
    if '' == courier.last_delivery_t:
        courier.last_delivery_t = assign_time
    log_event(f"Courier {current_user.name} assigned orders with numbers {res} at {t}", db_sess)
    db_sess.commit()
    return render_template('result.html', u=f"{len(res)} orders assigned")
    # return jsonify({"orders": res, 'assign_time': str(assign_time)}), 200


@app.route('/orders/complete/<order_id>', methods=["POST", 'GET'])
@login_required
def complete_orders(order_id):
    if current_user.user_type != 2:
        return redirect('/')
    # req_json = request.json
    db_sess = db_session.create_session()
    courier_id = current_user.c_id
    # courier_id = req_json['courier_id']
    # order_id = req_json['order_id']
    complete_t = str(datetime.datetime.utcnow().isoformat()) + 'Z'
    # complete_t = req_json['complete_time']
    courier = db_sess.query(Courier).filter(Courier.id == courier_id).first()
    order = db_sess.query(Order).filter(Order.id == order_id).first()
    if not courier:
        # return jsonify({'message': 'no courier with this id'}), 400
        return render_template('result.html', u=str({'message': 'no courier with this id'}))
    if not order:
        # return jsonify({'message': 'no order with this id'}), 400
        return render_template('result.html', u=str({'message': 'no order with this id'}))
    if order.orders_courier != courier.id:
        # return jsonify({'message': 'courier and order don\'t match'}), 400
        return render_template('result.html', u=str({'message': 'courier and order don\'t match'}))
    db_sess.commit()
    reg = db_sess.query(Region).filter(
        Region.region == order.region, Region.courier_id == courier_id
    ).first()
    reg.q += 1
    u = datetime.datetime.fromisoformat(complete_t.split('.')[0])
    v = datetime.datetime.fromisoformat(courier.last_delivery_t.split('.')[0])
    courier.last_delivery_t = complete_t
    reg.summa += (u - v).total_seconds()
    if order.complete_time == '':
        courier.currentw -= order.weight
    order.complete_time = complete_t
    if not db_sess.query(Order).filter(Order.orders_courier == courier_id,
                                       Order.complete_time == '').all():
        courier.earnings += courier.last_pack_cost
        courier.last_pack_cost = 0
    db_sess.commit()
    log_event(f"Courier {current_user.name} completed order number {order.id} at {order.complete_time}", db_sess)
    # return jsonify({'order_id': order.id}), 200
    return render_template('result.html', u=f"Order {order.id} completed")


@app.route('/orders/complete/list', methods=['POST', 'GET'])
@login_required
def list_orders():
    if current_user.user_type < 2:
        return redirect('/')
    courier_id = current_user.c_id
    db_sess = db_session.create_session()

    orders = db_sess.query(Order).filter(Order.orders_courier == courier_id).all()

    items = collect_info_about_orders(orders, db_sess, current_user.show_completed)

    items.reverse()

    return render_template('uncompleted_orders.html', title='Uncompleted Orders', items=items)


@app.route('/orders/complete/map', methods=['POST', 'GET'])
@login_required
def orders_on_map():
    if current_user.user_type < 2:
        return redirect('/')
    db_sess = db_session.create_session()
    courier_id = current_user.c_id
    points = ""

    max_distance = 0

    orders = []

    if current_user.user_type == 3:
        orders = db_sess.query(Order).all()
    else:
        orders = db_sess.query(Order).filter(Order.orders_courier == courier_id).all()

    for order in orders:

        if order.complete_time == "" or current_user.show_completed:
            coordinates = get_coordinates(order.address)
            points += ("~" + coordinates + ",pm2rdl" + str(order.id))
            max_distance = max(max_distance, count_distance(coordinates, COURIER_COORDINATES))

    courier_position = f"{COURIER_COORDINATES},round"

    zoom = "&z=15"
    if max_distance > 1:
        zoom = ""

    map_request = f"https://static-maps.yandex.ru/v1/?apikey={STATIC_API_KEY}&l=map&ll={COURIER_COORDINATES}" \
                  f"&pt={courier_position}{points}" \
                  f"&size=650,450{zoom}"

    print(map_request)

    print(map_request)
    response = requests.get(map_request)
    map_file = f"map_{courier_id}.png"
    with open("static/" + map_file, "wb") as file:
        file.write(response.content)

    return render_template('show_map.html', title="Address and Courier", file=map_file,
                           backlink="/orders/complete/list")


@app.route('/users/edit', methods=['POST', 'GET'])
@login_required
def change_about():
    form = EditAboutForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.id == current_user.id).first()
        packed_about = parse_to_about(form.type_of_courier.data, form.region.data, form.workhours_start.data,
                                      form.workhours_end.data)
        user.about = packed_about

        print(user.user_type)
        if user.user_type < 2:
            user.user_type = 1
            if AUTOAPPROVING:
                courier_info = form_couriers_json([current_user.id], db_sess)['data'][0]

                courier = Courier()
                courier.id = courier_info['courier_id']
                user = db_sess.query(User).filter(User.id == int(courier_info['user_id'])).first()
                user.c_id = courier.id
                user.user_type = 2

                # print(user)
                courier.maxw = c_type[courier_info['courier_type']]
                for i in list((courier_info['regions'])):
                    reg = Region()
                    reg.courier_id = courier.id
                    reg.region = i
                    db_sess.add(reg)
                for i in list(courier_info['working_hours']):
                    wh = WH()
                    wh.courier_id = courier.id
                    wh.hours = i
                    db_sess.add(wh)
                db_sess.add(courier)
                log_event(f"User {user.name} assigned as courier", db_sess)
            db_sess.commit()
            return redirect('/')
        db_sess.commit()
        return redirect("/couriers/edit", code=307)

        # print(form.about.data)

    parsed_about = parse_from_about(current_user.about)
    print(parsed_about)
    if parsed_about is not None:
        form.type_of_courier.data, form.region.data, form.workhours_start.data, form.workhours_end.data = parsed_about

    return render_template('edit_user.html', form=form, title="Edit Resume")


@app.route('/orders/view', methods=['POST', 'GET'])
@login_required
def get_user_orders():
    user_id = current_user.id
    db_sess = db_session.create_session()
    orders = []
    if current_user.user_type < 3:
        orders = db_sess.query(Order).filter(Order.user_id == user_id).all()
    else:
        orders = db_sess.query(Order).all()
    items = collect_info_about_orders(orders, db_sess, current_user.show_completed)
    items.reverse()

    return render_template('existing_orders.html', title="My Orders", items=items)


@app.route('/orders/view/<order_id>', methods=['POST', 'GET'])
@login_required
def get_map_of_order(order_id):
    db_sess = db_session.create_session()
    order = db_sess.query(Order).filter(Order.id == order_id).first()
    coordinates = get_coordinates(order.address)

    courier_position = "42.334,-71.118"
    zoom = "&z=14"

    if order.orders_courier:
        courier_position = f"~{COURIER_COORDINATES},round"
        distance = count_distance(coordinates, COURIER_COORDINATES)
        if distance > 1:
            zoom = ""

    map_request = f"https://maps.googleapis.com/maps/api/staticmap?center={coordinates}&" \
                  f"size=650x450&markers=color:blue%7Clabel:S%7C{coordinates}&" \
                  f"markers=color:red%7Clabel:S%7C{courier_position}&" \
                  f"key={STATIC_API_KEY}"

    print(map_request)
    response = requests.get(map_request)
    map_file = f"map_{current_user.id}_{order_id}.png"
    with open("static/" + map_file, "wb") as file:
        file.write(response.content)

    return render_template('show_map.html', title="Address and Courier", file=map_file)


@app.route('/orders/delete/<order_id>', methods=["POST", "GET"])
@login_required
def delete_orders(order_id):
    db_sess = db_session.create_session()
    order = db_sess.query(Order).filter(Order.id == order_id).first()
    if not order:
        return render_template('result.html', u=str({'message': 'no order with this id'}))
        # return jsonify({'message': 'no order with this id'}), 400
    db_sess.delete(order)

    log_event(f"Order {order_id} was deleted", db_sess)

    db_sess.commit()
    return render_template('result.html', u=f"Order {order_id} deleted")
    # return jsonify({"order_id": order_id}), 200


@app.route('/users/get', methods=['POST', 'GET'])
@login_required
def inside_about():
    if current_user.user_type > 1:
        return redirect('/')
    return render_template('user_info.html', title="About User", about=current_user.about)


# @app.route('/clear', methods=['POST', 'GET'])
# @login_required
# def clear():
#     # if request.json['code'] != CODE:
#     #     return jsonify({"error": "wrong code"}), 400
#     logout_user()
#     db_sess = db_session.create_session()
#     db_sess.query(Courier).delete()
#     db_sess.query(Order).delete()
#     db_sess.query(Region).delete()
#     db_sess.query(WH).delete()
#     db_sess.query(DH).delete()
#     db_sess.query(User).delete()
#     db_sess.query(Record).delete()
#     db_sess.commit()
#     user = User(
#         name='admin',
#         phone_number="8 (777) 777 7777",
#         about='main admin',
#         user_type=3
#     )
#     user.set_password('admin')
#     db_sess.add(user)
#     db_sess.commit()
#     return redirect('/')
#     # return jsonify({'status': 'all data cleared'}), 201


@app.route("/donations")
def donate():
    return render_template("donations.html")


@app.route("/change_flag")
@login_required
def change_show_completed_flag():
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.id == current_user.id).first()
    user.show_completed = (user.show_completed + 1) % 2
    db_sess.commit()
    return redirect(request.referrer)


def main():
    db_session.global_init("db/couriers.db")
    app.register_blueprint(shop_api.blueprint)
    app.run()
    # app.run(port=8080)
    # serve(app, host='127.0.0.1', port=8080)
    # app.run(host='0.0.0.0', port=8080)


def create_app():
    db_session.global_init("/home/mzhernevskii/ShipStream/db/couriers.db")
    app.register_blueprint(shop_api.blueprint)
    return app


if __name__ == '__main__':
    main()
