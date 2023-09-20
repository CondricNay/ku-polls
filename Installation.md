## Clone/Download the code from Github
First, clone the GitHub repository to your local machine using the following command:

```
git clone https://github.com/CondricNay/ku-polls.git
```

or alternatively, you can download this as a zip file

## Create a virtual environment

It's a good practice to create a virtual environment to isolate your project's dependencies. You can use `virtualenv` to create one:

```
# Install virtualenv if not already installed
pip install virtualenv

# Create a virtual environment
virtualenv venv
```

Activate the virtual environment:
```
# On Windows:
venv\Scripts\activate

# On macOS and Linux:
source venv/bin/activate
```

## Install dependencies
Install the required Python packages from the `requirements.txt` file:

```
pip install -r requirements.txt
```

## Set Values for Externalized Variables
To enhance security and flexibility, it's advisable to externalize certain configuration variables, such as **SECRET_KEY**, **DEBUG**, **ALLOWED_HOSTS**, and **TIME_ZONE**. You can achieve this using a library called `python-decouple`. First, install it using pip:

```
pip install python-decouple
```

Now, create a .env file in your project's root directory and specify the values for these variables:

**DO NOT PUT QUOTES BETWEEN THE VALUES!**

```
SECRET_KEY = my-secret-key-value

# Set DEBUG to True for development, False for actual use
DEBUG = False

# ALLOWED_HOSTS is a comma-separated list of hosts that can access the app.
# You can use wildcard chars (*) and IP addresses. Use * for any host.
ALLOWED_HOSTS = *.ku.th, localhost, 127.0.0.1, ::1

# Your timezone
TIME_ZONE = Asia/Bangkok
```

Now replace the my-secret-key-value with the actual secret key value

You can create a secret key using:
```
from django.core.management.utils import get_random_secret_key

secret_key = get_random_secret_key()
```

## Run Migrations
To set up the database schema, perform database migrations as follows:
```
python manage.py makemigrations polls
python manage.py migrate polls
```
This will create the necessary database tables based on your Django models.

## Run Tests
Before proceeding, it's crucial to ensure that your application functions correctly. Run tests to validate its behavior:
```
python manage.py test polls
```
This will execute the test suite for your 'polls' app.

## Install data from the data fixtures

```

```
## Running the Django Application
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
