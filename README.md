[![unit test](https://github.com/CondricNay/ku-polls/actions/workflows/python-app.yml/badge.svg)](https://github.com/CondricNay/ku-polls/actions/workflows/python-app.yml)

## KU Polls: Online Survey Questions 

This Django application is designed for conducting online polls and surveys. 

This application leverages Django's built-in functionality for web development based on this [Django Tutorial project][django-tutorial], with additional features.

This application provides a user-friendly interface for creating, viewing, and participating in polls and surveys. It serves as a practical tool for collecting and analyzing user opinions and feedback.

This app was created as part of the [Individual Software Process](
https://cpske.github.io/ISP) course at Kasetsart University.

---

## Install and Run

1. Start the server in the virtual environment. 
   ```
   # activate the virtualenv for this project. On Linux or MacOS:
   source env/bin/activate
   # on MS Windows:
   env\Scripts\activate

   # start the django server
   python3 manage.py runserver
   ```
   This starts a web server listening on port 8000.

2. You should see this message printed in the terminal window:
   ```
   Starting development server at http://127.0.0.1:8000/
   Quit the server with CONTROL-C.
   ```
   If you get a message that the port is unavailable, then run the server on a different port (1024 thru 65535) such as:
   ```
   python3 manage.py runserver 12345
   ```

3. In a web browser, navigate to <http://localhost:8000>

4. To stop the server, press CTRL-C in the terminal window. Exit the virtual environment by closing the window or by typing:
   ```
   deactivate
   ```

---

## Project Documents

All project documents are in the [Project Wiki](../../wiki/Home).

- [Vision Statement](../../wiki/Vision%20Statement)
- [Requirements](../../wiki/Requirements)
- [Domain Model](../../wiki/Domain-Model)
- [Development Plan](../../wiki/Development-Plan)
- [Iteration 1 Plan](../../wiki/Iteration-1-Plan)
- [Iteration 2 Plan](../../wiki/Iteration-2-Plan)
- [Iteration 3 Plan](../../wiki/Iteration-3-Plan)
- [Task Board](https://github.com/users/CondricNay/projects/3/views/1)

[django-tutorial]: https://docs.djangoproject.com/en/4.2/intro/tutorial01/


## Demo Users

| Username  | Password        |
|-----------|-----------------|
|   harry   | hackme22        |
|   ron     | hackme22        |
|  hermione | hackme22        |
|   draco   | hackme22        |

