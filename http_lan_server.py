import socket
import re
import json
import time
import sys
import os
import file
import databaselib
import user

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
        style_content = file.returnfiletext("style.css", encoding="utf-8")
        cl_socket.sendall((f"HTTP/1.1 200 OK\r\nContent-Type: text/css\r\n\r\n{style_content}").encode("utf-8"))
        print(f"\n===Sent style.css to {client_address}===\n")
        return True
    return False

#check if the request is for favicon.ico and send a 404 response if it is
def iffavicon(data, cl_socket, client_address = None):
    print("\n===Checking for favicon.ico request...===\n")
    if "favicon.ico" in data:
        cl_socket.sendall(b"HTTP/1.1 404 Not Found\r\nContent-Type: text/plain\r\n\r\nFavicon not found.")
        print(f"\n===Sent favicon.ico not found message to {client_address}===\n")
        return True
    return False

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

#send an 200 text/html response to the client
def send_html_response(client_socket, html_file):
    text = file.returnfiletext(html_file, encoding="utf-8")
    send_response(client_socket, "200 OK", "text/html", text)

#send a response to the client with the given status code, content type and content
def send_response(client_socket, status_code, content_type, content):
    #print(content)
    client_socket.sendall(f"HTTP/1.1 {status_code}\r\nContent-Type: {content_type}\r\n\r\n{content}".encode("utf-8"))
    client_socket.close()

#add a line to the html response at a specific position, for example for wrong login data, add a line to the login page at position 10
def add_line_to_html_response(flile_path, line_to_add, position):
    text = file.returnfiletext(flile_path, encoding="utf-8")
    lines = text.split("\n")
    lines.insert(position, line_to_add)
    text = "\n".join(lines)
    #print(text)
    return text

#main loop to accept connections and handle requests
#no request - send login page
#request = login - check if user is in database and if password is correct, send home page if it is, send login page with error message if it isn't
#request = create-account - send create account page
#request = register - check if user is in database, if it is send login page with error message, if it isn't add user to database and send home page
#request = update-profile-page - check if user is logged in and send UpdateProfile page
def main():
    #database as python object
    database = databaselib.open_database()
    s.listen(1)
    while True:
        #remove users from the active users list that have been there for a certain amount of 4.5 min
        user.remove_timeout_users()
        user.print_active_users()

        client_socket, client_address = s.accept()
        try:
            client_socket.settimeout(10.0)
            print(f"Connection from {client_address} has been established!")
            c_data = get_all_data(client_socket)

            if ifcss(c_data, client_socket, client_address) == False and iffavicon(c_data, client_socket, client_address) == False:
                #separate the request from the data        
                request = separate_request(c_data)

                #Handle the request with no body, like login or create account, and send the appropriate page

                #send the login page if there is no request
                if not request:
                    send_html_response(client_socket, "Login.html")
                    continue
                #send the create account page
                elif request == "create-account":
                    # Handle registration logic here
                    send_html_response(client_socket, "CreateAcount.html")
                    continue
                #check is user is logged in and send UpdateProfile page
                elif request == "update-profile-page":
                    if user.check_user_in_active_users(client_address[0]):
                        send_html_response(client_socket, "UpdateProfile.html")
                        user.update_user_timestapm(client_address[0])
                    else:
                        send_html_response(client_socket, "Login.html")
                
                #process the request
                if request == "add-pr" or request == "login" or request == "update-profile" or request == "register":
                    body = separate_body(c_data)
                    if body:
                        try:
                            #request body as python object
                            oby_body = body_to_object(body)
                            
                            #process the request based on the request type
                            if request == "login":
                                # Handle login logic here
                                if oby_body.get("username") and oby_body.get("password"):#check if request body has username and password
                                    #check if user is in database and if password is correct
                                    if databaselib.check_user_in_database(oby_body.get("username"), oby_body.get("password"), database) == True:

                                        #add the user to the active users list and send them to the home page
                                        user.add_user_to_active_users(client_address[0], oby_body.get("username"), database)
                                        send_html_response(client_socket, "home.html")
                                    #send login page with error message if user is not in database or password is incorrect
                                    elif databaselib.check_user_in_database(oby_body.get("username"), oby_body.get("password"), database) == False:
                                        response_content = add_line_to_html_response("Login.html", "<h2 class=\"error-message\">Wrong Username or Password</h2>\n", 12)
                                        send_response(client_socket, "200 OK", "text/html", response_content)
                                        continue

                            elif request == "register":#register the user, handel the data for new user and save it to the database
                                #check if request body has all information: username and password and confirm password and birthdate and email and gender
                                if oby_body.get("username") and oby_body.get("password") and oby_body.get("confirm_password") and oby_body.get("email") and oby_body.get("birthdate") and oby_body.get("gender"):
                                    print(f"\n===   ===REGISTER USER===    ===\n")
                                    #register the user if they don't exist in the database, otherwise send them to the login page
                                    if (not databaselib.check_user_exists(oby_body.get("username"), database)): 
                                        #check if the password and confirm password match, if they don't send the user to the create account page with an error message
                                        if oby_body.get("password") != oby_body.get("confirm_password") or oby_body.get("confirm_password") == None:
                                            response_content = add_line_to_html_response("CreateAcount.html", "<h2 class=\"error-message\">Passwords do not match</h2>\n", 12)
                                            send_response(client_socket, "200 OK", "text/html", response_content)
                                            continue
                                        
                                        #add the user to the database
                                        oby_body.pop("confirm_password")
                                        database = databaselib.add_user_to_database(oby_body, database)

                                        #add the user to the active users list and send them to the home page
                                        user.add_user_to_active_users(client_address[0], oby_body.get("username"), database)
                                        send_html_response(client_socket, "home.html")
                                        continue
                                    else:
                                        #user already exists, send them to the login page with an error message
                                        response_content = add_line_to_html_response("CreateAcount.html", "<h2 class=\"error-message\">User with this username already exists</h2>\n", 12)
                                        send_response(client_socket, "200 OK", "text/html", response_content)
                                        continue
                                
                                #if request body does not have all information, send the user to the login page with an error message
                                response_content = add_line_to_html_response("Login.html", "<h2 class=\"error-message\">Invalid request</h2>\n", 12)
                                send_response(client_socket, "200 OK", "text/html", response_content)
                            
                            #handle update profile request
                            elif request == "update-profile":
                                pass#TODO

                        except json.JSONDecodeError:
                            print("Error: Invalid JSON in request body.")
                            
            client_socket.close()

        except socket.timeout:
            print(f"Connection from {client_address} timed out.")
            client_socket.close()


    print("Server stopped.")
    s.close()

create_socket()
main()