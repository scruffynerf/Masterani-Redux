from resources.lib.modules import control
import requests
import time

email = control.setting("kitsu.user")
password = control.setting("kitsu.pass")
client_id = 'dd031b32d2f56c990b1425efe6c42ad847e7fe3ab46bf1299f05ecd856bdb7dd'
client_secret = '54d7307928f63414defd96399fc31ba847961ceaecef3a5fd93144e960c0e151'

def auth():
    email = control.setting("kitsu.user")
    password = control.setting("kitsu.pass")
    resp = requests.post("https://kitsu.io/api/oauth/token",
                          params={"grant_type": "password", "username": email, "password": password})
    print resp
    token = json.loads(resp.text)['access_token']
    control.setSetting("kitsu.token", token)
    useridScrobble_resp = requests.get('https://kitsu.io/api/edge/users?filter[self]=true', headers=kitsu_headers())
    userid = json.loads(useridScrobble_resp.text)['data'][0]['id']
    control.setSetting("kitsu.userid", userid) 

def update(anidetails, id):
    anime_id = id
    episodenumber = anidetails[0]
    episodecount = anidetails[1] 
    user_id = int(control.getSetting("kitsu.userid"))
    item_type = 'anime'	
    if episodenumber < episodecount:
        update = ['current', episodenumber]
    else:
        update = ['completed', episodenumber]    
    data = {'status': update[0],
            'progress': update[1]
            }			
    final_dict = {
        "data": {
            "type": "libraryEntries",
            "attributes": data,
            "relationships":{
                "user":{
                    "data":{
                        "id": user_id,
                        "type": "users"
                    }
                },
                "media":{
                    "data":{
                        "id": anime_id,
                        "kind": item_type
                        }
                    }
                }
            }
        }
    data = json.dumps(final_dict, separators=(',',':'))
    send = requests.post("https://kitsu.io/api/edge/library-entries", headers=kitsu_headers(), data=data)
    print send
    return True

def getID(showtitle):
    showid = requests.get("https://kitsu.io/api/edge/anime", params={"filter[text]": showtitle[1]}, headers=kitsu_headers())
    showid = json.loads(showid)
    data = showid[data]
    count = 0
    for a in data:
        if data[canonicalTitle] == showtitle[0]:
            showid = data[id]
        count = count + 1
    return showid

def kitsu(showtitle, epnum, epcount):
    title = showtitle
    search_term = title.replace(" ", "%20")
    show = [title, search_term]
    showid = getID(show)
    anidetails = [epnum, epcount]
    update(anidetails, showid) 

def kitsu_headers(self):
    token = control.setting("kitsu.token")
    headers = {
        'Content-Type': 'application/vnd.api+json',
        'Accept': 'application/vnd.api+json',
        'Authorization': "Bearer {}".format(token),
        }
    return headers
    

    

    
