[![unit test](https://github.com/CondricNay/ku-polls/actions/workflows/python-app.yml/badge.svg)](https://github.com/CondricNay/ku-polls/actions/workflows/python-app.yml)

## KU Polls: Online Survey Questions 

This Django application is designed for conducting online polls and surveys. 

This application leverages Django's built-in functionality for web development based on this [Django Tutorial project][django-tutorial], with additional features.

This application provides a user-friendly interface for creating, viewing, and participating in polls and surveys. It serves as a practical tool for collecting and analyzing user opinions and feedback.

This app was created as part of the [Individual Software Process](
https://cpske.github.io/ISP) course at Kasetsart University.

---

## Installing the Application

See [Installation.md](https://github.com/CondricNay/ku-polls/blob/main/Installation.md) for installations guide.

## Running the Application
Now that you've configured your Django project and set up the environment, it's time to run your application. Follow these steps:

Activate the virtual environment (if it's not already activated):
```
# On Windows:
venv\Scripts\activate
# On Unix/Linux/macOS:
source venv/bin/activate
```

Start the Django development server with the following command:

```
python manage.py runserver
```

This command will start the development server, and you'll see output similar to:
```
Starting development server at http://127.0.0.1:8000/
Quit the server with CONTROL-C.
```

Your Django application is now running locally at http://127.0.0.1:8000/ (or http://localhost:8000/). You can access it in your web browser.

If this is the first time you are running the server, you may need to migrate after running the server
```
python manage.py migrate polls
```

To stop the server, press CTRL-C in the terminal window. Exit the virtual environment by closing the window or by typing:
```
deactivate
```
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

