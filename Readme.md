# About This Project :
> It creates a fully functional Login page
- 2 Tier Architecture (Frontend - Python {Flask}, Backend - Mysql)
- Includes Sign Up, Login, Home Page
- It's `Reuseable` : You Pass in secrets using a Env File

# For Docker Container to Container
* `MYSQL_HOST` value 
1. For local development: `localhost`
2. For docker container to host: `host.docker.internal`
3. For docker container to container: `mysql_cn`
* First, create a .env file and load these environment variables according to you.
```env
EMAIL_ID=
EMAIL_PASS=
MYSQL_HOST=mysql_cn
MYSQL_USER=root
MYSQL_ROOT_PASSWORD=password
FULLSTACK_DB=full_stack
FULLSTACK_CRED_TABLE=creds
```
* Then run this in terminal one-by-one, **For Docker container to container**
```console
docker network create aansh-net
docker run --name mysql_cn -e MYSQL_ROOT_PASSWORD=password --rm --network aansh-net mysql
docker build . -t flask-app
docker run -p 5000:5000 --name flask_cn --env-file .\.env --rm --network aansh-net flask-app
```

* * Run these commands one-by-one, **For docker container to host**
```console
docker build . -t flask-app
docker network create aansh-net
docker run -p 5000:5000 --name flask-cn --env-file .\.env --rm --network aansh-net flask-app
```

* to stop `docker stop flask_cn mysql_cn` then `docker container prune`

# Features
- Recieve Password Reset Emails via Zoho
- Cam delete account, which deletes your details from the database
- Password Reset Link Valid for Only 10 min 
- Passwords are stored as Hash values in the Database
- Displays Your Provided Username after Login
- Can change Username, Email, name after login - Displays Changed Attributes instantly !
- If you try to directly visit homepage (without logging in) 'http://domain-name/home' Redirects you to login Page 'http://domain-name/login'

# Pre-Requisites
1. You must have MySQL installed in your machine.
2. First install all python libraries listed in requirements.txt
3. You need an `Zoho` Account to test `Reset Password` Feature !
4. Then create a .env file and load these environment variables according to you.
```env
EMAIL_ID=
EMAIL_PASS=
MYSQL_HOST=
MYSQL_USER=
MYSQL_PASS=
FULLSTACK_DB=
FULLSTACK_CRED_TABLE=
```
5. Run configs.envconfig.py file to load env variables in system.
6. Run mysql-config to configure database and tables.
7. Then run run.py to use the awesome app!


## Table of Contents
1. [Modules Required](requirements.txt)
2. [Using OS Environment Variables](#using-os-environment-variables)
3. [MySQL Connection](mysql-config.py)
4. [Hosting in Ubuntu VM](#hosting-in-ubuntu-vm)


## Using OS Environment Variables

I have used OS Environment Variables in many places like, specifying email, password, MySQL connection variables, etc.

To use OS Environment Variables,
1. Install and import `python-dotenv` module.
2. Create a file named ".env" in root directory.
3. Declare all variables related to email and MySQL.
4. Now run envconfig.py to declare the OS Environment Variables.

> Advantage of doing this- If you wish to change the name of DB, table, email, etc anything, only change the name in ".env" file!
>> Note: If you change FULLSTACK_DB or FULLSTACK_CRED_TABLE, you have to run mysql-config.py again.

### ⚠️ **Warning**
Don't know why but Flask-MySQLdb module does not installs in VM without virtual environment. 
Take care! This has taken my hours of sleep 🥲


## Hosting in Ubuntu VM
1. Git clone this repository.
2. Go to the folder
3. Create virtual environment
   ```console
   sudo apt update
   sudo apt install python3.12-venv
   python3 -m venv venv
   source venv/bin/activate
   ```
4. Install the modules
5. Error: failed to build wheel. 
how to fix: 
```console
sudo apt update
sudo apt install pkg-config
```
6. Install libraries
```sh
pip install -r requirements.txt
```

7. Install and configure AWS 
```console
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install
aws configure
```

8. Get AWS access IDs and others. Do as prompted.
9. `python run.py`