# Library API
Using Django and Django Rest Framework, I developed this library_api app

## What I learned ?
* Django and Djangos ORM
* Django Rest Framework
* Django URLs
* Django Knox
* Django Signals
* Class-Based Views and Mixins to Change Default beahviour
* Some Opinionated Architecture Decision
* Django User-Model and How to Make Custom One

## Docker Image
You can use the docker Image  
Image is Hosted on dockerhub @ consumedking/library_api
```
(sh) docker container run consumedking/library_api
```

## CLI Setup
### Installation
```
git clone <link-here> library_api
cd library_api
python3 -m venv .venv
source ./.venv/bin/activate
pip install -r requirements.txt
```

### Start Server
```
(.venv) python3 manage.py runserver
```

## Models
* User-Model
    * PATRON
    * AUTHOR
* Books
* Categories
* Profile Tables for Different types of users

## Endpoints
> login/ 

>signup/

>logut/

>logoutall/

