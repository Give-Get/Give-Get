"""
handles all database interaction
"""

from pymongo import MongoClient
from math import radians, sin, cos, sqrt, atan2


MONGO_URI = "mongodb+srv://praj:praj@give-and-get-data.undmkkl.mongodb.net/?appName=Give-and-Get-Data"

client = MongoClient(MONGO_URI)
db = client['HackPSU-User-Data']
users = db.users
orgs = db.organizations
app_stats = db.app_statistics 



'''---------------- DATABASE UTILITY FUNCTIONS ---------------'''

def update_database(id:str, new_json:dict, type:str):
    """
    id: id of user or org you want to change in users or orgs database
    type: is equal to either "users" or "organizations"
    """
    collection = db.users if type == "users" else db.organizations

    # Ensure the new JSON includes the same _id
    if "_id" not in new_json:
        new_json["_id"] = id

    result = collection.replace_one({"_id": id}, new_json, upsert=True)
    return f"Updated {result.modified_count} document(s)."


def update_user(id:str, new_json:dict):
    """
    id: id of user you want to change in users database
    things_changed: dictionary with changes you wish to make in ket,value format
    """
    update_database(id, new_json, "users") 
    return

def update_organization(id:str, new_json:dict):
    """
    id: id of org you want to change in orgs database
    things_changed: dictionary with changes you wish to make in ket,value format
    """
    update_database(id, new_json, "organizations")
    return

def create_user(new_json, id=None):
    """
    new_json: the json for the new user
    id: will be a num if called by create_org()
    """
    if not id:
        id = generate_id()
    
    update_user(id, new_json)

    pass

def create_organization(new_json):
    """
    """
    id = generate_id()

    update_organization(id, new_json)

    pass

def generate_id():
    
    return

def add_user_and_org(type, object_json):
    
    return

def collect_user(id:str):
    """
    id: id of user you want to in users database
    things_changed: dictionary with changes you wish to make in ket,value format
    """
    collection = db.users
    user = collection.find_one({"_id": id})
    if user:
        return user
    else:
        raise ValueError(f"User with id {id} not found")

def collect_organization(id:str):
    """
    id: id of org you want to change in orgs database
    things_changed: dictionary with changes you wish to make in ket,value format
    """
    collection = db.organizations
    organization = collection.find_one({"_id": id})
    if organization:
        return organization
    else:
        raise ValueError(f"User with id {id} not found")

def get_orgs_within_radius(location, radius, org_type = None):
    """
    location: {"lat": 0, "long": 0} <----- is actually the location of the donor, will need to add location entry to user 
    radius: (miles)
    org_type: type of organization you want to query: none by default
    """
    lat, lon = location['lat'], location['long'] 
    all_orgs_dict = db.organizations.find()

    orgs_within_radius = []
    for org in all_orgs_dict:
        org_lat, org_lon = get_org_coords(org)
        if calculate_distance(lat, lon, org_lat, org_lon) < radius:
            orgs_within_radius.append(org)

    if not org_type:
        return orgs_within_radius
    else: 
        return [o for o in orgs_within_radius if o['type'][org_type] == True]


def get_org_coords(org_dict):
    if not isinstance(org_dict,dict):
        return None
    
    lat = org_dict['location']['lat']
    lon = org_dict['location']['lon']
    return lat, lon


def calculate_distance(lat1, lon1, lat2, lon2):
    R = 3958.8  # Earth radius in miles
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat/2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon/2)**2
    return R * 2 * atan2(sqrt(a), sqrt(1 - a))



def order_by_matching():

    return


