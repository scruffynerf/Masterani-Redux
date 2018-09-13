from resources.lib.modules import control
import requests
import time

username = control.setting("kitsu.user")
password = control.setting("kitsu.pass")
client_id = 'dd031b32d2f56c990b1425efe6c42ad847e7fe3ab46bf1299f05ecd856bdb7dd'
client_secret = '54d7307928f63414defd96399fc31ba847961ceaecef3a5fd93144e960c0e151'

def auth():
    header = {
        'User-Agent': 'Pymoe (git.vertinext.com/ccubed/Pymoe)',
        'Accept': 'application/vnd.api+json',
        'Content-Type': 'application/vnd.api+json'
        }
    token = requests.post("https://kitsu.io/api/oauth/token",
                          params={"grant_type": "password", "username": username, "password": password,
                                  "client_id": client_id, "client_secret": client_secret})
    print token
    jsd = token.json()
    at = jsd['access_token']
    ex = int(jsd['expires_in'])
    cr = int(jsd['created_at'])
    re = jsd['refresh_token']
    authorization = "'" + str("Bearer " + str(at)) + "'"
    header = {
        'User-Agent': 'Pymoe (git.vertinext.com/ccubed/Pymoe)',
        'Accept': 'application/vnd.api+json',
        'Content-Type': 'application/vnd.api+json',
        'Authorization': authorization
        }
    authinfo = [header, ex, cr, re]
    return authinfo

def update(info, anidetails, id):
    header = info[0]
    date = info[2]    
    animeid = id[1]
    episodenumber = anidetails[0]
    episodecount = anidetails[1] 
    user_id = id[0]
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
                        "id": animeid,
                        "kind": item_type
                        }
                    }
                }
            }
        }
    send = requests.post("https://kitsu.io/api/edge/library-entries", json=final_dict, headers=header)
    print send
    return True

def getID(showtitle):
    header = {
        'User-Agent': 'Pymoe (git.vertinext.com/ccubed/Pymoe)',
        'Accept': 'application/vnd.api+json',
        'Content-Type': 'application/vnd.api+json'
        }
    userid = requests.get("https://kitsu.io/api/edge/users", params={"filter[name]": username}, headers=header)
    userid = json.loads(userid)
    userid = userid[data][id]
    showid = requests.get("https://kitsu.io/api/edge/anime", params={"filter[text]": showtitle[1]}, headers=header)
    showid = json.loads(showid)
    data = showid[data]
    count = 0
    for a in data:
        if data[canonicalTitle] == showtitle[0]:
            showid = data[id]
        count = count + 1
    print userid
    print showid
    id = [userid, showid]	

def kitsu(showtitle, epnum, epcount):
    if username is None:
        return
    token = auth()
    title = showtitle
    search_term = title.replace(" ", "%20")
    show = [title, search_term]
    id = getID(show)
    anidetails = [epnum, epcount]
    update(token, anidetails, id) 
    

    

    
