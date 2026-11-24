SHOPEASE - UPDATED DJANGO SHOPPING WEBSITE

This version automatically creates a starter catalogue of sample products the first time the homepage is opened on an empty database. Product images load from Unsplash over the internet. You can later edit/add/remove products in Django Admin.

SETUP
1. Extract this ZIP file.
2. Open the extracted shoppingProject folder in PyCharm (the folder containing manage.py).
3. Configure a Python interpreter / virtual environment in PyCharm.
4. Open the PyCharm Terminal in the folder containing manage.py.
5. Install packages:
   python -m pip install -r requirements.txt
6. Create/update database migrations:
   python manage.py makemigrations myapp
7. Apply database migrations:
   python manage.py migrate
8. Create an admin login (skip if you already created one):
   python manage.py createsuperuser
9. Start the website:
   python manage.py runserver
10. Open http://127.0.0.1:8000/ in Chrome.

The sample catalogue is inserted automatically if there are no products in the database. If you already have products, they are kept and the sample catalogue is not added. Product images need an internet connection.

Admin: http://127.0.0.1:8000/admin/
The checkout is a demonstration only. It records orders but does not process real payments.
