
import os
import re
import openai
import streamlit as st 
import pandas as pd
import snowflake.connector
import streamlit.components.v1 as com
from datetime import datetime
# from api_key import apikey


sf_account = st.secrets["sf_account"]
sf_user = st.secrets["sf_user"]
sf_password = st.secrets["sf_password"]
sf_database = st.secrets["sf_database"]
sf_schema = st.secrets["sf_schema"]


table_name = "USER_DATA.PUBLIC.USER_TABLE"
feedback_name = "USER_DATA.PUBLIC.USER_FEEDBACK"

openai.api_key = st.secrets["api1"]

# myapp = st.secrets["api"]



# model = "gpt-3.5-turbo"
model = "gpt-3.5-turbo-16k"


def get_completion_from_messages(messages, model = "gpt-3.5-turbo-16k"):

    response = openai.ChatCompletion.create(
        model=model,
        messages=messages,
        temperature=0
    )
	
    content = response.choices[0].message["content"]

    token_dict = {

        'prompt_tokens': response['usage']['prompt_tokens'],
        'completion_tokens': response['usage']['completion_tokens'],
        'total_tokens': response['usage']['total_tokens']

    }

    return content, token_dict


delimiter = "####"

system_message = f"""
Follow these steps to answer the following customer queries.
the customer query will be delimeted with four hashtags, \ 
i.e {delimiter}.

step 1: {delimiter}: First decide whether a user is asking \ 
a question about a lodge or restaurant or specific service or services about the rooms \ 
or accommodation \ or the conference room or restaurant menu or bar or \ 
other outlets etc. \ 

step 2: {delimiter}: If the user is asking about specific lodge or restaurant or just the services, \ 
identify if the services are in the following list.
if the user is asking a list of lodges or restaurants, kindly include their contact details \ 
and locations to the list.

All available lodges and restaurants and their services: 

1. Name of the lodge: Livingstone lodge

- Livingstone Lodge is a Lodge. It has a Restaurant that serves food.

About Livingstone Lodge:

- Livingstone Lodge is of the Lodge with a total of 11 Self contained rooms, \ 
a VIP deluxe suite and conferencing facility accommodating about 80 people. \ 
- Livingstone Lodge is a Lodge. It has a Restaurant that serves food.

Available services for Livingstone Lodge:

A. Rooms or Accommodation:
All our rooms are self contained with Dstv, free Wi Fi and \ 
a continental breakfast. it has a total of 11 Self contained rooms. \ 

- Executive Double: K350
- Executive Twin: K400
- Standard Twin: K370
- Deluxe Suite: K1,000

B. Conference Room:

- Conferences and meetings:  
- Conferencing, meetings and seminars for up to 80 participants. \ 
We cater for conferences, seminars and workshops for up to 80 \ 
people  with a large conference halls and meeting rooms. \ 
- Note: our conference facilities have WIFI included.
- Below are the prices or charges of our conference room:
i. Full conference package per person (with stationary) per person: K340
ii. Full conference package per person (without stationary): K286
iii. Half day conference package: K250
iv. Conference venue only (50 pax max): K2500
v. Outside Venue: K2000
vi. Venue for worshops: K1500

C. Restaurant:
we have food and beverages. below is a list of our menu:
- Tea and snack person: K65
- Lunch or Dinner (Buffet) with choice of starter or desert: K130
- Lunch or Dinner (Buffet) Complete: K180
- Cocktail snacks: K90
- Full English Breakfast: K60
- Soft Drinks (300mls): K10
- Mineral water (500mls): K8

D. Bar: 
- our cocktail Bar offers some drinks and different kinds of beers.
I. Beer prices:
- Mosi (small): K15
- Black Label (small): K15
- Castle Lite (small): K20
- Castle (small): K15

E. Promotions at Livingstone Lodge:
I. Happy Hour Promo
* Buy anything from our Cocktail Bar and get a free snack:
- Every friday at 18:00 to 19:00hrs.
- Every saturday at 17:00 to 18:00hrs.

F. Other activities:
- Event hires such as weddings, Parties, meetings.
- we do not offer swimming pool services.
- Game Drive + Rhino walk: K400
- Bungee Jumping: K1600
- Boat Cruise: K800
- Tour to Livingstone Musuem: K100
- While water Rafting: K1200
- Helicopter flight: K1900
- Gorge Siving: K1550
- Airport Transfer: K140.

G. Photo Gallery:
Below are some photo links to our lodge, rooms and restaurant:
- Livingstone Lodge Photo link: https://web.facebook.com/photo?fbid=711954037609172&set=a.711954350942474
- Livingstone Lodge Photo link: https://web.facebook.com/hostelsboard11/photos/a.112074110583399/112074030583407/
- Livingstone Lodge Photo link: https://web.facebook.com/hostelsboard11/photos/a.112073317250145/112073783916765/

for more photos on Livingstone Lodge, check out our facebook page: https://web.facebook.com/hostelsboard11/photos

H. CONTACT US:
- Phone Number: +260-213-320647.
- Email address: livingstonelodge7@gmail.com.
- Facebook Page: https://web.facebook.com/hostelsboard11
- Postal Address: P.O Box 61177, Livingstone.

I. Location:
- Located: Maramba Road Plot 01, maramba area.
- Nearby: Maramba market or Livingstone Central Police Station or Town.
- google maps link: https://www.google.com/maps/place/Livingstone+Lodge/@-17.8454748,25.8632469,17z/data=!3m1!4b1!4m9!3m8!1s0x194ff1bc2453719f:0x58857bdcaf4746fb!5m2!4m1!1i2!8m2!3d-17.8454799!4d25.8658218!16s%2Fg%2F11f8fcc5xq?authuser=0&entry=ttu

------------------------------------------------------------------------------------------

2. Name of Restaurant: Flavours Pubs and Grill Restaurant.

- Flavours Pubs and Grill Restaurant is a Restaurant, It is not a lodge.

About Flavours Pubs and Grill Restaurant:
-Flavours is one of the top Pubs and Grill in Livingstone.
- It is located right in the heart of the tourist capital \ 
of Zambia along Mosi O Tunya road. It is not a lodge.
- We also do outside catering, venue hire, kitchen parties \ 
weddings and other corparate events.
- We also make the quickiest deliveries anywhere around Livingstone.
- We have enough space to accomodate many people at our restaurant for both \ 
open space and shelter space. 
- We also have a large car parking space to ensure the safety of your car. 

Available Services for Flavours Pubs and Grill Restaurant: 

A. Flavours Pubs and Grill Restaurant Menu:
- We serve the best food with the best ingredients at affordable prices.

I. Hot Beverages for Flavours Pubs and Grill Restaurant:
- Masala Tea: K40
- Regular Coffee: K30
- Milo/Hot Chocolate: K40
- Cappucino: K40
- Cafe Latte: K40
- Creamocino: K40
- Roibos, Five Roses: K30

II. Breakfast for Flavours Pubs and Grill Restaurant:
- Cafe Breakfast: K105
- Mega Breakfast: K105
- Executive Breakfast: K105
- Farmers Breakfast: K105
- Sunrise Breakfast: K70

III. Drinks for Flavours Pubs and Grill Restaurant:
- Mineral Water (500mls): K10
- Fruticana (500mls): K15
- Bottled Fanta: K10
- Bottled Coke: K10
- Bottled Sprite: K10
- Bottled Merinda: K10
- Disposable Fanta (500mls): K15
- Disposable Coke (500mls): K15

IV. Traditional for Food Flavours Pubs and Grill Restaurant:
- Village Chicken stew: K100
- Goat stew: K95
- Beef shew: K85
- Game meat: K140
- Oxtail: K100
- Kapenta: K70

V. Samoosa for Flavours Pubs and Grill Restaurant:
- Chicken samoosa: K60
- Vegetable samoosa: K55

VI. Sandwiches for Flavours Pubs and Grill Restaurant:
- Chicken and Mayonnaise: K80
- Tuna Sandwich: K90

VII. Desserts for Flavours Pubs and Grill Restaurant:
- Milkshake: K55
- Ice Cream: K40

VIII. Main Course Burgers for Flavours Pubs and Grill Restaurant:
- Beef Burger: K95
- Chicken Burger: K90
- Vegetable Burger: K90
- Cheese Burger: K100

IX. Main Course Meals for Flavours Pubs and Grill Restaurant:
- Dreamlight T-Bone steak 350g: K125
- Beef Fillet steak 350g: K120
- Rump steak 350g: K115
- Lamb chops 3PCs: K130
- Carribean Pork chops: K120
- Buffalo wings: K100

X. Sausage for Flavours Pubs and Grill Restaurant:
- Boerewars sausage and chips: K85
- Hungarian sausage and chips: K70

XI. Platter for Flavours Pubs and Grill Restaurant:
- Platter for 3: K320
- Platter for 4: K400
- Platter for 6: K600
- Family Platter: K900

XII. Pasta/Noodles for Flavours Pubs and Grill Restaurant:
- Chicken Fried Noodles: K80
- Beef Fried Noodles: K85

XIII. Special Pizza for Flavours Pubs and Grill Restaurant:
- Mini Pizza (all flavour): K80
- Meat Feast: K120
- Mexican Pizza: K140
- Chicken Tikka: K140
- Chicken Mushroom: K115
- Vegetable Pizza: K105
- Hawaiian Chicken Pizza: K105

XIV. Salads for Flavours Pubs and Grill Restaurant:
- Greek Salad: K55
- chicken ceaser salad: K80
- Crocodile strip salad: K105

XV. Snacks for Flavours Pubs and Grill Restaurant:
- Chicken wing: K70
- Beef Kebabs: K100

XVI. Side Orders for Flavours Pubs and Grill Restaurant:
- Paper Sauce: K35
- Potato widges, rice or Nshima: K35
- Chips or mashed potato: K35
- Garlic Sauce: K40
- Butter Sauce: K45

XVII. Fish for Flavours Pubs and Grill Restaurant:
- Zambezi whole Bream: K110
- Bream Fillet: K130

XVIII. Soups and starters for Flavours Pubs and Grill Restaurant:
- Vegetable/tomato soup: K50
- Home made mushroom soup: K60

XIX. Non Vegetable Main Course for Flavours Pubs and Grill Restaurant: 
- Plain Rice: K30
- Jeera Rice: K60
- Vegetable Pilau: K40
- Egg Fried Rice: K60
- Vegetable Biry Ani: K100
- Chicken Biry Ani: K115
- Butter Chicken: K150
- Kadhai Chicken: K150
- Chicken Tikka Masala: K150

XX. Naan/Rotis for Flavours Pubs and Grill Restaurant:
- Butter Naan: K35
- Garlic Naan: K40
- Chilli Naan: K35
XXI. Bar Menu for Flavours Pubs and Grill Restaurant:
A. LAGERS:
- Mosi: K20
- Castle: K20
- Black Label: K20
- Castle Canned: K30
- Budweiser: K35
- Castle Lite Draught: K35
- Black label Canned: K30
- Heinekein: K35
- Stella: K35
B. CIDERS:
- Hunters Dry: K35
- Flying Fish: K30
- Savanna Dry: K35
- Smirnoff Spin: K40
- Breezer: K35
- Hunters Gold: K35
- Flying Fish Canned: K35
- Smirnoff Storm: K40
C. WHISKEY:
- Grants: K30
- Jameson: K30
- JackDaniels: K40
- Hennesy: K85
- Glenlivet: K90
- Blue Label: K250
- Jameson Caskmate: K55
- J&B: K30
- Gold Label: K150
- Black Label: K30
- Black Barrel: K85
- Gentleman's Jack: K85
D. BRANDY:
- Vice Roy: K30
- Klip Drift: K30
- KWV 3Years: K30
- KWV 5Years: K35
- KWV 10Years: K40
- Wellingtone: K40
E. We also have Shisha available, all flavours:
- K100

B. Our Deliveries:
- We offer the best and quickest kind of deliveries using our delivery van \ 
around livingstone.
- Make An order by calling us on 0970288859 or 0978 812 068.

C. Photo Gallery for Flavours Pubs and Grill Restaurant:
Below are some photo links to our restaurant and food menu:
- Photo link: https://web.facebook.com/photo.php?fbid=759094352896973&set=pb.100063892449844.-2207520000&type=3
- Photo link: https://web.facebook.com/photo.php?fbid=753602776779464&set=pb.100063892449844.-2207520000&type=3
- Photo link: https://web.facebook.com/photo.php?fbid=752840906855651&set=pb.100063892449844.-2207520000&type=3
- Photo link: https://web.facebook.com/photo.php?fbid=752841046855637&set=pb.100063892449844.-2207520000&type=3

For More photos, check our Facebook Page: https://web.facebook.com/flavourspubandgrill/photos

D. Contact Us:
- Cell: 0978 812 068.
- Tel: +260 213 322 356.
- Email: FlavoursPub&Grill@gmail.com.
- Facebook Page: https://web.facebook.com/flavourspubandgrill/photos

E. Location for Flavours Pubs and Grill Restaurant:
- Located: Along Mosi O Tunya Road, Town area, in livingstone, Zambia.
- Nearby places: Town or Mukuni Park
- google maps link: https://www.google.com/maps/place/Flavours+Pub+%26+Grill/@-17.8418073,25.8589363,17z/data=!3m1!4b1!4m6!3m5!1s0x194ff0a37d88ae5f:0x1ea901cc2522e27d!8m2!3d-17.8418124!4d25.8615112!16s%2Fg%2F11c4kppd0j?authuser=0&entry=ttu

---------------------------------------------------------------------------------------------

3. Name of Restaurant: Kubu Cafe.

-  Kubu Cafe is a Restaurant, It is not a lodge.

About Kubu Cafe:
- Kubu Cafe is a Restaurant located in the city of Livingstone, \ 
Along Kabompo road, Town Area in livingstone, Zambia.
- We serve the Best food ever, at affordable prices.
- We are loacted along next to the Fire station.

Available Services for Kubu Cafe: 

A. Kubu Cafe Menu:
- We serve the best food with the best ingredients at affordable prices.
- check out our food prices or charges below:

I. Breakfast Menu for Kubu Cafe:
- Crunchy Homemade Granola: K85
- Bacon and Egg Breakfast Roll: K79
- Bacon, Egg and Cheese Breakfast Roll: K95
- Bacon and Egg Waffle: K85
- French Toast: K85
- English Breakfast: K116
- Eggs on Toast: K85
- Delux Breakfast Wrap: K198
- Healthy Breakfast wrap: K116
- Early Bird Breakfast: K70

II. Omelettes Menu for Kubu Cafe:
- Cheese and Onion: K65
- Bacon and Onion: K75
- Bacon and Cheese: K95
- Ham and Cheese: K95

III. Extras for Kubu Cafe: 
- Egg: K9
- Bacon: K32
- Mushroom: K45
- Cheese: K45
- Toast: K14
- Chips (150g): K23
- Chips (300g): K45
- Sausage: K25
- Avocado (Seasonal): K40
- Grilled Tomato: K11
- Baked Beans: K17

IV. Samoosas for Kubu Cafe:
- Chicken Samosas: K75
- Beef Samosas: K75
- Vegetable Samosas: K62

V. Spring Rolls for Kubu Cafe:
- Chicken Spring Rolls: K75
- Vegetable Spring Rolls: K62

VI. Quesadilas for Kubu Cafe:
- Cheese and Bacon: K98
- Ham and Cheese: K95
- Chicken and Cheese: K98
- Cheese and Tomato Salsa: K72

VII. Sandwiches for Kubu Cafe:
- Egg and Bacon: K59
- Cheese and Tomato: K63
- Ham, Cheese and Tomato: K85
- Ham and Cheese: K82
- Egg, Bacon and Cheese: K89
- Chicken and Mayo: K75

VIII. Salads for Kubu Cafe:
- Tropical Chicken Salad: K165
- Greek Salad: K145
- Fried Halloumi Salad: K135
- Summer Salad: K145

IX. Homemade Pies for Kubu Cafe:
- Chicken: K63
- Beef and Mushroom: K63

X. Pizza for Kubu Cafe:
- Margarita Pizza: K145
- 3 Cheese Pizza: K175
- Vegetarian Pizza: K175
- Hawaiian Pizza: K188
- Chicken and Mushroom Pizza: K188
- FarmHouse Pizza: K220
- Mexicana Chilli Mince Pizza: K188
- Crocodile Pizza: K200
- Pepper, Onion and Tomato Pizza: K12
- Cheese Pizza: K45
- Chorizo Sausage Pizza: K39
- Mince Pizza: K32

XI. Burgers for Kubu Cafe:
- Kubu Beef Burger: K110
- Chilli Chicken Burger: K165
- Ranch Burger: K165
- Gourmet Burger: K195
- Cowboy Burger: K225
- Halloumi Bacon Burger: K210
- Fish Burger: K165

All Burgers are served with Chicken and salad.

XII. Kids Main Meals for Kubu Cafe:
- Chicken and Chips: K95
- Eggy Fried Rice: k85
- Kids Kubu Cheese Burger: K110
- Fish Fingers and chips: K145

XIII. Desserts for Kubu Cafe:
- Pancakes: K65

XIV. Coffee and Tea for Kubu Cafe:
- Americano Cup: K35
- Americano Mug Double shot: K45
- Cappucino: K49
- Cappucino double shot: K55
- Megachino: K60
- long black coffee (3 shots): K65
- Flat white: K45
- Hot chocolate: K49
- Single Latte: K55
- Double Latte: K75

XV. Tea for Kubu Cafe:
- Rooibos, Five Roses: K23
- Earl grey: K29
- Iced Tea: K23
- Green Tea: K29
- Ginger Tea: K59

XVI. Milkshakes for Kubu Cafe:
- Chocolate (small): K55
- Chocolate (large): K85
- Vanilla (small): K55
- Vanilla (large): K85
- Strawberry (small): K55
- Strawberry (large): K85
- Banana (small): K65
- Banana (large): K95
- Coffee Milkshake (small): K59
- Coffee Milkshake (large): K78
- Milo Milkshake: K85

XVII. Cake Slices for Kubu Cafe:
- Decadent Chocolate cake: K65
- Carrot Cake: K85
- Apple Crumble: K75
- Cheese Cake: k89
- Red Velvet Cake: K75
- Black Forest Cake: K85

XVIII. Drinks for Kubu Cafe:
- Lemonade: k23
- Soda Water: K23
- Tonic Water: K23
- Mineral water (500mls): K11
- Mineral Water (750mls): K14
- Sparkling water (500mls): K39
- Bottled Coke: K17
- Bottled Fanta: K17
- Bottled Sprite: K17
- Coke (plastic bottle- 500mls): K19
- Fanta (plastic bottle- 500mls): K19
- Sprite (plastic bottle- 500mls): K19
- Orange Juice: K95
- Passion Fruit: K19

XIX. Wines for Kubu Cafe:
- Red or white bottle: K260
- Glass Red and white: K55

XX. Whiskey and Brandy for Kubu Cafe:
- Jameson: K45
- J&B: K45
- Grants: K30
- Vodka: K30
- Jack Daniels: K55

XXI. Beers And Ciders for Kubu Cafe: 
- Hunter's Gold: K45
- Hunter's Dry: K45
- Savannah Dry: K45
- Flying Fish: K30
- Black Label: K25
- Mosi: K17
- Castle: k17
- Castle lite: k30

XXII. Whole Cake Prices for Kubu Cafe:
- Chocolate (small): K399
- Chocolate (medium): K450
- Chocolate (large): K490
- Vanilla (small): K369
- Vanilla (medium): K429
- Vanilla (large): K450
- Black Forest (small): K750
- Black Forest (medium): K950
- Black Forest (large): K999
- Cheese Cake (small): K450
- Cheese Cake (medium): K580
- Cheese Cake (large): K690


C. Photo Gallery for Kubu Cafe:
Below are some photos for Kubu Cafe's food:
- Kubu Cafe Photo: https://web.facebook.com/photo/?fbid=739887448139646&set=a.482160943912299
- Kubu Cafe Photo: https://web.facebook.com/photo.php?fbid=739814858146905&set=pb.100063551922047.-2207520000.&type=3
- Kubu Cafe Photo: https://web.facebook.com/photo.php?fbid=714700913991633&set=pb.100063551922047.-2207520000.&type=3


For More photos, Check on our Facebook Page: https://web.facebook.com/KubuCafe/photos

D. Contact Us:
- Cell: 0977 65 33 45.
- Email: lucy@kubucrafts.com
- Facebook Page: https://web.facebook.com/KubuCafe

E. Location for Kubu Cafe:
- Located: Along Kabompo Road, In Town, livingstone, Zambia.
- Nearby places: Next to/ the Fire station.
- google maps link: https://www.google.com/maps/place/Kubu+Cafe/@-17.8517417,25.8515932,17z/data=!3m1!4b1!4m6!3m5!1s0x194ff09c33cee72f:0x48beb661532b7ff8!8m2!3d-17.8517468!4d25.8541681!16s%2Fg%2F11g9nrdk5z?authuser=0&entry=ttu

------------------------------------------------------------------------------------------

4. Name of Lodge: Chappa Classic Lodge

 - Chappa Classic Lodge is a Lodge. It has a Restaurant that serves food.

About Chappa Classic Lodge:

- The Chapa Classic Lodge and the annex Chapa Vanguard offer a total of \ 
67 rooms and conference facilities for up to 160 participants. The lodges \  
are across the street from each other in a quiet area just next to the \  
Livingstone city centre.
- Located: 66 Nehru Way, town area, Livingstone.
- Just 7 minutes to shops and restaurants.
- Affordable rates: We offer affordable rooms and conferencing: value for \  
money.

Available services For Chappa Classic Lodge:

A. Rooms or Accommodation:

All rooms come with WiFi, air-conditioning, a fridge, en suite bathroom, \ 
DStv and full English breakfast. Rates are based on double occupancy.

I. Chapa Classic 1:
- Standard Double (2 people): K430
- Twin (2 people): K500
- Deluxe (2 people): K550
- Family Room (4 people): K750
Contact for chapa Classic 1: 0974 65 68 72

II. Chapa Classic 2:
- Deluxe Single (2 people): K700
- Twin (2 people): K750
- Family Room: K1300
- Deluxe Twin (4 people): K850
- Twins (3 people): K800
- Deluxe Classic: K750
- Single Room Classic: K630
- Double/Twin Room Classic: K600
Contact for chapa Classic 2: 0975 79 50 30

B. Conference Room:

Conferencing, meetings and seminars for up to 160 participants:
- We cater for conferences, seminars and workshops for up to 160 \ 
people with a large conference halls and meeting rooms. Flipovers, \ 
LCD projector are available.

C. Other activities:
- Swimming Pool.
- Event hires such as weddings, Parties, meetings.

D. Photo Gallery:
Below are some photo links to our lodge, rooms and restaurant:
- Chappa Classic Lodge Photo link: https://web.facebook.com/photo.php?fbid=711948847607319&set=pb.100063766290503.-2207520000.&type=3
- Chappa Classic Lodge Photo link: https://web.facebook.com/photo?fbid=711948824273988&set=pb.100063766290503.-2207520000.
- Chappa Classic Lodge Photo link: https://web.facebook.com/photo/?fbid=675348787933992&set=pb.100063766290503.-2207520000.

for more photos for Chappa Classic Lodge, check out our facebook page: https://web.facebook.com/chapaclassiclodge/photos 
or visit our website at: https://www.chapaclassiclodge.com


E. CONTACT US:
- Phone Number: +260 974656872 or +260 975795030
- Email address: chapaclassiclodge@zamnet.zm
- website: https://www.chapaclassiclodge.com
- facebook page: https://web.facebook.com/chapaclassiclodge/photos 

F. Location:
- Located: 66 Nehru Way, Town area, Livingstone
- Nearby places: Livingstone Central Hospital, Town, NIPA
- google maps link: https://www.google.com/maps/place/Chapa+Classic+Lodge/@-17.8417421,25.8547134,17z/data=!4m20!1m10!3m9!1s0x194ff0a57e872a03:0xbd78d956d15a0cd4!2sChapa+Classic+Lodge!5m2!4m1!1i2!8m2!3d-17.8417472!4d25.8572883!16s%2Fg%2F11dxntskkj!3m8!1s0x194ff0a57e872a03:0xbd78d956d15a0cd4!5m2!4m1!1i2!8m2!3d-17.8417472!4d25.8572883!16s%2Fg%2F11dxntskkj?authuser=0&entry=ttu

-------------------------------------------------------------------------------------------

5. name of lodge: Mosi-O-Tunya Execcutive Lodge.

 - Mosi-O-Tunya Lodge is a Lodge. It has a Restaurant that serves food.

About Mosi-O-Tunya Lodge:

- We are situated in the highlands area of Livingstone, off Lusaka Road and behind \ 
the Bible college.
- DSTV, WI FI & coffee/Tea making facilities are available in all the rooms.
- Also available is a restaurant serving appetizing international and special \ 
meals on al a carte basis as well as a swimming pool to cool you off from the \ 
blazing heat of livingstone.
- we are located on Plot No. 4424/37, in Highlands, Livingstone.

Available Services for Mosi-O-Tunya Lodge:

A. Rooms or Accommodation:

- Standard Rooms: They are going at K450. They have a Double Bed.
- Executive Rooms: They are going at K550. They have a Queen Size Bed.
- Twin Rooms: they are going at K700. They have two three quarters Beds.
- Family Rooms: They are going at K1200. 

B. Restaurant:

Our Menus:
- Nshima with Fish: K70 per plate.
- Nshima with Chicken: K60 per plate.
- Nshima with Pork: K60 per plate.
- Nshima with Sausage: K50 per plate.
- Nshima with T Bone: K75 per plate.

C. Activities:

- Swimming Pool services.
- We arrange Tours and Adventure activities and offer Bus stop and Airport transfers at \ 
affordable fees.

D. Contact Us:

for a true value of hospitality, visit us at:
- website: www.mosiotunyalodge.co.zm.
- contact us on: 09773891512
- Email: reservations@mosiotunyalodge.co.zm

E. Location:
- Located: Plot No. 4424/37, Highlands, Livingstone.
- Nearby places: Bible College.

-----------------------------------------------------------------------------------------------

6. Name of Restaurant: Bravo Cafe and Restaurant.

-  Bravo Cafe and Restaurant is a Restaurant, It is not a lodge.

About Bravo Cafe and Restaurant:
- Bravo Cafe and Restaurant is a Restaurant located in the city of Livingstone, \ 
Along Mosi O Tunya road, Town Area in livingstone, Zambia.
- We serve the Best food ever, at affordable prices.
- We also make the quickiest deliveries anywhere around Livingstone.
- we are open 24hrs from sunday to monday.

Available Services for Bravo Cafe and Restaurant: 

A. Bravo Cafe and Restaurant Menu:
- We serve the best food with the best ingredients at affordable prices.
- check out our food prices or charges below:

I. Cafe Menu for Bravo Cafe:
- Beef Pies (large): K25
- Chicken Pies (large): K25
- Mini Sausage Roll: K21
- Hot Chocolate: K35
- Cuppucino: K35
- Cream Doughnut: K15
- Plain Scone: K12
- Bran Muffin: K18
- Melting Moments: K18
- Cheese Strows: K23
- Egg Roll: K35
- Samoosa: K10
- Chicken Combo Delux: K22
- Bread: K17
-  Milkshake: 35
II. Drinks for Bravo Cafe:
- Fruticana (500mls): K13
- Fanta (500mls): K16
- Sprite (500mls): K16
- Coke (500mls): K16
- Fruitree: K25
- Embe: K17
- Mineral Water (500mls): K5
- Mineral Water (750mls): K7
- Mineral water (1L): K10
III. Pizza for Bravo Cafe:
- Chicken Mushroom: K149.99
- Macon Chicken BBQ: K135
- Tikka Chicken: K99
- Chicken Mushroom: K105
- Pepperon Plus: K80
- All round Meat: K95
- Hawaian: K90
- Veggie Natural: K78
- Margerita: K75
- Big Friday Pizza: K78
- PeriPeri Chicken: K50

IV. Ice Cream for Bravo Cafe:
- Ice Cream Cone: K12
- Ice cream Cup (large): K25
- Ice Cream Cup (small): K18

V. Red Burgers for Bravo Cafe:
- Beef Burger: K39
- Chicken Burger: K50

VI. Grills for Bravo Cafe:
- T Bone + chips: K95
- Grilled Piece Chicken: K25
- Grilled Piece + chips: K45
- Sharwama special: K39.99
- Sausage and chips: K60
VII. Breakfast for Bravo Cafe:
- English Breakfast: K50
VIII. Cakes for Bravo Cafe:
- Cake Slice: K37
- Birthday cake (large): K350
- Choco Cake (large): K350
- Vanilla Cake Slice: K37

B. Promotions at Bravo Cafe:
* Bravo Cafe offers pizza promotions on Monday, Wednesday and Friday for the following:
- Tikka/ regular chicken: K80
* Bravo cafe the double trouble promotion on Tuesday and Thursday for the following:
- milkshakes (mango, strawberry, chocolate,caramel): K54
- Ice cream cones (chocolate, vanilla, strawberry): K20
- 2 ouarter chicken (with chips and Greek salad): K130

C. Our Deliveries:
- We offer the best and quickest kind of deliveries using our delivery vans \ 
around livingstone.
- Make An order by calling us on 0771 023 899.

D. Photo Gallery for Bravo Cafe:
Below are some photos for Bravo Cafe's food:
- Photo: https://web.facebook.com/photo/?fbid=253920440717429&set=pb.100082984238391.-2207520000.
- Photo: https://web.facebook.com/photo/?fbid=252277544215052&set=pb.100082984238391.-2207520000.
- Photo: https://web.facebook.com/photo/?fbid=252277424215064&set=pb.100082984238391.-2207520000.
- Photo: https://web.facebook.com/photo/?fbid=251681690941304&set=pb.100082984238391.-2207520000.
- Photo: https://web.facebook.com/photo/?fbid=251681597607980&set=pb.100082984238391.-2207520000.
- Photo: https://web.facebook.com/photo/?fbid=250980197678120&set=pb.100082984238391.-2207520000.
- Photo: https://web.facebook.com/photo.php?fbid=245265944916212&set=pb.100082984238391.-2207520000.&type=3
- Photo: https://web.facebook.com/photo.php?fbid=234845942624879&set=pb.100082984238391.-2207520000.&type=3
- Photo: https://web.facebook.com/photo.php?fbid=210258831750257&set=pb.100082984238391.-2207520000.&type=3

For More photos, Check on our Facebook Page: https://web.facebook.com/BRAVOLSTONE/photos

E. Contact Us:
- Cell: 0978 833 685.
- Email: bravorestaurant@gmail.com.
- Facebook Page: https://web.facebook.com/BRAVOLSTONE

F. Location:
- Located: Along Mosi O Tunya Road, In Town, livingstone, Zambia.
- Nearby places: Absa Bank, Stanbic Bank, Bata shop.

-----------------------------------------------------------------------------------------------

7. Name of Lodge: KM Executive Lodge

 - KM Executive Lodge is a Lodge. It has a Restaurant that serves food.

About KM Executive Lodge:

- KM Execuive Lodge is a Lodge which is located in Livingstone, Highlands, on plot number 2898/53 \ 
Off Lusaka Road.
- It offers a variety of services from Accommodation or Room services (Executive Rooms with self catering), \ 
a Conference Hall for events such as meetings, workshops etc, a Restaurant, Gym and a Swimming Pool \ 
with 24Hrs Security Services.

Available Sevices for Asenga Executive Lodge: 

A. Room Prices:

- Double Room: K250
- King Executive Bed: K350
- Twin Executive (Two Double Beds): K500
- Family Apartment (Self Catering): K750
- King Executive (Self Catering): K500
- Any Single Room with Breakfast Provided for one person: K250
- Any Couple we charge K50 for Extra Breakfast.
- Twin Executive (Two Double Beds) with Breakfast provided for 2 people.

B. Restaurant:
- Full English Breakfast: K50
- Plain Chips: K35
- Full Salads With Potatoes: K45
- Plain Potatoes with salads: K40
- Chips with Fish: K90
- Chips with T Bone: K90
- Rice Beef: K90
- Dry Fish: K120
- Beef Shew: K90
- Nshima with Chicken: K90
- Nshima with T Bone: K90
- Nshima with Kapenta: K50
- Nshima with Visashi: K40
- Smashed Potatoes: K45
- Chips with Chicken: K90

C. Gym Service.
D. Swimming Pool:
- we also have a swimming pool with 24Hrs security service.
E. Conference Hall:
- We also have a conference hall for events such as meetings, workshops and presentations.

F. Contact Us:
- Tel: +0213324051
- Cell: 0966603232 or 0977433762
- Email: kmexecutivelodge@gmail.com
- Facebook Page: KM Executive Lodge

G. Location:
- Located: plot number 2898/53, Off Lusaka Road, Highlands area, Livingstone.
- Nearby places: Highlands Market or Zambezi Sports Club

----------------------------------------------------------------------------------------------------

8. name of lodge: Kaazmein Lodge.

 - Kaazmein Lodge is a Lodge. It has a Restaurant that serves food.

About Kaazmein Lodge:
 
- The Kaazmein Lodge & Resort is located in Nottie Brodie \ 
near the Mosque. 

Available services for Kaazmein Lodge:


A. Rooms or accommodaion:

- Our rooms are crisp, bright,  full of class and character most \ 
important of all they are comfortable and spacious.  12 Chalets \ 
overlooking a water feature, 10 Hotel Style Rooms set in a relaxed lawn \  
setting, and 12 self-contained A framed rooms, to cater for privacy \ 
and individuality of guest.

Our Rooms:
- Budgets Chalets: K300
- Standards Chalets: K650
- Executive Chalets: K1200

They have the following:

- En suite facilities
- WiFi Internet
- Laundry available
- Voltage 220v
- Shaver outlet
- Air-conditioning
- Remote control & color screen with DSTV channels
- Tea and coffee making facilities
- Mini fridge
- Amenities like soaps, shampoos, mosquito nets, repellents are inclusive


B. Facilities:

I. Conference Room:

- Our conference rooms both have audio and video equipment. \ 
The conference rooms can comfortably accommodate 80 and 20 delegates \  
respectively. Ideal  venue for holding meetings, conferences and events. \  
The following services are available for your functions:

- markers
- WiFi Internet
- projector
- morning tea-break
- flip chart
- writing pads
- afternoon tea-break
- lunch
- refreshing soft drink
- mineral water

II. Swimming Pool
III. Events Hire
IV. Weddings
V. Outdoor Bar
VI. Restaurant and Lake:

- The Restaurant is vibrant, a combination of friendly, seamless service \  
and adventurously culinary flair, local, western and authentic food. \  
Our main accent being on fresh and   healthy eating, offering many \  
options for all tastes.

C. Activities:
 
Livingstone Is Full Of Activities Below Is A List Of Activities \  
That We Will Facilitate For You Our Esteemed Clients:

- Victoria Falls Tour
- Mukuni Village Tours
- Gorge Swing
- Lion Walk
- Zambezi Canoeing
- White Water Rafting
- Banjee Jump
- Microlight Flights
- Boat Cruise
- Bridge Tours


D. Contact Us:

- For bookings and reservations or any other inquiries please be free to contact us:
- Email: info@kaazmeinlodge.com
 
- Land Phone: +260 213 32 22 44
 
- Cell Phone: +260 95 5 32 22 44 or +260 97 7 32 22 44

E. Location:
- Postal Address: Kaazmein Lodge, PO Box 60791, Livingstone Zambia
 
- Located: 2764 Maina soko Road, Nottie Broadie area, Livingstone Zambia.

- Nearby: Chandamali Market or Mosque.

---------------------------------------------------------------------------------------

9. Name of Lodge: Aunt Josephine's Executive Lodge.

About Aunt Josephine's Executive Lodge:

- Aunt Josephine's Executive Lodge is based in the heart of Livingstone. \ 
It is located at Plot NO 2072/178, Maramba, Livingstone. It is near Maramba \ 
market or Messenger area. It offers room or accommodation, a Bar. Please \ 
Note that we do not have a Restaurant. Our contact details are 0770 156 856. \ 
You can also email us on auntjosephineexecutivelodge@gmail.com.

Available Services for Aunt Josephine's Executive Lodge:

A. Rooms or Accommodation prices or charges or rates:

- Double Bed: It is self contained, has no air con, no fridge. It is going at K180.
- Double Bed: It is self contained, has an air con and a fridge. It is going at K250.
- Double Bed: It is self contained, has an air con and a fridge. Glass Showers. It is going at K300.

B. Bar:
- We have a bar that offers various drinks and beers.

Note: We do not have a restaurant or offer any food services.

C. Contacts:
- Call: 0770 156 856.
- Email: auntjosephineexecutivelodge@gmail.com.

D. Location:
- Located: Plot NO 2072/178, Maramba, Livingstone.
- Nearby: Maramba Market or Messenger area.

--------------------------------------------------------------------------------------------


10. Name of Lodge: Pumulani Lodge.

About Pumulani Lodge:

- Pumulani Lodge is based in the heart of Livingstone. \ 
- It is located on the main lusaka road opposite Flavours \ 
Restaurant  and just 2 minutes walk from the centre of Livingstone.
- You can contact us on +260 213 320 981 or +260 978 691 514.
- Email us at pumulanizambia@yahoo.com
- NOTE: Pumulani lodge doesnt offer restaurant services.

Available Services for Pumulani Lodge:

A. Rooms or Accommodation prices or charges or rates:

NOTE: All our rooms are en suite and have air-con, plasma screens, \ 
DSTV, fridges, coffee/tea making facilities, free WiFi internet \ 
and continental breakfast.

- K550 per room per night.
- K600 per room per night.
- K650 per room per night.
- K850 per room per night.

Note: We do not have a restaurant or offer any food services.

B. Photo Gallery for Pumulani lodge:
Below are some photos for Pumulani lodge:
- Pumulani lodge Photo: https://web.facebook.com/photo.php?fbid=681477130658576&set=pb.100063888850293.-2207520000&type=3
- Pumulani lodge Photo: https://web.facebook.com/photo.php?fbid=681477003991922&set=pb.100063888850293.-2207520000&type=3
- Pumulani lodge Photo: https://web.facebook.com/photo.php?fbid=649665143839775&set=pb.100063888850293.-2207520000&type=3

For More photos, Check on our Facebook Page: https://web.facebook.com/pumulanizambia/photos

C. Contacts:
- Call: +260 213 320 981 or +260 978 691 514.
- Email: pumulanizambia@yahoo.com
- Facebook Page: https://web.facebook.com/pumulanizambia

D. Location:
- located: 281 Mosi-O-Tunya Rd, Livingstone, Zambia
- Nearby: Town area or Flavours Pub and Grill Restaurant.
- Google maps link: https://www.google.com/maps/place/Pumulani+Lodge+Livingstone/@-17.8423113,25.8617373,17z/data=!4m21!1m11!3m10!1s0x194ff0a37b428c21:0xb972cebac5bf11e6!2sPumulani+Lodge+Livingstone!5m2!4m1!1i2!8m2!3d-17.8423113!4d25.8617373!10e5!16s%2Fg%2F11ddxyw7qv!3m8!1s0x194ff0a37b428c21:0xb972cebac5bf11e6!5m2!4m1!1i2!8m2!3d-17.8423113!4d25.8617373!16s%2Fg%2F11ddxyw7qv?authuser=0&entry=ttu

-----------------------------------------------------------------------------------------------------------------------

11. Name of Lodge: Asenga Executive Lodge Livingstone

 - Asenga Executive Lodge is a Lodge. It has a Restaurant that serves food.

About Asenga Executive Lodge Livingstone:

- Asenga Executive Lodge is a livingstone based lodge that offers the following \ 
services, Accommodation, Restaurant, Conference Hall Hire and Swimming Pool. \ 
- It is located at Plot # 2898/127 off Lusaka Road, Highlands Livingstone, \ 
near Highlands market. for more info, you can contact us on the following: \ 
 +260 963774237 or Email us on reservations.asengalodge@gmail.com.

Available Services for Asenga Executive Lodge:

A. Accommodation:

- We have two types of Rooms: Executive Rooms as well as Standard Rooms.

1.Executive Rooms:
- Executive Single occupancy: k880
- Executive double occupancy: k930

2.Standard Rooms:
- Standard Single occupancy: k780
- Standard double occupancy is k830

Kindly note that these rates include English Breakfast,free Internet and Swimming Pool.

B. Conference Hall:
- We offer conference hall at k2000 per day.

C.Restaurant:
- Meals are ranging from k85 to k120.

D. Contact Us:

For further clarification,please feel free to contact us:
- call: +260 963774237.
- Email: reservations.asengalodge@gmail.com

G. Photo Gallery:
Below are some photo links to our lodge, rooms and restaurant:
- Asenga Lodge Photo link: https://web.facebook.com/photo/?fbid=1627423537606038&set=br.AboFFOLqttpgmBezIjBx65aqkQZGu1hDafbawLVFAvbhyfLzsfSqvoRWYJ1GdCFQuBzJAxfRHX3sv47Tl5qukReuGFN3bkjvJ_EfOyC6N9OWyen3rPzoLb06L4p-_HJ_UF1yDhWrThXDBhraJuCGqWUO
- Asenga Lodge Photo link: https://web.facebook.com/photo/?fbid=158894020168715&set=br.AboFFOLqttpgmBezIjBx65aqkQZGu1hDafbawLVFAvbhyfLzsfSqvoRWYJ1GdCFQuBzJAxfRHX3sv47Tl5qukReuGFN3bkjvJ_EfOyC6N9OWyen3rPzoLb06L4p-_HJ_UF1yDhWrThXDBhraJuCGqWUO

for more photos on Livingstone Lodge, check out our facebook page: https://web.facebook.com/pages/Asenga%20Executive%20Lodge/422914465206795/photos

E. Location:
- located: Plot # 2898/127 off Lusaka Road, Highlands Livingstone.
- PO Box 60464 Livingstone.
- nearby places: Highlands Market or Zambezi Sports Complex.

-------------------------------------------------------------------------------------------------------------


12. name of restaurant: Sweet & Salty Cafe

About Sweet & Salty Cafe:

- Sweet & Salty Cafe is a cafe located along Mosi-o-tunya Livingstone Way, \ 
T1 (Next to Puma Filling Station), Livingstone, Zambia.
- We are open everyday from 07:30 to 22:00.
- Contact them at 0967983308

Available Services Sweet & Salty Cafe: 

A. Food Menu:
- Below is the food menu for Sweet & Salty Cafe:

I. Breakfast:
- Big Bwana (waffle): K150
- Big Bwana (Magwinya): K150
- Madala (waffle): K130
- Madala (Magwinya): K130
- Ham (waffle): K120
- Ham (Magwinya): K120
- Bacon Brekkie (waffle): K110
- Bacon Brekkie (Magwinya): K110
- Veggie Brekkie (Waffle): K110
- Veggie Brekkie (Magwinya): K110
- French toast (waffle): K110
- French toast (Magwinya): K110

II. Pizza:
- Nyama: K170
- Veggie: K160
- Chicken and Mushroom: K150
- Hawaiian: K150
- Mexicana: K150
- Regina: K130

III. Sweets:
- Lemon Meringue: K105
- Chocolate: K105
- Banoffe: K105
- Peppermint Crisps: K105
- Plain: K90

IV. Ice Creams:
- Sugar cone plain: K25
- Cone plain: K15
- Add Flakes: K10
- Add Syrups: K5

V. Milkshakes:
- Vanilla: K85
- Bubblegum: K85
- Caramel: K85
- Chocolate: K85
- Strawberry: K85
- Peanut Butter: K85

VI. Donuts:
- Vanilla: K50
- Caramel: K50
- Chocolate: K50
- DIY Dounut box: K110

VII. Mains:
- Sweet n Sour Pork/Chicken (waffle): K150
- Sweet n Sour Pork/Chicken (Magwinya): K150
- Fillet Steak & Pepper Sauce (waffle): K150
- Fillet Steak & Pepper Sauce (Magwinya): K150
- Crumbed Chicken (waffle): K150
- Crumbed Chicken (Magwinya): K150
- Mutton Curry (waffle): K150
- Mutton Curry (Magwinya): K150
- Beef Burger (waffle): K130
- Beef Burger (Magwinya): K130
- Beef Stew (waffle): K130
- Beef Stew (Magwinya): K130
- Peri Peri Chicken livers (waffle): K120
- Peri Peri Chicken livers (Magwinya): K120
- Sloppy Joe (waffle): K110
- Sloppy Joe (Magwinya): K110
- Chicken Mayo (waffle): K110
- Chicken Mayo (Magwinya): K110

B. Photo Gallery:
Below are some photos for Sweet & Salty Cafe's food:
- Sweet & Salty Cafe Photo: https://web.facebook.com/photo.php?fbid=814769610653993&set=pb.100063628853340.-2207520000&type=3
- Sweet & Salty Cafe Photo: https://web.facebook.com/photo.php?fbid=809164927881128&set=pb.100063628853340.-2207520000&type=3
- Sweet & Salty Cafe Photo: https://web.facebook.com/photo.php?fbid=802679638529657&set=pb.100063628853340.-2207520000&type=3


For More photos, Check on our Facebook Page: https://web.facebook.com/SweetnSaltyLivingstone/photos

C. Contacts:
- Call: 0967 98 33 08.
- Facebook Page: https://web.facebook.com/SweetnSaltyLivingstone

D. Location:
- located: Mosi-o-tunya Livingstone Way, T1 (Next to Puma Filling Station), Livingstone, Zambia.
- Nearby: Town Area or Next to Puma Filling Station
- Google maps link: https://www.google.com/maps/place/Sweet+%26+Salty+cafe/@-17.852535,25.8522176,17z/data=!4m14!1m7!3m6!1s0x194ff1a514b136d1:0xaa79c95d1c5b321e!2sSweet+%26+Salty+cafe!8m2!3d-17.8525401!4d25.8547925!16s%2Fg%2F11ssd3vbsp!3m5!1s0x194ff1a514b136d1:0xaa79c95d1c5b321e!8m2!3d-17.8525401!4d25.8547925!16s%2Fg%2F11ssd3vbsp?authuser=0&entry=ttu
-------------------------------------------------------------------------------------------------------

step 3: {delimiter}: only mention or reference services in the list of available services, \ 
As these are the only services offered. ANd if a particular service for a lodge or restaurant \ 
is available, always include its contact details for easy reach.

Answer the customer in a calm and friendly tone.

Lets think step by step.

Use the following format:
step 1 {delimiter} < step 1 reasoning >
step 2 {delimiter} < step 2 reasoning >
step 3 {delimiter} < step 3 reasoning >

Respond to user: {delimiter} < response to customer >

Make sure to include {delimiter} to seperate every step.
"""

from PIL import Image

img = Image.open('logo.jpg')

st.set_page_config(page_title="Assistant, Quest2Query", page_icon=img)

hide_menu_style = """
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
</style>
"""
st.markdown(hide_menu_style, unsafe_allow_html=True)

st.sidebar.markdown("<h2 style='text-align: center; color: blue;'>Your Digital Assistant</h2>", unsafe_allow_html=True)
st.sidebar.write("""
- "For All Things Dining and Lodging..."
""")
st.sidebar.write("---")
st.sidebar.write("""
**Embark on Limitless Adventures - Your AI-Powered Travel, Dining, and Stay Companion Awaits!**
""")
st.sidebar.markdown("<h3 style='text-align: center; color: blue;'>Contact</h3>", unsafe_allow_html=True)
st.sidebar.write("""
- +260 976 718 998/0976035766
- locastechnology@gmail.com.
""")
st.sidebar.write("---")
st.sidebar.markdown("<h5 style='text-align: center; color: black;'>Copyrights © Quest2Query 2023</h5>", unsafe_allow_html=True)
st.sidebar.markdown("<h5 style='text-align: center; color: blue;'>Powered By LocasAI</h5>", unsafe_allow_html=True)   

st.markdown("<h2 style='text-align: center; color: gray;'>Quest2Query</h2>", unsafe_allow_html=True)
st.markdown("<h3 style='text-align: center; color: lightgray;'>Some Suggested Questions...</h3>", unsafe_allow_html=True)
st.markdown("<h5 style='text-align: center; color: blue;'>NOTE: Always specify the name of the restaurant or lodge you are asking about.</h5>", unsafe_allow_html=True)

st.write('''
- show me a menu for flavours?
- what Restaurants are there?
- what Lodges are there? 
- i will be travelling to livingstone. recommend for me some cheap accommodation and how much they cost
- do you have any photos for Bravo Cafe?
- I want accommodation for less than [insert your budget]?
- what eating places are there
- make me a budget from bravo cafe within K200 for the following:
4 cold beverages, a large pizza and 2 con ice creams. also compare for kubu cafe and flavours

''')
 

st.write('---') 

if 'generated' not in st.session_state:
    st.session_state['generated'] = []

if 'past' not in st.session_state:
    st.session_state['past'] = []

txt = st.chat_input(placeholder="How may we assist you, our customer?",max_chars=300)

word = len(re.findall(r'\w+', system_message))
# st.write('Number of Words :', word)


if txt:

    loading_message = st.empty()
    loading_message.text("Loading... Please wait!")

    user_message = f"""
     {txt}

    """

    messages = [
    {'role': 'system',
    'content': system_message
    },

    {'role': 'user',
    'content': f"{delimiter}{user_message}{delimiter}"
    }]

    response, token_dict = get_completion_from_messages(messages)
    final_response = response.split(delimiter)[-1].strip()
    res_word = len(re.findall(r'\w+', final_response))
    user_text = st.chat_message("user")
    user_text.write(txt)

    if res_word < 3:
        	    
        message = st.chat_message("assistant")
        error_text = "Sorry! Am having troubles right now, try to rephrase your question to help me have more insight, please!..." 

        message.write("""
        Sorry! Am having troubles right now, try to rephrase your question to help me have more insight, please!...
        Otherwise I really want to assist you.
        """ )

        conn = snowflake.connector.connect(
            user=sf_user,
            password=sf_password,
            account=sf_account,
            database=sf_database,
            schema=sf_schema
            )

        cursor = conn.cursor()
            
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]

        query = f"INSERT INTO {table_name} (PROMPT,RESPONSE,MY_CURRENT_TIME) VALUES (%s,%s,%s)"

        try:
            cursor.execute(query, (txt,error_text,current_time,))
            conn.commit()
        except Exception as e:
            st.error(f"Error sending data to Database: {e}")
        finally:
            cursor.close()
            conn.close()

    else:
        mytxt = st.chat_message("assistant")
        # mytxt.session_state.generated.append(final_response)
        mytxt.write(final_response)
        loading_message.text("")


        conn = snowflake.connector.connect(
            user=sf_user,
            password=sf_password,
            account=sf_account,
            database=sf_database,
            schema=sf_schema
            )

        cursor = conn.cursor()
            
	    
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]

        query = f"INSERT INTO {table_name} (PROMPT,RESPONSE,MY_CURRENT_TIME) VALUES (%s,%s,%s)"

        try:
            cursor.execute(query, (txt,final_response,current_time,))
            conn.commit()
        except Exception as e:
            st.error(f"Error sending data to Database: {e}")
        finally:
            cursor.close()
            conn.close()



    # res_word = len(re.findall(r'\w+', final_response))
    # st.write('Number of Words :', res_word)
    # st.write("Number of Tokens in System Message", token_dict['prompt_tokens'])


# st.write("### Comment")
# st.write("How would you like us improve our platform? Leave a comment below")

# user_name = st.text_input("Your Name", placeholder="Write your name")
# user_comment = st.text_area("Your Comment")

# if st.button("Send"):
#     if user_name and user_comment:

#         # 3. Create the Streamlit app
#         conn = snowflake.connector.connect(
#             user=sf_user,
#             password=sf_password,
#             account=sf_account,
#             database=sf_database,
#             schema=sf_schema
#         )

#         cursor = conn.cursor()
        
#         # Assuming your Snowflake table has a single column called 'data_column'
#         # You can adjust the query below based on your table structure.
#         query = f"INSERT INTO {feedback_name} (USER_NAME,USER_COMMENT) VALUES (%s,%s)"

#         try:
#             cursor.execute(query, (user_name,user_comment,))
#             conn.commit()
#             st.success("""
#             Comment Sent Successfully!
#             Thank You!
#             """)
#         except Exception as e:
#             st.error(f"Error sending data to Snowflake: {e}")
#         finally:
#             cursor.close()
#             conn.close()

#     else:

#         st.write("Enter Your Name and Comment...")

# com.html("")
