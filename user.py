#list to keep track of active users
global active_users
active_users = []

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

#add a user to the active users list, the user is a user object, fill the information of the user object with the information from the database
def add_user_to_active_users(ip_address, username, database):
    new_user = user(ip_address=ip_address, username=username)
    new_user.fill_info(username, database)
    active_users.append(new_user)

#remove a user from the active users list, the user is a user object, remove the user from the active users list based on the ip address or username
def remove_user_from_active_users(ip_address=None, username=None):
    for user in active_users:
        if (user.ip_address == ip_address and ip_address != None) or (user.username == username and username != None):
            active_users.remove(user)

#remove users from the active users list that have been inactive for a certain amount of time, the default waiting time is 450 seconds (7.5 minutes)
def remove_timeout_users(waiting_time=450):
    for user in active_users:
        if time.time() - user.timestamp > waiting_time:
            active_users.remove(user)