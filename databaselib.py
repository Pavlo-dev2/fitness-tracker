import file
import json

#open the database and return it as a python object
def open_database():
    databasetext = file.returnfiletext("database.txt", encoding="utf-8")
    return json.loads(databasetext)

#add a user to the database, the user_dict is a dictionary with the user information
def add_user_to_database(user_dict):
    database = open_database()
    object_to_add = {
        "username": user_dict.get("username"),
        "email": user_dict.get("email"),
        "password": user_dict.get("password"),
        "birthdate": user_dict.get("birthdate"),
        "gender": user_dict.get("gender")
    }
    database.append(object_to_add)
    file.write_python_object_to_json_file(database)

#check if user is in database
def check_user_exists(username, database):
    if username == None:
        return False
    for user in database:
        if user.get("username") == username:
            return True
    return False

#check if the user is in database and if the password is correct, return True if it is, False if it isn't
def check_user_in_database(username, password, database):
    if username == None or password == None:
        return False
    for user in database:
        if user.get("username") == username:
            if user.get("password") == password:
                if user.get("username") == None or user.get("password") == None:
                    return False
                print(f"\n===User {username}, {user.get("username")}===\n")
                return True
            break
    return False