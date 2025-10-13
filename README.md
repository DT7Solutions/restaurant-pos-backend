# restaurant-pos-backend

1. Clone the project
2. Create the virtual env -> python3 -m venv venv
3. Install the requirements.txt file ->
        pip freeze > requirements.txt
        pip install -r requirements.txt
4. Collect all the static files -> python3 manage.py collectstatic
5. Migrate all the basic tables -> python3 manage.py migrate
6. Run the server -> python3 manage.py runserver
7. Open any browser and visit the localhost:8000/


env activate
*-------------*
1.pip install virtualenv
2.python -m venv env-pos
3.env-pos\Scripts\activate

python ../manage.py startapp 