import socket
import re#GET /UpdatPR HTTP/1.1
import json
import time
import sys
import os

#create a socket
def create_socket():
    print(sys.platform)
    global s
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(("192.168.178.27", 80))

#get all data from the client
def get_all_data(client_socket):
    print("\n===Receiving data from client...===\n")
    data = b""
    while b"\r\n\r\n" not in data:
        data = data + client_socket.recv(1024)
    print(f"===Received data from client:\n{data.decode('utf-8')}===\n")
    return data.decode("utf-8")

#check if the request is for style.css and send it if it is
def ifcss(data, cl_socket, client_address = None):
    if "style.css" in data:
        with open("style.css", "r", encoding="utf-8") as f:
            cl_socket.sendall((f"HTTP/1.1 200 OK\r\nContent-Type: text/css\r\n\r\n{f.read()}").encode("utf-8"))
            print(f"\n===Sent style.css to {client_address}===\n")
            return 1
    return 0

#check if the request is for favicon.ico and send a 404 response if it is
def iffavicon(data, cl_socket, client_address = None):
    print("\n===Checking for favicon.ico request...===\n")
    if "favicon.ico" in data:
        cl_socket.sendall(b"HTTP/1.1 404 Not Found\r\nContent-Type: text/plain\r\n\r\nFavicon not found.")
        print(f"\n===Sent favicon.ico not found message to {client_address}===\n")
        return 1
    return 0

#separate the request from the data
def separate_request(data):
    request = re.findall("[POSTGET]+ /(.*?) HTTP/1.1\r\n", data)
    print(f"\n===Separated request: {request}===\n")
    if len(request) > 0:
        return request[0]
    return None

#separate the body from the data
def separate_body(data):
    body = re.findall("\r\n\r\n(.*)", data)
    print(f"\n===Separated body: {body}===\n")
    if len(body) > 0:
        return body[0]
    return None

#convert the body to a python object
def body_to_object(body):
    infos = body.split("&")
    dicks = {}
    for info in infos:
        key, value = info.split("=")
        dicks[key] = value
    return dicks

#convert the json file to a python object
def json_file_to_object():
    with open("database.txt", "r", encoding="utf-8") as f:
        return json.load(f)

#convert a python object to a json file
def python_object_to_json_file(oby):
    text = json.dumps(oby)
    with open("database.txt", "w", encoding="utf-8") as f:
        f.seek(0)
        f.write(text)

#check if user is in database
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

def check_user_exists(username, database):
    if username == None:
        return False
    for user in database:
        if user.get("username") == username:
            return True
    return False

#send an 200 text/html response to the client
def send_html_response(client_socket, html_file):
    with open(html_file, "r", encoding="utf-8") as f:
        content = f.read()
        send_response(client_socket, "200 OK", "text/html", content)

def send_response(client_socket, status_code, content_type, content):
    print(content)
    client_socket.sendall(f"HTTP/1.1 {status_code}\r\nContent-Type: {content_type}\r\n\r\n{content}".encode("utf-8"))
    client_socket.close()

#add a line to the html response at a specific position, for example for wrong login data, add a line to the login page at position 10
def add_line_to_html_response(flile_path, line_to_add, position):
    with open(flile_path, "r", encoding="utf-8") as f:
        text = f.read()
    lines = text.split("\n")
    lines.insert(position, line_to_add)
    text = "\n".join(lines)
    #print(text)
    return text

def open_database():
    with open("database.txt", "r", encoding="utf-8") as f:
        database = json.load(f)
        return database

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
    python_object_to_json_file(database)

#the user class is used to create a user object that can be used to store user information and send it to the database
class user:
    type = "user"
    def __init__(self, ip_address=None, username=None, email=None, password=None, number_in_database=None, status="passive", timestamp=time.time(), age=None, gender=None):
        self.ip_address = ip_address
        self.number_in_database = number_in_database
        self.username = username
        self.password = password
        self.email = email
        self.status = status
        self.timestamp = timestamp
        self.age = age
        self.gender = gender
    
    def fill_info(self, username, database):
        number_in_database = 0
        for user_list_object in database:
            if user_list_object.get("username") == username:
                self.age = user_list_object.get("age")
                self.gender = user_list_object.get("gender")
                self.email = user_list_object.get("email")
                self.password = user_list_object.get("password")
                self.number_in_database = number_in_database
            number_in_database += 1

#list to keep track of active users [client_address, username, status, timestamp]
active_users = []

#main loop to accept connections and handle requests

def main():
    s.listen(1)
    while True:
        client_socket, client_address = s.accept()
        try:
            client_socket.settimeout(10.0)
            print(f"Connection from {client_address} has been established!")
            c_data = get_all_data(client_socket)

            if ifcss(c_data, client_socket, client_address) == 0 and iffavicon(c_data, client_socket, client_address) == 0:
                print(f"Received data:\n{c_data}")        
                request = separate_request(c_data)

                #Handle the request with no body, like login or create account, and send the appropriate page

                #send the login page if there is no request
                if not request:
                    send_html_response(client_socket, "Login.html")
                    continue
                elif request == "create-account":#send the create account page
                    # Handle registration logic here
                    send_html_response(client_socket, "CreateAcount.html")
                
                #process the request
                if request == "add-pr" or request == "login" or request == "update-profile" or request == "register":
                    body = separate_body(c_data)
                    if body:
                        try:
                            oby_body = body_to_object(body)#request body as python object
                            database = open_database()#database as python object
                            
                            #process the request based on the request type
                            if request == "login":
                                # Handle login logic here
                                if oby_body.get("username") and oby_body.get("password"):#check if request body has username and password
                                    print(oby_body)
                                    if check_user_in_database(oby_body.get("username"), oby_body.get("password"), database) == True:
                                        send_html_response(client_socket, "home.html")
                                    elif check_user_in_database(oby_body.get("username"), oby_body.get("password"), database) == False:
                                        response_content = add_line_to_html_response("Login.html", "<h2 class=\"error-message\">Wrong Username or Password</h2>\n", 12)
                                        send_response(client_socket, "200 OK", "text/html", response_content)

                            elif request == "register":#register the user, handel the data fo new user and save it to the database
                                if oby_body.get("username") and oby_body.get("password") and oby_body.get("confirm_password") and oby_body.get("email") and oby_body.get("birthdate") and oby_body.get("gender"):#check if request body has username and password and confirm password and birthdate and email and gender
                                    
                                    if (not check_user_exists(oby_body.get("username"), database)):
                                        
                                        if oby_body.get("password") != oby_body.get("confirm_password") or oby_body.get("confirm_password") == None:
                                            response_content = add_line_to_html_response("CreateAcount.html", "<h2 class=\"error-message\">Passwords do not match</h2>\n", 12)
                                            send_response(client_socket, "200 OK", "text/html", response_content)
                                            continue
                                        
                                        database = json_file_to_object()
                                        oby_body.pop("confirm_password")####work hier, remove the confirm password from the body before saving it to the database
                                        add_user_to_database(oby_body)
                                        send_html_response(client_socket, "home.html")
                                else:
                                    send_html_response(client_socket, "Login.html")#user already exists, send them to the login page

                        except json.JSONDecodeError:
                            print("Error: Invalid JSON in request body.")
                
                #client_socket.sendall(b"HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\n\r\nHello, World!")
            
            client_socket.close()

        except socket.timeout:
            print(f"Connection from {client_address} timed out.")
            client_socket.close()

    print("Server stopped.")
    s.close()

create_socket()
main()