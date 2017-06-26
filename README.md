# Business Analytics Tool

Default db located Userdata dir 
```
.superset/superset.db
```

if you use Superser before and database exist maybo conflict with exist in database user by unique email

# Installation & Configuration
```
git clone https://github.com/codesmart-co/bit
cd bit
```

# Venv
```
virtualenv venv

# or if use Python 3 from box 
python -m venv

# Linux 
source venv/bin/activate
pip install -r requirements.txt

# Windows
cd venv/Scripts & activate & cd ../..
pip install -r windows\requirements.txt
pip install -r requirements.txt
```

# Initialization
```
# Create an admin user (you will be prompted to set username, first and last name before setting a password)
fabmanager create-admin --app superset


# 1 Migrations
python bit db migrate

# 2 Initialize the database
python bit db upgrade



# Initialize the database
# python bit db init

# Upgrade the database
# python bit db upgrade

# Create default roles and permissions
# python bit init

# Load some data to play with
# python bit load_examples
```

# Run server
```
# Linux 
# Start the web server on port 8088, use -p to bind to another port
python bit runserver
```

```
# Please note that gunicorn, Superset default application server, does not work on Windows
# so you need to use the development web server.
# The development web server though is not intended to be used on production
# systems so better use a supported platform that can run gunicorn.
```

```
# Windows OR development web server, use the -d switch

python bit runserver -d
```
