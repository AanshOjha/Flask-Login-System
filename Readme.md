# About This Project :
> It creates a fully functional Login page
- 2 Tier Architecture (Frontend - Python {Flask}, Backend - Mysql)
- Includes Sign Up, Login, Home Page
- It's `Reuseable` : You Pass in secrets using a Env File

# Features
- Recive Password Reset Emails via Zoho
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
   ```sh
   sudo apt install python3.8-venv
   python3 -m venv venv
   source venv/bin/activate
   ```
4. Install the modules
```sh
pip install -r requirements.txt
```
5. Configure MySQL
```sh
sudo apt install mysql-server -y
sudo systemctl start mysql
sudo systemctl enable mysql
sudo mysql_secure_installation
```
Follow the on-screen instructions.

6. Set MySQL password
```sh
sudo mysql -u root
ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY 'your_new_password';
FLUSH PRIVILEGES;
EXIT;
```
7. Afer this, login to MySQL (Just to check MySQL is configured properly.)
```sh
mysql -u root -p
```
Don't forget to `exit;` MySQL :)

8. Configure [OS environment variables](#using-os-environment-variables) `EMAIL_ID` and `EMAIL_PASS` which are used to send emails of resetting password.

9. Configure nginx
```
sudo apt install nginx
```
```
sudo nano /etc/nginx/sites-available/default
```
Enter this code here:
```
server {
    listen 80;
    server_name your_domain_or_ip;

    location / {
        proxy_pass http://localhost:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```
Ctrl+X, Y, Enter
```
sudo nginx -t
sudo service nginx restart
```
I don't know why but port 5000 don't work <3!

10. Little change in run.py:
```
from flaskalbum import app

if __name__ == '__main__':
    app.run(debug=True, port=8080)
```

### Now run the run.py file...
### Hopefully your website will be visible in your VM's public ip address.

## For Version 2.0
Session id stored in Redis
Hosted in AWS
OTP based auth 


Lots Of Efforts from my side 💖 🥵
