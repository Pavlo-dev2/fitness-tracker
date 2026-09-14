# Fitness Tracker

A web service for tracking sports and fitness performance.

The project is a learning-oriented web application built from scratch with Python. It includes a custom HTTP server, HTML/CSS frontend, user registration and login, and a simple JSON-based data storage system.

The project is still under development.

## Features

### User Registration

Users can create an account by providing:

* Username
* Email
* Password
* Password confirmation
* Birth date
* Gender

During registration, the server:

1. Receives the HTTP request.
2. Parses the request body.
3. Checks that the required fields are present.
4. Checks whether the username already exists.
5. Verifies that the password and confirmation match.
6. Adds the new user to the database.
7. Opens the home page for the newly registered user.

### User Login

Existing users can log in using their username and password.

The server checks the submitted credentials against the stored user data.

If the credentials are correct, the user is added to the list of active users and the home page is returned.

If the credentials are incorrect, the login page is returned with an error message.

### Profile Page

The application contains a profile update page and functionality for checking whether a user is currently active before allowing access to the page.

The profile update functionality is currently under development.

### Active Users

The server maintains an in-memory list of active users.

For each active user, information such as:

* IP address
* Username
* Email
* Timestamp
* Age
* Gender

can be associated with the user object.

Inactive users are automatically removed after a timeout.

### Static Files

The server can serve HTML and CSS files directly.

For example, requests for `style.css` are handled by the server and returned with the appropriate `text/css` content type.

The server also handles requests for `favicon.ico`.

## Architecture

The application currently follows a simple client-server architecture:

```text
┌─────────────────────┐
│      Web Browser    │
└──────────┬──────────┘
           │
           │ HTTP
           ▼
┌─────────────────────┐
│  Python HTTP Server  │
│                     │
│  Request parsing    │
│  Routing            │
│  Authentication     │
│  Response handling  │
└──────────┬──────────┘
           │
      ┌────┴─────┐
      ▼          ▼
┌──────────┐ ┌──────────┐
│   User   │ │ Database │
│  module  │ │  module  │
└──────────┘ └────┬─────┘
                  │
                  ▼
             database.txt
```

The server is implemented directly on top of Python TCP sockets instead of using a web framework.

This makes the project useful for learning how HTTP communication works underneath frameworks such as Flask or Django.

## HTTP Server

The project implements a basic HTTP server using:

```python
socket.socket()
```

The server:

1. Creates a TCP socket.
2. Binds it to an IP address and port.
3. Listens for incoming connections.
4. Accepts a client connection.
5. Receives the HTTP request.
6. Parses the requested path and request body.
7. Processes the request.
8. Sends an HTTP response.
9. Closes the connection.

Simplified request flow:

```text
Browser
   │
   │ HTTP request
   ▼
TCP socket
   │
   ▼
HTTP request parser
   │
   ▼
Request handler
   │
   ├── Login
   ├── Registration
   ├── Profile
   └── Static files
   │
   ▼
HTTP response
   │
   ▼
Browser
```

## Supported Requests

The server currently handles several application routes, including:

```text
/                       → Login page
/create-account         → Account creation page
/login                  → User login
/register               → User registration
/update-profile-page    → Profile page for active users
```

The application also handles requests for static resources such as:

```text
/style.css
/favicon.ico
```

## Data Storage

The current version uses a JSON file as a simple database:

```text
database.txt
```

The database is loaded into a Python object when the server starts.

Users can then be:

* searched by username;
* checked during login;
* added during registration.

The database layer is separated into:

```text
databaselib.py
```

This keeps database-related operations separate from the HTTP server logic.

## Project Structure

```text
fitness-tracker/
├── CreateAcount.html       # Account creation page
├── Login.html              # Login page
├── UpdateProfile.html      # Profile page
├── UpdatPR.html            # Additional profile-related page
├── WPLogin.html            # Login-related page
├── home.html               # Home page
├── style.css               # Website styling
│
├── http_lan_server.py      # Custom HTTP server
├── databaselib.py          # Database operations
├── user.py                 # User and active-user management
├── file.py                 # File operations
├── database.txt            # JSON-based user database
│
├── README.md
├── LICENSE
└── todo.txt
```

## Technologies

### Backend

* Python 3
* TCP sockets
* HTTP
* JSON

### Frontend

* HTML
* CSS

### Storage

* JSON file

No external web framework is currently required.

## What I Learned

This project was created as a practical exercise in web development and networking.

The main concepts explored are:

* TCP sockets
* HTTP request and response structure
* HTTP request parsing
* Client-server architecture
* HTML
* CSS
* Form processing
* User registration
* Authentication logic
* Data storage
* JSON
* Python modules
* Basic session/active-user management
* Serving static files

One of the main goals of the project is to understand how a web application works underneath higher-level frameworks.

## Current Limitations

This is a learning project and is not intended for production use.

Current limitations include:

* Single-process request handling
* Basic HTTP parsing
* JSON file used as the database
* Limited request validation
* Basic active-user tracking
* Profile update functionality is still under development
* No production-grade session management
* No HTTPS/TLS
* No production-grade authentication security

These limitations are part of the project's current development stage.

## Future Development

Planned improvements include:

* [ ] Complete profile editing
* [ ] Add fitness/workout tracking
* [ ] Add workout history
* [ ] Add statistics and progress tracking
* [ ] Replace the JSON database with SQLite
* [ ] Improve HTTP request parsing
* [ ] Add proper routing
* [ ] Improve authentication and session management
* [ ] Add input validation
* [ ] Add automated tests
* [ ] Improve error handling
* [ ] Add a JavaScript frontend
* [ ] Create a REST API
* [ ] Improve project structure and documentation

## License

This project is licensed under the MIT License.

See [`LICENSE`](LICENSE) for the full license text.
