from config_files import CLIENT_ID, ClientSecret, Name, Shuffle

import json
import requests
import collections
import random
import operator

#User you want get subs from:
USER_NAME = Name

#Variable, which will be filled in get_user_id()
USER_ID = ""

SHUFFLE_NUMBER = Shuffle

#Subscriber list in a "highest sub" order
SUBS_LIST = []
#Ordered dictionary key:follower, value:user_id.
FOLLOWER_IDS = collections.OrderedDict()
#key:follower, value:sub_count
HELPER_DICT = collections.OrderedDict()
sorted_dict = {}

#Final list key: Username, value:User_id (shuffled first 5 subs at list)
FINAL_DICT = {}




#Gets new Oauth2 token for twitch API.
def get_new_twitch_token():
    payload = {"client_id": CLIENT_ID, "client_secret": ClientSecret,
                   "grant_type": "client_credentials"}
    print("Getting new token from server")

    Url = "https://id.twitch.tv/oauth2/token"
    

    resp = requests.post(url = Url, params=payload, headers={"Client-ID": CLIENT_ID})
    if resp.status_code == 200:
        with open("token", "w") as outfile:
            outfile.write(resp.json()["access_token"])
        return resp.json()["access_token"]
    else:
        print("Renewing twitch token failed")


#Gets USER_ID by using the USER_NAME
def get_user_id():
    
    inFile = open("token", "r")
    newToken = inFile.read()

    Url = 'https://api.twitch.tv/helix/users?login=' + USER_NAME
    Url.replace(" ", "")

    Headers = {'Client-ID': CLIENT_ID, 'Authorization': "Bearer " + newToken}

    r = requests.get(url = Url, headers = Headers)
    

    if r.status_code == 200:

        # returns JSON object as a dictionary
        data = json.loads(r.text)

        global USER_ID

        #Search for user id and puts it to USER_ID variable
        for element in data['data']: 
            for key in element['id']:
                USER_ID = USER_ID + key   
    else:
        print("Get_user_id() failed")
        get_new_twitch_token()
        get_user_id()
    

    

#Getting list of USER_NAME's followed streamers

def get_user_subs():
    
    inFile = open("token", "r")
    newToken = inFile.read()

    Headers = {'Client-ID': CLIENT_ID, 'Authorization': "Bearer " + newToken}

    Url = 'https://api.twitch.tv/helix/users/follows?from_id=' + USER_ID
    Url.replace(" ", "")

    r = requests.get(url = Url, headers = Headers)

    if r.status_code == 200:

        data = json.loads(r.text)

        global SUBS_LIST

        #Loops user follows json dict and gets subs from there.
        for subs in data ['data']:
            SUBS_LIST.append(subs['to_login'])

    else:
        print("Get_user_subs() failed")
        get_new_twitch_token()
        get_user_subs()



#Sorts [SUBS_LIST], in order who has most followers.
def highest_subs_count():

    #Makes dictionary of followers + user id's
    for follower in SUBS_LIST:

        #Resets the current USER_NAME here and puts SUBS_LIST username to the USER_name
        global USER_NAME
        USER_NAME = follower

        #Resets the current USER_ID and Gets ID from the USER_NAME
        global USER_ID
        USER_ID = ""
        get_user_id()

        #Adds username and user id to dictionary
        FOLLOWER_IDS[USER_NAME] = USER_ID
    
    #Sorts the dictionary by highest sub count
    sort_follower_ids()


#Sorts follower list by its subscriber count
def sort_follower_ids():
    #print(FOLLOWER_IDS)

    for key in FOLLOWER_IDS.keys():
        v = FOLLOWER_IDS[key]
        global USER_ID
        USER_ID = v

        inFile = open("token", "r")
        newToken = inFile.read()

        Headers = {'Client-ID': CLIENT_ID, 'Authorization': "Bearer " + newToken}

        Url = 'https://api.twitch.tv/helix/users/follows?to_id=' + USER_ID + '&first=1'
        Url.replace(" ", "")

        r = requests.get(url = Url, headers = Headers)

        data = json.loads(r.text)

        if r.status_code == 200:

            #Makes HELPER_DICT with key:Username, value: follower_count
            global HELPER_DICT
            total = data['total']
            HELPER_DICT.setdefault(key, []).append(total)
            
            
            
        else:
            get_new_twitch_token()
            sort_follower_ids()
                 
    sorting()
    keys = list(sorted_dict.keys())
    shuffle_slice(keys, 0, SHUFFLE_NUMBER)
    Final_list(keys)


def sorting():

    #Sorts dictionary by the follower count in a order  
    global sorted_dict
    #sorted_keys = sorted(HELPER_DICT.items(), key=operator.itemgetter(1), reverse=True)
    sorted_keys = sorted(HELPER_DICT, key=HELPER_DICT.get, reverse=True)
    
    for w in sorted_keys:
       sorted_dict[w] = HELPER_DICT[w]

def shuffle_slice(key, start, stop):

    #Shuffle part of the list
    i = start
    while (i < stop-1):
        idx = random.randrange(i, stop)
        key[i], key[idx] = key[idx], key[i]
        i += 1


def Final_list(key_list):

    for follower in key_list:
        global USER_NAME
        USER_NAME = follower

        global USER_ID
        USER_ID = ""
        get_user_id()

        FINAL_DICT[USER_NAME] = USER_ID
        

def Make_Final_list():
    get_new_twitch_token()
    get_user_id()
    get_user_subs()
    highest_subs_count()
    
    return FINAL_DICT