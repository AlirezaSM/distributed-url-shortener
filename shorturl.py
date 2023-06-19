from pymongo import MongoClient
from os import getenv
from flask import Flask, request, redirect
from string import digits, ascii_letters
from secrets import choice
from datetime import datetime
from yaml import Loader, load


# Load config.yml file
cfg = load(open("config.yml", "r"), Loader=Loader)

# Global constants
host_address = '0.0.0.0'
max_redirect_len = 4
alphabet = digits + ascii_letters
expiration_time = int(cfg["expiration"])    # In seconds

# Connect to the MongoDB
connection_string = f'mongodb://{cfg["db_username"]}:{cfg["db_password"]}@{cfg["db_address"]}'
mongo_client = MongoClient(connection_string)
db = mongo_client['URLs']
redirects = db.redirects

app = Flask(__name__, template_folder='/app/templates/')

@app.route('/')
def index():
    return "Hello, I'm a URL Shortener :)\n"

@app.route('/<path:path>', methods=['GET'])
def path_redirect(path):
    global redirects
    global expiration_time

    redirect_path = redirects.find_one({'path_from': path})

    if not redirect_path:
        return "404 Not Found\n"
    else:
        updated_at = redirect_path['updated_at']
        passed_time = (datetime.now() - updated_at).seconds
        print("passed time: ", passed_time)
        if passed_time > expiration_time:
            return "Your link expired, register again!\n"
        else:
            
            return redirect(redirect_path["path_to"], code=302)

@app.route('/register', methods=['POST'])
def register_path():
    global max_redirect_len
    global redirects
    global expiration_time
    
    path_to = request.form["u"]
    existing_redirect = redirects.find_one({'path_to':path_to})

    if existing_redirect:
        
        updated_at = existing_redirect['updated_at']
        passed_time = (datetime.now() - updated_at).seconds
        
        if passed_time > expiration_time:
            # Delete the previous one
            redirects.delete_one(existing_redirect)
            
            # Regenerating the shortened url
            path_from = ''.join([choice(alphabet) for i in range(max_redirect_len)])
        
            while redirects.find_one({'path_from':path_from}):
                path_from = ''.join([choice(alphabet) for i in range(max_redirect_len)])

            redirects.insert_one({'path_from':path_from, 'path_to':path_to, 'updated_at': datetime.now()})
            return f'URL for {path_to} updated to --> /{path_from}\n'
        else:
            return f'URL for {path_to} already exists at /{existing_redirect["path_from"]}\n'

    else:
        path_from = ''.join([choice(alphabet) for i in range(max_redirect_len)])
        
        while redirects.find_one({'path_from':path_from}):
            path_from = ''.join([choice(alphabet) for i in range(max_redirect_len)])

        redirects.insert_one({'path_from':path_from, 'path_to':path_to, 'updated_at': datetime.now()})

        return f'URL created for {path_to} at /{path_from}\n'

if __name__ == '__main__':
    app.run(host=host_address, port=int(cfg["port"]))