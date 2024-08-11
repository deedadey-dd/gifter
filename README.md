## Introduction

Gifter is an e-comerce website that uses the development of wishlists 
to create an avenue for people to gift their loved ones with the exact items they want. 


The site opens with a store with products that can be PURCHASED at once or 
GIFTED to other users who have created WISHLISTS. 


These products are posted there by VENDORS

The website is built on the django framework of with modules that have been compiled in requirements.txt
After installing the modules in the requirements.txt, the platform can be run using its 'manage.py runserver'


## Features
User registration and authentication
Create and manage wishlists
Add items to wishlists from various e-commerce sites
Share wishlists with friends and family
Place orders for wishlist items
Manage orders and delivery
Technologies Used
Django
Bootstrap (for front-end styling)
SQLite (default database, can be changed as per need)
Prerequisites
Python 3.6+
Django 3.2+
Virtualenv (recommended)


Installation
### 1. Clone the repository

### 2. Set up a virtual environment
It's recommended to use a virtual environment to manage dependencies. You can set up a virtual environment using venv or virtualenv.

Using venv (Python 3.6+):

python -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`
Using virtualenv:

virtualenv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`

### 3. Install dependencies
pip install -r requirements.txt

### 4. Set up the database
Apply the migrations to set up the database:

python manage.py makemigrations
python manage.py migrate

### 5. Creating new users
Because Authentication is done via email and phone verifications you could create users and 
manually go into the database to retrieve the pin since the environment variables needed
to make those requests work are not included (email sending and phone text message sending)

However, for testing purposes, 
an ordinary user account has been set up with the following credentials
username: user1
password: gifted1234

a vendor has been created with the following credentials
username: vendor1
password: gifted1234


Althernatively, you could create a superuser and used that to add users\

python manage.py createsuperuser

### 6. Run the development server
Start the Django development server:

python manage.py runserver
You can now access the application at http://127.0.0.1:8000/.

### Project Structure
```markdown
de_gifter/
├── de_gifter/
│   ├── __init__.py
│   ├── asgi.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── manage.py
├── db.sqlite3
├── main/
│   ├── migrations/
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── forms.py
│   ├── models.py
│   ├── tokens.py
│   ├── urls.py
│   ├── views.py
│   └── static/
│       └── css/
│           └── styles.css
│   └── templates/
│       ├── register.html
│       ├── login.html
│       ├── index.html
│       └── all_other_html_files/
├── media/
│   └── images/
│       └── greencheck.svg
│   └── items/
│       └── uploads/
│           └── profiles/
│               └── profile_pictures/
│   └── vendors/
├── store/
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── forms.py
│   ├── models.py
│   ├── tests.py
│   ├── urls.py
│   ├── views.py
│   └── templates/
│       └── store/
│           ├── checkout.html
│           ├── product_detail.html
│           ├── product_list.html
│           └── other_html_files/
└── requirements.txt
```

## Contributing
We welcome contributions to gifter! To contribute:

Fork the repository
Create a new branch (git checkout -b feature/your-feature-name)
Make your changes
Commit your changes (git commit -m 'Add some feature')
Push to the branch (git push origin feature/your-feature-name)
Create a pull request
License
This project is licensed under the MIT License - see the LICENSE file for details.

Contact
If you have any questions or suggestions, feel free to contact us at deedadey@gmail.com.

This README provides a clear guide for other developers to understand, set up, and contribute to the de_gifter project. Adjust the links, contact details, and other placeholders as necessary to fit your specific project and needs.

