# "RostovExpress" Delivery Service #

**RostovExpress** - reliable and fast delivery service in Rostov-on-Don!

We offer a wide range of goods delivery services: from small parcels to large-sized cargo. Our team of professional couriers is always ready to promptly deliver your order, preserving its integrity and safety.

Our prices are affordable and competitive in the delivery market in Rostov-on-Don.

Don't waste time going to the store or waiting for your order - trust us and we will deliver your parcel on time and safe and sound. Order delivery on the RostovExpress website today!

# [LINK](https://mzhernevskii.pythonanywhere.com)  #

## Technical Description ##
The service allows users to register in the system and take on various roles: regular user, courier, admin.

Each role has its own possibilities:
1. The user can order delivery.
2. The courier delivers, receives money, and earns a rating.
3. The admin has the right to hire and dismiss couriers, promote other users to the admin status.

Also, the service represents a REST API. The API gives the user both admin and courier rights simultaneously.

The main admin is always present in the database, allowing the appointment of couriers and admins.

## Transferring the Repository Folder to Your Computer ##
1. Click the fork button in the repository https://github.com/mishajirx/RostovExpress
2. Open the command line
3. Navigate to the folder of your choice
4. Enter the command git clone https://github.com/<YourName>/RostovExpress

## Installing Required Software ##
#### To download the necessary libraries, follow these steps: ####
0. Perform all actions listed below in the terminal
1. Navigate to the project directory in the command line
2. Execute pip install -r requirements.txt
#### Example ####
$ pip install -r requirements.txt

## Running the Application ##
To run the application, simply execute in the console
python3 main.py (or sudo python main.py)
#### Example #### 
$ python3 main.py

## Running Tests ##
To run tests, you need to:
1. Repeat the steps from the "Running the Application" section
2. Press ctrl+z. Execute bg
3. Execute pytest-3 test.py -x -s
4. Enter 'y'
#### Example: ####
$ sudo python3 main.py
$ ^Z
& bg
$ pytest-3 test.py -x -s

## Auto Start ##
To make the server start on system boot, enter the following commands in the console:
1. crontab -e
2. In the opened file, type the following in the last line:
   @reboot python3 /path_to_the_project/main.py

## Additional
#### User Types:
1. Courier
2. Admin
3. Bot
#### Bot capabilities:
1. Place an order (/orders)
2. Submit a courier application
#### Admin capabilities:
1. Approve courier applications (/couriers)
#### Courier capabilities:
1. Accept orders (/orders/assign)
2. Change their parameters (/courier/<courier_id>)
3. Complete an order (orders/complete)
4. Get information about themselves (/couriers/<couriers_id>)
