#!/usr/bin/env python3
import urllib3, json, certifi, base64, os, pyqrcode
from flask import send_file, make_response
from bson import ObjectId
from random import randint
import png, pyqrcode, zipfile, random
from os.path import basename
import random, hashlib, boto3
import requests
import time
import smtplib
import email.message
import operator
import shutil

from Crypto.Cipher import PKCS1_OAEP
from Crypto.PublicKey import RSA
from Crypto import Random

from firebase_admin import messaging
import firebase_admin

from constants_model_related import *
from payment_related import *
from rsa_methods import *
#########################################################################################
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/home/btech/jungle/arart-1560780743449-firebase-adminsdk-ktj6v-a636fdb7cd.json"
# print os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')
default_app = firebase_admin.initialize_app()



FORGET_PASSWORD_COLLECTION = "forget_pswd"

THUMBNAILS = {
        "food"          : "https://jediar.s3.amazonaws.com/food_thumbnail.JPG",
        "architecture"  : "https://jediar.s3.amazonaws.com/architecture_thumbnail.jpg",
        "decor"         : "https://jediar.s3.amazonaws.com/decor_thumbnail.jpg",
        "fashion"       : "https://jediar.s3.amazonaws.com/fashion_thumbnail.jpg",
        "equipment"     : "https://jediar.s3.amazonaws.com/equipment_thumbnail.jpg",
        "vehicle"       : "https://jediar.s3.amazonaws.com/vehicle_thumbnail.jpg",
        "interior"      : "https://jediar.s3.amazonaws.com/interior_thumbnail.jpg",
        "plant"         : "https://jediar.s3.amazonaws.com/plant_thumbnail.jpg",
        "electronics"   : "https://jediar.s3.amazonaws.com/electronics_thumbnail.jpg",
        "aircraft"      : "https://jediar.s3.amazonaws.com/aircraft_thumbnail.jpg"
        }
#########################################################################################

def isValidAppId(app_id):
    app_name = ""
    if app_id:
        if app_id == JEDI_APP:
            app_name = JEDI_APP
        elif app_id == ARART_APP:
            app_name = ARART_APP
        return app_name
    else:
        return app_name
#########################################################################################

def get_org_categories(app_id, namespace, DB_NEW_MODELS):
    '''
        Return the org's category names, thumbnails
    '''
    RETURN_LIST = []
    categories = []

    # get all categories
    collections = get_all_collections(DB_NEW_MODELS)

    # set format
    if app_id == JEDI_APP:
        FORMAT = ".scn"
    elif app_id == ARART_APP:
        FORMAT = ".sfb"
    else:
        print("Invalid app id, get_org_categories, get_org_categories method")
        return 0

    # traverse each category and check if org is owner of any model of this categories
    for collection in collections:
        response = DB_NEW_MODELS[collection].find({"$and": [{"owner_id": namespace}, {"format": FORMAT}]}, {"analytics.survey": 0})
        if response.count() > 0:
            # append in categories list
            categories.append(collection)

  
    if len(categories) > 0:
        for category in categories:
            # print(category)
            if CategoryThumbnails[category]:
                RETURN_ITEMS = {}
                RETURN_ITEMS["thumbnail"] = CategoryThumbnails[category]
                category_name = category.capitalize()
                RETURN_ITEMS["category_name"] = category_name

                RETURN_LIST.append(RETURN_ITEMS)
            else:
                print("No thumbnail found, check constants_model_related, get_org_categories method")
                return 0

        return RETURN_LIST
    else:
        return RETURN_LIST

#########################################################################################

def get_top_categories(app_id, DB_NEW_MODELS):
    CATEGORY_THUMBNAIL  = "https://jediar.s3.amazonaws.com/food_thumbnail.JPG"
    ARCH_THUMBNAIL      = "https://jediar.s3.amazonaws.com/architecture_thumbnail.jpg"
    DECOR_THUMBNAIL     = "https://jediar.s3.amazonaws.com/decor_thumbnail.jpg"
    FASHION_THUMBNAIL   = "https://jediar.s3.amazonaws.com/fashion_thumbnail.jpg"
    EQUIPMENT_THUMBNAIL = "https://jediar.s3.amazonaws.com/equipment_thumbnail.jpg"
    ELECTRONICS_THUMBNAIL = "https://jediar.s3.amazonaws.com/electronics_thumbnail.jpg"
    PLANT_THUMBNAIL     =   "https://jediar.s3.amazonaws.com/plant_thumbnail.jpg"

    
    RETURN_LIST     =   []

    RETURN_ITEMS    =   {}
    RETURN_ITEMS["thumbnail"]   =   CATEGORY_THUMBNAIL
    RETURN_ITEMS["category_name"]    =   "Food"

    RETURN_LIST.append(RETURN_ITEMS)
    RETURN_ITEMS    =   {}
    RETURN_ITEMS["thumbnail"]        =   ARCH_THUMBNAIL
    RETURN_ITEMS["category_name"]    =   "Architecture"

    RETURN_LIST.append(RETURN_ITEMS)
    RETURN_ITEMS    =   {}
    RETURN_ITEMS["thumbnail"]   =   DECOR_THUMBNAIL
    RETURN_ITEMS["category_name"]    =   "Decor"

    RETURN_LIST.append(RETURN_ITEMS)
    RETURN_ITEMS    =   {}
    RETURN_ITEMS["thumbnail"]   =   PLANT_THUMBNAIL
    RETURN_ITEMS["category_name"]    =   "Plant"

    RETURN_LIST.append(RETURN_ITEMS)
    RETURN_ITEMS    =   {}
    RETURN_ITEMS["thumbnail"]   =   ELECTRONICS_THUMBNAIL
    RETURN_ITEMS["category_name"]    =   "Electronics"

    RETURN_LIST.append(RETURN_ITEMS)
    # if app_id == "jedi":
    #     RETURN_ITEMS    =   {}
    #     RETURN_ITEMS["thumbnail"]   =   CATEGORY_THUMBNAIL
    #     RETURN_ITEMS["category_name"]    =   "food"

    #     RETURN_LIST.append(RETURN_ITEMS)
    #     RETURN_ITEMS    =   {}
    #     RETURN_ITEMS["thumbnail"]        =   ARCH_THUMBNAIL
    #     RETURN_ITEMS["category_name"]    =   "architecture"

    #     RETURN_LIST.append(RETURN_ITEMS)
    #     RETURN_ITEMS    =   {}
    #     RETURN_ITEMS["thumbnail"]   =   DECOR_THUMBNAIL
    #     RETURN_ITEMS["category_name"]    =   "decor"

    #     RETURN_LIST.append(RETURN_ITEMS)
    # elif app_id == "ar_art":
    #     RETURN_ITEMS    =   {}
    #     RETURN_ITEMS["thumbnail"]   =   CATEGORY_THUMBNAIL
    #     RETURN_ITEMS["category_name"]    =   "fashion"

    #     RETURN_LIST.append(RETURN_ITEMS)

    return RETURN_LIST
#########################################################################################

def get_popular_models_helper(namespace, app_id, COLLECTION, DB_NEW_MODELS, DB_USERS, DB_ANALYTICS):
    #if valid user namespace
    if isValidNamespace(namespace, DB_USERS):
                
        all_collections =  all_collections = get_all_collections(DB_NEW_MODELS)
        #set format
        if app_id == JEDI_APP:
            FORMAT = ".scn"
        elif app_id == ARART_APP:
            FORMAT = ".sfb"
        else:
            return json.dumps({"message": "Invalid app id"}), 400, {'ContentType': 'application/json'}


        FINAL_RETURN = []
        RETURN_ITEMS = []
        temp_diction = {}

        for COLLECTION in all_collections:        
            response = DB_NEW_MODELS[COLLECTION].find({"$and":[{"format": FORMAT},{"tested_status":1}]})
            for res in response:
                model_id = str(res["_id"])
                del res["_id"]
                temp_diction[model_id] = res["analytics"]["search_appearances"]


        sorted_temp_diction = sorted(temp_diction.items(), key=operator.itemgetter(1), reverse=True)

        count = 0
        for val in sorted_temp_diction:
            RETURN_ITEMS.append(val[0])
            if count >= 4:
                break
            count += 1

        for model in RETURN_ITEMS:
            FINAL_RETURN.append(search_model_by_id(namespace, model, COLLECTION, DB_NEW_MODELS, DB_ANALYTICS))

        TOP_CATEGORIES = get_top_categories(app_id, DB_NEW_MODELS)

        return json.dumps({"message": FINAL_RETURN, "popular_categories": TOP_CATEGORIES}), 200, {'ContentType': 'application/json'}
    elif isValidOrgNamespace(namespace, DB_USERS):
        return org_popular_models_helper(namespace, app_id, COLLECTION, DB_NEW_MODELS, DB_USERS, DB_ANALYTICS)
    else:
        return json.dumps({"message": "Invalid namespace"}), 400, {'ContentType': 'application/json'}
#########################################################################################

def org_popular_models_helper(namespace, app_id, COLLECTION, DB_NEW_MODELS, DB_USERS, DB_ANALYTICS):
    if isValidOrgNamespace(namespace, DB_USERS):

        all_collections =  all_collections = get_all_collections(DB_NEW_MODELS)

        if app_id == JEDI_APP:
            FORMAT = ".scn"
        elif app_id == ARART_APP:
            FORMAT = ".sfb"
        else:
            return json.dumps({"message": "Invalid app id"}), 400, {'ContentType': 'application/json'}
        

        FINAL_RETURN = []
        RETURN_ITEMS = []
        temp_diction = {}

        for COLLECTION in all_collections:
            response = DB_NEW_MODELS[COLLECTION].find({"$and": [{"owner_id": namespace}, {"format": FORMAT}]})
            for res in response:
                model_id = str(res["_id"])
                del res["_id"]
                temp_diction[model_id] = res["analytics"]["search_appearances"]


        sorted_temp_diction = sorted(temp_diction.items(), key=operator.itemgetter(1), reverse=True)

        count = 0
        for val in sorted_temp_diction:
            RETURN_ITEMS.append(val[0])
            if count >= 5:
                break
            count += 1

        for model in RETURN_ITEMS:
            FINAL_RETURN.append(search_model_by_id(namespace, model, COLLECTION, DB_NEW_MODELS, DB_ANALYTICS))

        # ALL_MODELS = search_all_models_method("rf2081", COLLECTION, DB_NEW_MODELS, DB_USERS)
        # TOP_CATEGORIES = get_top_categories(app_id, DB_NEW_MODELS)
        TOP_CATEGORIES = get_org_categories(app_id, namespace, DB_NEW_MODELS)
        return json.dumps({"message": FINAL_RETURN, "popular_categories": TOP_CATEGORIES}), 200, {'ContentType': 'application/json'}
    else:
        return json.dumps({"message": "Invalid org id"}), 400, {'ContentType': 'application/json'}
#########################################################################################

def send_email(USER_EMAIL):
    try:
        msg = email.message.Message()
        msg[SUBJECT] = "Download the amazing jedi app!"
        msg[FROM] = EMAIL_FROM
        msg[TO] = USER_EMAIL
        msg.add_header(CONTENT_TYPE, TEXT_HTML)
        
        body = "".join([DEAR, EMAIL_BODY, EMAIL_SIGNATURE])

        msg.set_payload(body)
        s = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        s.ehlo()
        s.starttls()
        s.ehlo()
        s.login(EMAIL_LOGIN,EMAIL_PASSWD)
        s.sendmail(msg[FROM], [msg[TO]], msg.as_string())
        s.quit()
        return True
    except Exception as e:
        print ("".join(["Exception in send_email: ", str(e)]))
        return False
#########################################################################################

def insert_in_payments_db(namespace, model_id, amount, currency, token, charge, DB_PAYMENTS):
    CHARGES_COLLECTION = "charges"

    charge_id =         str(charge["id"])
    receipt_number =    str(charge["receipt_number"])

    response = DB_PAYMENTS[CHARGES_COLLECTION].find({namespace: {'$exists': 1}}).count()

    INSERT_ITEMS = {}
    INSERT_ITEMS["model_id"] =      model_id
    INSERT_ITEMS["amount"] =        amount
    INSERT_ITEMS["currency"] =      currency
    INSERT_ITEMS["token"] =         token
    INSERT_ITEMS["timestamp"] =     int(time.time())
    INSERT_ITEMS["receipt_id"] =    receipt_number

    INSERT_CHARGE = {}
    INSERT_CHARGE[charge_id] = INSERT_ITEMS
    
    if response:
        # user already exists - jedi has payment record of this user
        DB_PAYMENTS[CHARGES_COLLECTION].update({namespace: {'$exists': 1}},
                                    {'$set': {str(namespace+"."+charge_id): INSERT_ITEMS}})
        return True
    elif response == 0:
        # user doesn't exist - it's user's first payment
        DB_PAYMENTS[CHARGES_COLLECTION].insert({namespace: INSERT_CHARGE})
        return True
#########################################################################################
def get_collection_name(model_id, DB_NEW_MODELS):
    RETURN_COLLECTION_NAME = ""
    all_collections = DB_NEW_MODELS.collection_names()
    print(all_collections)

    for collection in all_collections:
        temp_response = DB_NEW_MODELS[collection].find_one({"_id": ObjectId(model_id)})
        if temp_response:
            RETURN_COLLECTION_NAME = collection
            break

    return RETURN_COLLECTION_NAME
#########################################################################################



def charge_payment_helper(namespace, app_id, model_id, token, amount, currency, DB_USERS, 
                            DB_NEW_MODELS, collection, DB_PAYMENTS, DB_ANALYTICS):
    NOTIFICATION = "Payment for this model is successfull. Tap to preview model."
    print("in charge")

    # get collection name of the model id
    collection = get_collection_name(model_id, DB_NEW_MODELS)

    print(collection)

    if isValidNamespace(namespace, DB_USERS) and isValidAppId(app_id):
        if isValidModelId(model_id, DB_NEW_MODELS, collection):
            # decrypt token
            # decrypted_token = decrypt_token(token)
            print("valid model id")
            decrypted_token = token
            status, charge = stripe_charge(decrypted_token, charge_amount=(amount*100),
                                currency="usd", charge_descripton="sample description")
            if status: # payment successfull
                # insert in payments collection
                insert_in_payments_db(namespace, model_id, amount, currency,
                                        decrypted_token, charge, DB_PAYMENTS)
                # add in users_downloaded models
                add_model_in_user_downloads(namespace, model_id, DB_ANALYTICS)
                # update_downlaod_count (user)
                update_user_download_count(namespace, DB_USERS)
                # update_downlaod_count (user)
                update_model_download_count(model_id, DB_NEW_MODELS, collection)
                # send notifications
                send_push_notification_helper(app_id, namespace, NOTIFICATION, DB_USERS)

                return json.dumps({"message": "payment successfull!"}), 200, {'ContentType': 'application/json'}
            else:
                print(status)
                print(charge)
                return json.dumps({"message": charge}), 400, {'ContentType': 'application/json'}
        else:
            print("Invalid model id")
            return json.dumps({"message": "Invalid model id"}), 400, {'ContentType': 'application/json'}
    else:
        print("Invalid namespace/app_id")
        return json.dumps({"message": "Invalid namespace/app_id"}), 400, {'ContentType': 'application/json'}
#########################################################################################

def update_user_download_count(namespace, DB_USERS):
    USERS_COLLECTION = "users_data"

    try:
        DB_USERS[USERS_COLLECTION].update({"namespace": namespace}, {"$inc": {"model_downloads": 1}})
    except Exception as e:
        print(str(e))
        return False

    return True
#########################################################################################
#########################################################################################

def update_model_download_count(model_id, DB_NEW_MODELS, collection):
    try:
        DB_NEW_MODELS[collection].update({"_id": ObjectId(model_id)}, {"$inc": {"analytics.download_count": 1}})
    except Exception as e:
        print(str(e))
        return False

    return True
#########################################################################################

def add_model_in_user_downloads(namespace, model_id, DB_ANALYTICS):
    USER_DOWNLOADS_COLLECTION = "user_downloads"

    response = DB_ANALYTICS[USER_DOWNLOADS_COLLECTION].find({namespace: {'$exists': 1}}).count()

    if response == 0:
        # user_namespace not exists in collection
        insert_response = DB_ANALYTICS[USER_DOWNLOADS_COLLECTION].insert({namespace: [model_id]})
        return True
    else:
        # user_namespace exists in collection, push model_id in list
        insert_response = DB_ANALYTICS[USER_DOWNLOADS_COLLECTION].update(
                                                                    {namespace: {'$exists': 1}},
                                                                    {'$push': {namespace: model_id}}
                                                                    )
        return True
#########################################################################################

def decrypt_token(token):
    # get RSA private key
    try:
        private_key = RSA.import_key(open(PRIVATE_KEY_PATH, 'r').read())

        hex_token = bytearray.fromhex(token)

        decrypt = PKCS1_OAEP.new(key=private_key)
        decrypted_token = decrypt.decrypt(hex_token)
    except Exception as e:
        print ("Exception in decrypt_token method: "+str(e))
        return "Exception in decrypt_token method: "+str(e)

    return decrypted_token
#########################################################################################

def send_apns_notification(title, body, device_token):
    # [START apns_message]
    actions_list = ["new_notification", "order", "support"]

    message = messaging.Message(
        apns=messaging.APNSConfig(
            headers={'apns-priority': '10'},
            payload=messaging.APNSPayload(
                aps=messaging.Aps(
                    alert=messaging.ApsAlert(
                        title=title,
                        body=body,
                        loc_key=actions_list[1],
                        ),
                    #badge=42,
                    ),
                ),
            ),
        token=device_token,
    )
    # [END apns_message]
    response = messaging.send(message)
    if response:
        return True
    else:
        return False
##############################################################################
def send_android_notification(title, body, device_token):
    actions_list = ["new_notification", "order", "support"]

    message = messaging.Message(
        data={
            'title'     :   "Hello Testing",
            'body'      :   "testing by talha Umer did you recive notification",
            # 'loc_key'   :   actions_list[2],
        },
        token=device_token,
    )

    response = messaging.send(message)

    if response:
        return True
    else:
        return False
##############################################################################

def send_push_notification_helper(app_id, namespace, notification, DB_USERS):
    USERS_COLLECTION    =   "users_data"
    ORGS_COLLECTION     =   "organizations_data"

    isUser  =   isValidNamespace(namespace, DB_USERS)
    isOrg   =   isValidOrgNamespace(namespace, DB_USERS)

    if isUser:
        COLLECTION = USERS_COLLECTION
    elif isOrg:
        COLLECTION = ORGS_COLLECTION
    else:
        return json.dumps({"message": "Invalid namespace"}), 400, {'ContentType': 'application/json'}

    try:
        response = DB_USERS[COLLECTION].find_one({"namespace": namespace})

        app_name        =   response["token"]["app_id"]
        device_token    =   response["token"]["device_token"]
        del response["_id"]
        print(json.dumps(response))
        print(device_token)

    except Exception as e:
        return json.dumps({"message": str(e)}), 500, {'ContentType': 'application/json'}

    if app_name == "jedi":
        # send notification to iOS app
        notificationStatus = send_apns_notification("title", notification, device_token)
    elif app_name == "ar_art":
        # send notification to android app
        notificationStatus = send_android_notification("title", notification, device_token)
    else:
        return json.dumps({"message": "Invalid app name"}), 500, {'ContentType': 'application/json'}

    if notificationStatus:
        return json.dumps({"message": "success"}), 200, {'ContentType': 'application/json'}
    else:
        return json.dumps({"message": "notification not sent"}), 500, {'ContentType': 'application/json'}

#########################################################################################
def downloaded_models_helper(namespace, app_id, DB_ANALYTICS, DB_NEW_MODELS):
    USER_DOWNLOADS_COLLECTION = "user_downloads"
    RETURN_LIST = []

    download_response = DB_ANALYTICS[USER_DOWNLOADS_COLLECTION].find_one({namespace: {"$exists": 1}})
    if download_response:
        for model_id in download_response[namespace]:
            COLLECTION = get_collection_name(model_id, DB_NEW_MODELS)
            temp_res = search_model_by_id(namespace, model_id, COLLECTION, DB_NEW_MODELS, DB_ANALYTICS)
            if temp_res:
                if app_id == "jedi" and temp_res["format"] == ".scn":
                    RETURN_LIST.append(temp_res)
                if app_id == "ar_art" and temp_res["format"] == ".sfb":
                    RETURN_LIST.append(temp_res)

        return json.dumps({"message": RETURN_LIST}), 200, {'ContentType': 'application/json'}
    else:
        return json.dumps({"message": RETURN_LIST}), 200, {'ContentType': 'application/json'}

#########################################################################################
def get_all_categories_helper(namespace, app_id):
    CATEGORY_THUMBNAIL      = "https://jediar.s3.amazonaws.com/food_thumbnail.JPG"
    ARCH_THUMBNAIL          = "https://jediar.s3.amazonaws.com/architecture_thumbnail.jpg"
    DECOR_THUMBNAIL         = "https://jediar.s3.amazonaws.com/decor_thumbnail.jpg"
    FASHION_THUMBNAIL       = "https://jediar.s3.amazonaws.com/fashion_thumbnail.jpg"
    EQUIPMENT_THUMBNAIL     = "https://jediar.s3.amazonaws.com/equipment_thumbnail.jpg"
    VEHICLE_THUMBNAIL       = "https://jediar.s3.amazonaws.com/vehicle_thumbnail.jpg"
    INTERIOR_THUMBNAIL      = "https://jediar.s3.amazonaws.com/interior_thumbnail.jpg"
    PLANT_THUMBNAIL         = "https://jediar.s3.amazonaws.com/plant_thumbnail.jpg"
    ELECTRONICS_THUMBNAIL   = "https://jediar.s3.amazonaws.com/electronics_thumbnail.jpg"
    AIRCRAFT_THUMBNAIL      = "https://jediar.s3.amazonaws.com/aircraft_thumbnail.jpg"

    RETURN_LIST     =   []

    if app_id == "jedi":
        RETURN_ITEMS    =   {}
        RETURN_ITEMS["thumbnail"]   =   CATEGORY_THUMBNAIL
        RETURN_ITEMS["category_name"]    =   "Food"

        RETURN_LIST.append(RETURN_ITEMS)
        RETURN_ITEMS    =   {}
        RETURN_ITEMS["thumbnail"]   =   ARCH_THUMBNAIL
        RETURN_ITEMS["category_name"]    =   "Architecture"

        RETURN_LIST.append(RETURN_ITEMS)
        RETURN_ITEMS    =   {}
        RETURN_ITEMS["thumbnail"]   =   DECOR_THUMBNAIL
        RETURN_ITEMS["category_name"]    =   "Decor"

        RETURN_LIST.append(RETURN_ITEMS)
        RETURN_ITEMS    =   {}
        RETURN_ITEMS["thumbnail"]   =   FASHION_THUMBNAIL
        RETURN_ITEMS["category_name"]    =   "Fashion"

        RETURN_LIST.append(RETURN_ITEMS)
        RETURN_ITEMS    =   {}
        RETURN_ITEMS["thumbnail"]   =   EQUIPMENT_THUMBNAIL
        RETURN_ITEMS["category_name"]    =   "Equipment"

        RETURN_LIST.append(RETURN_ITEMS)
        RETURN_ITEMS    =   {}
        RETURN_ITEMS["thumbnail"]   =   INTERIOR_THUMBNAIL
        RETURN_ITEMS["category_name"]    =   "Interior"

        RETURN_LIST.append(RETURN_ITEMS)
        RETURN_ITEMS    =   {}
        RETURN_ITEMS["thumbnail"]   =   VEHICLE_THUMBNAIL
        RETURN_ITEMS["category_name"]    =   "Vehicle"

        RETURN_LIST.append(RETURN_ITEMS)
        RETURN_ITEMS    =   {}
        RETURN_ITEMS["thumbnail"]   =   PLANT_THUMBNAIL
        RETURN_ITEMS["category_name"]    =   "Plant"

        RETURN_LIST.append(RETURN_ITEMS)

        RETURN_ITEMS    =   {}
        RETURN_ITEMS["thumbnail"]   =  ELECTRONICS_THUMBNAIL
        RETURN_ITEMS["category_name"]    =   "Electronics"

        RETURN_LIST.append(RETURN_ITEMS)
        RETURN_ITEMS    =   {}
        RETURN_ITEMS["thumbnail"]   =   AIRCRAFT_THUMBNAIL
        RETURN_ITEMS["category_name"]    =   "aircraft"

        RETURN_LIST.append(RETURN_ITEMS)

    elif app_id == "ar_art":
        RETURN_ITEMS    =   {}

        RETURN_ITEMS["thumbnail"]   =   CATEGORY_THUMBNAIL
        RETURN_ITEMS["category_name"]    =   "Fashion"

        RETURN_LIST.append(RETURN_ITEMS)
        RETURN_ITEMS    =   {}
        RETURN_ITEMS["thumbnail"]   =   EQUIPMENT_THUMBNAIL
        RETURN_ITEMS["category_name"]    =   "Equipment"

        RETURN_LIST.append(RETURN_ITEMS)
        RETURN_ITEMS    =   {}
        RETURN_ITEMS["thumbnail"]   =   VEHICLE_THUMBNAIL
        RETURN_ITEMS["category_name"]    =   "Vehicle"

        RETURN_LIST.append(RETURN_ITEMS)
        RETURN_ITEMS    =   {}
        RETURN_ITEMS["thumbnail"]   =   ARCH_THUMBNAIL
        RETURN_ITEMS["category_name"]    =   "Architecture"

        RETURN_LIST.append(RETURN_ITEMS)
        RETURN_ITEMS    =   {}
        RETURN_ITEMS["thumbnail"]   =   DECOR_THUMBNAIL
        RETURN_ITEMS["category_name"]    =   "Decor"

        RETURN_LIST.append(RETURN_ITEMS)
        RETURN_ITEMS    =   {}
        RETURN_ITEMS["thumbnail"]   =   INTERIOR_THUMBNAIL
        RETURN_ITEMS["category_name"]    =   "Interior"

        RETURN_LIST.append(RETURN_ITEMS)
        RETURN_ITEMS    =   {}
        RETURN_ITEMS["thumbnail"]   =   PLANT_THUMBNAIL
        RETURN_ITEMS["category_name"]    =   "Plant"

        RETURN_LIST.append(RETURN_ITEMS)

        RETURN_ITEMS    =   {}
        RETURN_ITEMS["thumbnail"]   =  ELECTRONICS_THUMBNAIL
        RETURN_ITEMS["category_name"]    =   "Electronics"

        RETURN_LIST.append(RETURN_ITEMS)
        RETURN_ITEMS    =   {}
        RETURN_ITEMS["thumbnail"]   =   AIRCRAFT_THUMBNAIL
        RETURN_ITEMS["category_name"]    =   "Aircraft"

        RETURN_LIST.append(RETURN_ITEMS)

    else:
        return json.dumps({"message": "Invalid app_id"}), 400, {'ContentType': 'application/json'}

    return json.dumps({"message": RETURN_LIST}), 200, {'ContentType': 'application/json'}
#########################################################################################
def search_by_category_helper(app_id, NAMESPACE, DB_NEW_MODELS, DB_USERS, COLLECTION, DB_ANALYTICS):
    print("Searching by category")
    RETURN_LIST = []

    if app_id == JEDI_APP:
        FORMAT = ".scn"
    elif app_id == ARART_APP:
        FORMAT = ".sfb"
    else:
        return RETURN_LIST

    # returns models owned by the requesting org 
    if isValidOrgNamespace(NAMESPACE, DB_USERS):
        response = DB_NEW_MODELS[COLLECTION].find({"$and": [{"format": FORMAT}, {"owner_id": NAMESPACE}]})
    else:
        if NAMESPACE in TEST_NAMESPACES:
            response = DB_NEW_MODELS[COLLECTION].find({"format": FORMAT})
        else:
        # return all models of this category
            response = DB_NEW_MODELS[COLLECTION].find({"$and":[{"format": FORMAT},{"tested_status":1}]})
    #Return only all models to test users and only tested models to others
    for result in response:
        result['model_id'] = str(result['_id'])
        result['isFavorite'] = 0
        del result['_id']
        RETURN_LIST.append(result)
        # increment search appearance
        DB_NEW_MODELS[COLLECTION].update({'_id': ObjectId(result['model_id'])}, {'$inc': {'analytics.search_appearances': 1}})
        
    return json.dumps({"message": RETURN_LIST}), 200, {'ContentType': 'application/json'}
#########################################################################################
'''
def insert_fcm_token(app_id, token, namespace, COLLECTION, DB_USERS):
    token = {
        "app_id"        :   app_id,
        "device_token"  :   token,
    }

    DB_USERS[COLLECTION].update({"namespace"    :   namespace},
                            {"$set": {"token"   :   token}})
'''

#########################################################################################
def feature_request_helper(namespace, app_id, request_type,
                                request_description, timestamp, email, subject, DB_USERS):
    REQUEST_FEATURE_COLLECTION = "feature_request"

    if isValidNamespace(namespace, DB_USERS) or isValidOrgNamespace(namespace, DB_USERS):
        if app_id and request_type and request_description and timestamp:
            DB_USERS[REQUEST_FEATURE_COLLECTION].insert({
                                    "namespace"             :   namespace,
                                    "app_id"                :   app_id,
                                    "request_type"          :   request_type,
                                    "request_description"   :   request_description,
                                    "timestamp"             :   timestamp,
                                    "email"                 :   email,
                                    "subject"               :   subject
                                })
            # send email to user
            send_support_email(email, request_description, request_type, namespace, subject)
            return json.dumps({"message": "Success"}), 200, {'ContentType': 'application/json'}
        else:
            return json.dumps({"message": "Invalid keys"}), 400, {'ContentType': 'application/json'}
    else:
        return json.dumps({"message": "Invalid namespace"}), 400, {'ContentType': 'application/json'}
#########################################################################################
def get_feature_request_helper(namespace, app_id, DB_USERS):
    REQUEST_FEATURE_COLLECTION = "feature_request"

    if isValidNamespace(namespace, DB_USERS) or isValidOrgNamespace(namespace, DB_USERS):
        RETURN_ITEMS = []
        response = DB_USERS[REQUEST_FEATURE_COLLECTION].find({"namespace": namespace})

        for res in response:
            del res["_id"]
            RETURN_ITEMS.append(res)

        return json.dumps({"message": RETURN_ITEMS}), 200, {'ContentType': 'application/json'}
    else:
        return json.dumps({"message": "Invalid namespace"}), 400, {'ContentType': 'application/json'}
#########################################################################################

# helper
def get_downloads_of_my_models(namespace, app_id, DB_NEW_MODELS):
    ''' Get the total download count of all the models of this org. '''
    FOOD_COLLECTION     =   "food"
    FASHION_COLLECTION  =   "fashion"

    downloads_count  = 0

    if app_id == "jedi":
        COLLECTION = FOOD_COLLECTION
    elif app_id == "ar_art":
        COLLECTION = FASHION_COLLECTION

    response = DB_NEW_MODELS[COLLECTION].find({"owner_id": namespace})

    for res in response:
        downloads_count += res["analytics"]["download_count"]

    return int(downloads_count)

#########################################################################################

# helper
def get_search_appearances_of_my_models(namespace, app_id, DB_NEW_MODELS):
    ''' Get the total download count of all the models of this org. '''
    FOOD_COLLECTION     =   "food"
    FASHION_COLLECTION  =   "fashion"

    search_appearances  = 0

    if app_id == "jedi":
        COLLECTION = FOOD_COLLECTION
    elif app_id == "ar_art":
        COLLECTION = FASHION_COLLECTION

    response = DB_NEW_MODELS[COLLECTION].find({"owner_id": namespace})

    for res in response:
        search_appearances += res["analytics"]["search_appearances"]

    return int(search_appearances)

#########################################################################################
# helper
def get_count_of_my_models(namespace, app_id, DB_NEW_MODELS):
    ''' Get the total download count of all the models of this org. '''
    FOOD_COLLECTION     =   "food"
    FASHION_COLLECTION  =   "fashion"

    if app_id == "jedi":
        COLLECTION = FOOD_COLLECTION
    elif app_id == "ar_art":
        COLLECTION = FASHION_COLLECTION

    response = DB_NEW_MODELS[COLLECTION].find({"owner_id": namespace}).count()


    return int(response)

#########################################################################################
def get_profile_helper(namespace, app_id, DB_USERS, DB_ANALYTICS, DB_NEW_MODELS):
    USERS_COLLECTION                =   "users_data"
    ORGS_COLLECTION                 =   "organizations_data"
    USER_MEASUREMENTS_COLLECTION    =   "user_measurements"

    #### Org profile
    if isValidOrgNamespace(namespace, DB_USERS):
        RETURN_ITEMS                =   {}
        RETURN_ITEMS["metadata"]    =   {}

        response = DB_USERS[ORGS_COLLECTION].find_one({"namespace": namespace})

        if response:
            RETURN_ITEMS["metadata"]["name"]                =   response["org_name"]
            RETURN_ITEMS["metadata"]["namespace"]           =   response["namespace"]
            RETURN_ITEMS["metadata"]["email"]               =   response["email"]
            RETURN_ITEMS["metadata"]["total_downloads"]     =   get_downloads_of_my_models(
                                                                                namespace,
                                                                                app_id,
                                                                                DB_NEW_MODELS)
            RETURN_ITEMS["metadata"]["search_appearances"]  =  get_search_appearances_of_my_models(
                                                                                namespace,
                                                                                app_id,
                                                                                DB_NEW_MODELS)
            RETURN_ITEMS["metadata"]["total_models"]        =   get_count_of_my_models(
                                                                                namespace,
                                                                                app_id,
                                                                                DB_NEW_MODELS)    

            return json.dumps({"message": RETURN_ITEMS}), 200, {'ContentType': 'application/json'}
        else:
            return json.dumps({"message": "Invalid namespace"}), 400, {'ContentType': 'application/json'}

    #### User profile
    elif isValidNamespace(namespace, DB_USERS):
        RETURN_ITEMS = {}
        RETURN_ITEMS["metadata"] = {}
        
        response = DB_USERS[USERS_COLLECTION].find_one({"namespace": namespace})

        if response:
            RETURN_ITEMS["metadata"]["name"]                =   response["first_name"]
            RETURN_ITEMS["metadata"]["namespace"]           =   response["namespace"]
            RETURN_ITEMS["metadata"]["email"]               =   response["email"]
            RETURN_ITEMS["metadata"]["invitation_count"]    =   response["invitation_count"]
            RETURN_ITEMS["metadata"]["model_downloads"]     =   response["model_downloads"]
            RETURN_ITEMS["metadata"]["shares_count"]        =   response["share_count"]

        analytics_response = DB_ANALYTICS[USER_MEASUREMENTS_COLLECTION].find_one({namespace: {"$exists": 1}})
        
        if analytics_response:
            RETURN_ITEMS["metadata"]["total_projections"] = analytics_response[namespace]["total_projections"]
        else:
            RETURN_ITEMS["metadata"]["total_projections"] = 0
        return json.dumps({"message": RETURN_ITEMS}), 200, {'ContentType': 'application/json'}
    else:
        return json.dumps({"message": "Invalid namespace"}), 400, {'ContentType': 'application/json'}
#########################################################################################
def process_forget_password(app_id, email, DB_USERS):
    if isValidAppId(app_id):
        # get namespace, email of user
        namespace, username = get_namespace_and_email(email, DB_USERS)
        if isValidUsername(username, DB_USERS):
            # get a token
            token = get_token()
            # insert token in forget_pswd collection
            DB_USERS[FORGET_PASSWORD_COLLECTION].insert({"namespace": namespace, "token": token})
            # send token to user via email
            send_forget_password_email(email,str(username) , str(token))

            return json.dumps({"message": "Token is sent to registered email!"}), 200, {'ContentType': 'application/json'}
        else:
            return json.dumps({"message": "Invalid username"}), 400, {'ContentType': 'application/json'}
    else:
        return json.dumps({"message": "Invalid app id"}), 400, {'ContentType': 'application/json'}
#########################################################################################
def process_set_new_password(app_id, namespace, new_password, DB_USERS):
    USERS_COLLECTION    = "users_data"
    ORGS_COLLECTION     = "organizations_data"

    if isValidAppId(app_id):
        # response = DB_USERS[FORGET_PASSWORD_COLLECTION].find_one({"token": token})

        # if response:
        #     namespace = response["namespace"]
        if isValidUserNamespace(namespace, DB_USERS):
            DB_USERS[USERS_COLLECTION].update({"namespace": namespace}, {"$set": {"password": new_password}})
        elif isValidOrgNamespace(namespace, DB_USERS):
            DB_USERS[ORGS_COLLECTION].update({"namespace": namespace}, {"$set": {"password": new_password}})
        else:
            return json.dumps({"message": "Server exception while reseting password"}), 500, {'ContentType': 'application/json'}
        
        return json.dumps({"message": "Password changed!"}), 200, {'ContentType': 'application/json'}
        # else:
        #     return json.dumps({"message": "Invalid token"}), 400, {'ContentType': 'application/json'}
    else:
        return json.dumps({"message": "Invalid app id"}), 400, {'ContentType': 'application/json'}   

##############################################################################

def increment_search_appearance_count(model_id, collection, DB_NEW_MODELS):
    try:
        DB_NEW_MODELS[collection].update({'_id': ObjectId(model_id)}, {'$inc': {'analytics.search_appearances': 1}})
    except Exception as e:
        print ("".join(["Exception in increment_search_appearance_count Method", str(e)]))
        return False
    return True
#########################################################################################

def search_all_models_method(app_id, namespace, collection, DB_NEW_MODELS, DB_USERS, DB_ANALYTICS):
    RESULTS = []

    if app_id == JEDI_APP:
        FORMAT = ".scn"
    elif app_id == ARART_APP:
        FORMAT = ".sfb"
    else:
        return RESULTS

    try:
        all_collections = get_all_collections(DB_NEW_MODELS)

        for collection in all_collections:
            if isValidOrgNamespace(namespace, DB_USERS):
                response = DB_NEW_MODELS[collection].find({"$and": [{"format": FORMAT}, {"owner_id": namespace}]})
            else:
                if namespace in TEST_NAMESPACES:
                    response = DB_NEW_MODELS[collection].find({"format": FORMAT})
                else:
                    response = DB_NEW_MODELS[collection].find({"$and":[{"format": FORMAT},{"tested_status":1}]})

            for reso in response:
                reso['model_id'] = str(reso['_id'])
                reso['isFavorite'] = 0
                del reso["_id"]
                RESULTS.append(reso)
              #increment search appearance of each model
                DB_NEW_MODELS[collection].update({'_id': ObjectId(reso['model_id'])}, {'$inc': {'analytics.search_appearances': 1}})


                # if isValidNamespace(namespace, DB_USERS):
                #     if isFavorite(namespace, reso['model_id'], DB_USERS):
                #         reso["isFavorite"] = 1
                #     else:
                #         reso["isFavorite"] = 0
                #     RESULTS.append(reso)
                # else:
                #     RESULTS.append(reso)

    except Exception as e:
        print ("".join(["Exception in search_all_models Method: ", str(e)]))

    # for reso in response:
    #     reso['model_id'] = str(reso['_id'])
    #     del reso["_id"]

    #     if isValidNamespace(namespace, DB_USERS):
    #         if isFavorite(namespace, reso['model_id'], DB_USERS):
    #             reso["isFavorite"] = 1
    #         else:
    #             reso["isFavorite"] = 0
    #         RESULTS.append(reso)
    #     else:
    #         RESULTS.append(reso)

        # set purchase status
        # if is_downloaded(namespace, reso["model_id"], DB_ANALYTICS):
        #     reso["purchase_status"] = 1
        # else:
        #     reso["purchase_status"] = 0


    return RESULTS
#########################################################################################
def get_all_collections(DB_MODELS):
    all_collections = DB_MODELS.collection_names()
    return all_collections
##########################################################################################
def is_downloaded(namespace, model_id, DB_ANALYTICS):
    USER_DOWNLOADS_COLLECTION = "user_downloads"

    flag = False

    response = DB_ANALYTICS[USER_DOWNLOADS_COLLECTION].find_one({namespace: {"$exists": 1}})

    if response:
        del response["_id"]
        if model_id in response[namespace]:
            print("dowloaded=true")
            flag = True
            return flag
        # print(json.dumps(response[namespace]))

    else:
        return flag

#########################################################################################
def search_model_by_id(namespace, model_id, collection, DB_NEW_MODELS, DB_ANALYTICS):
    response = {}

    try:
        all_collections = get_all_collections(DB_NEW_MODELS)

        for collection in all_collections:
            response = DB_NEW_MODELS[collection].find_one({'_id': ObjectId(model_id)})
            if response:
                response['category'] = response['category'].capitalize()
                response["model_id"] =  str(response["_id"])
                del response["_id"]
                break

            # set purchase status
            # if is_downloaded(namespace, response["model_id"], DB_ANALYTICS):
            #     response["purchase_status"] = 1
            # else:
            #     response["purchase_status"] = 0

    except Exception as e:
        print ("".join(["Exception in search_model_by_id Method: ", str(e)]))
    return response
#########################################################################################
def search_model_by_keyword(keyword, collection, DB_NEW_MODELS):
    try:
        response = DB_NEW_MODELS[collection].find({'$or': [{'basic_info.name': { "$regex": keyword, "$options" :'i' }}, {'basic_info.manufacturer': { "$regex": keyword, "$options" :'i' }}, {'basic_info.model': { "$regex": keyword, "$options" :'i' }}, {'category': { "$regex": keyword, "$options" :'i' }}]})
    except Exception as e:
        print ("".join(["Exception in search_model_by_keyword Method: ", str(e)]))
    
    return response
#########################################################################################

def process_get_metadata(app_id ,QRCODE, namespace, DB_NEW_MODELS, DB_USERS, DB_ANALYTICS):
    ########
    # 1- Search by _id from models db
    # 2- increment the search appearance count
    # 
    ########
    RETURN_ITEMS = []
    try:
        collection = QRCODE.split('_')[0]
        model_id = QRCODE.split('_')[1]

        if not collection or not model_id:
            print ("Invalid QRCODE!")
            return json.dumps({'message': 'Invalid QRCODE'}), 400, {'ContentType': 'application/json'}
    except IndexError as e:
        print ("".join(["Exception in process_get_metadata Method: ", str(e)]))
        return json.dumps({'message': 'Invalid QRCODE'}), 400, {'ContentType': 'application/json'}
    else:
        result = search_model_by_id(namespace, model_id, collection, DB_NEW_MODELS, DB_ANALYTICS)
        if result:
        #Check app, return only model related to requested app, i.e ios or android.
            if app_id == JEDI_APP and result["format"] != ".scn":
                    return json.dumps({'message': 'This model is not for ios'}), 400, {'ContentType': 'application/json'}
            if app_id == ARART_APP and result["format"] != ".sfb":
                    return json.dumps({'message': 'This model is not for android'}), 400, {'ContentType': 'application/json'}
            if not result:
                return json.dumps({'message': RETURN_ITEMS}), 200, {'ContentType': 'application/json'}
            else:
                # set purchase status
                # if is_downloaded(namespace, result["model_id"], DB_ANALYTICS):
                #     result["purchase_status"] = 1
                # else:
                #     result["purchase_status"] = 0

                if isFavorite(namespace, model_id, DB_USERS):
                    result["isFavorite"] = 1
                else:
                    result["isFavorite"] = 0
                if increment_search_appearance_count(model_id, collection, DB_NEW_MODELS):
                    RETURN_ITEMS.append(result)
                    return json.dumps({'message': RETURN_ITEMS}), 200, {'ContentType': 'application/json'}
                else:
                    return json.dumps({'message': ["Exception on search_appearances increment count"]}), 500, {'ContentType': 'application/json'}
        else:
            return json.dumps({'message': 'Invalid QRCODE'}), 400, {'ContentType': 'application/json'}

#########################################################################################

def search_by_keyword_helper(app_id, keyword, namespace, DB_NEW_MODELS, DB_USERS, COLLECTION, DB_ANALYTICS):
    ########
    # 1- Search on basis of keyword from models db
    # 2- increment the search appearance count
    # 3- append the model_id by converting it to string
    # 
    ########
    cap_keyword = keyword.capitalize()
    RESULTS = []

    
    if app_id == JEDI_APP:
        FORMAT = ".scn"
    elif app_id == ARART_APP:
        FORMAT = ".sfb"
    else:
        return RESULTS

    if isValidNamespace(namespace, DB_USERS) or isValidOrgNamespace(namespace, DB_USERS):
        all_collections = get_all_collections(DB_NEW_MODELS)

        for collection in all_collections:
            if isValidOrgNamespace(namespace, DB_USERS): 
                response = DB_NEW_MODELS[collection].find({'$and': [{'format':FORMAT}, {'owner_id': namespace}, {'$or':[{'basic_info.name':{ "$regex": cap_keyword, "$options" :'i' }},{'basic_info.manufacturer':{ "$regex": cap_keyword, "$options" :'i' }},{'basic_info.model':{ "$regex": cap_keyword, "$options" :'i' }},{'category':{ "$regex": cap_keyword, "$options" :'i' }}]}]})
            else:
                if namespace in TEST_NAMESPACES:
                    response = DB_NEW_MODELS[collection].find({'$and': [{'format':FORMAT}, {'$or':[{'basic_info.name':{ "$regex": cap_keyword, "$options" :'i' }},{'basic_info.manufacturer':cap_keyword},{'basic_info.model':{ "$regex": cap_keyword, "$options" :'i' }},{'category':{ "$regex": cap_keyword, "$options" :'i' }}]}]})
                else:
                    response = DB_NEW_MODELS[collection].find({'$and': [{'format':FORMAT} ,{"tested_status": 1} , {'$or':[{'basic_info.name':{ "$regex": cap_keyword, "$options" :'i' }},{'basic_info.manufacturer':{ "$regex": cap_keyword, "$options" :'i' }},{'basic_info.model':{ "$regex": cap_keyword, "$options" :'i' }},{'category':{ "$regex": cap_keyword, "$options" :'i' }}]}]})

            # if response.count() == 0:
            #     print("empty response")
            #     return (json.dumps({'message': RESULTS}), 200, {'ContentType': 'application/json'})
            for result in response:
                DB_NEW_MODELS[collection].update({'_id': ObjectId(result['_id'])}, {'$inc': {'analytics.search_appearances': 1}})
                 #Kashif:: Return only teseted models to users and all models to test users.
                result['model_id'] = str(result['_id'])
                result['isFavorite'] = 0
                del result['_id']
                RESULTS.append(result)

                # if isValidNamespace(namespace, DB_USERS):
                #     if isFavorite(namespace, result["model_id"], DB_USERS):
                #         result["isFavorite"] = 1
                #     else:
                #         result["isFavorite"] = 0
                #     RESULTS.append(result)
                # else:
                #     RESULTS.append(result)

                # if isValidNamespace(namespace, DB_USERS):
                #     if isFavorite(namespace, result["model_id"], DB_USERS):
                #         result["isFavorite"] = 1
                #     else:
                #         result["isFavorite"] = 0
                #     RESULTS.append(result)
                # else:
                #     RESULTS.append(result)

        return (
         json.dumps({'message': RESULTS}), 200, {'ContentType': 'application/json'})
    else:
        return json.dumps({"message": "Invalid user namespace!"}), 400, {'ContentType': 'application/json'}
#########################################################################################

def search_all_models_helper(app_id, namespace, DB_NEW_MODELS, DB_USERS, COLLECTION, DB_ANALYTICS):
    ########
    # 1- Search all models from models db
    # 2- increment the search appearance count
    # 3- append the model_id by converting it to string
    # 
    ########
    # COLLECTION = 'food'

    if isValidNamespace(namespace, DB_USERS) or isValidOrgNamespace(namespace, DB_USERS):
        try:
            RETURN_ITEMS = search_all_models_method(app_id, namespace, COLLECTION, DB_NEW_MODELS, DB_USERS, DB_ANALYTICS)
        except Exception as e:
            print (str(e))
            return (json.dumps({"message": "Exception in search_all_models_helper Method"}), 500, {'ContentType': 'application/json'})

        return (json.dumps({"message": RETURN_ITEMS}), 200, {'ContentType': 'application/json'})
    else:
        return json.dumps({"message": "Invalid user namespace!"}), 400, {'ContentType': 'application/json'}

    # COLLECTION = 'food'
    # response = DB_NEW_MODELS[COLLECTION].find()
    # if response.count() == 0:
    #     return (json.dumps({'message': 'No models are found!'}), 200, {'ContentType': 'application/json'})
    # RESULTS = []
    # for result in response:
    #     DB_NEW_MODELS[COLLECTION].update({'_id': ObjectId(result['_id'])}, {'$inc': {'analytics.search_appearances': 1}})
    #     result['model_id'] = str(result['_id'])
    #     del result['_id']

    #     RESULTS.append(result)

    # return (
    #  json.dumps({"message": RESULTS}), 200, {'ContentType': 'application/json'})
#########################################################################################

def isFavorite(namespace, model_id, DB_USERS):
    flag = 0

    response = DB_USERS["users_data"].find_one({"namespace": namespace})

    if response and (model_id in response["favorite_models"]):
        flag = 1

    return flag
#########################################################################################

def search_all_orgs_helper(namespace, DB_USERS):
    COLLECTION = 'organizations_data'
    response = DB_USERS[COLLECTION].find()
    if response.count == 0:
        return (json.dumps({'message': 'No organizations are found!'}), 200, {'ContentType': 'application/json'})
    RESULT = []
    for result in response:
        del result['_id']
        RESULT.append(result)

    return (
     json.dumps(RESULT), 200, {'ContentType': 'application/json'})
#########################################################################################

def add_comment_helper(model_id, comment, rating, timestamp, namespace, DB_NEW_MODELS):
    COLLECTION = 'food'
    try:
        response = DB_NEW_MODELS[COLLECTION].update({'_id': ObjectId(model_id)}, {'$push': {'comment_feed': {'comment': comment, 'rating': 3.5, 'timestamp': timestamp, 'user': namespace}}})
        return (
         json.dumps({'success': True}), 200, {'ContentType': 'application/json'})
    except Exception as e:
        print (str(e))
        return (
         json.dumps({'message': 'Error while comment insertion ' + str(e)}), 200, {'ContentType': 'application/json'})
#########################################################################################

def request_custom_model_helper(body, DB_CUSTOM_MODELS):
    model_name = body['model_name']
    BASE_PATH   =   '/home/btech/models_data/custom_models/'
    BASE_S3_URL =   'https://s3.amazonaws.com/jediar/custom_models/' + model_name + '/'
    
    PATH = BASE_PATH + model_name
    request_id = 'req' + str(random.randint(1000, 9999))
    COLLECTION = 'models'
    
    try:
        os.mkdir(PATH)
    except OSError as e:
        print (str(e))
        return (
         json.dumps({'message': 'directory already exists'}), 500, {'ContentType': 'application/json'})


    email = body["user_email"]
    note  = body['notes_for_designer']
    namespace = body['namespace']


    DATA  = {}
    DATA['requester_namespace'] = namespace
    DATA['model_name']          = model_name
    DATA['model_format']        = body['model_format']
    DATA['number_of_revisions'] = body['number_of_revisions']
    DATA['notes_for_designer']  = note
    DATA['category']            = body['category']
    DATA['subcategory']         = body['subcategory']
    DATA['request_id']          = request_id                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        
    DATA['request_status']      = 'Pending for designer review'
    DATA['cloud_link']          = ''
    DATA['images']              = []
    DATA['user_email']          = email
    temp_links                       = []
    if 'cloud_link' in body:
        DATA['cloud_link'] = body['cloud_link']
        temp_links.append(body['cloud_link'])

    if 'images' in body:
        for i in range(len(body['images'])):
            IMAGE_FILE_PATH = PATH + '/' + body['images'][i]['file_name']
            image_base64_decode = base64.b64decode(body['images'][i]['image_base64'])
            #image_base64_decode = base64.decodestring(body['images'][i]['texture_base64'])
            image_file = open(IMAGE_FILE_PATH, 'wb')
            image_file.write(image_base64_decode)
            image_file.close()
            IMAGE_S3_PATH = BASE_S3_URL + body['images'][i]['file_name']
            DATA['images'].append(IMAGE_S3_PATH)
            temp_links.append(IMAGE_S3_PATH)
    if 'video_base64' in body:
        MODEL_VIDEO_PATH = PATH + '/' + 'model_video' + body['video_format']
        MODEL_video_base64_decode = base64.b64decode(body['video_base64'])
        #video_base64_decode = base64.decodestring(body['video_base64'])
        model_video = open(MODEL_VIDEO_PATH, 'wb')
        model_video.write(model_video_base64_decode)
        model_video.close()
        DATA['model_video'] = BASE_S3_URL + 'model_video' + body['video_format']
        temp_links.append(DATA['model_video'])

    response = insert_in_db(DB_CUSTOM_MODELS, COLLECTION, DATA)
    
    links = ", ".join(temp_links)
    if response:
        if 'video_base64' or 'images' in body:
            MODEL_DIR = BASE_PATH + model_name + '/'
            if upload_custom_files_to_s3(MODEL_DIR, model_name):
            # delete directory from server storage
                shutil.rmtree(MODEL_DIR)
                send_custom_model_email(email, note, namespace, links, model_name)
                return (json.dumps({'message': 'Submitted successfully.'}), 200, {'ContentType': 'application/json'})
            else:
                return json.dumps({'message': 'Upload error'}), 500, {'ContentType': 'application/json'}
    else:
        return json.dumps({'message': 'Upload error'}), 500, {'ContentType': 'application/json'}
#########################################################################################

def get_request_status_helper(namespace, request_id, DB_CUSTOM_MODELS):
    COLLECTION = 'models'
    response = DB_CUSTOM_MODELS[COLLECTION].find_one({'$and': [{'requester_namespace': namespace}, {'request_id': request_id}]})
    if response:
        return (json.dumps({'message': response['request_status']}), 200)
        {'ContentType': 'application/json'}
    else:
        return (json.dumps({'message': 'Request-ID or namespace is wrong'}), 500)
        {'ContentType': 'application/json'}
#########################################################################################

def update_download_count(filename, DB_NEW_MODELS):
    filename = '/' + filename
    COLLECTION = 'food'
    response = DB_NEW_MODELS[COLLECTION].find_one({'model_files.3d_model_file': filename})
    DB_NEW_MODELS[COLLECTION].update({'_id': response['_id']}, {'$inc': {'analytics.download_count': 1}})
    return True
#########################################################################################

def upload_survey_helper(body, DB_SURVEYS, DB_USERS):
    ORGS_COLLECTION = 'organizations_data'
    SURVEYS_COLLECTION = 'surveys'
    # print (body)
    namespace = body['namespace']
    survey_title = body['survey_title']
    
    response = DB_SURVEYS[SURVEYS_COLLECTION].find({'$and':[{'namespace':namespace},\
                                                   {'survey_title':survey_title}]}).count() 
    if response == 0:
        DB_SURVEYS[SURVEYS_COLLECTION].insert({'namespace':body['namespace'],\
                                            'survey_title':body['survey_title'],\
                                            'questions':body['questions']})
        return (json.dumps({'message': 'Valid ORG'}), 200, {'ContentType': 'application/json'})
    else:
        return (json.dumps({'message': 'Survey already exists!'}), 400, {'ContentType': 'application/json'})
    
    # print (namespace)
    # response = DB_USERS[ORGS_COLLECTION].find_one({'namespace': namespace})
    # if response:
    #     res2 = DB_SURVEYS[SURVEYS_COLLECTION].find({namespace: {'$exists': 1}}).count()
    #     # print (res2)
    #     if res2 != 0:
    #         # print ('exits')
    #         res = DB_SURVEYS[SURVEYS_COLLECTION].find({namespace + '.' + survey_title: {'$exists': 1}}).count()
    #         if res != 0:
    #             return (json.dumps({'message': 'Survey already exists'}), 400, {'ContentType': 'application/json'})
    #         else:
    #             DB_SURVEYS[SURVEYS_COLLECTION].update({namespace: {'$exists': 1}}, {'$push': {namespace: {body['survey_title']:body['questions']}}})
    #     else:
    #         # print ('not exits')
    #         questionnaire_list = []
    #         questionnaire_list.append({body['survey_title']:body['questions']})
    #         # print (questionnaire_list)
    #         res3 = DB_SURVEYS[SURVEYS_COLLECTION].insert({namespace: questionnaire_list})
    #     return (json.dumps({'message': 'Valid ORG'}), 200, {'ContentType': 'application/json'})
    # return (
    #  json.dumps({'message': 'Invalid organization namespace'}), 400, {'ContentType': 'application/json'})
#########################################################################################

def get_surveys_helper(namespace, DB_SURVEYS):
    RETURN_LIST = []
    SURVEYS_COLLECTION = 'surveys'
    response = DB_SURVEYS[SURVEYS_COLLECTION].find({'namespace':namespace}).count()
    if response == 0:
        return (json.dumps({'message': 'Invalid namespace, no survey against this user'}), 200, {'ContentType': 'application/json'})
    res2 = DB_SURVEYS[SURVEYS_COLLECTION].find({'namespace':namespace})
    for x in res2:
        x['survey_id'] = str(x['_id'])
        del x['_id']
        RETURN_LIST.append(x)
    return (json.dumps(RETURN_LIST), 200, {'ContentType': 'application/json'})
#########################################################################################

def submit_survey_helper(body, DB_SURVEYS):
    RESPONSE_COLLECTION = 'survey_responses'
    response = DB_SURVEYS[RESPONSE_COLLECTION].insert({'namespace': body['namespace'], 'model_id': body['model_id'], 
       'survey': body['survey']})
    return (
     json.dumps({'message': 'Successfully submitted'}), 200, {'ContentType': 'application/json'})
#########################################################################################

def get_base64(file):
    image = open(file, 'rb')
    image_read = image.read()
    return base64.encodestring(image_read)
#########################################################################################

def calculate_average(axis_list, count):
    total = 0
    if count == 0:
        return 0
    for i in axis_list:
        total += i

    avg = total / float(count)
    return avg
#########################################################################################

def model_popularity_in_category(model_id, DB_NEW_MODELS, COLLECTION):
    response = DB_NEW_MODELS[COLLECTION].find_one({"_id": ObjectId(model_id)})

    if response:
        # get this models search apearances
        my_popularity = response["analytics"]["search_appearances"]

        if my_popularity < 1:
            return 0
        else:
            # get highest search apearances of a model

            model_response = DB_NEW_MODELS[COLLECTION].find({})
            FINAL_RETURN = []
            RETURN_ITEMS = []
            temp_diction = {}

            for res in model_response:
                model_id = str(res["_id"])
                del res["_id"]
                temp_diction[model_id] = res["analytics"]["search_appearances"]

            sorted_temp_diction = sorted(temp_diction.items(), key=operator.itemgetter(1), reverse=True)

            # print my_popularity
            # print(sorted_temp_diction)

            total_projections = 0
            for each_val in sorted_temp_diction:
                total_projections += each_val[1]

            # print(total_projections)
            result = my_popularity/float(total_projections)*100

            return result
    else:
        return 0
#########################################################################################

def generate_report_helper(model_id, DB_ANALYTICS, DB_NEW_MODELS, COLLECTION):
    BASE_URL = 'https://jedi.gydpost.com/modelf5d074942eb0ceb273d346e3bile'
    RETURN_ITEMS = {}
    RETURN_ITEMS['analytics'] = {}
    RETURN_ITEMS['measurements'] = {}
    RETURN_ITEMS['metadata'] = {}
    # models_response = DB_NEW_MODELS['food'].find_one({'_id': ObjectId('5c939f17eb0ceb68d95e453e')})
    
    collections = get_all_collections(DB_NEW_MODELS)

    for collection in collections:
        # print(collection)
        models_response = DB_NEW_MODELS[collection].find_one({'_id': ObjectId(model_id)})
        if models_response:
            break
    
    measurements_response = DB_ANALYTICS['measurments'].find_one({model_id: {'$exists': 1}})
    
    if models_response is None:
        print ("models response is none")
    if measurements_response is None:
        print ("measurements_response is none")

    # if (models_response is None) or (measurements_response is None):
    #     return (json.dumps({'message': 'Not a valid id'}), 400, {'ContentType': 'application/json'})

    if models_response is None:
        print ("models response is none")
        return (json.dumps({'message': 'Not a valid id'}), 400, {'ContentType': 'application/json'})
    elif measurements_response is None:
        print ("measurements_response is none")
        return (json.dumps({'message': 'No measurements available for this model.'}), 400, {'ContentType': 'application/json'})

    # DOWNLOAD_COUNT = models_response['analytics']['download_count']
    # DOWNLOAD_COUNT = measurements_response[str(model_id+"."+"total_projections")]
    # DOWNLOAD_COUNT = measurements_response[model_id]["total_projections"]
    
    DOWNLOAD_COUNT = (measurements_response[model_id]['zoom_in']['count'] + \
                        measurements_response[model_id]['zoom_out']['count'] + \
                        measurements_response[model_id]['left_move']['count'] + \
                        measurements_response[model_id]['right_move']['count'] + \
                        measurements_response[model_id]['up']['count'] + \
                        measurements_response[model_id]['down']['count'] + \
                        measurements_response[model_id]['rotate_left']['count'] + \
                        measurements_response[model_id]['rotate_right']['count'])

    print("==========================")
    print("search_appearances: ", DOWNLOAD_COUNT)
    print("==========================")


    if DOWNLOAD_COUNT <= 0:
         return (json.dumps({'message': 'No measurements available for this model.'}), 400, {'ContentType': 'application/json'})


    RETURN_ITEMS['analytics']['download_count'] = models_response['analytics']['download_count']
    RETURN_ITEMS['analytics']['search_appearances'] = models_response['analytics']['search_appearances']
    RETURN_ITEMS['analytics']['shares'] = models_response['analytics']['shares_count']
    RETURN_ITEMS['analytics']['popularity_in_category'] = model_popularity_in_category(model_id, DB_NEW_MODELS, collection)
    RETURN_ITEMS['metadata']['name'] = models_response['basic_info']['name']
    RETURN_ITEMS['metadata']['manufacturer'] = models_response['basic_info']['manufacturer']
    RETURN_ITEMS['metadata']['category'] = models_response['category']
    RETURN_ITEMS['metadata']['manufacturing_date'] = models_response['manufacturing_date']
    RETURN_ITEMS['metadata']['description'] = models_response['description']
    RETURN_ITEMS['metadata']['owner_id'] = models_response['owner_id']
    RETURN_ITEMS['metadata']['thumbnail'] = models_response['model_files']['thumbnail']
    RETURN_ITEMS['measurements']['zoom_in'] = {}
    RETURN_ITEMS['measurements']['zoom_in']['popularity'] = measurements_response[model_id]['zoom_in']['count'] / float(DOWNLOAD_COUNT) * 100
    RETURN_ITEMS['measurements']['zoom_in']['axis_avg'] = {'x-axis': 0.0, 'y-axis': 0.0, 'z-axis': 0.0}
    if len(measurements_response[model_id]['zoom_in']['axis']['z-axis']):
        RETURN_ITEMS['measurements']['zoom_in']['axis_avg']['z-axis'] = calculate_average(measurements_response[model_id]['zoom_in']['axis']['z-axis'], measurements_response[model_id]['zoom_in']['count'])
    if len(measurements_response[model_id]['zoom_in']['axis']['x-axis']):
        RETURN_ITEMS['measurements']['zoom_in']['axis_avg']['x-axis'] = calculate_average(measurements_response[model_id]['zoom_in']['axis']['x-axis'], measurements_response[model_id]['zoom_in']['count'])
    if len(measurements_response[model_id]['zoom_in']['axis']['y-axis']):
        RETURN_ITEMS['measurements']['zoom_in']['axis_avg']['y-axis'] = calculate_average(measurements_response[model_id]['zoom_in']['axis']['y-axis'], measurements_response[model_id]['zoom_in']['count'])
    RETURN_ITEMS['measurements']['zoom_out'] = {}
    RETURN_ITEMS['measurements']['zoom_out']['popularity'] = measurements_response[model_id]['zoom_out']['count'] / float(DOWNLOAD_COUNT) * 100
    RETURN_ITEMS['measurements']['zoom_out']['axis_avg'] = {'x-axis': 0.0, 'y-axis': 0.0, 'z-axis': 0.0}
    if len(measurements_response[model_id]['zoom_out']['axis']['z-axis']):
        RETURN_ITEMS['measurements']['zoom_out']['axis_avg']['z-axis'] = calculate_average(measurements_response[model_id]['zoom_out']['axis']['z-axis'], measurements_response[model_id]['zoom_out']['count'])
    if len(measurements_response[model_id]['zoom_out']['axis']['x-axis']):
        RETURN_ITEMS['measurements']['zoom_out']['axis_avg']['x-axis'] = calculate_average(measurements_response[model_id]['zoom_out']['axis']['x-axis'], measurements_response[model_id]['zoom_out']['count'])
    if len(measurements_response[model_id]['zoom_out']['axis']['y-axis']):
        RETURN_ITEMS['measurements']['zoom_out']['axis_avg']['y-axis'] = calculate_average(measurements_response[model_id]['zoom_out']['axis']['y-axis'], measurements_response[model_id]['zoom_out']['count'])
    RETURN_ITEMS['measurements']['left_move'] = {}
    RETURN_ITEMS['measurements']['left_move']['popularity'] = measurements_response[model_id]['left_move']['count'] / float(DOWNLOAD_COUNT) * 100
    RETURN_ITEMS['measurements']['left_move']['axis_avg'] = {'x-axis': 0.0, 'y-axis': 0.0, 'z-axis': 0.0}
    if len(measurements_response[model_id]['left_move']['axis']['z-axis']):
        RETURN_ITEMS['measurements']['left_move']['axis_avg']['z-axis'] = calculate_average(measurements_response[model_id]['left_move']['axis']['z-axis'], measurements_response[model_id]['left_move']['count'])
    if len(measurements_response[model_id]['left_move']['axis']['x-axis']):
        RETURN_ITEMS['measurements']['left_move']['axis_avg']['x-axis'] = calculate_average(measurements_response[model_id]['left_move']['axis']['x-axis'], measurements_response[model_id]['left_move']['count'])
    if len(measurements_response[model_id]['left_move']['axis']['y-axis']):
        RETURN_ITEMS['measurements']['left_move']['axis_avg']['y-axis'] = calculate_average(measurements_response[model_id]['left_move']['axis']['y-axis'], measurements_response[model_id]['left_move']['count'])
    RETURN_ITEMS['measurements']['right_move'] = {}
    RETURN_ITEMS['measurements']['right_move']['popularity'] = measurements_response[model_id]['right_move']['count'] / float(DOWNLOAD_COUNT) * 100
    RETURN_ITEMS['measurements']['right_move']['axis_avg'] = {'x-axis': 0.0, 'y-axis': 0.0, 'z-axis': 0.0}
    if len(measurements_response[model_id]['right_move']['axis']['z-axis']):
        RETURN_ITEMS['measurements']['right_move']['axis_avg']['z-axis'] = calculate_average(measurements_response[model_id]['right_move']['axis']['z-axis'], measurements_response[model_id]['right_move']['count'])
    if len(measurements_response[model_id]['right_move']['axis']['x-axis']):
        RETURN_ITEMS['measurements']['right_move']['axis_avg']['x-axis'] = calculate_average(measurements_response[model_id]['right_move']['axis']['x-axis'], measurements_response[model_id]['right_move']['count'])
    if len(measurements_response[model_id]['right_move']['axis']['y-axis']):
        RETURN_ITEMS['measurements']['right_move']['axis_avg']['y-axis'] = calculate_average(measurements_response[model_id]['right_move']['axis']['y-axis'], measurements_response[model_id]['right_move']['count'])
    RETURN_ITEMS['measurements']['up'] = {}
    RETURN_ITEMS['measurements']['up']['popularity'] = measurements_response[model_id]['up']['count'] / float(DOWNLOAD_COUNT) * 100
    RETURN_ITEMS['measurements']['up']['axis_avg'] = {'x-axis': 0.0, 'y-axis': 0.0, 'z-axis': 0.0}
    if len(measurements_response[model_id]['up']['axis']['z-axis']):
        RETURN_ITEMS['measurements']['up']['axis_avg']['z-axis'] = calculate_average(measurements_response[model_id]['up']['axis']['z-axis'], measurements_response[model_id]['up']['count'])
    if len(measurements_response[model_id]['up']['axis']['x-axis']):
        RETURN_ITEMS['measurements']['up']['axis_avg']['x-axis'] = calculate_average(measurements_response[model_id]['up']['axis']['x-axis'], measurements_response[model_id]['up']['count'])
    if len(measurements_response[model_id]['up']['axis']['y-axis']):
        RETURN_ITEMS['measurements']['up']['axis_avg']['y-axis'] = calculate_average(measurements_response[model_id]['up']['axis']['y-axis'], measurements_response[model_id]['up']['count'])
    RETURN_ITEMS['measurements']['down'] = {}
    RETURN_ITEMS['measurements']['down']['popularity'] = measurements_response[model_id]['down']['count'] / float(DOWNLOAD_COUNT) * 100
    RETURN_ITEMS['measurements']['down']['axis_avg'] = {'x-axis': 0.0, 'y-axis': 0.0, 'z-axis': 0.0}
    if len(measurements_response[model_id]['down']['axis']['z-axis']):
        RETURN_ITEMS['measurements']['down']['axis_avg']['z-axis'] = calculate_average(measurements_response[model_id]['down']['axis']['z-axis'], measurements_response[model_id]['down']['count'])
    if len(measurements_response[model_id]['down']['axis']['x-axis']):
        RETURN_ITEMS['measurements']['down']['axis_avg']['x-axis'] = calculate_average(measurements_response[model_id]['down']['axis']['x-axis'], measurements_response[model_id]['down']['count'])
    if len(measurements_response[model_id]['down']['axis']['y-axis']):
        RETURN_ITEMS['measurements']['down']['axis_avg']['y-axis'] = calculate_average(measurements_response[model_id]['down']['axis']['y-axis'], measurements_response[model_id]['down']['count'])
    RETURN_ITEMS['measurements']['rotate_left'] = {}
    RETURN_ITEMS['measurements']['rotate_left']['popularity'] = measurements_response[model_id]['rotate_left']['count'] / float(DOWNLOAD_COUNT) * 100
    RETURN_ITEMS['measurements']['rotate_left']['axis_avg'] = {'x-axis': 0.0, 'y-axis': 0.0, 'z-axis': 0.0}
    if len(measurements_response[model_id]['rotate_left']['axis']['z-axis']):
        RETURN_ITEMS['measurements']['rotate_left']['axis_avg']['z-axis'] = calculate_average(measurements_response[model_id]['rotate_left']['axis']['z-axis'], measurements_response[model_id]['rotate_left']['count'])
    if len(measurements_response[model_id]['rotate_left']['axis']['x-axis']):
        RETURN_ITEMS['measurements']['rotate_left']['axis_avg']['x-axis'] = calculate_average(measurements_response[model_id]['rotate_left']['axis']['x-axis'], measurements_response[model_id]['rotate_left']['count'])
    if len(measurements_response[model_id]['rotate_left']['axis']['y-axis']):
        RETURN_ITEMS['measurements']['rotate_left']['axis_avg']['y-axis'] = calculate_average(measurements_response[model_id]['rotate_left']['axis']['y-axis'], measurements_response[model_id]['rotate_left']['count'])
    RETURN_ITEMS['measurements']['rotate_right'] = {}
    RETURN_ITEMS['measurements']['rotate_right']['popularity'] = measurements_response[model_id]['rotate_right']['count'] / float(DOWNLOAD_COUNT) * 100
    RETURN_ITEMS['measurements']['rotate_right']['axis_avg'] = {'x-axis': 0.0, 'y-axis': 0.0, 'z-axis': 0.0}
    if len(measurements_response[model_id]['rotate_right']['axis']['z-axis']):
        RETURN_ITEMS['measurements']['rotate_right']['axis_avg']['z-axis'] = calculate_average(measurements_response[model_id]['rotate_right']['axis']['z-axis'], measurements_response[model_id]['rotate_right']['count'])
    if len(measurements_response[model_id]['rotate_right']['axis']['x-axis']):
        RETURN_ITEMS['measurements']['rotate_right']['axis_avg']['x-axis'] = calculate_average(measurements_response[model_id]['rotate_right']['axis']['x-axis'], measurements_response[model_id]['rotate_right']['count'])
    if len(measurements_response[model_id]['rotate_right']['axis']['y-axis']):
        RETURN_ITEMS['measurements']['rotate_right']['axis_avg']['y-axis'] = calculate_average(measurements_response[model_id]['rotate_right']['axis']['y-axis'], measurements_response[model_id]['rotate_right']['count'])
    RETURN_ITEMS['measurements']['total_time_spent'] = measurements_response[model_id]['total_time_spent']
    RETURN_ITEMS['measurements']['video_preview_count'] = measurements_response[model_id]['video_preview_count']
    RETURN_ITEMS['measurements']['model_info_count'] = measurements_response[model_id]['model_info_count']
    return (
     json.dumps({'message': RETURN_ITEMS}), 200, {'ContentType': 'application/json'})
#########################################################################################

def add_to_favorites_helper(namespace, model_id, DB_USERS):
    USERS_COLLECTION = 'users_data'
    response = DB_USERS[USERS_COLLECTION].find_one({'namespace': namespace})
    if response:
        DB_USERS[USERS_COLLECTION].update({'namespace': namespace}, {'$addToSet': {'favorite_models': model_id}})
    else:
        return (
         json.dumps({'message': 'Not a valid user namespace'}), 400, {'ContentType': 'application/json'})
    return (
     json.dumps({'message': 'added to favorites'}), 200, {'ContentType': 'application/json'})
#########################################################################################

def get_my_favorites_helper(namespace, DB_USERS, DB_NEW_MODELS, COLLECTION):
    USERS_COLLECTION = 'users_data'
    # COLLECTION = 'food'

    if isValidNamespace(namespace, DB_USERS):
        return_items = []
        response = DB_USERS[USERS_COLLECTION].find_one({'namespace': namespace})
        print (response)
        if response:
            for model in response['favorite_models']:
                resp_model = DB_NEW_MODELS[COLLECTION].find_one({'_id': ObjectId(model)})
                if resp_model:
                    resp_model['model_id'] = str(resp_model['_id'])
                    del resp_model['_id']
                    return_items.append(resp_model)

            return (
             json.dumps({'message': return_items}), 200, {'ContentType': 'application/json'})
        else:
            return (
             json.dumps({'message': return_items}), 200, {'ContentType': 'application/json'})
        return (
         json.dumps({'message': 'Not a valid user namespace'}), 400, {'ContentType': 'application/json'})
    else:
        return json.dumps({"message": "Invalid user namespace!"}), 400, {'ContentType': 'application/json'}
#########################################################################################

def get_inprogress_orders_helper(producer_namespace, DB_CUSTOM_MODELS):
    CUSTOM_MODELS_COLLECTION = 'models'
    response = DB_CUSTOM_MODELS[CUSTOM_MODELS_COLLECTION].count({'requester_namespace': producer_namespace})
    if response:
        RESULTS = {}
        RESULTS['producer_namespace'] = producer_namespace
        RESULTS['inProgressOrders'] = response
        return (
         json.dumps({'message': RESULTS}), 200, {'ContentType': 'application/json'})
    return (
     json.dumps({'message': 'Not a valid user namespace'}), 400, {'ContentType': 'application/json'})
#########################################################################################
'''
def invite_user_helper(inviter_namespace, invitee_namespace, DB_USERS):
    INIVITATIONS_COLLECTION = "invitations"

    if invitee_namespace == inviter_namespace:
        return json.dumps({"message": "Can't invite yourself!"}), 400, {'ContentType': 'application/json'}

    if isValidNamespace(inviter_namespace, DB_USERS) and isValidNamespace(invitee_namespace, DB_USERS):
        response = DB_USERS[INIVITATIONS_COLLECTION].find({inviter_namespace: {'$exists': 1}}).count()

        if response != 0:
            resp2 = DB_USERS[INIVITATIONS_COLLECTION].update({inviter_namespace: {'$exists': 1}}, {'$addToSet': {inviter_namespace: invitee_namespace}})
        else:
            invitee_list = [] # because it's a list in db that's why inserting in form of list

            invitee_list.append(invitee_namespace)
            resp2 = DB_USERS[INIVITATIONS_COLLECTION].insert({inviter_namespace: invitee_list})

        return json.dumps({"message": "invitation sent to "+invitee_namespace}), 200, {'ContentType': 'application/json'}
    else:
        return json.dumps({"message": "Not valid namespace(s)."}), 400, {'ContentType': 'application/json'}
'''


def invite_user_helper(namespace, email, DB_USERS):
    if namespace and email:
        response = send_email(email)
        if response:
            return json.dumps({"message": "Invitation sent successfully."}), 200, {'ContentType': 'application/json'}
        else:
            return json.dumps({"message": "Invitation NOT sent!"}), 500, {'ContentType': 'application/json'}
    else:
        return json.dumps({"message": "Invalid email/link/namespace"}), 400, {'ContentType': 'application/json'}
    pass

#########################################################################################

def get_my_invitations_helper(namespace, DB_USERS):
    INIVITATIONS_COLLECTION = "invitations"
    RETURN_ITEMS = []

    if isValidNamespace(namespace, DB_USERS):
        response = DB_USERS[INIVITATIONS_COLLECTION].find({})
        for entry in response:
            del entry["_id"]
            for key in entry:
                if namespace in entry[key]:
                    tmp_dict = {}
                    tmp_dict["namespace"] =     key
                    tmp_dict["message"] =       "Download the amazing JEDI AR app!"
                    tmp_dict["first_name"] =    find_username_using_namespace(key, DB_USERS)
                    RETURN_ITEMS.append(tmp_dict)
                '''
                print entry[key]
                if namespace in entry[key]:
                    tmp_dict = {}
                    tmp_dict["namespace"] = namespace
                    tmp_dict["message"] = "Download the amazing JEDI AR app!"
                    tmp_dict["first_name"] = find_username_using_namespace(namespace, DB_USERS)
                    RETURN_ITEMS.append(tmp_dict)
                '''
        return json.dumps({"message": RETURN_ITEMS}), 200, {'ContentType': 'application/json'}
    else:
        return json.dumps({"message": "Not valid namespace(s)."}), 400, {'ContentType': 'application/json'}
#########################################################################################

def get_reward_info_helper(namespace):
    API_ENDPOINT = "https://dnxr7vm27d.execute-api.us-east-1.amazonaws.com/prod/GetRewardInfo"
    API_KEY = "0licid7INt99oaExspwAjFYffGtdX1a9qYSpzD8c" # API key
    headers = {"x-api-key": API_KEY, "Content-Type": "application/json"} # Headers
    # Data to be sent to API
    data = {
        'appId': 'af39d80a-2f10-43b2-bd53-d65cf9f4ad96',
        'momentId': 'MomentsReward',
        'deviceType': 'Web',
        'campaignId': '8505d8bb-6eff-47f1-8205-4634704edf5d',
        'rewardGroupId': 'US'
        }

    r = requests.post(url = API_ENDPOINT, headers=headers, json = data)

    temp = r.json()
    # print type(temp)
    # print temp

    return json.dumps({"message": temp["rewardNotificationText"]}), 200, {'ContentType': 'application/json'}
#########################################################################################

def get_my_reward_helper(namespace, DB_USERS, DB_ANALYTICS):
    ########
    # 1- Check eligibilty of user 
    # 2- if eligible - get amazon reward
    # 
    #
    ########

    RETURN_ITEMS = {}
    RETURN_ITEMS["eligible"] = 0
    RETURN_ITEMS["rewardNotificationText"] =    ""
    RETURN_ITEMS["rewardNotificationUrl"] =     ""
    RETURN_ITEMS["expiration_date"] =           ""

    eligible = isEligibleForReward(namespace, DB_USERS, DB_ANALYTICS)

    # print (eligible)
    if eligible:
        result = get_amazon_award()
        
        RETURN_ITEMS["eligible"] = 1
        RETURN_ITEMS["rewardNotificationText"] =    result["rewardNotificationText"]
        RETURN_ITEMS["rewardNotificationUrl"] =     result["rewardNotificationUrl"]
        RETURN_ITEMS["expiration_date"] =           result["campaignEndDate"]
        RETURN_ITEMS["rewards_count"] = eligible
        return json.dumps({"message": RETURN_ITEMS}), 200, {'ContentType': 'application/json'}
    else:
        return json.dumps({"message": RETURN_ITEMS}), 200, {'ContentType': 'application/json'}
#########################################################################################

def get_amazon_award():
    API_ENDPOINT = "https://dnxr7vm27d.execute-api.us-east-1.amazonaws.com/prod/GetReward"
    API_KEY = "0licid7INt99oaExspwAjFYffGtdX1a9qYSpzD8c" # API key
    headers = {"x-api-key": API_KEY, "Content-Type": "application/json"} # Headers
    # Data to be sent to API
    data = {
        'appId': 'af39d80a-2f10-43b2-bd53-d65cf9f4ad96',
        'momentId': 'MomentsReward',
        'deviceType': 'Web',
        'campaignId': '8505d8bb-6eff-47f1-8205-4634704edf5d',
        'rewardGroupId': 'US'
        }

    r = requests.post(url = API_ENDPOINT, headers=headers, json = data)

    temp = r.json()

    return temp
#########################################################################################

def isEligibleForReward(namespace, DB_USERS, DB_ANALYTICS):
    REWARDS_COLLECTION = "rewards"

    flag = False

    if isValidNamespace(namespace, DB_USERS):
        invitation_count = getInvitationCount(namespace, DB_USERS)

        rewards_response = DB_ANALYTICS[REWARDS_COLLECTION].find({namespace: {"$exists": 1}}).count()
        if rewards_response == 0:
            flag = True
            # add in rewards db
            DB_ANALYTICS[REWARDS_COLLECTION].insert({namespace: {"rewards_sent_count": 1,
                                                    "last_reward_sent_at": invitation_count}})
            res = int(invitation_count/5)
            return res
        else:
            # check the last_reward_at Count
            temp_response = DB_ANALYTICS[REWARDS_COLLECTION].find_one({namespace: {"$exists": 1}})
            if (invitation_count - temp_response[namespace]["last_reward_sent_at"]) >= 5:
                print("eligible")
                flag = True

                temp_dictionary = {}
                temp2 = {} 
                temp_dictionary = DB_ANALYTICS[REWARDS_COLLECTION].find_one({namespace: {"$exists": 1}})

                temp2["rewards_sent_count"] =   temp_dictionary[namespace]["rewards_sent_count"]
                temp2["last_reward_sent_at"] =  (temp_dictionary[namespace]["last_reward_sent_at"]+5)

                DB_ANALYTICS[REWARDS_COLLECTION].update({namespace: {"$exists": 1}},
                                                {"$set": {namespace: temp2}})

                res = (int(invitation_count - temp_response[namespace]["last_reward_sent_at"])/5)
                # print "returning: "+str(res)

                return res

    return flag

    # flag = False

    # if isValidNamespace(namespace, DB_USERS):
    #     invitation_count = getInvitationCount(namespace, DB_USERS)
    #     if invitation_count >= 5:
    #         flag = True

    # return flag
#########################################################################################
def get_my_campaigns_helper(namespace, app_id, DB_ANALYTICS, DB_USERS):
    CAMPAIGNS_COLLECTION = "reward_campaigns"

    RETURN_ITEMS = []

    if isValidOrgNamespace(namespace, DB_USERS) and isValidAppId(app_id):
        response = DB_ANALYTICS[CAMPAIGNS_COLLECTION].find({"campaign_creator": namespace})

        for res in response:
            del res["_id"]
            # temp = {}
            # temp["campaign_title"] =    res["campaign_title"]
            # temp["campaign_creator"] =  res["campaign_creator"]
            # temp["campaign_id"] =       res["campaignId"]
            # temp["downloads_count"] =   res["downloads_count"]
            # temp["creation_time"] =     res["creation_time"]
            # temp["applicable_for"] =    res["applicable_for"]
            # temp["campaign_status"] =   res["campaign_status"]

            # RETURN_ITEMS.append(temp)

            RETURN_ITEMS.append(res)

        return json.dumps({"message": RETURN_ITEMS}), 200, {'ContentType': 'application/json'}
    else:
        return json.dumps({"message": "Invalid org namespace OR Invalid app id"}), 400, {'ContentType': 'application/json'}

#########################################################################################

def delete_campaign_helper(namespace, campaign_id, DB_ANALYTICS, DB_USERS):
    CAMPAIGNS_COLLECTION = "reward_campaigns"

    if isValidOrgNamespace(namespace, DB_USERS):
        response = DB_ANALYTICS[CAMPAIGNS_COLLECTION].find_one({"campaignId": campaign_id,
                                                            "campaign_creator": namespace})
        if response:
            res = DB_ANALYTICS[CAMPAIGNS_COLLECTION].remove({"campaignId": campaign_id,
                                                            "campaign_creator": namespace})
            return json.dumps({"message": "Campaign Deleted!"}), 200, {'ContentType': 'application/json'}
        else:
            return json.dumps({"message": "Invalid campaign_id"}), 400, {'ContentType': 'application/json'}
    else:
        return json.dumps({"message": "Invalid org namespace"}), 400, {'ContentType': 'application/json'}
#########################################################################################

def change_campaign_status_helper(namespace, campaign_id, status, DB_ANALYTICS, DB_USERS):
    CAMPAIGNS_COLLECTION = "reward_campaigns"

    if isValidOrgNamespace(namespace, DB_USERS):
        response = DB_ANALYTICS[CAMPAIGNS_COLLECTION].find_one({"campaignId": campaign_id,
                                                            "campaign_creator": namespace})
        if response:
            if status == 1:
                # get all the campaigns
                # make sure only a signle campaign is activated
                resp = DB_ANALYTICS[CAMPAIGNS_COLLECTION].find({"campaign_creator": namespace})

                for each_resp in resp:
                    if each_resp["campaignId"] == campaign_id:
                        DB_ANALYTICS[CAMPAIGNS_COLLECTION].update({"_id": each_resp["_id"]},
                                                            {"$set": {"campaign_status": 1}})
                    elif each_resp["campaign_status"] == 1 and each_resp["campaignId"]\
                     != campaign_id:
                        DB_ANALYTICS[CAMPAIGNS_COLLECTION].update({"_id": each_resp["_id"]},
                                                            {"$set": {"campaign_status": 0}})
                pass
            elif status == 0:
                res = DB_ANALYTICS[CAMPAIGNS_COLLECTION].update({"campaignId": campaign_id},
                                                            {"$set": {"campaign_status": status}})
                return json.dumps({"message": "Campaign deactivated successfully."}), 200, {'ContentType': 'application/json'}
            if status == 1 or status == 0:
                res = DB_ANALYTICS[CAMPAIGNS_COLLECTION].update({"campaignId": campaign_id},
                                                            {"$set": {"campaign_status": status}})
                return json.dumps({"message": "Campaign status changed successfully."}), 200, {'ContentType': 'application/json'}
            else:
                return json.dumps({"message": "Invalid status key in data"}), 400, {'ContentType': 'application/json'}
        else:
            return json.dumps({"message": "Invalid campaign_id"}), 400, {'ContentType': 'application/json'}
    else:
        return json.dumps({"message": "Invalid org namespace"}), 400, {'ContentType': 'application/json'}


    # if isValidOrgNamespace(namespace, DB_USERS):
    #     response = DB_ANALYTICS[CAMPAIGNS_COLLECTION].find_one({"campaignId": campaign_id,
    #                                                         "campaign_creator": namespace})
    #     if response:
    #         if status == 1 or status == 0:
    #             res = DB_ANALYTICS[CAMPAIGNS_COLLECTION].update({"campaignId": campaign_id},
    #                                                         {"$set": {"campaign_status": status}})
    #             return json.dumps({"message": "Campaign status changed successfully."}), 200, {'ContentType': 'application/json'}
    #         else:
    #             return json.dumps({"message": "Invalid status key in data"}), 400, {'ContentType': 'application/json'}
    #     else:
    #         return json.dumps({"message": "Invalid campaign_id"}), 400, {'ContentType': 'application/json'}
    # else:
    #     return json.dumps({"message": "Invalid org namespace"}), 400, {'ContentType': 'application/json'}
#########################################################################################

def start_rewards_campaign_helper(body, DB_ANALYTICS, DB_USERS):
    CAMPAIGNS_COLLECTION = "reward_campaigns"

    namespace = body["namespace"]
    app_id =    body["app_id"]

    appId =             body["data"]["appId"]
    momentId =          body["data"]["momentId"] 
    x_api_key =         body["data"]["x-api-key"]
    campaignId =        body["data"]["campaignId"]
    rewardGroupId =     body["data"]["rewardGroupId"]
    campaign_title =    body["data"]["campaign_title"]
    campaign_status =   body["data"]["campaign_status"]

    downloads_count =   body["data"]["downloads_count"]

    # campaign_id

    if isValidOrgNamespace(namespace, DB_USERS) and isValidAppId(app_id): 
        if appId and momentId and x_api_key and campaignId and rewardGroupId:
            res = DB_ANALYTICS[CAMPAIGNS_COLLECTION].find({"campaignId": campaignId}).count()
            if res == 0:
                response = DB_ANALYTICS[CAMPAIGNS_COLLECTION].insert({
                                                                "appId":            appId,
                                                                "momentId":         momentId,
                                                                "x-api-key":        x_api_key,
                                                                "campaignId":       campaignId,
                                                                "rewardGroupId":    rewardGroupId,
                                                                "downloads_count":  downloads_count,
                                                                "campaign_creator": namespace,
                                                                "campaign_title":   campaign_title,
                                                                "applicable_for":   "all models",
                                                                "campaign_status":  campaign_status,
                                                                "creation_time":    int(time.time())
                                                                 })
                # change the status of all other campaigns to '0'
                resp = DB_ANALYTICS[CAMPAIGNS_COLLECTION].find({"campaign_creator": namespace})

                # print "==========="
                # print str(response)
                # print "==========="
                for each_resp in resp:
                    if each_resp["_id"] == ObjectId(response):
                        print ("Added this as new campaign")
                    elif each_resp["campaign_status"] == 1 and each_resp["_id"]\
                     != ObjectId(response):
                        DB_ANALYTICS[CAMPAIGNS_COLLECTION].update({"_id": each_resp["_id"]},
                                                            {"$set": {"campaign_status": 0}})

                return json.dumps({"message": "Campaign created!"}), 200, {'ContentType': 'application/json'}
            else:
                return json.dumps({"message": "Can't create a duplicate campaign"}), 400, {'ContentType': 'application/json'}
        else:
            return json.dumps({"message": "data fields can't be empty"}), 400, {'ContentType': 'application/json'}
    else:
        return json.dumps({"message": "Invalid org namespace OR Invalid app id"}), 400, {'ContentType': 'application/json'}
#########################################################################################

def edit_rewards_campaign_helper(namespace, campaignId, campaign_title, downloads_count ,DB_ANALYTICS, DB_USERS):
    CAMPAIGNS_COLLECTION = "reward_campaigns"

    if isValidOrgNamespace(namespace, DB_USERS):
        res = DB_ANALYTICS[CAMPAIGNS_COLLECTION].find({"campaignId": campaignId}).count()
        if res == 0:
            return json.dumps({"message": "Invalid campaignId"}), 400, {'ContentType': 'application/json'}
        else:
            if not campaign_title or not downloads_count:
                return json.dumps({"message": "campaign_title/downloads_count can't be empty"}), 400, {'ContentType': 'application/json'}
            else:
                response = DB_ANALYTICS[CAMPAIGNS_COLLECTION].update({"campaignId": campaignId},
                    {"$set": {"campaign_title": campaign_title, "downloads_count": downloads_count}})
                return json.dumps({"message": "campaign updated successfully"}), 200, {'ContentType': 'application/json'}
    else:
        return json.dumps({"message": "Invalid org namespace"}), 400, {'ContentType': 'application/json'}



def getInvitationCount(namespace, DB_USERS):
    USERS_COLLECTION = "users_data"

    try:
        response = DB_USERS[USERS_COLLECTION].find_one({"namespace": namespace})
        print (response["invitation_count"])

        return response["invitation_count"]
    except Exception as e:
        print ("".join(["Exception in getInvitationCount Method: ", str(e)]))
        return 0
#########################################################################################

def find_username_using_namespace(namespace, DB_USERS):
    USERS_COLLECTION = "users_data"

    response = DB_USERS[USERS_COLLECTION].find_one({"namespace": namespace})

    if response:
        return response["first_name"]
    else:
        return ""
#########################################################################################

def isValidOrgNamespace(namespace, DB_USERS):
    ORGS_COLLECTION = "organizations_data"
    flag = False

    if namespace:
        response = DB_USERS[ORGS_COLLECTION].find_one({"namespace": namespace})
        if response:
            flag = True

    return flag
#########################################################################################

def isValidNamespace(namespace, DB_USERS):
    USERS_COLLECTION = "users_data"
    flag = False

    if namespace:
        response = DB_USERS[USERS_COLLECTION].find_one({"namespace": namespace})

        if response:
            flag = True

    return flag
#########################################################################################

def exist_in_list(value, array):
    for key in array:
        if value == key:
            return True
    return False
#########################################################################################

def respond_to_invitation_helper(invitee_namespace, inviter_namespace, req_response, DB_USERS):
    USERS_COLLECTION =          "users_data"
    INIVITATIONS_COLLECTION =   "invitations"

    try:
        invitations_response = DB_USERS[INIVITATIONS_COLLECTION].find({inviter_namespace: {"$exists": 1}})
    except Exception as e:
        return json.dumps(str(e)), 500, {'ContentType': 'application/json'}
    else:
        if not invitations_response.count():
            return json.dumps({"message": "No invitation against the inviter " + str(inviter_namespace)}), 400, {'ContentType': 'application/json'}
        else:
            for invites in invitations_response:
                del invites["_id"]

                if exist_in_list(invitee_namespace, invites[inviter_namespace]):
                    # print ("not where should be")
                    DB_USERS[INIVITATIONS_COLLECTION].update({inviter_namespace: {"$exists": 1}}, {"$pull": {inviter_namespace: invitee_namespace}})
                    if req_response == 1:
                        DB_USERS[USERS_COLLECTION].update({"namespace": inviter_namespace}, {"$inc": {"invitation_count": 1}})
                        return json.dumps({"message": "Invitation accepted!"}), 200, {'ContentType': 'application/json'}
                    else:
                        return json.dumps({"message": "Invitation rejected!"}), 200, {'ContentType': 'application/json'}
                else:
                    return json.dumps({"message": "No invitation against the inviter " + str(inviter_namespace)}), 400, {'ContentType': 'application/json'}
                break
        return json.dumps({"message": "success"}), 200, {'ContentType': 'application/json'}
#########################################################################################

def upload_files_to_s3(path, model_dir):
    '''Upload model to S3 bucket.'''
    
    dir_name = 'models/' + model_dir + '/'
    session = boto3.Session(aws_access_key_id='AKIA6LNQDLNY64EAG26A', aws_secret_access_key='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', region_name='us-east-1')
    s3 = session.resource('s3')
    bucket = s3.Bucket('jediar')

    try:
        for subdir, dirs, files in os.walk(path):
            for file in files:
                full_path = os.path.join(subdir, file)
                with open(full_path, 'rb') as (data):
                    bucket.put_object(Key=dir_name + full_path[len(path):], Body=data)
                    object_acl = s3.ObjectAcl('jediar', dir_name + full_path[len(path):])
                    # set file status to public readable
                    response = object_acl.put(ACL='public-read')
        return True
    except Exception as e:
        print(str(e))
        return False
#########################################################################################
def upload_custom_files_to_s3(path, model_dir):
    '''Upload model to S3 bucket.'''
    
    dir_name = 'custom_models/' + model_dir + '/'
    session = boto3.Session(aws_access_key_id='AKIA6LNQDLNY64EAG26A', aws_secret_access_key='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', region_name='us-east-1')
    s3 = session.resource('s3')
    bucket = s3.Bucket('jediar')

    try:
        for subdir, dirs, files in os.walk(path):
            for file in files:
                full_path = os.path.join(subdir, file)
                with open(full_path, 'rb') as (data):
                    bucket.put_object(Key=dir_name + full_path[len(path):], Body=data)
                    object_acl = s3.ObjectAcl('jediar', dir_name + full_path[len(path):])
                    # set file status to public readable
                    response = object_acl.put(ACL='public-read')
        return True
    except Exception as e:
        print(str(e))
        return False
#########################################################################################

def get_my_models_helper(namespace, app_id, DB_NEW_MODELS):
    RETURN_ITEMS = []

    all_collections =  all_collections = get_all_collections(DB_NEW_MODELS)

    if app_id == JEDI_APP:
        FORMAT = ".scn"
    elif app_id == ARART_APP:
        FORMAT = ".sfb"
    else:
        return json.dumps({"message": "Invalid app id"}), 400, {'ContentType': 'application/json'}

    for collection in all_collections:
        response = DB_NEW_MODELS[collection].find({"$and": [{"owner_id": namespace}, {"format": FORMAT}]}, {"analytics.survey": 0})
        if response.count() > 0:
            for model in response:
                model['model_id'] =  str(model['_id'])
                del model['_id']
                RETURN_ITEMS.append(model)
    # end of loop
                
    return json.dumps({"message": RETURN_ITEMS}), 200, {'ContentType': 'application/json'}

    #### previous code ###
    # response = DB_NEW_MODELS[COLLECTION].find({"owner_id": namespace}, {"analytics.survey": 0})
    # if response.count() > 0:
    #     for model in response:
    #         model['model_id'] = str(model['_id'])
    #         del model["_id"]
    #         RETURN_ITEMS.append(model)

    #     return json.dumps({"message": RETURN_ITEMS}), 200, {'ContentType': 'application/json'}
    # else:
    #     return json.dumps({"message": RETURN_ITEMS}), 200, {'ContentType': 'application/json'}
    #########################

#########################################################################################

def increment_download_count_helper(namespace, model_id, DB_USERS, DB_NEW_MODELS):
    ##################
    # 1- Update the download count in the model collection
    # 2- Update the download count in the user collection
    #
    ###################
    FOOD_COLLECTION = 'food'
    USERS_COLLECTION = 'users_data'

    model_response = DB_NEW_MODELS[FOOD_COLLECTION].find_one({'_id': ObjectId(model_id)})

    if model_response and isValidNamespace(namespace, DB_USERS):
        # del model_response['_id']
        # print json.dumps(model_response)
        DB_NEW_MODELS[FOOD_COLLECTION].update({"_id": ObjectId(model_id)}, {"$inc": {"analytics.download_count": 1}})
        DB_USERS[USERS_COLLECTION].update({"namespace": namespace}, {"$inc": {"model_downloads": 1}})
        
        return json.dumps({"message": "Success!"}), 200, {'ContentType': 'application/json'}
    else:
        return json.dumps({"message": "model_id/namespace is Invalid!"}), 400, {'ContentType': 'application/json'}
#########################################################################################

def share_model_helper(inviter_namespace, model_id, timestamp, DB_USERS, DB_NEW_MODELS, COLLECTION, DB_ANALYTICS):
    # print("===========")
    # print(COLLECTION)
    # print("===========")

    collections = get_all_collections(DB_NEW_MODELS)

    for coll in collections:
        responsive = DB_NEW_MODELS[coll].find_one({"_id": ObjectId(model_id)})
        if responsive:
            COLLECTION = coll
            break


    RETURN_ITEMS = []
    #print (timestamp)
    
    # if isValidNamespace(inviter_namespace, DB_USERS) and isValidModelId(model_id, DB_NEW_MODELS, COLLECTION):
    if isValidNamespace(inviter_namespace, DB_USERS):
        # check timestamp
        if isinstance(timestamp, int):
            if (int(time.time()) - timestamp) > 86400:
                return json.dumps({"message": "Link is expired!"}), 400, {'ContentType': 'application/json'}
            else:
                response = search_model_by_id("namespace", model_id, COLLECTION, DB_NEW_MODELS, DB_ANALYTICS)
                increment_share_count(inviter_namespace, DB_USERS)
                DB_NEW_MODELS[COLLECTION].update({"_id": ObjectId(model_id)},
                                            {"$inc": {"analytics.shares_count": 1}})
                RETURN_ITEMS.append(response)
                return json.dumps({"message": RETURN_ITEMS}), 200, {'ContentType': 'application/json'}
        else:
            return json.dumps({"message": "Invalid timestamp"}), 400, {'ContentType': 'application/json'}
    else:
        return json.dumps({"message": "Invalid URL"}), 400, {'ContentType': 'application/json'}


#########################################################################################

def increment_share_count(namespace, DB_USERS):
    USERS_COLLECTION = "users_data"

    flag = False

    response = DB_USERS[USERS_COLLECTION].update({"namespace": namespace},
                                                {"$inc": {"share_count": 1}})

    if response:
        flag = True

    return flag
    
#########################################################################################

def isValidModelId(model_id, DB_NEW_MODELS, COLLECTION):
    print("model_id: ", model_id)
    print("collection: ", COLLECTION)

    flag = False
    if model_id:
        response = DB_NEW_MODELS[COLLECTION].find_one({'_id': ObjectId(model_id)})
        if response:
            flag = True

    return flag
#########################################################################################
#########################################################################################
#########################################################################################

def generate_user_report_helper(namespace, DB_ANALYTICS, DB_USERS):
    USERS_COLLECTION = "users_data"
    USER_MEASUREMENTS_COLLECTION = "user_measurements"

    if isValidNamespace(namespace, DB_USERS):
        response = DB_ANALYTICS[USER_MEASUREMENTS_COLLECTION].find({namespace: {"$exists": 1}}).count()

        if response == 0:
            return json.dumps({"message": "No measurements found for this user."}), 400, {'ContentType': 'application/json'}
        else:
            RETURN_ITEMS = {}
            RETURN_ITEMS["analytics"] = {}
            RETURN_ITEMS["measurements"] = {}

            download_count = 0
            projections_count = 0
            shares_count = 0

            ### analytics
            res2 = DB_USERS[USERS_COLLECTION].find_one({"namespace": namespace})
            RETURN_ITEMS["analytics"]["download_count"] = res2["model_downloads"]
            RETURN_ITEMS["analytics"]["shares_count"] =      res2["share_count"]
            RETURN_ITEMS["analytics"]["invitation_count"] = res2["invitation_count"]


            res3 = DB_ANALYTICS[USER_MEASUREMENTS_COLLECTION].find_one({namespace: {"$exists": 1}})
            RETURN_ITEMS["analytics"]["projections_count"] = res3[namespace]["total_projections"]

            ### measurements

            temp_diction = process_user_measurments(res3[namespace])

            RETURN_ITEMS["measurements"] = temp_diction



            return json.dumps({"message": RETURN_ITEMS}), 200, {'ContentType': 'application/json'}
    else:
        return json.dumps({"message": "Invalid namespace"}), 400, {'ContentType': 'application/json'}
#########################################################################################

def process_user_measurments(user_diction):
    # temp = {
    #         "popularity": 0.0,
    #         "axis_avg": {"x-axis": 0.0, "y-axis": 0.0, "z-axis": 0.0}
    #         }

    RETURN_ITEMS = {}
    RETURN_ITEMS["right_move"] =    {"popularity":0.0,"axis_avg":{"x-axis":0.0,"y-axis":0.0,"z-axis":0.0}}
    RETURN_ITEMS["left_move"] =     {"popularity":0.0,"axis_avg":{"x-axis":0.0,"y-axis":0.0,"z-axis":0.0}}
    RETURN_ITEMS["up"] =            {"popularity":0.0,"axis_avg":{"x-axis":0.0,"y-axis":0.0,"z-axis":0.0}}
    RETURN_ITEMS["down"] =          {"popularity":0.0,"axis_avg":{"x-axis":0.0,"y-axis":0.0,"z-axis":0.0}}
    RETURN_ITEMS["rotate_left"] =   {"popularity":0.0,"axis_avg":{"x-axis":0.0,"y-axis":0.0,"z-axis":0.0}}
    RETURN_ITEMS["rotate_right"] =  {"popularity":0.0,"axis_avg":{"x-axis":0.0,"y-axis":0.0,"z-axis":0.0}}
    RETURN_ITEMS["zoom_in"] =       {"popularity":0.0,"axis_avg":{"x-axis":0.0,"y-axis":0.0,"z-axis":0.0}}
    RETURN_ITEMS["zoom_out"] =      {"popularity":0.0,"axis_avg":{"x-axis":0.0,"y-axis":0.0,"z-axis":0.0}}

    RETURN_ITEMS["model_info_count"]    =  0 # user_diction["model_info_count"]
    RETURN_ITEMS["video_preview_count"] =  0 # user_diction["video_preview_count"]
    RETURN_ITEMS["total_time_spent"]    =  0 # user_diction["total_time_spent"]


    MEASUREMENTS_LIST = []
    total_projections = user_diction["total_projections"]

    del user_diction["total_projections"]

    # print json.dumps(user_diction)

    for tmp_dict in user_diction.values():
        MEASUREMENTS_LIST.append(tmp_dict)

    total_time_spent    = 0
    video_preview_count = 0
    model_info_count    = 0

    right_move_count    = 0
    left_move_count     = 0
    up_count            = 0
    down_count          = 0
    rotate_right_count  = 0
    rotate_left_count   = 0
    zoom_in_count       = 0
    zoom_out_count      = 0

    right_avg_axis      = {"x-axis": 0.0, "y-axis": 0.0, "z-axis": 0.0}
    left_avg_axis       = {"x-axis": 0.0, "y-axis": 0.0, "z-axis": 0.0}
    up_avg_axis         = {"x-axis": 0.0, "y-axis": 0.0, "z-axis": 0.0}
    down_avg_axis       = {"x-axis": 0.0, "y-axis": 0.0, "z-axis": 0.0}
    rotate_r_avg_axis   = {"x-axis": 0.0, "y-axis": 0.0, "z-axis": 0.0}
    rotate_l_avg_axis   = {"x-axis": 0.0, "y-axis": 0.0, "z-axis": 0.0}
    zoom_in_avg_axis    = {"x-axis": 0.0, "y-axis": 0.0, "z-axis": 0.0}
    zoom_out_avg_axis   = {"x-axis": 0.0, "y-axis": 0.0, "z-axis": 0.0}

    for j in range(len(MEASUREMENTS_LIST)):
        right_move_count +=     MEASUREMENTS_LIST[j]["right_move"]["count"]
        left_move_count +=      MEASUREMENTS_LIST[j]["left_move"]["count"]
        up_count +=             MEASUREMENTS_LIST[j]["up"]["count"]
        down_count +=           MEASUREMENTS_LIST[j]["down"]["count"]
        rotate_right_count +=   MEASUREMENTS_LIST[j]["rotate_right"]["count"]
        rotate_left_count +=    MEASUREMENTS_LIST[j]["rotate_left"]["count"]
        zoom_in_count +=        MEASUREMENTS_LIST[j]["zoom_in"]["count"]
        zoom_out_count +=       MEASUREMENTS_LIST[j]["zoom_out"]["count"]

        right_avg_axis["x-axis"] += calculate_average(MEASUREMENTS_LIST[j]["right_move"]["axis"]["x-axis"], len(MEASUREMENTS_LIST[j]["right_move"]["axis"]["x-axis"]))
        right_avg_axis["y-axis"] += calculate_average(MEASUREMENTS_LIST[j]["right_move"]["axis"]["y-axis"], len(MEASUREMENTS_LIST[j]["right_move"]["axis"]["y-axis"]))
        right_avg_axis["z-axis"] += calculate_average(MEASUREMENTS_LIST[j]["right_move"]["axis"]["z-axis"], len(MEASUREMENTS_LIST[j]["right_move"]["axis"]["z-axis"]))

        left_avg_axis["x-axis"] += calculate_average(MEASUREMENTS_LIST[j]["left_move"]["axis"]["x-axis"], len(MEASUREMENTS_LIST[j]["left_move"]["axis"]["x-axis"]))
        left_avg_axis["y-axis"] += calculate_average(MEASUREMENTS_LIST[j]["left_move"]["axis"]["y-axis"], len(MEASUREMENTS_LIST[j]["left_move"]["axis"]["y-axis"]))
        left_avg_axis["z-axis"] += calculate_average(MEASUREMENTS_LIST[j]["left_move"]["axis"]["z-axis"], len(MEASUREMENTS_LIST[j]["left_move"]["axis"]["z-axis"]))

        up_avg_axis["x-axis"] += calculate_average(MEASUREMENTS_LIST[j]["up"]["axis"]["x-axis"], len(MEASUREMENTS_LIST[j]["up"]["axis"]["x-axis"]))
        up_avg_axis["y-axis"] += calculate_average(MEASUREMENTS_LIST[j]["up"]["axis"]["y-axis"], len(MEASUREMENTS_LIST[j]["up"]["axis"]["y-axis"]))
        up_avg_axis["z-axis"] += calculate_average(MEASUREMENTS_LIST[j]["up"]["axis"]["z-axis"], len(MEASUREMENTS_LIST[j]["up"]["axis"]["z-axis"]))
        
        down_avg_axis["x-axis"] += calculate_average(MEASUREMENTS_LIST[j]["down"]["axis"]["x-axis"], len(MEASUREMENTS_LIST[j]["down"]["axis"]["x-axis"]))
        down_avg_axis["y-axis"] += calculate_average(MEASUREMENTS_LIST[j]["down"]["axis"]["y-axis"], len(MEASUREMENTS_LIST[j]["down"]["axis"]["y-axis"]))
        down_avg_axis["z-axis"] += calculate_average(MEASUREMENTS_LIST[j]["down"]["axis"]["z-axis"], len(MEASUREMENTS_LIST[j]["down"]["axis"]["z-axis"]))

        rotate_r_avg_axis["x-axis"] += calculate_average(MEASUREMENTS_LIST[j]["rotate_right"]["axis"]["x-axis"], len(MEASUREMENTS_LIST[j]["rotate_right"]["axis"]["x-axis"]))
        rotate_r_avg_axis["y-axis"] += calculate_average(MEASUREMENTS_LIST[j]["rotate_right"]["axis"]["y-axis"], len(MEASUREMENTS_LIST[j]["rotate_right"]["axis"]["y-axis"]))
        rotate_r_avg_axis["z-axis"] += calculate_average(MEASUREMENTS_LIST[j]["rotate_right"]["axis"]["z-axis"], len(MEASUREMENTS_LIST[j]["rotate_right"]["axis"]["z-axis"]))

        rotate_l_avg_axis["x-axis"] += calculate_average(MEASUREMENTS_LIST[j]["rotate_left"]["axis"]["x-axis"], len(MEASUREMENTS_LIST[j]["rotate_left"]["axis"]["x-axis"]))
        rotate_l_avg_axis["y-axis"] += calculate_average(MEASUREMENTS_LIST[j]["rotate_left"]["axis"]["y-axis"], len(MEASUREMENTS_LIST[j]["rotate_left"]["axis"]["y-axis"]))
        rotate_l_avg_axis["z-axis"] += calculate_average(MEASUREMENTS_LIST[j]["rotate_left"]["axis"]["z-axis"], len(MEASUREMENTS_LIST[j]["rotate_left"]["axis"]["z-axis"]))

        zoom_in_avg_axis["x-axis"] += calculate_average(MEASUREMENTS_LIST[j]["zoom_in"]["axis"]["x-axis"], len(MEASUREMENTS_LIST[j]["zoom_in"]["axis"]["x-axis"]))
        zoom_in_avg_axis["y-axis"] += calculate_average(MEASUREMENTS_LIST[j]["zoom_in"]["axis"]["y-axis"], len(MEASUREMENTS_LIST[j]["zoom_in"]["axis"]["y-axis"]))
        zoom_in_avg_axis["z-axis"] += calculate_average(MEASUREMENTS_LIST[j]["zoom_in"]["axis"]["z-axis"], len(MEASUREMENTS_LIST[j]["zoom_in"]["axis"]["z-axis"]))

        zoom_out_avg_axis["x-axis"] += calculate_average(MEASUREMENTS_LIST[j]["zoom_out"]["axis"]["x-axis"], len(MEASUREMENTS_LIST[j]["zoom_out"]["axis"]["x-axis"]))
        zoom_out_avg_axis["y-axis"] += calculate_average(MEASUREMENTS_LIST[j]["zoom_out"]["axis"]["y-axis"], len(MEASUREMENTS_LIST[j]["zoom_out"]["axis"]["y-axis"]))
        zoom_out_avg_axis["z-axis"] += calculate_average(MEASUREMENTS_LIST[j]["zoom_out"]["axis"]["z-axis"], len(MEASUREMENTS_LIST[j]["zoom_out"]["axis"]["z-axis"]))

        total_time_spent    += MEASUREMENTS_LIST[j]["total_time_spent"]
        video_preview_count += MEASUREMENTS_LIST[j]["video_preview_count"]
        model_info_count    += MEASUREMENTS_LIST[j]["model_info_count"]
    # print "rotate_right_popularity: " + str(rotate_right_count/float(total_projections)*100)



    total_projections = (right_move_count+left_move_count+up_count+down_count+rotate_right_count+rotate_left_count+zoom_in_count+zoom_out_count)


    RETURN_ITEMS["right_move"]["popularity"] = right_move_count/float(total_projections)*100
    RETURN_ITEMS["right_move"]["axis_avg"]["x-axis"] = division_helper(right_avg_axis["x-axis"], right_move_count)
    RETURN_ITEMS["right_move"]["axis_avg"]["y-axis"] = division_helper(right_avg_axis["y-axis"], right_move_count)
    RETURN_ITEMS["right_move"]["axis_avg"]["z-axis"] = division_helper(right_avg_axis["z-axis"], right_move_count)

    RETURN_ITEMS["left_move"]["popularity"] = left_move_count/float(total_projections)*100
    RETURN_ITEMS["left_move"]["axis_avg"]["x-axis"] = division_helper(left_avg_axis["x-axis"], left_move_count)
    RETURN_ITEMS["left_move"]["axis_avg"]["y-axis"] = division_helper(left_avg_axis["y-axis"], left_move_count)
    RETURN_ITEMS["left_move"]["axis_avg"]["z-axis"] = division_helper(left_avg_axis["z-axis"], left_move_count)

    RETURN_ITEMS["up"]["popularity"] = up_count/float(total_projections)*100
    RETURN_ITEMS["up"]["axis_avg"]["x-axis"] = division_helper(up_avg_axis["x-axis"], up_count)
    RETURN_ITEMS["up"]["axis_avg"]["y-axis"] = division_helper(up_avg_axis["y-axis"], up_count)
    RETURN_ITEMS["up"]["axis_avg"]["z-axis"] = division_helper(up_avg_axis["z-axis"], up_count)

    RETURN_ITEMS["down"]["popularity"] = down_count/float(total_projections)*100
    RETURN_ITEMS["down"]["axis_avg"]["x-axis"] = division_helper(down_avg_axis["x-axis"], down_count)
    RETURN_ITEMS["down"]["axis_avg"]["y-axis"] = division_helper(down_avg_axis["y-axis"], down_count)
    RETURN_ITEMS["down"]["axis_avg"]["z-axis"] = division_helper(down_avg_axis["z-axis"], down_count)  

    RETURN_ITEMS["rotate_right"]["popularity"] = rotate_right_count/float(total_projections)*100
    RETURN_ITEMS["rotate_right"]["axis_avg"]["x-axis"] = division_helper(rotate_r_avg_axis["x-axis"], rotate_right_count)
    RETURN_ITEMS["rotate_right"]["axis_avg"]["y-axis"] = division_helper(rotate_r_avg_axis["y-axis"], rotate_right_count)
    RETURN_ITEMS["rotate_right"]["axis_avg"]["z-axis"] = division_helper(rotate_r_avg_axis["z-axis"], rotate_right_count)

    RETURN_ITEMS["rotate_left"]["popularity"] = rotate_left_count/float(total_projections)*100
    RETURN_ITEMS["rotate_left"]["axis_avg"]["x-axis"] = division_helper(rotate_l_avg_axis["x-axis"], rotate_left_count)
    RETURN_ITEMS["rotate_left"]["axis_avg"]["y-axis"] = division_helper(rotate_l_avg_axis["y-axis"], rotate_left_count)
    RETURN_ITEMS["rotate_left"]["axis_avg"]["z-axis"] = division_helper(rotate_l_avg_axis["z-axis"], rotate_left_count)

    RETURN_ITEMS["zoom_in"]["popularity"] = zoom_in_count/float(total_projections)*100
    RETURN_ITEMS["zoom_in"]["axis_avg"]["x-axis"] = division_helper(zoom_in_avg_axis["x-axis"], zoom_in_count)
    RETURN_ITEMS["zoom_in"]["axis_avg"]["y-axis"] = division_helper(zoom_in_avg_axis["y-axis"], zoom_in_count)
    RETURN_ITEMS["zoom_in"]["axis_avg"]["z-axis"] = division_helper(zoom_in_avg_axis["y-axis"], zoom_in_count)

    RETURN_ITEMS["zoom_out"]["popularity"] = zoom_out_count/float(total_projections)*100
    RETURN_ITEMS["zoom_out"]["axis_avg"]["x-axis"] = division_helper(zoom_out_avg_axis["x-axis"], zoom_out_count)
    RETURN_ITEMS["zoom_out"]["axis_avg"]["y-axis"] = division_helper(zoom_out_avg_axis["y-axis"], zoom_out_count)
    RETURN_ITEMS["zoom_out"]["axis_avg"]["z-axis"] = division_helper(zoom_out_avg_axis["z-axis"], zoom_out_count)

    RETURN_ITEMS["model_info_count"]    =  model_info_count
    RETURN_ITEMS["video_preview_count"] =  video_preview_count
    RETURN_ITEMS["total_time_spent"]    =  total_time_spent

    return RETURN_ITEMS
    # print total_projections
    # tp = rotate_right_count/float(total_projections)
    # print tp*100
    # print "".join(["rotate_right popularity: ", str (rotate_right_count/total_projections)])

#########################################################################################

def division_helper(num_a, num_b):
    if num_b == 0:
        return 0
    else:
        return num_a/float(num_b)
#########################################################################################


def get_model_measurements_helper(namespace, model_id, DB_ANALYTICS, DB_USERS, DB_NEW_MODELS, MODELS_COLLECTION):
    USER_MEASUREMENTS_COLLECTION = "user_measurements"

    if (isValidNamespace(namespace, DB_USERS) or isValidOrgNamespace(namespace, DB_USERS)) and isValidModelId(model_id, DB_NEW_MODELS, MODELS_COLLECTION):
        response = DB_ANALYTICS[USER_MEASUREMENTS_COLLECTION].find({namespace: {"$exists": 1}}).count()

        if response == 0:
            return json.dumps({"message": "Measurements data not available for this user."}), 400, {'ContentType': 'application/json'}
        else:
            resp = DB_ANALYTICS[USER_MEASUREMENTS_COLLECTION].find_one({namespace: {"$exists": 1}})
            # del resp["_id"]
            # print type(resp)
            # print json.dumps(resp)
            if model_id in resp[namespace]:
                # print resp[namespace][model_id]
                return process_model_measurements(model_id, resp[namespace][model_id], DB_ANALYTICS)
                # return json.dumps({"message": "testing success"}), 200, {'ContentType': 'application/json'}
            else:
                return json.dumps({"message": "Measurements data not available for this model, this user has not downloaded this model."}), 400, {'ContentType': 'application/json'}
    else:
        return json.dumps({"message": "Invalid namespace/model_id"}), 400, {'ContentType': 'application/json'}
#########################################################################################

def process_model_measurements(model_id, measurements_diction ,DB_ANALYTICS):

    # print measurements_diction

    RETURN_ITEMS = {}

    RETURN_ITEMS["right_move"] =    {"popularity":0.0,"axis_avg":{"x-axis":0.0,"y-axis":0.0,"z-axis":0.0}}
    RETURN_ITEMS["left_move"] =     {"popularity":0.0,"axis_avg":{"x-axis":0.0,"y-axis":0.0,"z-axis":0.0}}
    RETURN_ITEMS["up"] =            {"popularity":0.0,"axis_avg":{"x-axis":0.0,"y-axis":0.0,"z-axis":0.0}}
    RETURN_ITEMS["down"] =          {"popularity":0.0,"axis_avg":{"x-axis":0.0,"y-axis":0.0,"z-axis":0.0}}
    RETURN_ITEMS["rotate_left"] =   {"popularity":0.0,"axis_avg":{"x-axis":0.0,"y-axis":0.0,"z-axis":0.0}}
    RETURN_ITEMS["rotate_right"] =  {"popularity":0.0,"axis_avg":{"x-axis":0.0,"y-axis":0.0,"z-axis":0.0}}
    RETURN_ITEMS["zoom_in"] =       {"popularity":0.0,"axis_avg":{"x-axis":0.0,"y-axis":0.0,"z-axis":0.0}}
    RETURN_ITEMS["zoom_out"] =      {"popularity":0.0,"axis_avg":{"x-axis":0.0,"y-axis":0.0,"z-axis":0.0}}

    RETURN_ITEMS["model_info_count"] = 0
    RETURN_ITEMS["video_preview_count"] = 0


    RETURN_ITEMS["right_move"]["popularity"] = measurements_diction["right_move"]["count"]
    RETURN_ITEMS["right_move"]["axis_avg"]["x-axis"] = calculate_average(measurements_diction["right_move"]["axis"]["x-axis"], len(measurements_diction["right_move"]["axis"]["x-axis"]))
    RETURN_ITEMS["right_move"]["axis_avg"]["y-axis"] = calculate_average(measurements_diction["right_move"]["axis"]["y-axis"], len(measurements_diction["right_move"]["axis"]["y-axis"]))
    RETURN_ITEMS["right_move"]["axis_avg"]["z-axis"] = calculate_average(measurements_diction["right_move"]["axis"]["z-axis"], len(measurements_diction["right_move"]["axis"]["z-axis"]))

    RETURN_ITEMS["left_move"]["popularity"] = measurements_diction["left_move"]["count"]
    RETURN_ITEMS["left_move"]["axis_avg"]["x-axis"] = calculate_average(measurements_diction["left_move"]["axis"]["x-axis"], len(measurements_diction["left_move"]["axis"]["x-axis"]))
    RETURN_ITEMS["left_move"]["axis_avg"]["y-axis"] = calculate_average(measurements_diction["left_move"]["axis"]["y-axis"], len(measurements_diction["left_move"]["axis"]["y-axis"]))
    RETURN_ITEMS["left_move"]["axis_avg"]["z-axis"] = calculate_average(measurements_diction["left_move"]["axis"]["z-axis"], len(measurements_diction["left_move"]["axis"]["z-axis"]))

    RETURN_ITEMS["up"]["popularity"] = measurements_diction["up"]["count"]
    RETURN_ITEMS["up"]["axis_avg"]["x-axis"] = calculate_average(measurements_diction["up"]["axis"]["x-axis"], len(measurements_diction["up"]["axis"]["x-axis"]))
    RETURN_ITEMS["up"]["axis_avg"]["y-axis"] = calculate_average(measurements_diction["up"]["axis"]["y-axis"], len(measurements_diction["up"]["axis"]["y-axis"]))
    RETURN_ITEMS["up"]["axis_avg"]["z-axis"] = calculate_average(measurements_diction["up"]["axis"]["z-axis"], len(measurements_diction["up"]["axis"]["z-axis"]))

    RETURN_ITEMS["down"]["popularity"] = measurements_diction["down"]["count"]
    RETURN_ITEMS["down"]["axis_avg"]["x-axis"] = calculate_average(measurements_diction["down"]["axis"]["x-axis"], len(measurements_diction["down"]["axis"]["x-axis"]))
    RETURN_ITEMS["down"]["axis_avg"]["y-axis"] = calculate_average(measurements_diction["down"]["axis"]["y-axis"], len(measurements_diction["down"]["axis"]["y-axis"]))
    RETURN_ITEMS["down"]["axis_avg"]["z-axis"] = calculate_average(measurements_diction["down"]["axis"]["z-axis"], len(measurements_diction["down"]["axis"]["z-axis"]))

    RETURN_ITEMS["rotate_right"]["popularity"] = measurements_diction["rotate_right"]["count"]
    RETURN_ITEMS["rotate_right"]["axis_avg"]["x-axis"] = calculate_average(measurements_diction["rotate_right"]["axis"]["x-axis"], len(measurements_diction["rotate_right"]["axis"]["x-axis"]))
    RETURN_ITEMS["rotate_right"]["axis_avg"]["y-axis"] = calculate_average(measurements_diction["rotate_right"]["axis"]["y-axis"], len(measurements_diction["rotate_right"]["axis"]["y-axis"]))
    RETURN_ITEMS["rotate_right"]["axis_avg"]["z-axis"] = calculate_average(measurements_diction["rotate_right"]["axis"]["z-axis"], len(measurements_diction["rotate_right"]["axis"]["z-axis"]))

    RETURN_ITEMS["rotate_left"]["popularity"] = measurements_diction["rotate_left"]["count"]
    RETURN_ITEMS["rotate_left"]["axis_avg"]["x-axis"] = calculate_average(measurements_diction["rotate_left"]["axis"]["x-axis"], len(measurements_diction["rotate_left"]["axis"]["x-axis"]))
    RETURN_ITEMS["rotate_left"]["axis_avg"]["y-axis"] = calculate_average(measurements_diction["rotate_left"]["axis"]["y-axis"], len(measurements_diction["rotate_left"]["axis"]["y-axis"]))
    RETURN_ITEMS["rotate_left"]["axis_avg"]["z-axis"] = calculate_average(measurements_diction["rotate_left"]["axis"]["z-axis"], len(measurements_diction["rotate_left"]["axis"]["z-axis"]))

    RETURN_ITEMS["zoom_in"]["popularity"] = measurements_diction["zoom_in"]["count"]
    RETURN_ITEMS["zoom_in"]["axis_avg"]["x-axis"] = calculate_average(measurements_diction["zoom_in"]["axis"]["x-axis"], len(measurements_diction["zoom_in"]["axis"]["x-axis"]))
    RETURN_ITEMS["zoom_in"]["axis_avg"]["y-axis"] = calculate_average(measurements_diction["zoom_in"]["axis"]["y-axis"], len(measurements_diction["zoom_in"]["axis"]["y-axis"]))
    RETURN_ITEMS["zoom_in"]["axis_avg"]["z-axis"] = calculate_average(measurements_diction["zoom_in"]["axis"]["z-axis"], len(measurements_diction["zoom_in"]["axis"]["z-axis"]))

    RETURN_ITEMS["zoom_out"]["popularity"] = measurements_diction["zoom_out"]["count"]
    RETURN_ITEMS["zoom_out"]["axis_avg"]["x-axis"] = calculate_average(measurements_diction["zoom_out"]["axis"]["x-axis"], len(measurements_diction["zoom_out"]["axis"]["x-axis"]))
    RETURN_ITEMS["zoom_out"]["axis_avg"]["y-axis"] = calculate_average(measurements_diction["zoom_out"]["axis"]["y-axis"], len(measurements_diction["zoom_out"]["axis"]["y-axis"]))
    RETURN_ITEMS["zoom_out"]["axis_avg"]["z-axis"] = calculate_average(measurements_diction["zoom_out"]["axis"]["z-axis"], len(measurements_diction["zoom_out"]["axis"]["z-axis"]))

    RETURN_ITEMS["total_time_spent"] = measurements_diction["total_time_spent"]
    return json.dumps({"message": RETURN_ITEMS}), 200, {'ContentType': 'application/json'}
#########################################################################################

def top_user_models_helper(namespace, app_id ,DB_ANALYTICS, DB_USERS, DB_NEW_MODELS):
    USER_MEASUREMENTS_COLLECTION = "user_measurements"

    if isValidNamespace(namespace, DB_USERS) or isValidOrgNamespace(namespace, DB_USERS):
        response = DB_ANALYTICS[USER_MEASUREMENTS_COLLECTION].find({namespace: {"$exists": 1}}).count()
        if response == 0:
            return json.dumps({"message": "Measurements data not available for this user."}), 400, {'ContentType': 'application/json'}
        else:
            resp = DB_ANALYTICS[USER_MEASUREMENTS_COLLECTION].find_one({namespace: {"$exists": 1}})
            # del resp["_id"]
            # print type(resp)
            # print json.dumps(resp)

            if namespace in resp:
                # print resp[namespace][model_id]
                if app_id == "ar_art":
                    COLLECTION = "fashion"
                elif app_id == "jedi":
                    COLLECTION = "food"

                print(process_top_models(app_id, resp[namespace], DB_ANALYTICS, DB_NEW_MODELS, COLLECTION, namespace, DB_USERS))
                return process_top_models(app_id, resp[namespace], DB_ANALYTICS, DB_NEW_MODELS, COLLECTION, namespace, DB_USERS)
            else:
                return json.dumps({"message": "Measurements data not available for this user."}), 400, {'ContentType': 'application/json'}
    else:
        return json.dumps({"message": "Invalid namespace."}), 400, {'ContentType': 'application/json'}

#########################################################################################

def process_top_models(app_id, measurements_diction, DB_ANALYTICS, DB_NEW_MODELS, COLLECTION, namespace, DB_USERS):
    if len(measurements_diction) <= 5:
        print("models less than 5")

        RETURN_ITEMS = []

        for model in measurements_diction.values():
            # print("========================")
            # print(model)
            # print("========================")
            if isinstance(model, dict):
                if "total_projections" in model:
                     RETURN_ITEMS.append(list(measurements_diction.keys())[list(measurements_diction.values()).index(model)])
        

        print(RETURN_ITEMS)
        # RETURN_DICTION =    {}
        FINAL_RETURN =      []

        for model_id in RETURN_ITEMS:
            # print(model_id)
            # print(COLLECTION)
            collections = get_all_collections(DB_NEW_MODELS)

            for collection in collections:
                resp = DB_NEW_MODELS[collection].find_one({"_id": ObjectId(model_id)})
                if resp:
                    if resp["format"] == ".scn" and app_id == "jedi":
                        del resp["_id"]
                        RETURN_DICTION =    {}
                        RETURN_DICTION["model_id"] =        model_id
                        RETURN_DICTION["name"] =            resp["basic_info"]["name"]
                        RETURN_DICTION["manufacturer"] =    resp["basic_info"]["manufacturer"]
                        RETURN_DICTION["thumbnail"] =       resp["model_files"]["thumbnail"]
                        RETURN_DICTION["description"] =     resp["description"]
                        FINAL_RETURN.append(RETURN_DICTION)
                    if resp["format"] == ".sfb" and app_id == "ar_art":
                        del resp["_id"]
                        RETURN_DICTION =    {}
                        RETURN_DICTION["model_id"] =        model_id
                        RETURN_DICTION["name"] =            resp["basic_info"]["name"]
                        RETURN_DICTION["manufacturer"] =    resp["basic_info"]["manufacturer"]
                        RETURN_DICTION["thumbnail"] =       resp["model_files"]["thumbnail"]
                        RETURN_DICTION["description"] =     resp["description"]
                        FINAL_RETURN.append(RETURN_DICTION)   
                    ########
                    # del resp["_id"]
                    # RETURN_DICTION =    {}
                    # RETURN_DICTION["model_id"] =        model_id
                    # RETURN_DICTION["name"] =            resp["basic_info"]["name"]
                    # RETURN_DICTION["manufacturer"] =    resp["basic_info"]["manufacturer"]
                    # RETURN_DICTION["thumbnail"] =       resp["model_files"]["thumbnail"]
                    # RETURN_DICTION["description"] =     resp["description"]

                    # FINAL_RETURN.append(RETURN_DICTION)          



        # ALL_MODELS = search_all_models_method(namespace, COLLECTION, DB_NEW_MODELS, DB_USERS)
        # print ALL_MODELS
        return json.dumps({"message": FINAL_RETURN}), 200, {'ContentType': 'application/json'}
    
    elif len(measurements_diction) > 5:
        RETURN_ITEMS = []
        temp_diction = {}

        # print json.dumps(measurements_diction)

        # if app_id == "ar_art":
        #     FORMAT = ".sfb"
        # elif app_id == "jedi":
        #     FORMAT = ".scn"

        colls = get_all_collections(DB_NEW_MODELS)
        to_delete = []

        for key, val in measurements_diction.items():
            if key != "total_projections":
                for col in colls:
                    temp = DB_NEW_MODELS[col].find_one({"_id": ObjectId(key)})
                    # if temp["format"] == ".scn" and app_id != "jedi":
                    #     del temp_diction[k]
                    if temp and temp["format"] == ".scn" and app_id == "ar_art":
                        to_delete.append(key)

        for temp_id in to_delete:
            if temp_id in measurements_diction:
                del measurements_diction[temp_id]

        for model in measurements_diction.values():
            # print measurements_diction[k]
            if isinstance(model, dict):
                if "total_projections" in model:
                    temp_diction[list(measurements_diction.keys())[list(measurements_diction.values()).index(model)]] = model["total_projections"]
                     #RETURN_ITEMS.append(list(measurements_diction.keys())[list(measurements_diction.values()).index(model)])

        sorted_temp_diction = sorted(temp_diction.items(), key=operator.itemgetter(1), reverse=True)

        counter = 0
        for val in sorted_temp_diction:
            RETURN_ITEMS.append(val[0])
            counter += 1
            if counter > 4:
                break


        FINAL_RETURN =      []

        print(RETURN_ITEMS)
        for model_id in RETURN_ITEMS:
            collections = get_all_collections(DB_NEW_MODELS)

            for collection in collections:
                resp = DB_NEW_MODELS[collection].find_one({"_id": ObjectId(model_id)})
                if resp:
                    if resp["format"] == ".scn" and app_id == "jedi":
                        del resp["_id"]
                        RETURN_DICTION =    {}
                        RETURN_DICTION["model_id"] =        model_id
                        RETURN_DICTION["name"] =            resp["basic_info"]["name"]
                        RETURN_DICTION["manufacturer"] =    resp["basic_info"]["manufacturer"]
                        RETURN_DICTION["thumbnail"] =       resp["model_files"]["thumbnail"]
                        RETURN_DICTION["description"] =     resp["description"]
                        FINAL_RETURN.append(RETURN_DICTION)
                    if resp["format"] == ".sfb" and app_id == "ar_art":
                        del resp["_id"]
                        RETURN_DICTION =    {}
                        RETURN_DICTION["model_id"] =        model_id
                        RETURN_DICTION["name"] =            resp["basic_info"]["name"]
                        RETURN_DICTION["manufacturer"] =    resp["basic_info"]["manufacturer"]
                        RETURN_DICTION["thumbnail"] =       resp["model_files"]["thumbnail"]
                        RETURN_DICTION["description"] =     resp["description"]
                        FINAL_RETURN.append(RETURN_DICTION)      

        # for model in measurements_diction.values():
        #     if isinstance(model, dict):
        #         if "total_projections" in model:
        #             print model["total_projections"]
        return json.dumps({"message": FINAL_RETURN}), 200, {'ContentType': 'application/json'}
################################################################################################






def upload_model_helper(body, DB_NEW_MODELS):
    # COLLECTION = 'food'
    model_name = replace_name(body['name'])
    

    COLLECTION = body["category"]

    BASE_PATH   =   '/home/btech/models_data/android/'
    # BASE_S3_URL =   'https://s3.amazonaws.com/jediar/models/' + body['name'] + '/'
    BASE_S3_URL =   'https://s3.amazonaws.com/jediar/models/' + model_name + '/'

    MODEL_JSON                                  =   {}
    MODEL_JSON['basic_info']                    =   {}
    MODEL_JSON['basic_info']['name']            =   body['name']
    MODEL_JSON['basic_info']['manufacturer']    =   body['manufacturer']
    MODEL_JSON['basic_info']['model']           =   body['model']
    MODEL_JSON['price_related']                 =   {}
    MODEL_JSON['price_related']['price']        =   float(body['price'])
    MODEL_JSON['price_related']['currency']     =   body['price_currency']
    MODEL_JSON['scaling']                       =   {}
    MODEL_JSON['scaling']['x-axis']             =   float(body['scale_x'])
    MODEL_JSON['scaling']['y-axis']             =   float(body['scale_y'])
    MODEL_JSON['scaling']['z-axis']             =   float(body['scale_z'])
    MODEL_JSON['scaling']['scaling_unit']       =   body['scaling_unit']
    #####################################KASHIF###################################
    #environment recognition and tested status default values.  
    MODEL_JSON['tested_status']                 = 0
    MODEL_JSON['hyperlink']                     = ""
    MODEL_JSON['document']                      = ""
    MODEL_JSON['promotional_video']             = ""
    MODEL_JSON['images']                      = []
    ##############################################################################
    # PATH = BASE_PATH + body['name']
    PATH = BASE_PATH + model_name
    try:
        os.mkdir(PATH)
    except OSError as e:
        print (str(e))
        return (
         json.dumps({'message': 'directory already exists'}), 500, {'ContentType': 'application/json'})

    # MODEL_FILE_PATH = PATH + '/' + body['name'] + body['model_format']
    MODEL_FILE_PATH = PATH + '/' + model_name + body['model_format']
    ###################### WORKING ###############
    # model_b64 = str.encode(body['model_base64'])
    # model_base64_decode = base64.decodestring(model_b64)

    model_base64_decode = base64.b64decode(body['model_base64'])
    # model_base64_decode = base64.decodestring(body['model_base64'])
    model_file = open(MODEL_FILE_PATH, 'wb')
    model_file.write(model_base64_decode)
    model_file.close()
    # THUMBNAIL_FILE_PATH = PATH + '/' + body["name"] + '_thumbnail' + body['thumbnail_format']
    THUMBNAIL_FILE_PATH = PATH + '/' + model_name + '_thumbnail' + body['thumbnail_format']


    thumbnail_base64_decode = base64.b64decode(body['thumbnail_base64'])
    # thumbnail_base64_decode = base64.decodestring(body['thumbnail_base64'])
    
    thumbnail_file = open(THUMBNAIL_FILE_PATH, 'wb')
    thumbnail_file.write(thumbnail_base64_decode)
    thumbnail_file.close()
    VIDEO_FILE_PATH = PATH + '/' + 'modelvideo' + body['video_format']

    video_base64_decode = base64.b64decode(body['video_base64'])
    #video_base64_decode = base64.decodestring(body['video_base64'])

    video_file = open(VIDEO_FILE_PATH, 'wb')
    video_file.write(video_base64_decode)
    video_file.close()

    #############Document##################################################################
    if 'document_base64' in body:

        DOCUMENT_FILE_PATH = PATH + '/' + 'modeldocument' + body['document_format']
        document_base64_decode = base64.b64decode(body['document_base64'])
        #video_base64_decode = base64.decodestring(body['video_base64'])
        document_file = open(DOCUMENT_FILE_PATH, 'wb')
        document_file.write(document_base64_decode)
        document_file.close()
        MODEL_JSON['document'] = BASE_S3_URL + 'modeldocument' + body['document_format']
    #######################################################################################
    #############Promotional Video#########################################################
    if 'promotional_video_base64' in body:
        PROMOTIONAL_VIDEO_PATH = PATH + '/' + 'promotionalvideo' + body['promotional_video_format']
        promotional_video_base64_decode = base64.b64decode(body['promotional_video_base64'])
        #video_base64_decode = base64.decodestring(body['video_base64'])
        promotional_video = open(PROMOTIONAL_VIDEO_PATH, 'wb')
        promotional_video.write(promotional_video_base64_decode)
        promotional_video.close()
        MODEL_JSON['promotional_video'] = BASE_S3_URL + 'promotionalvideo' + body['promotional_video_format']
    #######################################################################################
    # MODEL_LOCATION = ('').join([PATH, '/', body['name']])
    MODEL_LOCATION = ('').join([PATH, '/', model_name])
    COMPRESSED_LOCATION = ('').join([MODEL_LOCATION, '.zip'])
    MODEL_JSON['cryptographic_info'] = {}
    public_key, private_key = generate_keypair()
    compress_model(MODEL_FILE_PATH, COMPRESSED_LOCATION)
    zipped_sha1 = calculate_hash_of_file(COMPRESSED_LOCATION)
    encrypted_msg = encrypt(private_key, zipped_sha1)
    unzipped_sha1 = calculate_hash_of_file(MODEL_FILE_PATH)
    unzipped_size = os.stat(MODEL_FILE_PATH).st_size
    zipped_size = os.stat(COMPRESSED_LOCATION).st_size
    MODEL_JSON['cryptographic_info']['digital_sig'] = encrypted_msg
    MODEL_JSON['cryptographic_info']['public_key'] = public_key
    # MODEL_JSON['cryptographic_info']['private_key'] = private_key
    MODEL_JSON['cryptographic_info']['model_sha1'] = unzipped_sha1
    MODEL_JSON['cryptographic_info']['unzipped_size'] = unzipped_size
    MODEL_JSON['cryptographic_info']['zipped_size'] = zipped_size
    MODEL_JSON['analytics'] = {}
    MODEL_JSON['analytics']['shares_count'] = 0
    MODEL_JSON['analytics']['download_count'] = 0
    MODEL_JSON['analytics']['search_appearances'] = 0
    MODEL_JSON['analytics']['survey'] = body['survey']
    MODEL_JSON['video'] = BASE_S3_URL + 'modelvideo' + body['video_format']
    # MODEL_JSON['promotional_video'] = "https://jediar.s3.amazonaws.com/promotionalvideo.mp4"
    MODEL_JSON['model_files'] = {}
    # MODEL_JSON['model_files']['3d_model_file'] = BASE_S3_URL + body['name'] + '.zip'
    MODEL_JSON['model_files']['3d_model_file'] = BASE_S3_URL + model_name + '.zip'
    # MODEL_JSON['model_files']['thumbnail'] = BASE_S3_URL + body["name"]+'_thumbnail' + body['thumbnail_format']
    MODEL_JSON['model_files']['thumbnail'] = BASE_S3_URL + model_name +'_thumbnail' + body['thumbnail_format']
    MODEL_JSON['model_files']['textures'] = []
    if body['textures']:
        for i in range(len(body['textures'])):
            TEXTURE_FILE_PATH = PATH + '/' + body['textures'][i]['file_name']
            texture_base64_decode = base64.b64decode(body['textures'][i]['texture_base64'])
            #texture_base64_decode = base64.decodestring(body['textures'][i]['texture_base64'])
            texture_file = open(TEXTURE_FILE_PATH, 'wb')
            texture_file.write(texture_base64_decode)
            texture_file.close()
            TEXTURE_S3_PATH = BASE_S3_URL + body['textures'][i]['file_name']
            MODEL_JSON['model_files']['textures'].append(TEXTURE_S3_PATH)
    #add addtional images if given by user.
    if 'images' in body:
        for i in range(len(body['images'])):
            IMAGE_FILE_PATH = PATH + '/' + body['images'][i]['file_name']
            image_base64_decode = base64.b64decode(body['images'][i]['image_base64'])
            #image_base64_decode = base64.decodestring(body['images'][i]['texture_base64'])
            image_file = open(IMAGE_FILE_PATH, 'wb')
            image_file.write(image_base64_decode)
            image_file.close()
            IMAGE_S3_PATH = BASE_S3_URL + body['images'][i]['file_name']
            MODEL_JSON['images'].append(IMAGE_S3_PATH)
    MODEL_JSON['category'] = body['category']
    MODEL_JSON['manufacturing_date'] = body['manufacturing_date']
    # MODEL_JSON['owner_id'] = body['namespace']
    MODEL_JSON['owner_id'] = "org6150"
    MODEL_JSON["purchase_status"] = 1
    MODEL_JSON['format'] = body['model_format']
    MODEL_JSON['license'] = body['license']
    MODEL_JSON['description'] = body['description']
    if 'hyperlink' in body:
        MODEL_JSON['hyperlink'] = body['hyperlink']
        

    MODEL_JSON['additional_info'] = body['additional_info']
    MODEL_JSON['questionnaire'] = [
     'Does the restaurant have sufficient selection of healthy choices?',
     'Does the restaurant have family friendly environment?',
     'How do you rate the cleanliness of restaurant?',
     'How would you rate the food?', 'How would you rate the ambiance?',
     'How would you rate the service?']
    MODEL_JSON['comment_feed'] = []
    mongo_id = insert_in_db(DB_NEW_MODELS, COLLECTION, MODEL_JSON)
    generate_qrcode(COLLECTION + '_' + mongo_id, model_name)
    # MODEL_DIR = BASE_PATH + MODEL_JSON['basic_info']['name'] + '/'
    MODEL_DIR = BASE_PATH + model_name + '/'
    # upload model data to s3 server
    # upload_files_to_s3(MODEL_DIR, MODEL_JSON['basic_info']['name'])
    if upload_files_to_s3(MODEL_DIR, model_name):
        # delete directory from server storage
        shutil.rmtree(MODEL_DIR)
        return (
         json.dumps({'message': 'Success'}), 200, {'ContentType': 'application/json'})
    else:
        return json.dumps({'message': 'Upload error'}), 500, {'ContentType': 'application/json'}

##############################################################################
############################# HELPER METHODS #################################
##############################################################################
# helper method
def replace_name(name):
    '''Rename the (model)name string, convert to lower case, replace spaces \
        with underscore.'''

    # convert to lower case
    lowercase = name.lower()
    # replace spaces with underscore
    rename = lowercase.replace(" ", "_")
    # return the new string(name)
    return rename
##############################################################################

# helper
def send_forget_password_email(USER_EMAIL, USERNAME, token):

    #### Constants
    EMAIL_FROM              =   'noreply.support@dmoat.com' 
    EMAIL_LOGIN             =   'support@dmoat.com' 
    EMAIL_PASSWD            =   'uR6-8kL-gJy-Lem'
    SMTP_SERVER             =   'secure.emailsrvr.com'
    SMTP_PORT               =   587

    SUBJECT                 =   'Subject'
    FROM                    =   'From'
    TO                      =   'To'
    CONTENT_TYPE            =   'Content-Type'
    TEXT_HTML               =   'text/html'
    DEAR                    =   '<p>Dear <font size="3"><b>'
    EMAIL_SIGNATURE         =   '<p>Regards,<br>\
                                Admin<br>'
    EMAIL_BODY_FIRST_HALF   =   '</b>,<br><br></p>\
                                <p>Your forget password information is: </p>\
                                <p>'
    EMAIL_BODY_SECOND_HALF  =   '<b></p>'
    U_NAME = "USERNAME : "
    TOKEN = "RESET TOKEN:"

    try:
        msg = email.message.Message()
        msg[SUBJECT] = "Username Jedi Enterprise!"
        msg[FROM] = EMAIL_FROM
        msg[TO] = USER_EMAIL
        msg.add_header(CONTENT_TYPE, TEXT_HTML)

        body = "".join([DEAR, EMAIL_BODY_FIRST_HALF,U_NAME, USERNAME,EMAIL_BODY_SECOND_HALF, TOKEN, token, EMAIL_BODY_SECOND_HALF, EMAIL_SIGNATURE])

        msg.set_payload(body)
        s = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        s.ehlo()
        s.starttls()
        s.ehlo()
        s.login(EMAIL_LOGIN,EMAIL_PASSWD)
        s.sendmail(msg[FROM], [msg[TO]], msg.as_string())
        s.quit()
        return True
    except Exception as e:
        print ("".join(["Exception in send_email: ", str(e)]))
        return False
##############################################################################

################################### MODEL UPLOAD HELPERS ################################
#########################################################################################
# helper
def zipdir(path, ziph):
    #print 'Path: ' + path
    for root, dirs, files in os.walk(path):
        for file in files:
            ziph.write(os.path.join(root, file), file)
#########################################################################################
# helper
def compress_model(model_location, compressed_location):
    try:
        my_zip = zipfile.ZipFile(compressed_location, 'w', zipfile.ZIP_DEFLATED)
        my_zip.write(model_location, basename(model_location))
        my_zip.close()
    except Exception as e:
        print (str(e))
        # print ('').join(['compress_model, models_related : ', str(e)])
#########################################################################################
# helper
def calculate_hash_of_file(filename):
    BUF_SIZE = 65536
    file = open(filename, 'rb')
    sha1 = hashlib.sha1()
    while True:
        data = file.read(BUF_SIZE)
        if not data:
            break
        sha1.update(data)

    hsh = sha1.hexdigest()
    return hsh
#########################################################################################
# helper
def generate_qrcode(qr_string, name):
    qr_name = "/home/btech/qrcodes/"+ name + '.png'
    qr = pyqrcode.create(qr_string)
    qr.png(qr_name, scale=2)
#########################################################################################
# helper
def insert_in_db(DB_NEW_MODELS, COLLECTION, DATA):
    response = DB_NEW_MODELS[COLLECTION].insert(DATA)
    print ('==============================')
    print (response)
    print ('==============================')
    return str(response)
#########################################################################################
############################## MODEL UPLOAD HELPERS (END) ###############################


def mask_email(email):
    if email:
        for i in range(len(email)):
            if i <= 2:
                continue
            else:
                if email[i] == '@':
                    i+=2
                    continue
                email[i] = '*'
    
    return email
#####################################################################

# helper
def isValidUsername(username, DB_USERS):
    USERS_COLLECTION    = "users_data"
    ORGS_COLLECTION     = "organizations_data"

    users_response  = DB_USERS[USERS_COLLECTION].find_one({"username": username})
    orgs_response   = DB_USERS[ORGS_COLLECTION].find_one({"username": username})

    if users_response or orgs_response:
        return True
    else:
        return False
##############################################################################

# helper
def get_token():
    token = 'fgtpswd' + str(random.randint(10000, 99999))
    return token
##############################################################################


def get_namespace_and_email(email, DB_USERS):
    USERS_COLLECTION    = "users_data"
    ORGS_COLLECTION     = "organizations_data"

    users_response  = DB_USERS[USERS_COLLECTION].find_one({"email": email})
    orgs_response   = DB_USERS[ORGS_COLLECTION].find_one({"email": email})
    if users_response:
        del users_response["_id"]
        # print(users_response)
        return (users_response["namespace"], users_response["username"])
    elif orgs_response:
        del orgs_response["_id"]
        # print(orgs_response)
        return (orgs_response["namespace"], orgs_response["username"])
    else:
        return None, None
##############################################################################

##############################################################################

# helper
def isValidUserNamespace(namespace, DB_USERS):
    USERS_COLLECTION    = "users_data"

    response = DB_USERS[USERS_COLLECTION].find({"namespace": namespace}).count()

    if response == 0 or response < 0:
        return False
    else:
        return True
##############################################################################

# helper
def isValidOrgNamespace(namespace, DB_USERS):
    ORGS_COLLECTION     = "organizations_data"

    response = DB_USERS[ORGS_COLLECTION].find({"namespace": namespace}).count()

    if response == 0 or response < 0:
        return False
    else:
        return True
##############################################################################

def process_delete_model(model_id, category, DB_NEW_MODELS):
    response = DB_NEW_MODELS[category].find_one({"_id": ObjectId(model_id)})
    name = response["basic_info"]["name"]
    f=open("deleted_models.txt", "a+")
    f.write("Model name : "  + name)
    f.close()
    if response:
        delete_response = DB_NEW_MODELS[category].remove({"_id": ObjectId(model_id)})
        # TODO: Delete model dir from S3 as well
        return json.dumps({"message": "Deleted successfully"}), 200, {'ContentType': 'application/json'}
    else:
        return json.dumps({"message": "Invalid model id/category"}), 400, {'ContentType': 'application/json'}
##############################################################################



################################KASHIF######################################

# helper
def get_categories_list(namespace, app_id, DB_USERS, DB_NEW_MODELS):
    # TODO: (Kashif) Complete this method and test it.

    '''fetch list of all (model)categories
        Args: namespace, app_id
        Returns: list of all categories and their thumbnails
        Return format: [{"thumbnail": "", "category_name": ""}, {}]
        '''
    # local constants
    
    
    # check if namespace is valid or not
    if isValidNamespace(namespace, DB_USERS) or isValidOrgNamespace(namespace, DB_USERS):
        # fetch list of categories
        RETURN_LIST = []

        categories_list = get_all_collections(DB_NEW_MODELS)

        for category in categories_list:
            if category == ' ':
                print("Test")
                DB_NEW_MODELS[category].rename("Empty")
            # RETURN_ITEMS = dict(RETURN_ITEMS)
            # fetch thumbnail of this category
            RETURN_ITEMS    =   {}
            RETURN_ITEMS["category_name"] = category.capitalize()
            RETURN_ITEMS["thumbnail"] =  THUMBNAILS[category]
            # append each category and thumbnail in return list
            if app_id == "jedi" and namespace not in TEST_NAMESPACES:
                if category == "equipment" or category == "fashion":
                    continue
            RETURN_LIST.append(RETURN_ITEMS)
        # loop ends here

        return json.dumps({"message": RETURN_LIST}), 200, {'ContentType': 'application/json'}
    else:
        return json.dumps({"message": "Invalid namespace."}), 400, {'ContentType': 'application/json'}
##############################################################################

# Update testing status method
def set_status(DB_NEW_MODELS):
    # cap_keyword = name.capitalize()
    all_collections = get_all_collections(DB_NEW_MODELS)
    for collection in all_collections:
        response = DB_NEW_MODELS[collection].update({}, {'$set': {'tested_status': 1}}, multi=True)
##############################################################################  
# def set_document(DB_NEW_MODELS):
#     # cap_keyword = name.capitalize()
#     all_collections = get_all_collections(DB_NEW_MODELS)
#     for collection in all_collections:
       
#         response = DB_NEW_MODELS[collection].update({}, {'$set': {'images': []}}, upsert=False, multi=True)  

##############################################################################
#helper
#Update Model if user want.
#Done By :Kashif
#Date: 26/09/2019
def update_model_helper(body, DB_NEW_MODELS):
    process_delete_model(body["model_id"],
                                    body["current_category"],
                                    DB_NEW_MODELS)

    # COLLECTION = 'food'
    model_name = replace_name(body['name'])
    
    model_id = body['model_id']

    COLLECTION = body["category"]

    BASE_PATH   =   '/home/btech/models_data/android/'
    # BASE_S3_URL =   'https://s3.amazonaws.com/jediar/models/' + body['name'] + '/'
    BASE_S3_URL =   'https://s3.amazonaws.com/jediar/models/' + model_name + '/'
    MODEL_JSON                                  =   {}
    MODEL_JSON['_id']                           =  ObjectId(model_id)
    MODEL_JSON['basic_info']                    =   {}
    MODEL_JSON['basic_info']['name']            =   body['name']
    MODEL_JSON['basic_info']['manufacturer']    =   body['manufacturer']
    MODEL_JSON['basic_info']['model']           =   body['model']
    MODEL_JSON['price_related']                 =   {}
    MODEL_JSON['price_related']['price']        =   float(body['price'])
    MODEL_JSON['price_related']['currency']     =   body['price_currency']
    MODEL_JSON['scaling']                       =   {}
    MODEL_JSON['scaling']['x-axis']             =   float(body['scale_x'])
    MODEL_JSON['scaling']['y-axis']             =   float(body['scale_y'])
    MODEL_JSON['scaling']['z-axis']             =   float(body['scale_z'])
    MODEL_JSON['scaling']['scaling_unit']       =   body['scaling_unit']
    #####################################KASHIF###################################
    #environment recognition and tested status default values.  
    MODEL_JSON['tested_status']                 = 0
    MODEL_JSON['hyperlink']                     = ""
    MODEL_JSON['document']                      = ""
    MODEL_JSON['promotional_video']             = ""
    MODEL_JSON['images']                      = []
    ##############################################################################
    # PATH = BASE_PATH + body['name']
    PATH = BASE_PATH + model_name
    try:
        os.mkdir(PATH)
    except OSError as e:
        print (str(e))
        return (
         json.dumps({'message': 'directory already exists'}), 500, {'ContentType': 'application/json'})

    # MODEL_FILE_PATH = PATH + '/' + body['name'] + body['model_format']
    MODEL_FILE_PATH = PATH + '/' + model_name + body['model_format']
    ###################### WORKING ###############
    # model_b64 = str.encode(body['model_base64'])
    # model_base64_decode = base64.decodestring(model_b64)

    model_base64_decode = base64.b64decode(body['model_base64'])
    # model_base64_decode = base64.decodestring(body['model_base64'])
    model_file = open(MODEL_FILE_PATH, 'wb')
    model_file.write(model_base64_decode)
    model_file.close()
    # THUMBNAIL_FILE_PATH = PATH + '/' + body["name"] + '_thumbnail' + body['thumbnail_format']
    THUMBNAIL_FILE_PATH = PATH + '/' + model_name + '_thumbnail' + body['thumbnail_format']


    thumbnail_base64_decode = base64.b64decode(body['thumbnail_base64'])
    # thumbnail_base64_decode = base64.decodestring(body['thumbnail_base64'])
    
    thumbnail_file = open(THUMBNAIL_FILE_PATH, 'wb')
    thumbnail_file.write(thumbnail_base64_decode)
    thumbnail_file.close()
    VIDEO_FILE_PATH = PATH + '/' + 'modelvideo' + body['video_format']

    video_base64_decode = base64.b64decode(body['video_base64'])
    #video_base64_decode = base64.decodestring(body['video_base64'])

    video_file = open(VIDEO_FILE_PATH, 'wb')
    video_file.write(video_base64_decode)
    video_file.close()

    #############Document##################################################################
    if 'document_base64' in body:

        DOCUMENT_FILE_PATH = PATH + '/' + 'modeldocument' + body['document_format']
        document_base64_decode = base64.b64decode(body['document_base64'])
        #video_base64_decode = base64.decodestring(body['video_base64'])
        document_file = open(DOCUMENT_FILE_PATH, 'wb')
        document_file.write(document_base64_decode)
        document_file.close()
        MODEL_JSON['document'] = BASE_S3_URL + 'modeldocument' + body['document_format']
    #######################################################################################
    #############Promotional Video#########################################################
    if 'promotional_video_base64' in body:
        PROMOTIONAL_VIDEO_PATH = PATH + '/' + 'promotionalvideo' + body['promotional_video_format']
        promotional_video_base64_decode = base64.b64decode(body['promotional_video_base64'])
        #video_base64_decode = base64.decodestring(body['video_base64'])
        promotional_video = open(PROMOTIONAL_VIDEO_PATH, 'wb')
        promotional_video.write(promotional_video_base64_decode)
        promotional_video.close()
        MODEL_JSON['promotional_video'] = BASE_S3_URL + 'promotionalvideo' + body['promotional_video_format']
    #######################################################################################
    # MODEL_LOCATION = ('').join([PATH, '/', body['name']])
    MODEL_LOCATION = ('').join([PATH, '/', model_name])
    COMPRESSED_LOCATION = ('').join([MODEL_LOCATION, '.zip'])
    MODEL_JSON['cryptographic_info'] = {}
    public_key, private_key = generate_keypair()
    compress_model(MODEL_FILE_PATH, COMPRESSED_LOCATION)
    zipped_sha1 = calculate_hash_of_file(COMPRESSED_LOCATION)
    encrypted_msg = encrypt(private_key, zipped_sha1)
    unzipped_sha1 = calculate_hash_of_file(MODEL_FILE_PATH)
    unzipped_size = os.stat(MODEL_FILE_PATH).st_size
    zipped_size = os.stat(COMPRESSED_LOCATION).st_size
    MODEL_JSON['cryptographic_info']['digital_sig'] = encrypted_msg
    MODEL_JSON['cryptographic_info']['public_key'] = public_key
    # MODEL_JSON['cryptographic_info']['private_key'] = private_key
    MODEL_JSON['cryptographic_info']['model_sha1'] = unzipped_sha1
    MODEL_JSON['cryptographic_info']['unzipped_size'] = unzipped_size
    MODEL_JSON['cryptographic_info']['zipped_size'] = zipped_size
    MODEL_JSON['analytics'] = {}
    MODEL_JSON['analytics']['shares_count'] = 0
    MODEL_JSON['analytics']['download_count'] = 0
    MODEL_JSON['analytics']['search_appearances'] = 0
    MODEL_JSON['analytics']['survey'] = body['survey']
    MODEL_JSON['video'] = BASE_S3_URL + 'modelvideo' + body['video_format']
    # MODEL_JSON['promotional_video'] = "https://jediar.s3.amazonaws.com/promotionalvideo.mp4"
    MODEL_JSON['model_files'] = {}
    # MODEL_JSON['model_files']['3d_model_file'] = BASE_S3_URL + body['name'] + '.zip'
    MODEL_JSON['model_files']['3d_model_file'] = BASE_S3_URL + model_name + '.zip'
    # MODEL_JSON['model_files']['thumbnail'] = BASE_S3_URL + body["name"]+'_thumbnail' + body['thumbnail_format']
    MODEL_JSON['model_files']['thumbnail'] = BASE_S3_URL + model_name +'_thumbnail' + body['thumbnail_format']
    MODEL_JSON['model_files']['textures'] = []
    if body['textures']:
        for i in range(len(body['textures'])):
            TEXTURE_FILE_PATH = PATH + '/' + body['textures'][i]['file_name']
            texture_base64_decode = base64.b64decode(body['textures'][i]['texture_base64'])
            #texture_base64_decode = base64.decodestring(body['textures'][i]['texture_base64'])
            texture_file = open(TEXTURE_FILE_PATH, 'wb')
            texture_file.write(texture_base64_decode)
            texture_file.close()
            TEXTURE_S3_PATH = BASE_S3_URL + body['textures'][i]['file_name']
            MODEL_JSON['model_files']['textures'].append(TEXTURE_S3_PATH)
#add addtional images if given by user.
    if body['images']:
        for i in range(len(body['images'])):
            IMAGE_FILE_PATH = PATH + '/' + body['images'][i]['file_name']
            image_base64_decode = base64.b64decode(body['images'][i]['image_base64'])
            #image_base64_decode = base64.decodestring(body['images'][i]['texture_base64'])
            image_file = open(IMAGE_FILE_PATH, 'wb')
            image_file.write(image_base64_decode)
            image_file.close()
            IMAGE_S3_PATH = BASE_S3_URL + body['images'][i]['file_name']
            MODEL_JSON['images'].append(IMAGE_S3_PATH)

    MODEL_JSON['category'] = body['category']
    MODEL_JSON['manufacturing_date'] = body['manufacturing_date']
    # MODEL_JSON['owner_id'] = body['namespace']
    MODEL_JSON['owner_id'] = "org6150"
    MODEL_JSON["purchase_status"] = 1
    MODEL_JSON['format'] = body['model_format']
    MODEL_JSON['license'] = body['license']
    MODEL_JSON['description'] = body['description']
    if 'hyperlink' in body:
        MODEL_JSON['hyperlink'] = body['hyperlink']
        

    MODEL_JSON['additional_info'] = body['additional_info']
    MODEL_JSON['questionnaire'] = [
     'Does the restaurant have sufficient selection of healthy choices?',
     'Does the restaurant have family friendly environment?',
     'How do you rate the cleanliness of restaurant?',
     'How would you rate the food?', 'How would you rate the ambiance?',
     'How would you rate the service?']
    MODEL_JSON['comment_feed'] = []
    mongo_id = insert_in_db(DB_NEW_MODELS, COLLECTION, MODEL_JSON)
    generate_qrcode(COLLECTION + '_' + mongo_id, model_name)
    # MODEL_DIR = BASE_PATH + MODEL_JSON['basic_info']['name'] + '/'
    MODEL_DIR = BASE_PATH + model_name + '/'
    # upload model data to s3 server
    # upload_files_to_s3(MODEL_DIR, MODEL_JSON['basic_info']['name'])
    if upload_files_to_s3(MODEL_DIR, model_name):
        # delete directory from server storage
        shutil.rmtree(MODEL_DIR)
        return (
         json.dumps({'message': 'Success'}), 200, {'ContentType': 'application/json'})
    else:
        return json.dumps({'message': 'Upload error'}), 500, {'ContentType': 'application/json'}                   
                                  
##############################################################################
def update_survey_helper(body, DB_SURVEYS, DB_USERS):
    ORGS_COLLECTION = 'organizations_data'
    SURVEYS_COLLECTION = 'surveys'
    # print (body)
    survey_title = body['survey_title']
    namespace = body['namespace']
    survey_id = body['survey_id']
    response = DB_SURVEYS[SURVEYS_COLLECTION].find_one({"_id": ObjectId(survey_id)})
    if response:
        DB_SURVEYS[SURVEYS_COLLECTION].update({"_id": ObjectId(survey_id)}, {"$set": {'survey_title':survey_title, \
                                                                    'questions': body['questions']}})
        return json.dumps({"message": "Updated successfully"}), 200, {'ContentType': 'application/json'}
    else:
        return json.dumps({"message": "Invalid Survey id"}), 400, {'ContentType': 'application/json'} 
    
################################Kashif##########################################
def delete_survey_helper(body, DB_SURVEYS, DB_USERS):
    ORGS_COLLECTION = 'organizations_data'
    SURVEYS_COLLECTION = 'surveys'
    # print (body)
    namespace = body['namespace']
    survey_id = body['survey_id']
    response = DB_SURVEYS[SURVEYS_COLLECTION].find_one({"_id": ObjectId(survey_id)})
    if response:
        delete_response = DB_SURVEYS[SURVEYS_COLLECTION].remove({"_id": ObjectId(survey_id)})
        # TODO: Delete model dir from S3 as well
        return json.dumps({"message": "Deleted successfully"}), 200, {'ContentType': 'application/json'}
    else:
        return json.dumps({"message": "Invalid survey id"}), 400, {'ContentType': 'application/json'}
############################Kashif##############################################
#Send email to support.
def send_support_email(USER_EMAIL, request, REQUEST_TYPE, NAMESPACE, EMAIL_SUBJECT):
    SUPPORT_EMAIL = "social@broadstonetech.com"
    DEAR = '<p>Dear,<br> User need your help. Details are given below.<br>'
    EMAIL = '<p><b>Email : </b>'
    USER_ID ='<p><b>User_id: </b>'
    DESCRIPTION = '<p><b>Description: </b>'
    EMAIL_SIGNATURE =   '<p>Regards,<br>\
                    Jedi Team<br>'
    USER_EMAIL_SUBJECT = '<p><b>Subject: </b>'
    try:
        msg = email.message.Message()
        msg[SUBJECT] = "Jedi Feature Request: " + REQUEST_TYPE 
        msg[FROM] = EMAIL_FROM
        msg[TO] = SUPPORT_EMAIL
        msg.add_header(CONTENT_TYPE, TEXT_HTML)
        
        body = "".join([DEAR, USER_EMAIL_SUBJECT, EMAIL_SUBJECT, EMAIL, USER_EMAIL,USER_ID, NAMESPACE,
                         DESCRIPTION, request, EMAIL_SIGNATURE])

        msg.set_payload(body)
        s = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        s.ehlo()
        s.starttls()
        s.ehlo()
        s.login(EMAIL_LOGIN,EMAIL_PASSWD)
        s.sendmail(msg[FROM], [msg[TO]], msg.as_string())
        s.quit()
        return True
    except Exception as e:
        print ("".join(["Exception in send_email: ", str(e)]))
        return False
# #########################################################################################
def send_custom_model_email(USER_EMAIL, NOTE, NAMESPACE, LINKS, MODEL_NAME):
    SUPPORT_EMAIL = "social@broadstonetech.com"
    DEAR = '<p>Dear,<br> User requires a custom model. Details are given below.<br>'
    EMAIL = '<p><b>Email : </b>'
    USER_ID ='<p><b>User id: </b>'
    DESCRIPTION = '<p><b>Description: </b>'
    EMAIL_SIGNATURE =   '<p>Regards,<br>\
                    Jedi Team<br>'
    RELATED_FILES = '<p><b>Model related files: </b>'
    MODEL = '<p><b>Model name: </b>'
    try:
        msg = email.message.Message()
        msg[SUBJECT] = "Custom model request"
        msg[FROM] = EMAIL_FROM
        msg[TO] = SUPPORT_EMAIL
        msg.add_header(CONTENT_TYPE, TEXT_HTML)
        
        body = "".join([DEAR, EMAIL, USER_EMAIL,USER_ID, NAMESPACE, MODEL, MODEL_NAME,
                         DESCRIPTION, NOTE, RELATED_FILES, LINKS, EMAIL_SIGNATURE])

        msg.set_payload(body)
        s = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        s.ehlo()
        s.starttls()
        s.ehlo()
        s.login(EMAIL_LOGIN,EMAIL_PASSWD)
        s.sendmail(msg[FROM], [msg[TO]], msg.as_string())
        s.quit()
        return True
    except Exception as e:
        print ("".join(["Exception in send_email: ", str(e)]))
        return False


# ###################################################################################
def process_verify_token(app_id, token, DB_USERS):
    if isValidAppId(app_id):
        RETURN_ITEMS = {}
        response = DB_USERS[FORGET_PASSWORD_COLLECTION].find_one({"token": token})

        if response:
            RETURN_ITEMS['namespace'] = response["namespace"]
            return json.dumps({"message":RETURN_ITEMS}), 200, {'ContentType': 'application/json'}
        else:
            return json.dumps({"message": "Invalid token"}), 400, {'ContentType': 'application/json'}
    else:
            return json.dumps({"message": "Invalid app id"}), 400, {'ContentType': 'application/json'}
###################################################################################
