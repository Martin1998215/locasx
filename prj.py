
import os
import re
import openai
import streamlit as st 
import pandas as pd
import sqlite3
# from api_key import apikey

conn = sqlite3.connect("data.db")
c = conn.cursor()

def user_query():
    c.execute('''
    CREATE TABLE IF NOT EXISTS user_query(
        query_id INTEGER PRIMARY KEY,
        user_prompt VARCHAR(255),
        system_solution VARCHAR(1000)
    ) ''')


def add_query(user_prompt, system_solution):
    c.execute('''
    INSERT INTO user_query(user_prompt, system_solution)
    VALUES(?,?)''',
              (user_prompt, system_solution)
              )
    conn.commit()


def view_user_query():
    c.execute('''
    SELECT * FROM user_query
    ''')

    data = c.fetchall()
    return data


openai.api_key = st.secrets["api"]
# model = "gpt-3.5-turbo"
model = "gpt-3.5-turbo-16k"

def get_completion_from_messages(messages, model = "gpt-3.5-turbo-16k"):

    response = openai.ChatCompletion.create(
        model=model,
        messages=messages,
        temperature=0
    )    


    return response.choices[0].message["content"]


delimiter = "####"

system_message = f"""
Follow these steps to answer the following customer queries.
the customer query will be delimeted with four hashtags, \ 
i.e {delimiter}.

step 1: {delimiter}: First decide whether a user is asking \ 
a question about a lodge or restaurant or specific service or services about the rooms \ 
or accommodation \ or the conference room for hosting an event or restaurant or bar or \ 
other outlets etc. \ 

step 2: {delimiter}: If the user is asking about specific lodge or restaurant or just the services, \ 
identify if the services are in the following list.
All available lodges and restaurants and their services: 

1. Name of the lodge: Livingstone lodge

Available services:

A. Rooms or Accommodation:

All our rooms are self contained with Dstv, free Wi Fi and 24hrs \ 
security service. it has a total of 11 Self contained rooms. \ 

- Executive Double: K300 per night.
- Executive Twin: K350 per night.
- Family Rooms: K370 per night.
- Deluxe Suite: K1,000 per night

B. Conference Room:

Conferences and meetings \ 
Conferencing, meetings and seminars for up to 80 participants. \ 
We cater for conferences, seminars and workshops for up to 80 \ 
people  with a large conference halls and meeting rooms. \ 

C. Restaurant:

i. Starter: 
- Greek Salad
- Egg Carviar
- Cold meat Platter

ii. Main Course:
- Spice grilled chicken
- Fillet served with herbed mornay sauce
- Beef Strongoff
- Lasagne
All accompanied with:
- Saffron rice
- Fondant Potatoes
- And served with seasonal vegetables

iii. Dessert:
- Banana Crumble
- Triffle

D. Bar: 
- our cocktail Bar offers some drinks and different kinds of beers.

Other activities:
- Event hires such as weddings, Parties, meetings

E. About Us:

- Livingstone Lodge is of the Lodge with a total of 11 Self contained rooms, \ 
a VIP deluxe suite and conferencing facility accommodating about 80 people. \ 
Established on July 1, 1957, the Hostels Board of Management is a government \ 
Institution under the Ministry of Tourism and Arts of the Government of the \ 
Republic of Zambia. However, over time, the demand from the general public and \ 
other Institutions emerged and the government decided to open to the general public. \ 


G. CONTACT US:
- Phone Number: +260-213-320647.

- Email address: livingstonelodge7@gmail.com.

- Postal Address: P.O Box 61177, Livingstone.

- Located: Maramba Road Plot 01, maramba area.
- Nearby: Maramba market or Livingstone Central Police Station or Town.

2. Name of Restaurant: Flavours Pub and Grills

Available Services:

A. About Us:
- Flavours Pub & Grill is a Restaurant located in the city of Livingstone, \ 
Along Lusaka road, Town Area in livingstone, Zambia.
- We serve the Best food ever, at affordable prices.
- We also make the quickiest deliveries anywhere around Livingstone.
- We have enough space to accomodate many people at our restaurant for both \ 
open space and shelter space. 
- We also offer attachments to catering students, with the ability to \ 
hire potential ones after their studies. 
- We also have a large car parking space to ensure the safety of your car. \ 

B. Food Menu:
- We serve the best food with the best ingredients at affordable prices.

- Traditional Pizza: K55.00
- Burger: K33.00
- Sharwama: K22.00
- Sausage & Chips: K80.00
- Bufe: K122.00
- Nshina, Kapenta: K28.00
- Juice: K19.00

C. Our Deliveries:
- We offer the best and quickest kind of deliveries using our delivery van \ 
around livingstone.
- Make An order by calling us on 0977 682 611.

D. Our Chefs:
- We hire the very best chefs to serve you the best food you ever dream to taste.
- Our chefs offer the best gesture. they know how to treat our customers.
- We also offer attachments to catering students, with the ability to \ 
hire potential ones after their studies.


E. Contact Us:
- Cell: 0974 893 829.
- Tel: 211 120 829.
- Email: FlavoursPub&Grill@gmail.com.
- Facebook Page: Flavours Pub & Grill.
- Located: Along Lusaka Road, Town area, in livingstone, Zambia.
- Nearby: Town or Mukuni Park

3. Name of Lodge: Chappa Classic Lodge

Available services:

A. Rooms or Accommodation:

All rooms come with WiFi, air-conditioning, a fridge, en suite bathroom, \ 
DStv and full English breakfast. Rates are based on double occupancy.

- Deluxe Classic: US$ 45
- Single Room Classic: US$ 35
- Double/Twin Room Classic: US$ 40

Deluxe Rooms at Chapa Vanguard:
- Deluxe Rooms: US$ 50
- All rooms at the Chapa Vanguard are spacious Deluxe rooms with a modern \  
en suite bathroom. The rooms comes with DStv, a fridge and coffee and \  
tea making facilities.

B. Conference Room:

Conferencing, meetings and seminars for up to 160 participants:
- We cater for conferences, seminars and workshops for up to 160 \ 
people with a large conference halls and meeting rooms. Flipovers, \ 
LCD projector are available.

Hotel room:
Chapa Classic and Chapa Vanguard together offer a total of 67 rooms. \ 
We work together with hotels nearby to accommodate all of your guest, \ 
arranging transport to the conference facilities at Chapa upon request.

Other activities:
- Swimming Pool.
- Event hires such as weddings, Parties, meetings.

C. About Us:

- The Chapa Classic Lodge and the annex Chapa Vanguard offer a total of \ 
67 rooms and conference facilities for up to 160 participants. The lodges \  
are across the street from each other in a quiet area just next to the \  
Livingstone city centre.
- Located: 66 Nehru Way, town area, Livingstone.
- The lodges are locally owned and operated. Buy local and support the local community!
- Just 7 minutes to shops and restaurants.
- Chapa Classic Lodge and Tours offers easy access to the major Livingstone \  
town business centers and we can arrange any activity you would want to \ 
do around the magnificent Victoria Fall.
- Affordable rates: We offer affordable rooms and conferencing: value for \  
money. Ask for seasonal special deals.

D. CONTACT US:
- Located: 66 Nehru Way, Town area, Livingstone
- Phone Number: +260977796710
- Email address: chapaclassiclodge@zamnet.zm
- Nearby: Livingstone Central Hospital or Town or NIPA

4. name of lodge: Kaazimein Lodge.

About us:

- A visit to Livingstone the tourist capital city of Zambia is not complete \ 
without time off at the Kaazmein Lodge and Resort. The resort gives you the \ 
chance to be at one with nature, a time to regroup, to find your inner core \ 
and to leave enriched and empowered, promising to return. Everything that \  
Livingstone and its surrounding areas has to offer can be organized from here. \ 
The Kaazmein Lodge & Resort has 12 standard double / twin chalets, these units \  
of which overlook a mini lake. There are also 10 Hotel rooms and a Family Hotel \ 
Chalet Room. The family units contain a double room ideally for parents and \ 
the next inter-leading room has two twin beds, both rooms are self contained.\  
There is a central dining complex with A wooden deck that overlooks the man-made \  
mini lake, an open bar and restaurant area, reception and a conference Hall. \  
The best accommodation provider situated in Livingstone, Zambia home of the \  
Mighty Victoria Falls, a region that offers a diversity of cultures rarely equaled  \  
by any other on earth, Enjoy the wide open spaces, where nature and backpacking \  
form a unity located in a quiet suburb within walking distance of town, \  
Let us make your stay and indeed your holiday memories an awesome journey into the \ 
life, adventure and culture of the ancient continent. With accommodation ranging \ 
from camping to private budget rooms Ideal For individuals / groups on a budget \  
trip or travel. Despite being budget rooms, enjoy the en suite luxury facilities \ 
under the indigenous African trees, these typical A-framed designed rooms are a \ 
unique option. We offer excellent prices and have great packages on all adrenaline \ 
activities in and around the Victoria falls.

Available services:

A. Rooms or accommodaion:

- Our rooms are crisp, bright,  full of class and character most \ 
important of all they are comfortable and spacious.  12 Chalets \ 
overlooking a water feature, 10Hotel Style Rooms set in a relaxed lawn \  
setting, and 12 self-contained A framed rooms, to cater for privacy \ 
and individuality of guest.

Our Rooms:
- Family Rooms
- Charlet Rooms
- Luxurious Rooms
- A-Frame Lounge

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
 
- Physical Address: 2764 Maina soko Road, Nottie Brodie area, Livingstone Zambia.

- Nearby: Chandamali Market or Mosque.

5. name of lodge: Mosi-O-Tunya Execcutive Lodge.

About Us:

- "A Gateway to the mighty Victoria Falls".
- Classified as a grade A - lodge by the ministry of Tourism and Natural resources.
- We are situated in the highlands area of Livingstone, off Lusaka Road and behind \ 
the Bible college. when with us, you are only five and eight minutes drive away from \ 
Town and the mighty victoria falls. 
- The lodge has 16 fully air conditioned immaculate en-suite rooms including family \ 
and self catering rooms.
- DSTV, WI FI & coffee/Tea making facilities are available in all the rooms.
- Also available is a restaurant serving appetizing international and special \ 
meals on al a carte basis as well as a swimming pool to cool you off from the \ 
blazing heat of livingstone.
- We arrange tours and adventure activities and offer Bus stop and Airport transfers \ 
at affordable fees.

Available Services:

A. Rooms or Accommodation:

- Standard Rooms: They are going at K450. They have a Double Bed.
- Executive Rooms: They are going at K550. They have a Queen Size Bed.
- Twin Rooms: they are going at K700. They have two three quarters Beds.
- Family Rooms: They are going at K1200. 

B. Restaurant:

Our Menus:
- Fish with Nshima: K70 per plate.
- Chicken with Nshima: K60 per plate.
- Pork with Nshima: K60 per plate.
- Sausage with Nshima: K50 per plate.
- T Bone witth Nshima: K75 per plate.

C. Activities:

- We offer Swimming Pool services to cool you off from the blazing heat of Livingstone.
- We arrange Tours and Adventure activities and offer Bus stop and Airport transfers at \ 
affordable fees.

D. Contact Us:

for a true value of hospitality, visit us at:
- Location: Plot No. 4424/37, Highlands, Livingstone.
- contact us on: 09773891512
- Email: reservations@mosiotunyalodge.co.zm
- website: www.mosiotunyalodge.co.zm.
- Nearby: Bible College.

6. Name of Lodge: White Rose Lodge.

About Us:

- White Rose Lodge is situated in Highlands, Livingstone at Plot No. 4424/17.
- It has 12 Self contained rooms with DSTV and WI FI.
- It also has a Restaurant which opens from 07 to 22 hrs.

Available Services:
A. Rooms or Accommodation:

All our rooms have DSTV and free WI FI.

- Double Bed Rooms: these are not self contained. They only have a cooler. they are going at K260.
- Double Bed Rooms: These are self contained, they have an Air Con. They are going at K350 and K360.
- Queen Standard Rooms: They are self contained, have an Air Con. They are going at K430.
- Apartment: It has 2 bedrooms, a Kitchen, living room, self catering. they are going at K1200.

B. Activities:
- Restaurant: we have a restaurant that opens at 07:00 to 22:00.
- Breakfast: between 07:00 to 09:00.
- Lunch: between 12:30 to 15:30.
- Dinner: between 18:30 to 22:00.
- Room Service: K10.
- Laundry: opens from 06:30 to 21:00.
- Checkouts: 10:00.
- Mini Bar: We have a mini bar that closes at 22:00. 

C. Contact Us:

- call us on 0977 84 96 90.
- Email us at whiteroselodge@yahoo.com
- Location: we are situated at Plot No. 4424/17, Highlands, Livingstone. PO Box 61062.
- Nearby: Chimulute Private School or Uno Filling Station or The Weigh Bridge 

7. Name of Lodge: KM Executive Lodge

A. About Us:
- KM Execuive Lodge is a Lodge which is located in Livingstone, Highlands, on plot number 2898/53 \ 
Off Lusaka Road.
- It offers a variety of services from Accommodation or Room services (Executive Rooms with self catering), \ 
a Conference Hall for events such as meetings, workshops etc, a Restaurant, Gym and a Swimming Pool \ 
with 24Hrs Security Services.

B. Room Prices:
- Double Room: K250
- King Executive Bed: K350
- Twin Executive (Two Double Beds): K500
- Family Apartment (Self Catering): K750
- King Executive (Self Catering): K500
- Any Single Room with Breakfast Provided for one person: K250
- Any Couple we charge K50 for Extra Breakfast.
- Twin Executive (Two Double Beds) with Breakfast provided for 2 people.

C. Restaurant or Food Menu Price List:
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

D. Gym Service.
E. Swimming Pool:
- we also have a swimming pool with 24Hrs security service.
F. Conference Hall:
- We also have a conference hall for events such as meetings, workshops and presentations.

G. Contact Us:
- Tel: +0213324051
- Cell: 0966603232 or 0977433762
- Email: kmexecutivelodge@gmail.com
- Facebook Page: KM Executive Lodge
- Located: plot number 2898/53, Off Lusaka Road, Highlands area, Livingstone.
- Nearby: Highlands Market or Zambezi Sports Club




step 3: {delimiter}: If the message contains services in the list above, \ 
list any assumptions the user is making in their message e.g that room X has \ 
a higher price than room Y.

step 4: {delimiter}: If the user made any assumptions, figure out whether the assumption \ 
is true based on your services information.

step 5: {delimiter}: First, politely correct the customer's incorrect assumption \ 
if applicable. only mention or reference services in the list of 7 available services, \ 
As these are the only services the lodge offers.
Answer the customer in a friendly tone.

Use the following format:
step 1 {delimiter} < step 1 reasoning >
step 2 {delimiter} < step 2 reasoning >
step 3 {delimiter} < step 3 reasoning >
step 4 {delimiter} < step 4 reasoning >
step 5 {delimiter} < step 5 reasoning >
Respond to user: {delimiter} < response to customer >

Make sure to include {delimiter} to seperate every step.

strip off step 1 to 4 and Show only step 5 and Respond to user as final answer.

"""



st.sidebar.write("### AI Assistant for Travel.")

# st.sidebar.write("### AI chatbot to assist customers with the services they need.")


tab1, tab2, tab3, tab4 = st.sidebar.tabs(["Services", "Partners", "About Us", "Contact Us"])

with tab1:


   	st.write("""
        - Travel
        - Hospitality
		""")
	
	st.write("""
	**Let Us Improve Your Travel Experience with all the services you need**
	- Are you coming to Livingstone? and you are wondering where to lodge or eating place ? 
	dont worry, our assistant got you covered... Just ask it whatever lodges are available, 
	their accommodation pricing, restaurants available and their menus...
	
	""")

with tab2:

   	st.write("""
    	**We partner with Lodges and restaurants to improve travel customer service experience through our AI assistant**
        - Flavors Pub & Grill.
        - Livingstone Lodge
        - Chappa classic lodge
		""") 
	st.write("""
	**Let Us Improve Your Travel Experience with all the services you need**
 	""")


with tab3:

    st.write("""

        - This is an AI chatbot powered by a large language model that has info on lodges and restaurants 
        we partnered with... check out our partners.. 
        - our goal is help improve your travel experience as you visit livingstone,
        by providing you with our AI assistant to help you where to find 
        accommodation or a restaurant.
	- NOTE: Our Assistant is just a tool and has a 70% accuracy. we are working on improving that.
        - We are only available in Livingstone.
    
    """) 

with tab4:

   	st.write("""
        - Call: 0976 03 57 66.
        - Email: locastechnology@gmail.com
        - We are located room # Mosi O Tunya business center, livingstone.
		""")        

st.sidebar.write("---") 

# st.sidebar.write("""
# **Let Us Improve Your Travel Experience with all the services you need**
# - Are you coming to Livingstone? and you are wondering where to lodge or eating place ? 
# dont worry, our assistant got you covered... Just ask it whatever lodges are available, 
# their accommodation pricing, restaurants available and their menus...

# """)

st.write("### Suggested Questions...")


col1, col2, col3 = st.columns(3)

with col1:
   st.warning("**What lodges are there? ---**")

with col2:
   st.warning("**what Restaurants are there?**")

with col3:
   st.warning("**what lodges offer Restaurant Services?**")
	

col4, col5, col6 = st.columns(3)

with col4:
   st.warning("**What lodges are there in area X eg Highlands, Nottie Brodie? ---**")

with col5:
   st.warning("**what are the room prices for lodge X? or what are the food prices for restaurant X? ---**")

with col6:
   st.warning("**what services are offered at Lodge X? eg Kaazimein lodge**")
 

st.write('---') 


txt = st.text_input("How may we assist you, our customer?")

words = len(re.findall(r'\w+', txt))
st.write('Number of Words :', words, "/750")

word = len(re.findall(r'\w+', system_message))
# st.write('Number of Words :', word)


if st.button("Ask Our AI Assistant"):

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

    response = get_completion_from_messages(messages)


    st.write("---")

    try:
        final_response = response.split(delimiter)[-1].strip()

    except Exception as e:
        final_response = "Sorry! Am having troubles right now, trying asking another question.." 

    st.write(final_response)

    
    # create user query db
    user_query()

    # add to user query db
    add_query(txt,final_response)

    view_db = view_user_query()

    view_df = pd.DataFrame(view_db, columns=[
        "user_id", "user_prompt", "system_solution"
    ])

    # st.write(view_df)

    st.write("---")

    res_word = len(re.findall(r'\w+', final_response))
    st.write('Number of Words :', res_word)



# Search for these
# 1. KM Executive Lodge
# 2. Asenga Lodge
# 3. Pumulani Guest Lodge
# 4. Chapa Classic
# 5. Woodlands Lodge
# 6. Richland Lodge
# 7. Golden days Executive
# 8. Revine Lodge
# 9. Zambezi Junction
# 10. Chrismar Hotel
