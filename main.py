from pickle import APPEND

from bson import ObjectId
import datetime
from flask import Flask, render_template, request, redirect, session
import pymongo
my_client=pymongo.MongoClient("mongodb://localhost:27017")
my_database=my_client["ticketbooking"]
game_hosts_collection=my_database["game_hosts"]
audience_collection=my_database["audience"]
stadiums_collection=my_database["stadiums"]
teams_collection=my_database["teams"]
schedules_collection=my_database["schedules"]
games_collection=my_database["games"]
tickets_collection=my_database["tickets"]
bookings_collection=my_database["bookings"]
payments_collection=my_database["payments"]
app= Flask(__name__)
app.secret_key="ticketbooking"
admin_username="admin1"
admin_password="admin1"

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/admin_login")
def admin_login():
    return render_template("admin_login.html")

@app.route("/admin_login_action", methods=['post'])
def admin_login_action():
    username = request.form.get("username")
    password = request.form.get("password")
    if username == admin_username and password == admin_password:
        session["role"] = "admin"
        return redirect("/admin_home")
    else:
        return render_template("message.html", message="Invalid login details")


@app.route("/admin_home")
def admin_home():
    return render_template("admin_home.html")

@app.route("/game_host_registration")
def game_host_registration():
    return render_template("game_host_registration.html")

@app.route("/game_host_registration_action" ,methods=['post'])
def game_host_registration_action():
    first_name = request.form.get("first_name")
    last_name = request.form.get("last_name")
    email = request.form.get("email")
    phone = request.form.get("phone")
    password = request.form.get("password")
    address = request.form.get("address")
    zipcode = request.form.get("zipcode")
    query = {"email": email}
    count = game_hosts_collection.count_documents(query)
    if count > 0:
        return render_template("message.html", message="Duplicate Email Address")
    query = {"phone": phone}
    count = game_hosts_collection.count_documents(query)
    if count > 0:
        return render_template("message.html", message="Duplicate phone numer")
    query = {"first_name": first_name,"last_name":last_name, "email": email, "phone": phone, "password": password,"address":address,"zipcode":zipcode,"status":'unauthorized'}
    game_hosts_collection.insert_one(query)
    return render_template("message.html", message="gamehost registration successful")

@app.route("/game_host_login")
def game_host_login():
    return render_template("game_host_login.html")

@app.route("/game_host_login_action" ,methods=['post'])
def game_host_login_action():
    email = request.form.get("email")
    password = request.form.get("password")
    query = {"email": email, "password": password}
    count = game_hosts_collection.count_documents(query)
    if count > 0:
        game_host = game_hosts_collection.find_one(query)
        if game_host['status'] == 'authorized' :
            session['game_host_id'] = str(game_host['_id'])
            session['role'] = 'game_host'
            return redirect("/game_host_home")
        else:
            return render_template("message.html", message='you are not authorised')
    else:
        return render_template("message.html", message="invalid login details")

@app.route("/game_host_home")
def game_host_home():
    return render_template("game_host_home.html")

@app.route("/audien_login")
def audien_login():
    return render_template("audien_login.html")

@app.route("/audien_login_action" ,methods=['post'])
def audien_login_action():
    email = request.form.get("email")
    password = request.form.get("password")
    query = {"email": email, "password": password}
    count = audience_collection.count_documents(query)
    if count > 0:
        audien = audience_collection.find_one(query)
        session['audien_id'] = str(audien['_id'])
        session['role'] = 'audien'
        return redirect("/audien_home")
    else:
        return render_template("message.html", message="invalid login details")

@app.route("/audien_home")
def audien_home():
    return render_template("audien_home.html")

@app.route("/audien_registration")
def audien_registration():
    return render_template("audien_registration.html")

@app.route("/audien_registration_action" ,methods=['post'])
def audien_registration_action():
    first_name = request.form.get("first_name")
    last_name = request.form.get("last_name")
    email = request.form.get("email")
    phone = request.form.get("phone")
    password = request.form.get("password")
    address = request.form.get("address")
    zipcode = request.form.get("zipcode")
    query = {"email": email}
    count = audience_collection.count_documents(query)
    if count > 0:
        return render_template("message.html", message="Duplicate Email Address")
    query = {"phone": phone}
    count = audience_collection.count_documents(query)
    if count > 0:
        return render_template("message.html", message="Duplicate phone numer")
    query = {"first_name": first_name,"last_name":last_name, "email": email, "phone": phone, "password": password,"address":address,"zipcode":zipcode}
    audience_collection.insert_one(query)
    return render_template("message.html", message="audien registration successful")

@app.route("/view_game_host")
def view_game_host():
    query = {}
    game_hosts = game_hosts_collection.find(query)
    game_hosts = list(game_hosts)
    return render_template("view_game_host.html", game_hosts = game_hosts)

@app.route("/authorize_game_host")
def authorize_game_host():
    game_host_id = request.args.get('game_host_id')
    query = {"_id": ObjectId(game_host_id)}
    query2 = {"$set": {"status": "authorized"}}
    game_hosts_collection.update_one(query, query2)
    return redirect("/view_game_host")

@app.route("/unauthorize_game_host")
def unauthorize_game_host():
    game_host_id = request.args.get('game_host_id')
    query = {"_id": ObjectId(game_host_id)}
    query2 = {"$set": {"status": "unauthorized"}}
    game_hosts_collection.update_one(query, query2)
    return redirect("/view_game_host")

@app.route("/stadiums")
def stadiums():
    query = {}
    stadiums=stadiums_collection.find(query)
    stadiums=list(stadiums)
    message = request.args.get('message')
    return render_template("stadiums.html",message=message,stadiums=stadiums)

@app.route("/stadium_action",methods=['POST'])
def stadium_action():
    stadium_name = request.form.get('stadium_name')
    stadium_location = request.form.get('stadium_location')
    query = {"stadium_name": stadium_name,"stadium_location": stadium_location}
    count = stadiums_collection.count_documents(query)
    if count > 0:
        return redirect("/stadiums?message=stadium name already registered")
    query = {"stadium_name":stadium_name ,"stadium_location": stadium_location}
    stadiums_collection.insert_one(query)
    return redirect("/stadiums?message=Stadium added successfully")

@app.route("/teams")
def teams():
    query = {}
    teams=teams_collection.find(query)
    teams=list(teams)
    message = request.args.get('message')
    return render_template("teams.html",message=message,teams=teams)

@app.route("/team_action",methods=['POST'])
def team_action():
    team_name = request.form.get('team_name')
    no_of_players = request.form.get('no_of_players')
    coach_name = request.form.get('coach_name')
    query = {"team_name": team_name,"no_of_players":no_of_players,"coach_name":coach_name }
    count = teams_collection.count_documents(query)
    if count > 0:
        return redirect("/teams?message=Team name already registered")
    query = {"team_name":team_name,"no_of_players":no_of_players,"coach_name":coach_name}
    teams_collection.insert_one(query)
    return redirect("/teams?message=Team Added Successfully")

@app.route("/games")
def games():
    query = {}
    games=games_collection.find(query)
    games=list(games)
    message = request.args.get('message')
    return render_template("games.html",message=message,games=games)

@app.route("/game_action",methods=['POST'])
def game_action():
    game_title = request.form.get('game_title')
    game_type = request.form.get('game_type')
    query = {"game_title": game_title,"game_type":game_type }
    count = games_collection.count_documents(query)
    if count > 0:
        return redirect("/games?message=Game Title Already registered")
    query = {"game_title": game_title,"game_type":game_type}
    games_collection.insert_one(query)
    return redirect("/games?message=Game Title Added Successfully")

@app.route("/schedules")
def schedules():
    query = {}
    schedules=schedules_collection.find(query)
    schedules=list(schedules)
    message = request.args.get('message')
    return render_template("schedules.html",message=message,schedules=schedules)

@app.route("/add_schedules")
def add_schedules():
    game_id=request.args.get("game_id")
    stadium_id=request.args.get("stadium_id")

    if game_id== None:
        game_id=""
    if stadium_id== None:
        stadium_id=""
    query = {}
    stadiums=stadiums_collection.find(query)
    stadiums=list(stadiums)
    games = games_collection.find(query)
    games = list(games)
    teams = teams_collection.find(query)
    teams = list(teams)
    message = request.args.get('message')
    today = datetime.datetime.now()
    today = today.strftime("%Y-%m-%dT%H:%M")
    return render_template("add_schedules.html",message=message,schedules=schedules,stadiums=stadiums,games=games,teams=teams,game_id=game_id,stadium_id=stadium_id,str=str, today=today)


@app.route("/add_schedules_action", methods=['post'])
def add_schedules_action():
    stadium_id=request.form.get('stadium_id')
    game_id = request.form.get('game_id')
    team1_id = request.form.get('team1_id')
    team2_id = request.form.get('team2_id')
    start_date = request.form.get('start_date')
    end_date = request.form.get('end_date')
    schedule_price = request.form.get("schedule_price")
    return render_template("next.html",stadium_id=stadium_id,game_id=game_id,team1_id=team1_id,team2_id=team2_id,start_date=start_date,end_date=end_date, schedule_price=schedule_price)

@app.route("/add_schedules_action2" ,methods=['post'])
def add_schedules_action2():
    stadium_id=request.form.get('stadium_id')
    game_id = request.form.get('game_id')
    team1_id=request.form.get('team1_id')
    team2_id = request.form.get('team2_id')
    start_date=request.form.get('start_date')
    end_date = request.form.get('end_date')
    schedule_price = request.form.get('schedule_price')
    orchestra_couple_seats=request.form.get('orchestra_couple_seats')
    orchestra_couple_seats_price=request.form.get('orchestra_couple_seats_price')
    orchestra_general_seats = request.form.get('orchestra_general_seats')
    orchestra_general_seats_price = request.form.get('orchestra_general_seats_price')
    mezzanine_couple_seats = request.form.get('mezzanine_couple_seats')
    mezzanine_couple_seats_price = request.form.get('mezzanine_couple_seats_price')
    mezzanine_general_seats = request.form.get('mezzanine_general_seats')
    mezzanine_general_seats_price = request.form.get('mezzanine_general_seats_price')
    balcony_couple_seats = request.form.get('balcony_couple_seats')
    balcony_couple_seats_price = request.form.get('balcony_couple_seats_price')
    balcony_general_seats = request.form.get('balcony_general_seats')
    balcony_general_seats_price = request.form.get('balcony_general_seats_price')
    start_date= datetime.datetime.strptime(start_date,"%Y-%m-%dT%H:%M")
    end_date = datetime.datetime.strptime(end_date, "%Y-%m-%dT%H:%M")
    team1 = get_team_by_team_id(ObjectId(team1_id))
    team2 = get_team_by_team_id(ObjectId(team2_id))

    query = {"$or": [{"start_date": {"$gte": start_date, "$lte": end_date},
                      "end_date": {"$gte": end_date}, "stadium_id": ObjectId(stadium_id)},
                     {"start_date": {"$lte": start_date},
                      "end_date": {"$gte": start_date, "$lte": end_date}, "stadium_id": ObjectId(stadium_id)},
                     {"start_date": {"$lte": start_date},
                      "end_date": {"$gte": end_date}, "stadium_id": ObjectId(stadium_id)},
                     {"start_date": {"$gte": start_date,"$lte": end_date},
                      "end_date": {"$gte": start_date,"$lte": end_date}, "stadium_id": ObjectId(stadium_id)}
                     ]}
    count = schedules_collection.count_documents(query)
    if count!=0:
        return render_template("message.html", message="Stadium has time Collision for this timings")

    query = {"$or": [{"start_date": {"$gte": start_date, "$lte": end_date},
                      "end_date": {"$gte": end_date}, "team1_id": ObjectId(team1_id)},
                     {"start_date": {"$lte": start_date},
                      "end_date": {"$gte": start_date, "$lte": end_date}, "team1_id": ObjectId(team1_id)},
                     {"start_date": {"$lte": start_date},
                      "end_date": {"$gte": end_date}, "team1_id": ObjectId(team1_id)},
                     {"start_date": {"$gte": start_date,"$lte": end_date},
                      "end_date": {"$gte": start_date,"$lte": end_date}, "team1_id": ObjectId(team1_id)}
                     ]}

    count = schedules_collection.count_documents(query)
    if count != 0:
        return render_template("message.html", message=team1['team_name']+" has time Collision for this timings")

    query = {"$or": [{"start_date": {"$gte": start_date, "$lte": end_date},
                      "end_date": {"$gte": end_date}, "team1_id": ObjectId(team2_id)},
                     {"start_date": {"$lte": start_date},
                      "end_date": {"$gte": start_date, "$lte": end_date}, "team1_id": ObjectId(team2_id)},
                     {"start_date": {"$lte": start_date},
                      "end_date": {"$gte": end_date}, "team1_id": ObjectId(team2_id)},
                     {"start_date": {"$gte": start_date,"$lte": end_date},
                      "end_date": {"$gte": start_date,"$lte": end_date}, "team1_id": ObjectId(team2_id)}
                     ]}
    count = schedules_collection.count_documents(query)
    if count != 0:
        return render_template("message.html", message=team2['team_name']+" has time Collision for this timings")

    query = {"$or": [{"start_date": {"$gte": start_date, "$lte": end_date},
                      "end_date": {"$gte": end_date}, "team2_id": ObjectId(team2_id)},
                     {"start_date": {"$lte": start_date},
                      "end_date": {"$gte": start_date, "$lte": end_date}, "team2_id": ObjectId(team2_id)},
                     {"start_date": {"$lte": start_date},
                      "end_date": {"$gte": end_date}, "team2_id": ObjectId(team2_id)},
                     {"start_date": {"$gte": start_date, "$lte": end_date},
                      "end_date": {"$gte": start_date, "$lte": end_date}, "team2_id": ObjectId(team2_id)}
                     ]}
    count = schedules_collection.count_documents(query)
    if count != 0:
        return render_template("message.html", message=team2['team_name'] + " has time Collision for this timings")

    query = {"$or": [{"start_date": {"$gte": start_date, "$lte": end_date},
                      "end_date": {"$gte": end_date}, "team2_id": ObjectId(team1_id)},
                     {"start_date": {"$lte": start_date},
                      "end_date": {"$gte": start_date, "$lte": end_date}, "team2_id": ObjectId(team1_id)},
                     {"start_date": {"$lte": start_date},
                      "end_date": {"$gte": end_date}, "team2_id": ObjectId(team1_id)},
                     {"start_date": {"$gte": start_date, "$lte": end_date},
                      "end_date": {"$gte": start_date, "$lte": end_date}, "team2_id": ObjectId(team1_id)}
                     ]}
    count = schedules_collection.count_documents(query)
    if count != 0:
        return render_template("message.html", message=team1['team_name'] + " has time Collision for this timings")

    query = {"stadium_id":ObjectId(stadium_id),"game_id":ObjectId(game_id),"team1_id":ObjectId(team1_id),"team2_id":ObjectId(team2_id),"start_date":start_date,"end_date":end_date,"orchestra_couple_seats":orchestra_couple_seats,"orchestra_couple_seats_price":orchestra_couple_seats_price,"orchestra_general_seats":orchestra_general_seats,"orchestra_general_seats_price":orchestra_general_seats_price,"mezzanine_couple_seats":mezzanine_couple_seats,"mezzanine_couple_seats_price":mezzanine_couple_seats_price,"mezzanine_general_seats":mezzanine_general_seats,"mezzanine_general_seats_price":mezzanine_general_seats_price,"balcony_couple_seats":balcony_couple_seats,"balcony_couple_seats_price":balcony_couple_seats_price,"balcony_general_seats":balcony_general_seats,"balcony_general_seats_price":balcony_general_seats_price, "schedule_price": schedule_price, "status": "Not Published"}
    schedules_collection.insert_one(query)
    return render_template("message.html",message="Schedule Added Successfully")

@app.route("/view_schedules")
def view_schedules():
    stadium_id = request.args.get('stadium_id')
    game_id = request.args.get('game_id')
    schedule_type=request.args.get('schedule_type')
    today=datetime.datetime.now()
    if game_id == None:
        game_id=""
    if stadium_id == None:
        stadium_id=""
    if schedule_type == None:
        schedule_type="Future"
    if game_id=="" and stadium_id=="" :
        query={}
    elif game_id=="" and stadium_id!="" :
        query={"stadium_id":ObjectId(stadium_id)}
    elif game_id!="" and stadium_id=="" :
        query={"game_id":ObjectId(game_id)}
    elif game_id!="" and stadium_id!="" :
        query={"game_id":ObjectId(game_id),"stadium_id":ObjectId(stadium_id)}

    if schedule_type=='Future':
        if game_id == "" and stadium_id == "":
            query = {"start_date":{"$gte":today}}
        elif game_id == "" and stadium_id != "":
            query = {"stadium_id": ObjectId(stadium_id),"start_date":{"$gte":today}}
        elif game_id != "" and stadium_id == "":
            query = {"game_id": ObjectId(game_id),"start_date":{"$gte":today}}
        elif game_id != "" and stadium_id != "":
            query = {"game_id": ObjectId(game_id), "stadium_id": ObjectId(stadium_id),"start_date":{"$gte":today}}
    else:
        if game_id == "" and stadium_id == "":
            query = {"start_date":{"$lt":today}}
        elif game_id == "" and stadium_id != "":
            query = {"stadium_id": ObjectId(stadium_id),"start_date":{"$lt":today}}
        elif game_id != "" and stadium_id == "":
            query = {"game_id": ObjectId(game_id),"start_date":{"$lt":today}}
        elif game_id != "" and stadium_id != "":
            query = {"game_id": ObjectId(game_id), "stadium_id": ObjectId(stadium_id),"start_date":{"$lt":today}}

    if session['role'] == 'game_host':
        game_host_id = session['game_host_id']
        if schedule_type == 'Future':
            if game_id == "" and stadium_id == "":
                query = {"$or":[{"start_date": {"$gte": today}, "status": "Not Published"},{"start_date": {"$gte": today}, "game_host_id": ObjectId(game_host_id)}]}
            elif game_id == "" and stadium_id != "":
                query = {"$or": [{"stadium_id": ObjectId(stadium_id),"start_date": {"$gte": today}, "status": "Not Published"},{"stadium_id": ObjectId(stadium_id),"start_date": {"$gte": today}, "game_host_id": ObjectId(game_host_id)}]}
            elif game_id != "" and stadium_id == "":
                query = {"$or":[{"game_id": ObjectId(game_id), "start_date": {"$gte": today}, "status": "Not Published"},{"game_id": ObjectId(game_id), "start_date": {"$gte": today}, "game_host_id": ObjectId(game_host_id)}]}
            elif game_id != "" and stadium_id != "":
                query = {"$or": [{"stadium_id": ObjectId(stadium_id),"game_id": ObjectId(game_id),"start_date": {"$gte": today}, "status": "Not Published"},{"stadium_id": ObjectId(stadium_id),"game_id": ObjectId(game_id),"start_date": {"$gte": today}, "game_host_id": ObjectId(game_host_id)}]}
        else:
            if game_id == "" and stadium_id == "":
                query = {"start_date": {"$lt": today}, "game_host_id": ObjectId(game_host_id)}
            elif game_id == "" and stadium_id != "":
                query = {"stadium_id": ObjectId(stadium_id), "start_date": {"$lt": today}, "game_host_id": ObjectId(game_host_id)}
            elif game_id != "" and stadium_id == "":
                query = {"game_id": ObjectId(game_id), "start_date": {"$lt": today}, "game_host_id": ObjectId(game_host_id)}
            elif game_id != "" and stadium_id != "":
                query = {"game_id": ObjectId(game_id), "stadium_id": ObjectId(stadium_id), "start_date": {"$lt": today}, "game_host_id": ObjectId(game_host_id)}
    if session['role'] == 'audien':
        if game_id == "" and stadium_id == "":
            query = {"start_date":{"$gte":today}}
        elif game_id == "" and stadium_id != "":
            query = {"stadium_id": ObjectId(stadium_id), "status":"Published" ,"start_date":{"$gte":today}}
        elif game_id != "" and stadium_id == "":
            query = {"game_id": ObjectId(game_id),"status":"Published", "start_date":{"$gte":today}}
        elif game_id != "" and stadium_id != "":
            query = {"game_id": ObjectId(game_id), "status":"Published", "stadium_id": ObjectId(stadium_id),"start_date":{"$gte":today}}
    print(query)
    schedules=schedules_collection.find(query)
    schedules=list(schedules)
    schedules.reverse()
    print(schedules)
    stadiums=stadiums_collection.find({})
    stadiums=list(stadiums)
    games=games_collection.find({})
    games=list(games)
    return render_template("view_schedules.html",schedules=schedules,stadiums=stadiums,games=games,str=str,stadium_id=stadium_id,game_id=game_id,schedule_type=schedule_type,get_stadium_by_stadium_id=get_stadium_by_stadium_id,get_game_by_game_id=get_game_by_game_id,get_team_by_team_id=get_team_by_team_id, get_game_host_by_game_host_id=get_game_host_by_game_host_id)

def get_stadium_by_stadium_id(stadium_id):
    print(stadium_id)
    query={"_id":ObjectId(stadium_id)}
    stadium=stadiums_collection.find_one(query)
    return stadium

def get_game_by_game_id(game_id):
    query={"_id":game_id }
    game=games_collection.find_one(query)
    return game

def get_team_by_team_id(team_id):
    query={"_id":team_id}
    team=teams_collection.find_one(query)
    return team

@app.route("/book_tickets")
def book_tickets():
    schedule_id=request.args.get('schedule_id')
    seat_type=request.args.get('seat_type')
    query={"_id" : ObjectId(schedule_id)}
    schedule=schedules_collection.find_one(query)
    total_seats = 0
    price_per_seat = 0
    persons_count = 0
    if seat_type == 'orchestra_couple':
        total_seats = schedule['orchestra_couple_seats']
        price_per_seat = schedule['orchestra_couple_seats_price']
        persons_count = 2
    elif seat_type == 'orchestra_general':
        total_seats = schedule['orchestra_general_seats']
        price_per_seat = schedule['orchestra_general_seats_price']
        persons_count = 1
    elif seat_type == 'mezzanine_couple':
        total_seats = schedule['mezzanine_couple_seats']
        price_per_seat = schedule['mezzanine_couple_seats_price']
        persons_count = 2
    elif seat_type == 'mezzanine_general':
        total_seats = schedule['mezzanine_general_seats']
        price_per_seat = schedule['mezzanine_general_seats_price']
        persons_count = 1
    elif seat_type == 'balcony_couple':
        total_seats = schedule['balcony_couple_seats']
        price_per_seat = schedule['balcony_couple_seats_price']
        persons_count = 2
    elif seat_type == 'balcony_general':
        total_seats = schedule['balcony_general_seats']
        price_per_seat = schedule['balcony_general_seats_price']
        persons_count = 1
    total_seats = int(total_seats)
    price_per_seat = int(price_per_seat)
    print(total_seats)
    print(price_per_seat)
    return render_template("book_tickets.html",schedule_id=schedule_id,seat_type=seat_type,schedule=schedule,get_stadium_by_stadium_id=get_stadium_by_stadium_id,get_game_by_game_id=get_game_by_game_id,get_team_by_team_id=get_team_by_team_id, total_seats=total_seats, price_per_seat=price_per_seat, persons_count=persons_count, is_seat_booked=is_seat_booked)

@app.route("/book_tickets2")
def book_tickets2():
    schedule_id=request.args.get("schedule_id")
    seat_type=request.args.get("seat_type")
    total_seats = request.args.get("total_seats")
    price_per_seat=request.args.get("price_per_seat")
    persons_count=request.args.get("persons_count")
    selected_seats=[]
    for i in range(1,int(total_seats)+1):
        selected_seat=request.args.get("seat"+ str(i))
        if selected_seat != None :
            selected_seats.append(i)
    print(selected_seats)
    if len(selected_seats) == 0:
        return render_template("message.html",message="choose seats")
    booking_date=datetime.datetime.now()
    price=len(selected_seats)*int(price_per_seat)
    status='payment pending'
    audien_id=session['audien_id']
    query={"booking_date":booking_date,"price":price,"status":status,"schedule_id":ObjectId(schedule_id),"seat_type":seat_type,"persons_count":persons_count,"audien_id":ObjectId(audien_id), "selected_seats": selected_seats}
    result=bookings_collection.insert_one(query)
    booking_id=result.inserted_id
    query={"_id":booking_id}
    booking=bookings_collection.find_one(query)
    print(booking)
    print(selected_seats)

    return render_template("book_tickets2.html",booking=booking,selected_seats=selected_seats, price=price)

@app.route("/book_tickets3")
def book_tickets3():
    booking_id = request.args.get("booking_id")
    price = request.args.get("price")
    card_type = request.args.get("card_type")
    card_number = request.args.get("card_number")
    holder_name = request.args.get("holder_name")
    cvv = request.args.get("cvv")
    expire_date = request.args.get("expire_date")
    query={"_id":ObjectId(booking_id)}
    booking=bookings_collection.find_one(query)
    for selected_seat in booking["selected_seats"]:
        name=request.args.get("name"+str(selected_seat))
        query={"name":name,"seat_number":selected_seat,"booking_id":ObjectId(booking_id)}
        if int(booking['persons_count']) == 2:
            name2 = request.args.get("name2" + str(selected_seat))
            query["name2"] = name2
        tickets_collection.insert_one(query)
    query1={"_id":ObjectId(booking_id)}
    query2={"$set":{"status":"Booked"}}
    bookings_collection.update_one(query1,query2)
    admin_commission = int(price) *.05
    game_host_price = int(price) *.95
    query={"card_type":card_type,"card_number":card_number,"holder_name":holder_name,"cvv":cvv,"expire_date":expire_date,"price":price,"booking_id":ObjectId(booking_id), "admin_commission": admin_commission, "game_host_price": game_host_price}
    payments_collection.insert_one(query)
    return render_template("message.html",message="Tickets Booked Successfully")

@app.route("/buy_schedule")
def buy_schedule():
    schedule_id = request.args.get("schedule_id")
    schedule_price = request.args.get("schedule_price")
    return render_template("buy_schedule.html", schedule_id=schedule_id, schedule_price=schedule_price)

@app.route("/buy_schedule_action")
def buy_schedule_action():
    schedule_id=request.args.get("schedule_id")
    schedule_price=request.args.get("schedule_price")
    card_type=request.args.get("card_type")
    card_number=request.args.get("card_number")
    holder_name=request.args.get("holder_name")
    cvv=request.args.get("cvv")
    expire_date=request.args.get("expire_date")
    game_host_id=session['game_host_id']
    query1={"_id":ObjectId(schedule_id)}
    query2={"$set":{"status":"Published","game_host_id":ObjectId(game_host_id)}}
    schedules_collection.update_one(query1,query2)
    query={"schedule_id":ObjectId(schedule_id),"status":"payment successful","price":schedule_price,"card_number":card_number,"holder_name":holder_name,"card_type":card_type,"cvv":cvv,"expire_date":expire_date,"game_host_id":ObjectId(game_host_id)}
    payments_collection.insert_one(query)
    return render_template("message.html",message="schedules bought successfully")

@app.route("/bookings")
def bookings():
    if session['role'] == 'audien':
        audien_id=session['audien_id']
        query={"audien_id":ObjectId(audien_id), "status": {"$ne": "payment pending"}}
    else:
        schedule_id=request .args.get("schedule_id")
        seat_type=request .args.get("seat_type")
        query={"schedule_id":ObjectId(schedule_id),"seat_type":seat_type, "status": {"$ne": "payment pending"}}
    bookings=bookings_collection.find(query)
    bookings=list(bookings)
    print(bookings)
    bookings.reverse()
    today = datetime.datetime.now()
    return render_template("bookings.html",bookings=bookings, get_schedule_by_schedule_id=get_schedule_by_schedule_id,get_stadium_by_stadium_id=get_stadium_by_stadium_id, get_game_by_game_id=get_game_by_game_id, get_team_by_team_id=get_team_by_team_id, get_game_host_by_game_host_id=get_game_host_by_game_host_id, get_tickets_by_booking_id=get_tickets_by_booking_id, today=today)

def get_game_host_by_game_host_id(game_host_id):
    query = {"_id": game_host_id}
    game_host = game_hosts_collection.find_one(query)
    return game_host

def get_schedule_by_schedule_id(schedule_id):
    print(schedule_id)
    query = {"_id": ObjectId(schedule_id)}
    schedule = schedules_collection.find_one(query)
    print(schedule)
    return schedule
def get_tickets_by_booking_id(booking_id):
    query = {"booking_id": booking_id}
    tickets = tickets_collection.find(query)
    tickets = list(tickets)
    return tickets
def is_seat_booked(seat_number, schedule_id, seat_type):
    query = {"selected_seats": seat_number, "schedule_id": ObjectId(schedule_id), "seat_type": seat_type, "status": "Booked"}
    count = bookings_collection.count_documents(query)
    if count != 0:
        return True
    return False

@app.route("/cancel_booking")
def cancel_booking():
    booking_id = request.args.get("booking_id")
    query1 = {"_id": ObjectId(booking_id)}
    query2 = {"$set" : {"status": "Cancelled"}}
    bookings_collection.update_one(query1, query2)
    query1 = {"booking_id": ObjectId(booking_id)}
    payment = payments_collection.find_one(query1)
    game_host_price = int(payment['price'])*0.10
    refund_price = int(payment['price'])*0.85
    query2 = {"$set": {"status": "Cancelled", "game_host_price": game_host_price, "refund_price": refund_price}}
    payments_collection.update_one(query1, query2)
    return render_template("message.html", message="Booking Cancelled")
@app.route("/payments")
def payments():
    booking_id = request.args.get("booking_id")
    query = {"booking_id": ObjectId(booking_id)}
    payment = payments_collection.find_one(query)
    return render_template("payments.html", payment=payment)

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


app.run(debug=True,port=5001)


