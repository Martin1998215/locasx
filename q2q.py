
import os
import re
import openai
import streamlit as st 
import pandas as pd
import snowflake.connector
import streamlit.components.v1 as com
from datetime import datetime
# from api_key import apikey

from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate, PromptTemplate
from langchain.chains import ConversationChain, LLMChain
from langchain.schema import BaseOutputParser
from langchain.memory import ConversationBufferMemory

os.environ["OPENAI_API_KEY"] = st.secrets["api1"]

# openai.api_key = 

# model = "gpt-3.5-turbo"
model = "gpt-3.5-turbo-16k"


delimiter = "####"

# full info for available lodges and Restaurants


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

1. Name of Cafe: Bravo Restaurant and Cafe.

-  Bravo Restaurant and Cafe is a Restaurant, It is not a lodge.

About Bravo Restaurant and Cafe:
- Bravo Restaurant and Cafe is a Restaurant located in the city of Livingstone, \ 
Along Mosi O Tunya road, Town Area in livingstone, Zambia.
- We serve the Best food ever, at affordable prices.
- We also make the quickiest deliveries anywhere around Livingstone.
- we are open 24hrs from sunday to monday.

Available Services for Bravo Restaurant and Cafe: 

A. Bravo Restaurant and Cafe Menu:
- We serve the best food with the best ingredients at affordable prices.
- check out our food prices or charges below:

I. Cafe Menu for Bravo Restaurant and Cafe:
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

II. Drinks for Bravo Restaurant and Cafe:
- Fruticana (500mls): K13
- Fanta (500mls): K16
- Sprite (500mls): K16
- Coke (500mls): K16
- Fruitree: K25
- Embe: K17
- Mineral Water (500mls): K5
- Mineral Water (750mls): K7
- Mineral water (1L): K10

III. Pizza for Bravo Restaurant and Cafe:
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

IV. Ice Cream for Bravo Restaurant and Cafe:
- Ice Cream Cone: K12
- Ice cream Cup (large): K25
- Ice Cream Cup (small): K18

V. Burgers for Bravo Restaurant and Cafe:
- Beef Burger: K39
- Chicken Burger: K50

VI. Grills for Bravo Restaurant and Cafe:
- T Bone + chips: K95
- Grilled Piece Chicken: K25
- Grilled Piece + chips: K45
- Sharwama special: K39.99
- Sausage and chips: K60

VII. Breakfast for Bravo Restaurant and Cafe:
- English Breakfast: K50
VIII. Cakes for Bravo Cafe:
- Cake Slice: K37
- Birthday cake (large): K350
- Choco Cake (large): K350
- Vanilla Cake Slice: K37

VIX. Platters for Bravo Restaurant and Cafe:
- Beef Platter: K175
- Bravo Platter: K152
- Universal Bravo Platter: 322
- Bravo 4 Grilled wings & Chips: 123

B. Promotions at Bravo Restaurant and Cafe:
* Bravo Restaurant and Cafe offers pizza promotions on Monday, Wednesday and Friday for the following:
- Tikka/ regular chicken: K80
* Bravo cafe the double trouble promotion on Tuesday and Thursday for the following:
- milkshakes (mango, strawberry, chocolate,caramel): K54
- Ice cream cones (chocolate, vanilla, strawberry): K20
- 2 ouarter chicken (with chips and Greek salad): K130

C. Our Deliveries:
- We offer the best and quickest kind of deliveries using our delivery vans \ 
around livingstone.
- Make An order by calling us on 0771 023 899.

D. Photo Gallery for Bravo Restaurant and Cafe:
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

E. Contact for Bravo Restaurant and Cafe:
- Cell: 0978 833 685.
- Email: bravorestaurant@gmail.com.
- Facebook Page: https://web.facebook.com/BRAVOLSTONE

F. Location for Bravo Restaurant and Cafe:
- Located: Along Mosi O Tunya Road, In Town, livingstone, Zambia.
- Nearby places: Absa Bank, Stanbic Bank, Bata shop.

----------------------------------------------------------------------------------------------------------------------

2. Name of the lodge: Livingstone lodge

- Livingstone Lodge is a Lodge. It has a Restaurant that serves food.

About Livingstone Lodge:

- Livingstone Lodge is of the Lodge with a total of 11 Self contained rooms, \ 
a VIP deluxe suite and conferencing facility accommodating about 80 people. \ 
- Livingstone Lodge is a Lodge. It has a Restaurant that serves food.

Available services for Livingstone Lodge:

A. Rooms or Accommodation:
All our rooms are self contained with Dstv, free Wi Fi and \ 
a continental breakfast. it has a total of 11 Self contained rooms. \ 

- Executive Double: K400
- Executive Twin: K450
- Standard Twin: K430
- Deluxe Suite: K1,000

B. Conference Room:

- Conferences and meetings:  
- Conferencing, meetings and seminars for up to 80 participants. \ 
We cater for conferences, seminars and workshops for up to 80 \ 
people  with a large conference halls and meeting rooms. \ 
- Note: our conference facilities have WIFI included.
- Below are the prices or charges of our conference room:
i. Full conference package per person (with stationary) per person: K390
ii. Full conference package per person (without stationary): K340
iii. Half day conference package: K750
iv. Conference venue only (50 pax max): K2500
v. Outside Venue: K2000
vi. Venue for worshops: K1500

C. Restaurant:
we have food and beverages. below is a list of our menu:
- Tea and snack person: K80
- Lunch or Dinner (Buffet) with choice of starter or desert: K150
- Lunch or Dinner (Buffet) Complete: K200
- Cocktail snacks: K100
- Full English Breakfast: K80
- Soft Drinks (300mls): K10
- Mineral water (500mls): K10

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
- Game Drive + Rhino walk
- Bungee Jumping
- Boat Cruise
- Tour to Livingstone Musuem
- While water Rafting
- Helicopter flight
- Gorge Siving


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

----------------------------------------------------------------------------------------------------------

3. Name of Lodge: Chappa Classic Lodge

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

----------------------------------------------------------------------------------------------------------



4. name of lodge: Kaazmein Lodge.

 - Kaazmein Lodge is a Lodge. It has a Restaurant that serves food.

About Kaazmein Lodge:
 
- The Kaazmein Lodge & Resort has 12 standard double twin chalets, \ 
these units of which overlook a mini lake. There are also 10 Hotel \  
rooms and a Family Hotel Chalet Room. The family units contain a \ 
double room ideally for parents and the next inter-leading room \ 
has two twin beds, both rooms are self contained.

Available services for Kaazmein Lodge:


A. Rooms or accommodaion:
- Budgets Chalets: K300
- Standards Chalets: K650
- Executive Chalets: K1200


B. Facilities:

I. Conference Room:

- Our conference rooms both have audio and video equipment. \ 
The conference rooms can comfortably accommodate 80 and 20 delegates \  
respectively. Ideal  venue for holding meetings, conferences and events. \  

II. Swimming Pool
III. Events Hire
IV. Weddings
V. Outdoor Bar
VI. Restaurant 

C. Contact Us:

- For bookings and reservations or any other inquiries please be free to contact us:
- Email: info@kaazmeinlodge.com
- Land Phone: +260 213 32 22 44
- Cell Phone: +260 95 5 32 22 44 or +260 97 7 32 22 44

E. Location:
- Postal Address: Kaazmein Lodge, PO Box 60791, Livingstone Zambia
- Located: 2764 Maina soko Road, Nottie Broadie area, Livingstone Zambia.
- Nearby: Chandamali Market or Mosque.

---------------------------------------------------------------------------------------------------------

5. Name of Restaurant: Flavours Pubs and Grill Restaurant.

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
- Village Chicken stew: K125
-Charcoal Grill Fish: K115
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
- Dreamlight T-Bone steak 350g: K140
- Beef Fillet steak 350g: K135
- Rump steak 350g: K130
- Lamb chops 3PCs: K145
- Carribean Pork chops: K135
- Buffalo wings: K105

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
- Mini Pizza (all flavour): K90
- Meat Feast: K130
- Mexican Pizza: K150
- Chicken Tikka: K150
- Chicken Mushroom: K125
- Vegetable Pizza: K115
- Hawaiian Chicken Pizza: K115

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
XXI. Wraps menu for Flavours Pub and Grill Restaurant:
- chicken wrap: K90
- Beef wrap: K95

XXII. Bar Menu for Flavours Pubs and Grill Restaurant:
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


6. Name of Lodge: KM Executive Lodge

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

7. Name of Lodge: Aunt Josephine's Executive Lodge.

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


8. Name of Lodge: Pumulani Lodge.

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


9. Name of Lodge: Asenga Executive Lodge Livingstone

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

E. Location:
- located: Plot # 2898/127 off Lusaka Road, Highlands Livingstone.
- PO Box 60464 Livingstone.
- nearby places: Highlands Market or Zambezi Sports Complex.

------------------------------------------------------------------------------------------------------------


10. Name of Lodge: White Rose Lodge.

 - White Rose Lodge is a Lodge. It has a Restaurant that serves food.

About White Rose Lodge:

- White Rose Lodge is situated in Highlands, Livingstone at Plot No. 4424/17.
- It has 12 Self contained rooms with DSTV and WI FI.
- It also has a Restaurant which opens from 07 to 22 hrs.

Available Services for White Rose Lodge:
A. Rooms or Accommodation:

All our rooms have DSTV and free WI FI.

- Double Bed Rooms: K260. these are not self contained.
- Double Bed Rooms: K350 and K360. These are self contained.
- Queen Standard Rooms: K430. They are self contained.
- Apartment: K1200. It has 2 bedrooms, a Kitchen, living room, self catering.

B. Activities:
- Restaurant: we have a restaurant that opens at 07:00 to 22:00.
- Breakfast: between 07:00 to 09:00.
- Lunch: between 12:30 to 15:30.
- Dinner: between 18:30 to 22:00.
- Room Service: K10.
- Laundry: opens from 06:30 to 21:00.
- Mini Bar: We have a mini bar that closes at 22:00. 
- we do not offer swimming pool services.

C. Contact Us:

- call us on 0977 84 96 90.
- Email us at whiteroselodge@yahoo.com


D. Location:
- Located: at Plot No. 4424/17, Highlands, Livingstone. PO Box 61062.
- Nearby: Chimulute Private School or Uno Filling Station or The Weigh Bridge . 

---------------------------------------------------------------------------------------------------------



11. Name of Hotel: Radisson Blu Mosi-Oa-Tunya Livingstone Resort

About Radisson Blu Mosi-Oa-Tunya Livingstone Resort:

- Experience one of the Seven Natural Wonders of the World from our new Radisson Blu hotel in Zambia:
Tune out from the rest of the world and connect to the natural beauty of Mosi-Oa-Tunya National Park. \ 
This exceptional UNESCO site is home to one of the largest waterfalls in the world and a wildlife park. \ 
Relax in this magical setting or find an adventure – in addition to 200 rooms and suites, our hotel offers \ 
locally-inspired restaurants, a spa and fitness center, a river cruiser, and a sports pavilion. We also offer \ 
a conference center with five rooms. Host a unique event for up to 250 people with the spectacular \ 
Victoria Falls nearby.
- Feed your soul with comfortable rooms, suites, and villas by the Zambezi River:
An idyllic stay is waiting at Radisson Blu Mosi-Oa-Tunya, Livingstone Resort. Find your \ 
perfect accommodation among the 200 rooms, including suites and villas. Gaze at the Zambezi \ 
River as you enjoy your first cup of coffee with the room's facilities and plan each day in \ 
this unique location.
- How to arrive to Radisson Blu Mosi-Oa-Tunya, Livingstone Resort:
(i) Confluence of the Maramba River and Mosi-Oa-Tunya Road, Livingstone 10101, Zambia:
While off the beaten path within this superb natural ecosystem, the Radisson Blu Mosi-Oa-Tunya, \ 
 Livingstone Resort, is still easy to reach. Fly into Harry Mwanga Nkumbula International Airport, \ 
just 10 kilometers away, and drive or take a taxi the rest of the way. We are also just 8 \ 
kilometers from downtown Livingstone. Parking is available on site for guests who plan on driving.
- Nearby Attractions
Discover one of the world's most magnificent landmarks. Our Radisson Blu hotel sits by the \ 
Zambezi River and is near Victoria Falls. Explore the fauna and flora in the Mosi-Oa-Tunya \ 
National Park, a UNESCO World Heritage Site, in addition to the spectacular cascades, or head \  
into Livingstone and visit a museum. Read on for more suggestions of things to see and do.

Available Services at Radisson Blu Mosi-Oa-Tunya Livingstone Resort:

A. Rooms or Accommodation prices or charges or rates:
- Superior room with bush view at @ ZMW3,999.00 Single occupancy per night inclusive breakfast
- Superior room with bush view at @ ZMW4,499.00 Double occupancy per night inclusive breakfast
- Premium room with River view at @ ZMW4,299.00 Single occupancy per night inclusive breakfast
- Premium room with River view at @ ZMW4,699.00 Double occupancy per night inclusive breakfast 

B. Restaurant And Bar For Radisson Blu Mosi-Oa-Tunya Livingstone Resort:
I. Kuomboka restaurant:
- Signature cuisine featuring local and international dishes, \ 
plus an open show kitchen, make Kuomboka a treat for the entire family. \ 
Choose between indoor or outdoor seating and enjoy our contemporary \  
African grill. A children's menu is also available for the little ones.

- Opening hours: Daily 6:30 am - 10:00 pm

II. Shungu Bar:
- Sophisticated and social, our bar and lounge offer an excellent spot \ 
for a light meal or drink. Select a wine or cocktail from our full bar \  
and pair it with a tapa from our menu. There is also a separate coffee \ 
lounge where you can indulge your sweet tooth in aromatic coffee and \ 
sweet treats.
- Opening hours: Daily 6:30 am - 10:00 pm

III. Viewing Deck:
- Gaze out at the Zambezi River from the Viewing Deck. The spectacular Victoria \ 
Falls can also be seen in the distance. This is a romantic spot for a drink and \ 
a light meal while the sun sets.

- Opening hours: Daily 9:00 am - 9:00 pm

IV. Boma restaurant:
- Experience traditional African cuisine in Mosi-Oa-Tunya while sitting around a \ 
fire pit. Boma dining invites guests to sit al fresco at dinner. Visit with friends \ 
or make new friends in this unique setting.

- Opening hours: 6:00 pm - 9:00 pm

V. Adventure of Mosi-Oa-Tunya River Cruiser:
- Explore the Zambezi River on our River Cruiser boat. The Adventure of Mosi-Oa-Tunya River \  
Cruiser has a lounge on the first deck and a full bar and lounge on the second deck, \  
both letting you enjoy snacks and drinks on the water. Sail out in the afternoon and enjoy \ 
a unique sunset - the boat docks after the sun sets. There is also a third deck with a viewing platform.

- Opening hours: 4:00 pm - 9:00 pm

VI. Pool Bar & Creamery Cart:
- Order snacks, drinks, and ice cream while cooling off by the outdoor pool. The pool bar and decks \  
include international dishes and a separate kid's menu.

- Opening hours: Daily 9:00 am - 9:00 pm

C. Services at Radisson Blu Mosi-Oa-Tunya Livingstone Resort:
- Below is the website link to the services: 
- https://www.radissonhotels.com/en-us/hotels/radisson-blu-resort-mosi-oa-tunya/services?fbclid=IwAR3MhYemXZgBKpG6IWEara2g57hgkpTOg2uqO1oR8rhlh3VkQrfT_5fQEFQ

D. Activities at Radisson Blu Mosi-Oa-Tunya Livingstone Resort:
- Below is the website link to the activities:
- https://www.radissonhotels.com/en-us/hotels/radisson-blu-resort-mosi-oa-tunya/activities?fbclid=IwAR3MhYemXZgBKpG6IWEara2g57hgkpTOg2uqO1oR8rhlh3VkQrfT_5fQEFQ

E. Photo Gallery for Radisson Blu Mosi-Oa-Tunya Livingstone Resort:
- Photos: https://web.facebook.com/Radissonblulivingstone/photos_by

F. Contacts for Radisson Blu Mosi-Oa-Tunya Livingstone Resort:
- Tel: +260 630 373 250  
- Mobile: +260 962 409 696
- Email: henry.chandalala@radissonblu.com
- website: https://www.radissonhotels.com/en-us/hotels/radisson-blu-resort-mosi-oa-tunya?fbclid=IwAR3MhYemXZgBKpG6IWEara2g57hgkpTOg2uqO1oR8rhlh3VkQrfT_5fQEFQ
- Facebook Page: https://web.facebook.com/Radissonblulivingstone

-------------------------------------------------------------------------------------------------------------------------

12. Name: Sweet & Salty Cafe.

 - About Sweet & Salty Cafe:

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


------------------------------------------------------------------------------------------------------------------------------------

step 3: {delimiter}: only mention or reference services in the list of available services, \ 
As these are the only services offered. ANd if a particular service for a lodge or restaurant \ 
is available, always include its contact details for easy reach.
Please note: each service is seperated by dashed lines. 

Answer the customer in a calm and friendly tone.

Lets think step by step.

Use the following format:
step 1 {delimiter} < step 1 reasoning >
step 2 {delimiter} < step 2 reasoning >
step 3 {delimiter} < step 3 reasoning >

Respond to user: {delimiter} < response to customer >

Make sure to include {delimiter} to seperate every step.

"""

# for individual sevices:

# about bravo cafe info
def bravo_cafe():


        
    items = f"""
    -  Bravo Restaurant and Cafe is a Restaurant, It is not a lodge.

    About Bravo Restaurant and Cafe:
    - Bravo Restaurant and Cafe is a Restaurant located in the city of Livingstone, \ 
    Along Mosi O Tunya road, Town Area in livingstone, Zambia.
    - We serve the Best food ever, at affordable prices.
    - We also make the quickiest deliveries anywhere around Livingstone.
    - we are open 24hrs from sunday to monday.

    Available Services for Bravo Restaurant and Cafe: 

    A. Bravo Restaurant and Cafe Menu:
    - We serve the best food with the best ingredients at affordable prices.
    - check out our food prices or charges below:

    I. Main Course for Bravo Restaurant and Cafe:
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

    II. Drinks for Bravo Restaurant and Cafe:
    - Fruticana (500mls): K13
    - Fanta (500mls): K16
    - Sprite (500mls): K16
    - Coke (500mls): K16
    - Fruitree: K25
    - Embe: K17
    - Mineral Water (500mls): K5
    - Mineral Water (750mls): K7
    - Mineral water (1L): K10

    III. Pizza for Bravo Restaurant and Cafe:
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

    IV. Ice Cream for Bravo Restaurant and Cafe:
    - Ice Cream Cone: K12
    - Ice cream Cup (large): K25
    - Ice Cream Cup (small): K18

    V. Burgers for Bravo Restaurant and Cafe:
    - Beef Burger: K39
    - Chicken Burger: K50

    VI. Grills for Bravo Restaurant and Cafe:
    - T Bone + chips: K95
    - Grilled Piece Chicken: K25
    - Grilled Piece + chips: K45
    - Sharwama special: K39.99
    - Sausage and chips: K60

    VII. Breakfast for Bravo Restaurant and Cafe:
    - English Breakfast: K50

    VIII. Cakes for Bravo Restaurant and Cafe:
    - Cake Slice: K37
    - Birthday cake (large): K350
    - Choco Cake (large): K350
    - Vanilla Cake Slice: K37

    VIX. Platters for Bravo Restaurant and Cafe:
    - Beef Platter: K175
    - Bravo Platter: K152
    - Universal Bravo Platter: 322
    - Bravo 4 Grilled wings & Chips: 123

    B. Promotions at Bravo Restaurant and Cafe:
    * Bravo Restaurant and Cafe offers pizza promotions on Monday, Wednesday and Friday for the following:
    - Tikka/ regular chicken: K80
    * Bravo cafe the double trouble promotion on Tuesday and Thursday for the following:
    - milkshakes (mango, strawberry, chocolate,caramel): K54
    - Ice cream cones (chocolate, vanilla, strawberry): K20
    - 2 ouarter chicken (with chips and Greek salad): K130

    C. Our Deliveries:
    - We offer the best and quickest kind of deliveries using our delivery vans \ 
    around livingstone.
    - Make An order by calling us on 0771 023 899.

    D. Photo Gallery for Bravo Restaurant and Cafe:
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

    E. Contact for Bravo Restaurant and Cafe:
    - Cell: 0978 833 685.
    - Email: bravorestaurant@gmail.com.
    - Facebook Page: https://web.facebook.com/BRAVOLSTONE

    F. Location for Bravo Restaurant and Cafe:
    - Located: Along Mosi O Tunya Road, In Town, livingstone, Zambia.
    - Nearby places: Absa Bank, Stanbic Bank, Bata shop. """

    return items


# Livingstone Lodge info
def livingstone_lodge():

    items = f"""
        
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

    """

    return items



# Radisson Blu info
def radisson_hotel():

    items = f"""
        
    About Radisson Blu Mosi-Oa-Tunya Livingstone Resort:

    - Experience one of the Seven Natural Wonders of the World from our new Radisson Blu hotel in Zambia:
    Tune out from the rest of the world and connect to the natural beauty of Mosi-Oa-Tunya National Park. \ 
    This exceptional UNESCO site is home to one of the largest waterfalls in the world and a wildlife park. \ 
    Relax in this magical setting or find an adventure – in addition to 200 rooms and suites, our hotel offers \ 
    locally-inspired restaurants, a spa and fitness center, a river cruiser, and a sports pavilion. We also offer \ 
    a conference center with five rooms. Host a unique event for up to 250 people with the spectacular \ 
    Victoria Falls nearby.
    - Feed your soul with comfortable rooms, suites, and villas by the Zambezi River:
    An idyllic stay is waiting at Radisson Blu Mosi-Oa-Tunya, Livingstone Resort. Find your \ 
    perfect accommodation among the 200 rooms, including suites and villas. Gaze at the Zambezi \ 
    River as you enjoy your first cup of coffee with the room's facilities and plan each day in \ 
    this unique location.
    - How to arrive to Radisson Blu Mosi-Oa-Tunya, Livingstone Resort:
    (i) Confluence of the Maramba River and Mosi-Oa-Tunya Road, Livingstone 10101, Zambia:
    While off the beaten path within this superb natural ecosystem, the Radisson Blu Mosi-Oa-Tunya, \ 
    Livingstone Resort, is still easy to reach. Fly into Harry Mwanga Nkumbula International Airport, \ 
    just 10 kilometers away, and drive or take a taxi the rest of the way. We are also just 8 \ 
    kilometers from downtown Livingstone. Parking is available on site for guests who plan on driving.
    - Nearby Attractions
    Discover one of the world's most magnificent landmarks. Our Radisson Blu hotel sits by the \ 
    Zambezi River and is near Victoria Falls. Explore the fauna and flora in the Mosi-Oa-Tunya \ 
    National Park, a UNESCO World Heritage Site, in addition to the spectacular cascades, or head \  
    into Livingstone and visit a museum. Read on for more suggestions of things to see and do.

    Available Services at Radisson Blu Mosi-Oa-Tunya Livingstone Resort:

    A. Rooms or Accommodation prices or charges or rates:
    - Superior room with bush view at @ ZMW3,999.00 Single occupancy per night inclusive breakfast
    - Superior room with bush view at @ ZMW4,499.00 Double occupancy per night inclusive breakfast
    - Premium room with River view at @ ZMW4,299.00 Single occupancy per night inclusive breakfast
    - Premium room with River view at @ ZMW4,699.00 Double occupancy per night inclusive breakfast 

    B. Restaurant And Bar For Radisson Blu Mosi-Oa-Tunya Livingstone Resort:
    I. Kuomboka restaurant:
    - Signature cuisine featuring local and international dishes, \ 
    plus an open show kitchen, make Kuomboka a treat for the entire family. \ 
    Choose between indoor or outdoor seating and enjoy our contemporary \  
    African grill. A children's menu is also available for the little ones.

    - Opening hours: Daily 6:30 am - 10:00 pm

    II. Shungu Bar:
    - Sophisticated and social, our bar and lounge offer an excellent spot \ 
    for a light meal or drink. Select a wine or cocktail from our full bar \  
    and pair it with a tapa from our menu. There is also a separate coffee \ 
    lounge where you can indulge your sweet tooth in aromatic coffee and \ 
    sweet treats.
    - Opening hours: Daily 6:30 am - 10:00 pm

    III. Viewing Deck:
    - Gaze out at the Zambezi River from the Viewing Deck. The spectacular Victoria \ 
    Falls can also be seen in the distance. This is a romantic spot for a drink and \ 
    a light meal while the sun sets.

    - Opening hours: Daily 9:00 am - 9:00 pm

    IV. Boma restaurant:
    - Experience traditional African cuisine in Mosi-Oa-Tunya while sitting around a \ 
    fire pit. Boma dining invites guests to sit al fresco at dinner. Visit with friends \ 
    or make new friends in this unique setting.

    - Opening hours: 6:00 pm - 9:00 pm

    V. Adventure of Mosi-Oa-Tunya River Cruiser:
    - Explore the Zambezi River on our River Cruiser boat. The Adventure of Mosi-Oa-Tunya River \  
    Cruiser has a lounge on the first deck and a full bar and lounge on the second deck, \  
    both letting you enjoy snacks and drinks on the water. Sail out in the afternoon and enjoy \ 
    a unique sunset - the boat docks after the sun sets. There is also a third deck with a viewing platform.

    - Opening hours: 4:00 pm - 9:00 pm

    VI. Pool Bar & Creamery Cart:
    - Order snacks, drinks, and ice cream while cooling off by the outdoor pool. The pool bar and decks \  
    include international dishes and a separate kid's menu.

    - Opening hours: Daily 9:00 am - 9:00 pm

    C. Services at Radisson Blu Mosi-Oa-Tunya Livingstone Resort:
    - Below is the website link to the services: 
    - https://www.radissonhotels.com/en-us/hotels/radisson-blu-resort-mosi-oa-tunya/services?fbclid=IwAR3MhYemXZgBKpG6IWEara2g57hgkpTOg2uqO1oR8rhlh3VkQrfT_5fQEFQ

    D. Activities at Radisson Blu Mosi-Oa-Tunya Livingstone Resort:
    - Below is the website link to the activities:
    - https://www.radissonhotels.com/en-us/hotels/radisson-blu-resort-mosi-oa-tunya/activities?fbclid=IwAR3MhYemXZgBKpG6IWEara2g57hgkpTOg2uqO1oR8rhlh3VkQrfT_5fQEFQ

    E. Photo Gallery for Radisson Blu Mosi-Oa-Tunya Livingstone Resort:
    - Photos: https://web.facebook.com/Radissonblulivingstone/photos_by

    F. Contacts for Radisson Blu Mosi-Oa-Tunya Livingstone Resort:
    - Tel: +260 630 373 250  
    - Mobile: +260 962 409 696
    - Email: henry.chandalala@radissonblu.com
    - website: https://www.radissonhotels.com/en-us/hotels/radisson-blu-resort-mosi-oa-tunya?fbclid=IwAR3MhYemXZgBKpG6IWEara2g57hgkpTOg2uqO1oR8rhlh3VkQrfT_5fQEFQ
    - Facebook Page: https://web.facebook.com/Radissonblulivingstone
    """

    return items


# chapa classic lodge info
def chapa_lodge():

   
    items = f"""

        
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
    """

    return items


def sweet_salt_cafe():

    items = f"""

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

    """

    return items


# flavours info
def flavours_pub():

    items = f"""

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
    - Village Chicken stew: K125
    -Charcoal Grill Fish: K115
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
    - Dreamlight T-Bone steak 350g: K140
    - Beef Fillet steak 350g: K135
    - Rump steak 350g: K130
    - Lamb chops 3PCs: K145
    - Carribean Pork chops: K135
    - Buffalo wings: K105

    X. Sausage for Flavours Pubs and Grill Restaurant:
    - Boerewars sausage and chips: K85
    - Hungarian sausage and chips: K70

    XI. Platter for Flavours Pubs and Grill Restaurant:
    - platter for 2: K270
    - Platter for 3: K320
    - Platter for 4: K400
    - Platter for 6: K600
    - Family Platter: K900

    XII. Pasta/Noodles for Flavours Pubs and Grill Restaurant:
    - Chicken Fried Noodles: K80
    - Beef Fried Noodles: K85

    XIII. Special Pizza for Flavours Pubs and Grill Restaurant:
    - Mini Pizza (all flavour): K90
    - Meat Feast: K130
    - Mexican Pizza: K150
    - Chicken Tikka: K150
    - Chicken Mushroom: K125
    - Vegetable Pizza: K115
    - Hawaiian Chicken Pizza: K115

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
    XXI. Wraps menu for Flavours Pub and Grill Restaurant:
    - chicken wrap: K90
    - Beef wrap: K95

    XXII. Bar Menu for Flavours Pubs and Grill Restaurant:
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

    """

    return items


def pumulani_lodge():

    items = f"""
    
    About Pumulani Lodge:

    - Pumulani Lodge is based in the heart of Livingstone. \ 
    - It is located on the main lusaka road opposite Flavours \ 
    Restaurant  and just 2 minutes walk from the centre of Livingstone.
    - You can contact us on +260 213 320 981 or +260 978 691 514.
    - Email us at pumulanizambia@yahoo.com
    - NOTE: Pumulani lodge doesnt offer restaurant services.

    Available Services for Aunt Josephine's Executive Lodge:

    A. Rooms or Accommodation prices or charges or rates:

    All our rooms are en suite and have air-con, plasma screens, \ 
    DSTV, fridges, coffee/tea making facilities, free WiFi internet \ 
    and continental breakfast.

    - K550 per room per night.
    - K600 per room per night.
    - K650 per room per night.
    - K850 per room per night.

    Note: We do not have a restaurant or offer any food services.

    B. Photo Gallery:
    Below are some photos for Kubu Cafe's food:
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
    - Google maps location: https://www.google.com/maps/place/Pumulani+Lodge+Livingstone/@-17.8423113,25.8617373,17z/data=!4m21!1m11!3m10!1s0x194ff0a37b428c21:0xb972cebac5bf11e6!2sPumulani+Lodge+Livingstone!5m2!4m1!1i2!8m2!3d-17.8423113!4d25.8617373!10e5!16s%2Fg%2F11ddxyw7qv!3m8!1s0x194ff0a37b428c21:0xb972cebac5bf11e6!5m2!4m1!1i2!8m2!3d-17.8423113!4d25.8617373!16s%2Fg%2F11ddxyw7qv?authuser=0&entry=ttu

    """

    return items

def auntjose_lodge():

    items = f"""
        
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


    """

    return items


def km_executive_lodge():

    items = f"""
        
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
    - Nearby: Highlands Market or Zambezi Sports Club

    """

    return items



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
- 0976 03 57 66
- locastechnology@gmail.com.
""")
st.sidebar.write("---")
st.sidebar.markdown("<h5 style='text-align: center; color: black;'>Copyrights © Quest2Query 2023</h5>", unsafe_allow_html=True)
st.sidebar.markdown("<h5 style='text-align: center; color: blue;'>Powered By LocasAI</h5>", unsafe_allow_html=True) 

st.markdown("<h2 style='text-align: center; color: gray;'>Quest2Query</h2>", unsafe_allow_html=True)

for_you, my_explore, about_us, feedback = st.tabs(["For You", "Explorer AI","About Us","Feedback"])

with feedback:

    st.markdown("""
    <h3>Feedback</h3>
    <h5>Give us your thoughts on the performance of our AI Assistant, Quest2Query.</h5>
    <h5>Your feedback helps us improve it</h5>
    
    """, unsafe_allow_html=True)

    st.write("---")

    name = st.text_input("Enter Your Name")
    comment = st.text_area("Give your comment...", max_chars=100)

    if st.button("Send Comment"):

        if name and comment:

            st.write("### Comment Has been sent successfully! Thank you.")

        else:

            st.write("### Kindly Input both the name and comment field!!!")

with about_us:

    st.markdown("""
    <h3>About Quest2Query</h3>
    <div style='background-color: #ffffff; box-shadow: 0 2px 6px rgba(0, 0, 0, 0.15); border-radius: 4px; padding: 20px; margin: 20px 0px;'>
    At Quest2Query, we are fueled by a passion for travel, culinary delights,
    and unforgettable experiences. We believe that every journey should be filled 
    with wonder, excitement, and cherished memories. That's why we've created the
    ultimate AI-powered travel assistant that puts the world at your fingertips.
    </div>
    <div style='background-color: #ffffff; box-shadow: 0 2px 6px rgba(0, 0, 0, 0.15); border-radius: 4px; padding: 20px; margin: 20px 0px;'>
    Our team of dedicated experts and technology enthusiasts have worked tirelessly 
    to design an intelligent companion that empowers you to explore the globe with 
    confidence. From helping you find the perfect restaurant for a romantic dinner 
    to suggesting hidden gems and must-visit destinations, our AI Travel Guru is 
    your go-to guide for all things travel-related.
    </div>
    <div style='background-color: #ffffff; box-shadow: 0 2px 6px rgba(0, 0, 0, 0.15); border-radius: 4px; padding: 20px; margin: 20px 0px;'>
    We understand that every traveler is unique, and that's why our AI assistant is 
    tailored to suit your preferences and desires. Whether you're an adventurous 
    explorer seeking thrilling escapades or a foodie on the hunt for mouthwatering 
    cuisines, our smart algorithms curate personalized recommendations that match 
    your taste and style.
    </div>
    <div style='background-color: #ffffff; box-shadow: 0 2px 6px rgba(0, 0, 0, 0.15); border-radius: 4px; padding: 20px; margin: 20px 0px;'>
    With Quest2Query, planning your dream vacation is as effortless as a few taps on 
    your device. Say goodbye to endless hours of research and guesswork, and say hello 
    to seamless travel planning, top-notch restaurant suggestions, and handpicked 
    accommodations that cater to your every need.
    </div>
    <div style='background-color: #ffffff; box-shadow: 0 2px 6px rgba(0, 0, 0, 0.15); border-radius: 4px; padding: 20px; margin: 20px 0px;'>
    Join us on this extraordinary journey as we redefine the way you travel, dine, and stay. 
    Embark on a world of limitless possibilities, where each moment is enriched by our AI 
    assistant's insightful guidance. Let's create lasting memories together and unlock the 
    true essence of exploration.
    </div>
    <div style='background-color: #ffffff; box-shadow: 0 2px 6px rgba(0, 0, 0, 0.15); border-radius: 4px; padding: 20px; margin: 20px 0px;'>
    <h5 style='color: #0056b3;'>Welcome to a new era of travel - where adventure knows no bounds, and unforgettable experiences await you. Welcome to Quest2Query</h5>    
    </div>
    <div style='background-color: #ffffff; box-shadow: 0 2px 6px rgba(0, 0, 0, 0.15); border-radius: 4px; padding: 20px; margin: 20px 0px;'>
        <ul style='padding-top: 20px;'>
            <h4 style='text-align:center;'>Contact Us</h4>
            <li><i class="fa-solid fa-phone", style="padding-right: 10px"></i>0976035766/0976718998</li>
            <li><i class="fa-solid fa-envelope" style="padding-right: 10px"></i>locastechnology@gmail.com.</li>
            <li style='padding-top: 20px;'>Copyrights &copy; Quest2Query 2024</li> 
            <h5 style='color: #0056b3; text-align:center;'>Powered By Locas AI</h5>
            </ul>
    </div>
    
    """, unsafe_allow_html=True)

with for_you:

    
    st.markdown("<h5 style='text-align: center; color: blue;'>Explore the services for a specific Lodge/Restaurant.</h5>", unsafe_allow_html=True)

    menu = st.selectbox("Choose Service", ("Select A Service here",
    "Aunt Josephine Lodge","Bravo Cafe","Chapa Classic Lodge","Flavours Pub & Gill",
    "KM Executive Lodge","Livingstone Lodge","Pumulani Lodge","Radisson Blu Hotel",
    "Sweet & Salty Cafe"))


    text = st.text_input("Ask about the service you have selected...", max_chars=300)

    user_message = f""" {text} """

    chat_model = ChatOpenAI(temperature=0, model="gpt-3.5-turbo")


    # select a service
    if menu == "Select A Service here":

        if st.button("Enter"):

            st.write("### Please! Select A service you want to inquire on in the search bar above...")

    
    # About Chapa Classic Lodge
    chapa_system_message = f"""
    You will be provided with customer service queries. \
    The customer service query will be delimited with \
    {delimiter} characters.

    step 1: {delimiter}: First decide whether a user is asking \ 
    a question about anything related to restaurants or cafes, menus, \ 
    dinners, party planning, travel, restaurant or accommodation suggestions \ 
    recommendations on cafes, eating places, restaurants, travel guide, \ 
    or just any of the above.

    step 2: {delimiter}: If the user is asking a question related to step 1, \ 
    check the services below and answer only based on the available services:


    All available services for {menu} are:
    { chapa_lodge() }


    step 3: {delimiter}: only mention or reference services in the list of all available services in step 2, \ 
    As these are the only services offered. And always include its contact details for easy reach.

    step 4: {delimiter}: If the question is not related to the available services, \ 
    say "Sorry, I can only answer questions about the available services for {menu}." \ 
    If the question is unclear or incomplete, say "Please rephrase or complete your \ 
    question to help me have a clear insight.
    

    Answer the customer in a calm and friendly tone.

    Lets think step by step.

    Use the following format:
    step 1 {delimiter} < step 1 reasoning >
    step 2 {delimiter} < step 2 reasoning >
    step 3 {delimiter} < step 3 reasoning >
    step 4 {delimiter} < step 4 reasoning >


    Respond to user: {delimiter} < response to customer >

    Make sure to include {delimiter} to seperate every step.
    Note: only display the answer. DO NOT SHOW THE STEPS.

    """


    chapa_prompt_template = f"""

        Answer the question based on the contexts below. 

        {delimiter}

        Contexts: {{chapa_system_message}}

        {delimiter}

        Question:{{user_message}}

        Answer:"""    


    chapa_prompt = ChatPromptTemplate.from_template(chapa_prompt_template)


    chapa_customer_messages = chapa_prompt.format_messages(
        chapa_system_message = chapa_system_message,
        user_message= user_message
    )



    if menu == "Chapa Classic Lodge":

        if st.button("Enter"):

            chapa_response = chat_model(chapa_customer_messages)

            st.write(chapa_response.content)

    
    
    # About Chapa Classic Lodge
    km_system_message = f"""
    You will be provided with customer service queries. \
    The customer service query will be delimited with \
    {delimiter} characters.

    step 1: {delimiter}: First decide whether a user is asking \ 
    a question about anything related to restaurants or cafes, menus, \ 
    dinners, party planning, travel, restaurant or accommodation suggestions \ 
    recommendations on cafes, eating places, restaurants, travel guide, \ 
    or just any of the above.

    step 2: {delimiter}: If the user is asking a question related to step 1, \ 
    check the services below and answer only based on the available services:


    All available services for {menu} are:
    { km_executive_lodge() }


    step 3: {delimiter}: only mention or reference services in the list of all available services in step 2, \ 
    As these are the only services offered. And always include its contact details for easy reach.

    step 4: {delimiter}: If the question is not related to the available services, \ 
    say "Sorry, I can only answer questions about the available services for {menu}." \ 
    If the question is unclear or incomplete, say "Please rephrase or complete your \ 
    question to help me have a clear insight.
    

    Answer the customer in a calm and friendly tone.

    Lets think step by step.

    Use the following format:
    step 1 {delimiter} < step 1 reasoning >
    step 2 {delimiter} < step 2 reasoning >
    step 3 {delimiter} < step 3 reasoning >
    step 4 {delimiter} < step 4 reasoning >


    Respond to user: {delimiter} < response to customer >

    Make sure to include {delimiter} to seperate every step.
    Note: only display the answer. DO NOT SHOW THE STEPS.

    """


    km_prompt_template = f"""

        Answer the question based on the contexts below. 

        {delimiter}

        Contexts: {{km_system_message}}

        {delimiter}

        Question:{{user_message}}

        Answer:"""    


    km_prompt = ChatPromptTemplate.from_template(km_prompt_template)


    km_customer_messages = km_prompt.format_messages(
        km_system_message = km_system_message,
        user_message= user_message
    )



    if menu == "KM Executive Lodge":

        if st.button("Enter"):

            km_response = chat_model(km_customer_messages)

            st.write(km_response.content)



    # About Chapa Classic Lodge
    auntjose_system_message = f"""
    You will be provided with customer service queries. \
    The customer service query will be delimited with \
    {delimiter} characters.

    step 1: {delimiter}: First decide whether a user is asking \ 
    a question about anything related to restaurants or cafes, menus, \ 
    dinners, party planning, travel, restaurant or accommodation suggestions \ 
    recommendations on cafes, eating places, restaurants, travel guide, \ 
    or just any of the above.

    step 2: {delimiter}: If the user is asking a question related to step 1, \ 
    check the services below and answer only based on the available services:


    All available services for {menu} are:
    { auntjose_lodge() }


    step 3: {delimiter}: only mention or reference services in the list of all available services in step 2, \ 
    As these are the only services offered. And always include its contact details for easy reach.

    step 4: {delimiter}: If the question is not related to the available services, \ 
    say "Sorry, I can only answer questions about the available services for {menu}." \ 
    If the question is unclear or incomplete, say "Please rephrase or complete your \ 
    question to help me have a clear insight.
    

    Answer the customer in a calm and friendly tone.

    Lets think step by step.

    Use the following format:
    step 1 {delimiter} < step 1 reasoning >
    step 2 {delimiter} < step 2 reasoning >
    step 3 {delimiter} < step 3 reasoning >
    step 4 {delimiter} < step 4 reasoning >

    Respond to user: {delimiter} < response to customer >

    Make sure to include {delimiter} to seperate every step.
    Note: only display the answer. DO NOT SHOW THE STEPS.

    """


    auntjose_prompt_template = f"""

        Answer the question based on the contexts below. 

        {delimiter}

        Contexts: {{auntjose_system_message}}

        {delimiter}

        Question:{{user_message}}

        Answer:"""    


    auntjose_prompt = ChatPromptTemplate.from_template(auntjose_prompt_template)


    auntjose_customer_messages = auntjose_prompt.format_messages(
        auntjose_system_message = auntjose_system_message,
        user_message= user_message
    )



    if menu == "Aunt Josephine Lodge":

        if st.button("Enter"):

            auntjose_response = chat_model(auntjose_customer_messages)

            st.write(auntjose_response.content)


    
    # About Pumulani Lodge
    pumulani_system_message = f"""
    You will be provided with customer service queries. \
    The customer service query will be delimited with \
    {delimiter} characters.

    step 1: {delimiter}: First decide whether a user is asking \ 
    a question about anything related to restaurants or cafes, menus, \ 
    dinners, party planning, travel, restaurant or accommodation suggestions \ 
    recommendations on cafes, eating places, restaurants, travel guide, \ 
    or just any of the above.

    step 2: {delimiter}: If the user is asking a question related to step 1, \ 
    check the services below and answer only based on the available services:


    All available services for {menu} are:
    { pumulani_lodge() }


    step 3: {delimiter}: only mention or reference services in the list of all available services in step 2, \ 
    As these are the only services offered. And always include its contact details for easy reach.

    step 4: {delimiter}: If the question is not related to the available services, \ 
    say "Sorry, I can only answer questions about the available services for {menu}." \ 
    If the question is unclear or incomplete, say "Please rephrase or complete your \ 
    question to help me have a clear insight.
    

    Answer the customer in a calm and friendly tone.

    Lets think step by step.

    Use the following format:
    step 1 {delimiter} < step 1 reasoning >
    step 2 {delimiter} < step 2 reasoning >
    step 3 {delimiter} < step 3 reasoning >
    step 4 {delimiter} < step 4 reasoning >


    Respond to user: {delimiter} < response to customer >

    Make sure to include {delimiter} to seperate every step.
    Note: only display the answer. DO NOT SHOW THE STEPS.

    """


    pumulani_prompt_template = f"""

        Answer the question based on the contexts below. 

        {delimiter}

        Contexts: {{pumulani_system_message}}

        {delimiter}

        Question:{{user_message}}

        Answer:"""    


    pumulani_prompt = ChatPromptTemplate.from_template(pumulani_prompt_template)


    pumulani_customer_messages = pumulani_prompt.format_messages(
        pumulani_system_message = pumulani_system_message,
        user_message= user_message
    )



    if menu == "Pumulani Lodge":

        if st.button("Enter"):

            pumulani_response = chat_model(pumulani_customer_messages)

            st.write(pumulani_response.content)



    # About Sweet & Salty Cafe
    sweet_system_message = f"""
    You will be provided with customer service queries. \
    The customer service query will be delimited with \
    {delimiter} characters.

    step 1: {delimiter}: First decide whether a user is asking \ 
    a question about anything related to restaurants or cafes, menus, \ 
    dinners, party planning, travel, restaurant or accommodation suggestions \ 
    recommendations on cafes, eating places, restaurants, travel guide, \ 
    or just any of the above.

    step 2: {delimiter}: If the user is asking a question related to step 1, \ 
    check the services below and answer only based on the available services:


    All available services for {menu} are:
    { sweet_salt_cafe() }


    step 3: {delimiter}: only mention or reference services in the list of all available services in step 2, \ 
    As these are the only services offered. And always include its contact details for easy reach.

    step 4: {delimiter}: If the question is not related to the available services, \ 
    say "Sorry, I can only answer questions about the available services for {menu}." \ 
    If the question is unclear or incomplete, say "Please rephrase or complete your \ 
    question to help me have a clear insight.
    

    Answer the customer in a calm and friendly tone.

    Lets think step by step.

    Use the following format:
    step 1 {delimiter} < step 1 reasoning >
    step 2 {delimiter} < step 2 reasoning >
    step 3 {delimiter} < step 3 reasoning >
    step 4 {delimiter} < step 4 reasoning >

    Respond to user: {delimiter} < response to customer >

    Make sure to include {delimiter} to seperate every step.
    Note: only display the answer. DO NOT SHOW THE STEPS.

    """


    sweet_prompt_template = f"""

        Answer the question based on the contexts below. 

        {delimiter}

        Contexts: {{sweet_system_message}}

        {delimiter}

        Question:{{user_message}}

        Answer:"""    


    sweet_prompt = ChatPromptTemplate.from_template(sweet_prompt_template)


    sweet_customer_messages = sweet_prompt.format_messages(
        sweet_system_message = sweet_system_message,
        user_message= user_message
    )



    if menu == "Sweet & Salty Cafe":

        if st.button("Enter"):

            sweet_response = chat_model(sweet_customer_messages)

            st.write(sweet_response.content)



    # About Radisson Blu Hotel

    radisson_system_message = f"""
    You will be provided with customer service queries. \
    The customer service query will be delimited with \
    {delimiter} characters.

    step 1: {delimiter}: First decide whether a user is asking \ 
    a question about anything related to restaurants or cafes, menus, \ 
    dinners, party planning, travel, restaurant or accommodation suggestions \ 
    recommendations on cafes, eating places, restaurants, travel guide, \ 
    or just any of the above.

    step 2: {delimiter}: If the user is asking a question related to step 1, \ 
    check the services below and answer only based on the available services:


    All available services for {menu} are:
    { radisson_hotel() }


    step 3: {delimiter}: only mention or reference services in the list of all available services in step 2, \ 
    As these are the only services offered. And always include its contact details for easy reach.

    step 4: {delimiter}: If the question is not related to the available services, \ 
    say "Sorry, I can only answer questions about the available services for {menu}." \ 
    If the question is unclear or incomplete, say "Please rephrase or complete your \ 
    question to help me have a clear insight.
    

    Answer the customer in a calm and friendly tone.

    Lets think step by step.

    Use the following format:
    step 1 {delimiter} < step 1 reasoning >
    step 2 {delimiter} < step 2 reasoning >
    step 3 {delimiter} < step 3 reasoning >
    step 4 {delimiter} < step 4 reasoning >


    Respond to user: {delimiter} < response to customer >

    Make sure to include {delimiter} to seperate every step.
    Note: only display the answer. DO NOT SHOW THE STEPS.

    """


    radisson_prompt_template = f"""

        Answer the question based on the contexts below. 

        {delimiter}

        Contexts: {{radisson_system_message}}

        {delimiter}

        Question:{{user_message}}

        Answer:"""    


    radisson_prompt = ChatPromptTemplate.from_template(radisson_prompt_template)


    radisson_customer_messages = radisson_prompt.format_messages(
        radisson_system_message = radisson_system_message,
        user_message= user_message
    )



    if menu == "Radisson Blu Hotel":

        if st.button("Enter"):

            radisson_response = chat_model(radisson_customer_messages)

            st.write(radisson_response.content)


    # about bravo cafe
    bravo_system_message = f"""
    You will be provided with customer service queries. \
    The customer service query will be delimited with \
    {delimiter} characters.

    step 1: {delimiter}: First decide whether a user is asking \ 
    a question about anything related to restaurants or cafes, menus, \ 
    dinners, party planning, travel, restaurant or accommodation suggestions \ 
    recommendations on cafes, eating places, restaurants, travel guide, \ 
    or just any of the above.

    step 2: {delimiter}: If the user is asking a question related to step 1, \ 
    check the services below and answer only based on the available services:


    All available services for {menu} are:
    { bravo_cafe() }


    step 3: {delimiter}: only mention or reference services in the list of all available services in step 2, \ 
    As these are the only services offered. And always include its contact details for easy reach.

    step 4: {delimiter}: If the question is not related to the available services, \ 
    say "Sorry, I can only answer questions about the available services for {menu}." \ 
    If the question is unclear or incomplete, say "Please rephrase or complete your \ 
    question to help me have a clear insight.
    

    Answer the customer in a calm and friendly tone.

    Lets think step by step.

    Use the following format:
    step 1 {delimiter} < step 1 reasoning >
    step 2 {delimiter} < step 2 reasoning >
    step 3 {delimiter} < step 3 reasoning >
    step 4 {delimiter} < step 4 reasoning >


    Respond to user: {delimiter} < response to customer >

    Make sure to include {delimiter} to seperate every step.
    Note: only display the answer. DO NOT SHOW THE STEPS.

    """


    bravo_prompt_template = f"""

        Answer the question based on the contexts below. 

        {delimiter}

        Contexts: {{bravo_system_message}}

        {delimiter}

        Question:{{user_message}}

        Answer:"""    


    bravo_prompt = ChatPromptTemplate.from_template(bravo_prompt_template)


    bravo_customer_messages = bravo_prompt.format_messages(
        bravo_system_message = bravo_system_message,
        user_message= user_message
    )



    if menu == "Bravo Cafe":

        if st.button("Enter"):

            bravo_response = chat_model(bravo_customer_messages)


            st.write(bravo_response.content)

    # About Flavours Pub

    flavours_system_message = f"""
    You will be provided with customer service queries. \
    The customer service query will be delimited with \
    {delimiter} characters.

    step 1: {delimiter}: First decide whether a user is asking \ 
    a question about anything related to restaurants or cafes, menus, \ 
    dinners, party planning, travel, restaurant or accommodation suggestions \ 
    recommendations on cafes, eating places, restaurants, travel guide, \ 
    or just any of the above.

    step 2: {delimiter}: If the user is asking a question related to step 1, \ 
    check the services below and answer only based on the available services:


    All available services for {menu} are:
    { flavours_pub() }


    step 3: {delimiter}: only mention or reference services in the list of all available services in step 2, \ 
    As these are the only services offered. And always include its contact details for easy reach.

    step 4: {delimiter}: If the question is not related to the available services, \ 
    say "Sorry, I can only answer questions about the available services for {menu}." \ 
    If the question is unclear or incomplete, say "Please rephrase or complete your \ 
    question to help me have a clear insight.
    

    Answer the customer in a calm and friendly tone.

    Lets think step by step.

    Use the following format:
    step 1 {delimiter} < step 1 reasoning >
    step 2 {delimiter} < step 2 reasoning >
    step 3 {delimiter} < step 3 reasoning >
    step 4 {delimiter} < step 4 reasoning >


    Respond to user: {delimiter} < response to customer >

    Make sure to include {delimiter} to seperate every step.
    Note: only display the answer. DO NOT SHOW THE STEPS.

    """


    flavours_prompt_template = f"""

        Answer the question based on the contexts below. 

        {delimiter}

        Contexts: {{flavours_system_message}}

        {delimiter}

        Question:{{user_message}}

        Answer:"""    


    flavours_prompt = ChatPromptTemplate.from_template(flavours_prompt_template)


    flavours_customer_messages = flavours_prompt.format_messages(
        flavours_system_message = flavours_system_message,
        user_message= user_message
    )



    if menu == "Flavours Pub & Gill":

        if st.button("Enter"):

            flavours_response = chat_model(flavours_customer_messages)


            st.write(flavours_response.content)


    # About Livingstone Lodge

    llodge_system_message = f"""
    You will be provided with customer service queries. \
    The customer service query will be delimited with \
    {delimiter} characters.

    step 1: {delimiter}: First decide whether a user is asking \ 
    a question about anything related to restaurants or cafes, menus, \ 
    dinners, party planning, travel, restaurant or accommodation suggestions \ 
    recommendations on cafes, eating places, restaurants, travel guide, \ 
    or just any of the above.

    step 2: {delimiter}: If the user is asking a question related to step 1, \ 
    check the services below and answer only based on the available services:


    All available services for {menu} are:
    { livingstone_lodge() }


    step 3: {delimiter}: only mention or reference services in the list of all available services in step 2, \ 
    As these are the only services offered. And always include its contact details for easy reach.

    step 4: {delimiter}: If the question is not related to the available services, \ 
    say "Sorry, I can only answer questions about the available services for {menu}." \ 
    If the question is unclear or incomplete, say "Please rephrase or complete your \ 
    question to help me have a clear insight.
    

    Answer the customer in a calm and friendly tone.

    Lets think step by step.

    Use the following format:
    step 1 {delimiter} < step 1 reasoning >
    step 2 {delimiter} < step 2 reasoning >
    step 3 {delimiter} < step 3 reasoning >
    step 4 {delimiter} < step 4 reasoning >


    Respond to user: {delimiter} < response to customer >

    Make sure to include {delimiter} to seperate every step.
    Note: only display the answer. DO NOT SHOW THE STEPS.

    """


    llodge_prompt_template = f"""

        Answer the question based on the contexts below. 

        {delimiter}

        Contexts: {{llodge_system_message}}

        {delimiter}

        Question:{{user_message}}

        Answer:"""    


    llodge_prompt = ChatPromptTemplate.from_template(llodge_prompt_template)


    llodge_customer_messages = llodge_prompt.format_messages(
        llodge_system_message = llodge_system_message,
        user_message= user_message
    )



    if menu == "Livingstone Lodge":

        if st.button("Enter"):

            llodge_response = chat_model(llodge_customer_messages)


            st.write(llodge_response.content)



# memory = ConversationBufferMemory(memory_key="chat_history")

with my_explore:

    # st.markdown("<h5 style='text-align: center; color: blue;'>NOTE: Always specify the name of the restaurant or lodge you are asking about.</h5>", unsafe_allow_html=True)

    st.markdown('''
    <div>
    <div style="border: 0.3px solid gray; padding: 10px; border-radius: 10px; margin: 10px 0px;">
    <p><b>Access Menus for Restaurants</b><br>
    <i>- Show me a menu for flavours? or Bravo Cafe or Sweet & Salty Cafe? (Lodges inclusive)</i></p>
    </div>
    <div style="border: 0.3px solid gray; padding: 10px; border-radius: 10px; margin: 10px 0px;">
    <p><b>Access Room rates or Conference or restaurant menus for Lodges</b><br>
    <i>- Room rates for Livingstone Lodge? Chapa Classic Lodge? and More...</i></p>
    </div>
    <div style="border: 0.3px solid gray; padding: 10px; border-radius: 10px; margin: 10px 0px;">
    <p><b>Plan Trips or Date outings at your favourite Restaurants</b><br>
    <i>- Make me a budget from bravo cafe within K200 for the following: 
    4 cold beverages, a large pizza and 2 con ice creams. also compare for kubu cafe and flavours</i><br>
    <i>- I will be travelling to livingstone. recommend for me some cheap accommodation and how much they cost</i></p>
    </div>
    </div>
    ''', unsafe_allow_html=True)  

    st.write("---")  

    txt = st.text_input("How may we assist you, our customer?", max_chars=300)

    user_message = f""" {txt} """

    # prompt = f"""
    # System Message: {system_message}
    # Customer Query: {user_message}
    # """

    prompt_template = f"""
    Answer the question based on the contexts below. 

    {delimiter}

    Contexts: {{system_message}}

    {delimiter}

    Question:{{user_message}}

    Answer:"""


    my_prompt = ChatPromptTemplate.from_template(prompt_template)


    customer_messages = my_prompt.format_messages(
        system_message= system_message,
        user_message= user_message
    )


    chat_model = ChatOpenAI(temperature=0, model=model)

    # llm = chat_model(customer_messages)

    # memory = ConversationBufferMemory()

    # conversation = ConversationChain(
    #     llm=chat_model,
    #     memory=memory,
    
    #     verbose=False
    # )



    if st.button("Send"):

        response = chat_model(customer_messages)


        st.write(response.content)

    # parser = PromptTemplate(
    #     input_variables=["system_message", "txt"],
    #     template= prompt
    # )

    # chain = LLMChain(llm=chat_model, prompt=prompt)



    # if txt:

    #     chain.run({"system_message": system_message,"txt":txt})

    # if 'generated' not in st.session_state:
    #     st.session_state['generated'] = []

    # if 'past' not in st.session_state:
    #     st.session_state['past'] = []

    # txt = st.chat_input(placeholder="How may we assist you, our customer?",max_chars=300)

    # word = len(re.findall(r'\w+', system_message))
    # st.write('Number of Words :', word)


    # if txt:

    #     loading_message = st.empty()
    #     loading_message.text("Loading... Please wait!")

    #     user_message = f"""
    #      {txt}

    #     """

    #     messages = [
    #     {'role': 'system',
    #     'content': system_message
    #     },

    #     {'role': 'user',
    #     'content': f"{delimiter}{user_message}{delimiter}"
    #     }]

    #     response, token_dict = get_completion_from_messages(messages)
    #     final_response = response.split(delimiter)[-1].strip()
    #     res_word = len(re.findall(r'\w+', final_response))
    #     user_text = st.chat_message("user")
    #     user_text.write(txt)

    #     if res_word < 3:
                    
    #         message = st.chat_message("assistant")
    #         error_text = "Sorry! Am having troubles right now, try to rephrase your question to help me have more insight, please!..." 

    #         message.write("""
    #         Sorry! Am having troubles right now, try to rephrase your question to help me have more insight, please!...
    #         Otherwise I really want to assist you.
    #         """ )

    #         conn = snowflake.connector.connect(
    #             user=sf_user,
    #             password=sf_password,
    #             account=sf_account,
    #             database=sf_database,
    #             schema=sf_schema
    #             )

    #         cursor = conn.cursor()
                
    #         current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]

    #         query = f"INSERT INTO {table_name} (PROMPT,RESPONSE,MY_CURRENT_TIME) VALUES (%s,%s,%s)"

    #         try:
    #             cursor.execute(query, (txt,error_text,current_time,))
    #             conn.commit()
    #         except Exception as e:
    #             st.error(f"Error sending data to Database: {e}")
    #         finally:
    #             cursor.close()
    #             conn.close()

    #     else:
    #         mytxt = st.chat_message("assistant")
    #         # mytxt.session_state.generated.append(final_response)
    #         mytxt.write(final_response)
    #         loading_message.text("")


    #         conn = snowflake.connector.connect(
    #             user=sf_user,
    #             password=sf_password,
    #             account=sf_account,
    #             database=sf_database,
    #             schema=sf_schema
    #             )

    #         cursor = conn.cursor()
                
            
    #         current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]

    #         query = f"INSERT INTO {table_name} (PROMPT,RESPONSE,MY_CURRENT_TIME) VALUES (%s,%s,%s)"

    #         try:
    #             cursor.execute(query, (txt,final_response,current_time,))
    #             conn.commit()
    #         except Exception as e:
    #             st.error(f"Error sending data to Database: {e}")
    #         finally:
    #             cursor.close()
    #             conn.close()



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
