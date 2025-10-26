"""
handles all database interaction
"""

from pymongo import MongoClient
from math import radians, sin, cos, sqrt, atan2


MONGO_URI = "mongodb+srv://praj:praj@give-and-get-data.undmkkl.mongodb.net/?appName=Give-and-Get-Data"

client = MongoClient(MONGO_URI)
db = client['HackPSU-User-Data']
users = db.users
orgs = db.orgs
app_stats = db.app_statistics 



'''---------------- DATABASE UTILITY FUNCTIONS ---------------'''

def update_database(id:str, new_json:dict, type:str):
    """
    id: id of user or org you want to change in users or orgs database
    type: is equal to either "users" or "organizations"
    """
    return

def update_users(id:str, new_json:dict):
    """
    id: id of user you want to change in users database
    things_changed: dictionary with changes you wish to make in ket,value format
    """
    update_database(id, new_json, "users") #change "new_json" from the new_json parameter when done with func
    return

def update_organizations(id:str, new_json:dict):
    """
    id: id of org you want to change in orgs database
    things_changed: dictionary with changes you wish to make in ket,value format
    """
    update_database(id, new_json, "organizations") #change "new_json" from the new_json parameter when done with func
    return

def create_user(id):

    pass

def create_org(id):
    
    pass

def add_user_and_org(type, object_json):
    
    return



def collect_from_database(id:str, type:str):
    """
    id: id of user or org you want to change in users or orgs database
    type: is equal to either "users" or "organizations"
    """
    return

def colleect_users(id:str):
    """
    id: id of user you want to in users database
    things_changed: dictionary with changes you wish to make in ket,value format
    """
    collect_from_database(id, "users") #change "new_json" from the new_json parameter when done with func
    return

def collect_organizations(id:str):
    """
    id: id of org you want to change in orgs database
    things_changed: dictionary with changes you wish to make in ket,value format
    """
    collect_from_database(id, "organizations") #change "new_json" from the new_json parameter when done with func
    return

def get_orgs_within_radius(location, radius, org_type = None):
    """
    location: {"lat": 0, "long": 0} <----- is actually the location of the donor, will need to add location entry to user 
    radius: (miles)
    org_type: type of organization you want to query: none by default
    """
    lat, lon = location['lat'], location['long'] 
    all_orgs_dict = list(db.organizations.find())[0]

    orgs_within_radius = []
    for org_id, org_dict in all_orgs_dict.items:
        org_lat, org_lon = get_org_coords(org_dict)
        if calculate_distance(lat, lon, org_lat, org_lon) < radius and not None:
            orgs_within_radius.append(org_dict)

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


