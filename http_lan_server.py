import socket
import re#GET /UpdatPR HTTP/1.1
import json
import time

#create a socket
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
def ifcss(data, cl_socket):
    if "style.css" in data:
        with open("style.css", "r", encoding="utf-8") as f:
            cl_socket.sendall((f"HTTP/1.1 200 OK\r\nContent-Type: text/css\r\n\r\n{f.read()}").encode("utf-8"))
            print(f"\n===Sent style.css to {client_address}===\n")
            return 1
    return 0

#check if the request is for favicon.ico and send a 404 response if it is
def iffavicon(data, cl_socket):
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
def check_user_in_database(username, password):
    with open("database.txt", "r", encoding="utf-8") as f:
        database = json.load(f)
        for user in database:
            if user.get("username") == username:
                if user.get("password") == password:
                    return True
                break
    return False

def check_user_exists(username):
    with open("database.txt", "r", encoding="utf-8") as f:
        database = json.load(f)
        for user in database:
            if user.get("username") == username:
                return True
    return False

def send_html_response(client_socket, html_file):
    with open(html_file, "r", encoding="utf-8") as f:
        content = f.read()
        client_socket.sendall(f"HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n{content}".encode("utf-8"))
        client_socket.close()

s.listen(1)

#list to keep track of active users [client_address, username, status, timestamp]
active_users = []

while True:
    client_socket, client_address = s.accept()
    try:
        client_socket.settimeout(1.0)
        print(f"Connection from {client_address} has been established!")
        c_data = get_all_data(client_socket)

        if ifcss(c_data, client_socket) == 0 and iffavicon(c_data, client_socket) == 0:
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



                        #print(f"===Parsed JSON body: {oby_body}===\n")
                        #database = json_file_to_object()
                        #database.append(oby_body)
                        #python_object_to_json_file(database)
                        
                        
                        
                        #process the request based on the request type
                        if request == "login":
                            # Handle login logic here
                            with open("database.txt", "r", encoding="utf-8") as f:

                                database = json.load(f)#database as python object

                                if check_user_in_database(oby_body.get("username"), oby_body.get("password")) == True:
                                    active_users.append([client_address, oby_body.get("username"), "loged_in", time.time()])
                                    send_html_response(client_socket, "home.html")

                                elif check_user_in_database(oby_body.get("username"), oby_body.get("password")) == False:
                                    active_users.append([client_address, oby_body.get("username"), "wrong_login_data", time.time()])
                                    send_html_response(client_socket, "WPLogin.html")

                        elif request == "register":#register the user, handel the data fo new user and save it to the database
                            if not check_user_exists(oby_body.get("username")):
                                database = json_file_to_object()
                                database.append(oby_body)
                                python_object_to_json_file(database)
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