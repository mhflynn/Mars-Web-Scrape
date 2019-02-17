from flask import Flask, render_template, redirect
from pymongo import MongoClient
from pymongo import errors as pymerr
import scrape_mars as sm

# Start Flask server
app = Flask(__name__)

# Establish database connection
client = MongoClient('mongodb://localhost:27017', serverSelectionTimeoutMS=3000)
db = client.mars_data

# Common error message string if no database connection
dberr = 'Error : No Mongo database connection available. Please start Mongo engine.'

# Clear database for first update, drop mars_info collection
try :
    db.mars_info.drop()
    
except pymerr.ServerSelectionTimeoutError :
    print('Initialization', dberr)


@app.route('/')
def index():
    # Get latest entry for Mars data
    try :
        data = db.mars_info.find_one()   # Only one entry in mars_info collection

    except pymerr.ServerSelectionTimeoutError :
        data = {'news':False}  
        print('Root (/)', dberr)
        
    return render_template("index.html", data=data)


@app.route('/scrape')
def scraper():
    # Update Mars data with scrape function
    doc = sm.scrape_mars()

    # Update Mars database with latest Mars data
    try :
        db.mars_info.replace_one({}, doc, upsert=True)
        
    except pymerr.ServerSelectionTimeoutError :
        print('/scrape', dberr)
        
    return redirect('/', code=302)


@app.route('/clear')
def clear():
    # Clear current Mars data collection
    try :
        db.mars_info.drop()
        
    except pymerr.ServerSelectionTimeoutError :
        print('/clear', dberr)
        
    return redirect('/', code=302)


if __name__ == '__main__':
    app.run(debug=True)
