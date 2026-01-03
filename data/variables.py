import re


courier_fields = {'courier_id', 'courier_type', 'regions', 'working_hours'}
order_fields = {'order_id', 'weight', 'region', 'delivery_hours'}
c_type = {'foot': 10, 'bike': 15, 'car': 50}
translate_to_russian = {'foot': 'Foot', 'bike': "Bike", 'car': "Car"}
rev_c_type = {10: 'foot', 15: 'bike', 50: 'car'}
kd = {10: 2, 15: 5, 50: 9}
CODE = 'zhern0206eskiy'
PATTERN = r = re.compile('.{2}:.{2}-.{2}:.{2}')
COURIER_COORDINATES = "42.334,-71.118"
AUTOAPPROVING = True
PRESENTATION_CITY = ", Brookline, "
regions_table = {1: "Alabama",
                2: "Alaska",
                4: "Arizona",
                5: "Arkansas",
                6: "California",
                8: "Colorado",
                9: "Connecticut",
                10: "Delaware",
                11: "District of Columbia",
                12: "Florida",
                13: "Georgia",
                15: "Hawaii",
                16: "Idaho",
                17: "Illinois",
                18: "Indiana",
                19: "Iowa",
                20: "Kansas",
                21: "Kentucky",
                22: "Louisiana",
                23: "Maine",
                24: "Maryland",
                25: "Massachusetts",
                26: "Michigan",
                27: "Minnesota",
                28: "Mississippi",
                29: "Missouri",
                30: "Montana",
                31: "Nebraska",
                32: "Nevada",
                33: "New Hampshire",
                34: "New Jersey",
                35: "New Mexico",
                36: "New York",
                37: "North Carolina",
                38: "North Dakota",
                39: "Ohio",
                40: "Oklahoma",
                41: "Oregon",
                42: "Pennsylvania",
                44: "Rhode Island",
                45: "South Carolina",
                46: "South Dakota",
                47: "Tennessee",
                48: "Texas",
                49: "Utah",
                50: "Vermont",
                51: "Virginia",
                53: "Washington",
                54: "West Virginia",
                55: "Wisconsin",
                56: "Wyoming",
                }