# -*- coding: utf-8 -*-

'''
    Masterani Redux add-on

    this program is free software: you can redistribute it and/or modify
    it under the terms of the gnu general public license as published by
    the free software foundation, either version 3 of the license, or
    (at your option) any later version.

    this program is distributed in the hope that it will be useful,
    but without any warranty; without even the implied warranty of
    merchantability or fitness for a particular purpose.  see the
    gnu general public license for more details.

    you should have received a copy of the gnu general public license
    along with this program.  if not, see <http://www.gnu.org/licenses/>.
'''

import base64
import json
import re
import requests
import xbmc
import xbmcgui
import re
from resources.lib.modules import cache
from resources.lib.modules import client
from resources.lib.modules import control
from resources.lib.modules import masterani
from resources.lib.modules.control import progressDialog
from resources.lib.modules.watched import Watched
import resolveurl

#GETLINKS
def getlinks(url):
    link_list = []	
    with requests.session() as s:
        p = s.get(url)
        print (p.text).encode('utf-8')
        try:
            videos = re.findall(r'videos = (\[.*?\])', p.text)[0]
            print videos
            videos = json.loads(videos)
            for i in videos:
                type = ''
                if type == '':
                    type = 1
                embed_id = 'None Required' #Literally only got this part to fix an error
                link_list.append({'url': i['src'], 'name': 'Aika', 'quality': i['res'], 'type': type, 'embed_id': embed_id})
        except:
            mirrors = re.findall(r'mirrors: (.*?), auto_update', p.text)[0]
            mirrors = json.loads(mirrors)
            for i in mirrors:
                link_list.append({'embed_id':i['embed_id'],'url': i['host']['embed_prefix'] + i['embed_id'], 'name': i['host']['name'], 'quality': i['quality'], 'type': i['type']})
    print link_list
    return link_list

def getid(url):
    with requests.session() as s:
        p = s.get(url)
        id = p.text
        id = id.split('"id":', 2)[2]
        print id
        id = id.split(',', 1)[0]
        print id        
    return id
	
def getcover(url):
    with requests.session() as s:
        p = s.get(url)
        cover = p.text
        cover = cover.split('<img class="cover" src="', 1)[1]
        print cover
        cover = cover.split('"', 1)[0]
        print cover 		
    return cover
	
def getdirect(hostname, url, quality, embed_id):
    if 'Stream.moe' in hostname:
        mp4 = resolveurl.resolve(url)
    if 'MP4Upload' in hostname:
        mp4 = resolveurl.resolve(url)
    if 'Bakavideo' in hostname:
        #Couldn't actually find any instances of bakavideo on Masterani so I'll assume the original way works.
        #Actually believe that the site doesn't exist anymore
        content = re.compile("go\((.+?)\)").findall(client.request(url))[0]
        content = content.replace("'", "").replace(", ", "/")
        content = "https://bakavideo.tv/" + content
        content = client.request(content)
        content = json.loads(content)
        content = content['content']
        content = base64.b64decode(content)
        mp4s = client.parsedom(content, 'source', ret='src')
        mp4 = ""
        for link in mp4s:
            if str(quality) in link:
                mp4 = link
            if mp4 is "":
                mp4 = mp4s[0]
    if 'Beta' in hostname:
        #Same as Bakavideo, I couldn't actually find any Aniupload on the site, but if it is still there I'll assume the original way works.
        mp4 = embed_id       
    if 'Vidstreaming' in hostname:
        mp4 = resolveurl.resolve(url)
    if 'Aniupload' in hostname:
        #Same as Bakavideo, I couldn't actually find any Aniupload on the site, but if it is still there I'll assume the original way works.
        mp4 = re.compile("\(\[\{src: \"(.+?)\"").findall(client.request(url))[0]
    if 'Openload' in hostname:
        mp4 = resolveurl.resolve(url)
    if 'Drive.g' in hostname:
        mp4 = resolveurl.resolve(url)
    if 'Rapidvideo' in hostname:
        duration=10000   #in milliseconds
        message = "Cannot Play URL"
        stream_url = resolveurl.HostedMediaFile(url=url).resolve()
        # If urlresolver returns false then the video url was not resolved.
        if not stream_url:
            dialog = xbmcgui.Dialog()
            dialog.notification("ResolveURL Error", message, xbmcgui.NOTIFICATION_INFO, duration)
        else:        
            mp4 = stream_url
    if 'Aika' in hostname:
        mp4 = url
    if 'Streamango' in hostname:
        mp4 = resolveurl.resolve(url)
    mp4 = str(mp4)
    return mp4

def play(anime_id, episode_id):

    episode_link = episode_id
	
    l1 = "Fetching video."
    progressDialog.create(heading="Masterani", line1="Fetching video.")
    progressDialog.update(0, line1=l1, line3="Loading hosts.")
    
    hosts = getlinks(episode_link)   
    ep_id = getid(episode_link)
    #linkforcover = getcover(episode_link)
	
    if hosts is None:
        xbmcgui.Dialog().ok("Masterani", "Something went wrong.", "Please try again later.")
        return

		
    #Remove Tiwi Kiwi as it is broken
	
    for e in hosts:
        if 'Tiwi.kiwi' in e['name']:
            hosts.remove(e)

    #Remove Disabled Hosts

    if control.setting("host.mp4upload") == "false":
            for e in hosts:
                if 'MP4Upload' in e['name']:
                    hosts.remove(e)

    if control.setting("host.aniupload") == "false":
        for e in hosts:
            if 'Aniupload' in e['name']:
                hosts.remove(e)

    if control.setting("host.bakavide") == "false":
        for e in hosts:
            if 'Bakavideo' in e['name']:
                hosts.remove(e)

    if control.setting("host.youtube") == "false":
        for e in hosts:
            if 'YouTube' in e['name']:
                hosts.remove(e)

    if control.setting("host.beta") == "false":
        for e in hosts:
            if 'Beta' in e['name']:
                hosts.remove(e)
        
    if control.setting("host.stream.moe") == "false":
        for e in hosts:
            if 'Stream.moe' in e['name']:
                hosts.remove(e)

    if control.setting("host.drive.g") == "false":
        for e in hosts:
            if 'Drive.g' in e['name']:
                hosts.remove(e)
                
    if control.setting("host.vidstreaming") == "false":
        for e in hosts:
            if 'Vidstreaming' in e['name']:
                hosts.remove(e)
            
    if control.setting("host.rapidvideo") == "false":
        for e in hosts:
            if 'Rapidvideo' in e['name']:
                hosts.remove(e)

    if control.setting("host.aika") == "false":
        for e in hosts:
            if 'Aika' in e['name']:
                hosts.remove(e)

    if control.setting("host.streamango") == "false":
        for e in hosts:
            if 'Streamango' in e['name']:
                hosts.remove(e)
        
    if control.setting("host.openload") == "false":
        for e in hosts:
            if 'Openload' in e['name']:
                hosts.remove(e)

    progressDialog.update(25, line1=l1, line3="Loading episodes urls.")
    progressDialog.update(50, line1=l1, line3="Picking nose.")

    hostlist = []

    videos = sorted(hosts, key=lambda k: (-int(k['type']), int(k['quality'])), reverse=True)
    print videos

    autoplay = control.setting("autoplay.enabled")
    maxq = control.setting("autoplay.maxquality")
    subdub = control.setting("autoplay.subdub")

    videoCounter = 0
    autoplayHost = 0
    hostCounter = 0

    while videoCounter < len(videos):
        try:
            hostname = videos[videoCounter]['name']
            subs = 'Sub' if videos[videoCounter]['type'] is 1 else 'Dub'
            quality = videos[videoCounter]['quality']
            if 'true' in autoplay:
                if subdub == subs and int(quality) <= int(maxq):
                    hostlist.append("%s | %s | %s" % (quality, subs, hostname))
                    autoplayHost = hostCounter
                    break
                hostCounter += 1
            else:
                hostlist.append("%s | %s | %s" % (quality, subs, hostname))
            videoCounter += 1
        except:
            videos.remove(videos[videoCounter])

    if len(hostlist) is 0:
        progressDialog.close()
        xbmcgui.Dialog().ok("Masterani Redux", "No supported hosts found.")
        return

    if 'false' in autoplay:
        hostDialog = control.dialog.select("Select host.", hostlist)
    else:
        if len(hostlist) is 0:
            progressDialog.close()
            xbmcgui.Dialog().ok("Masterani Redux", "No hosts found for autoplay.", "Change addon settings and try again.")
            hostDialog = -1
        else:
            hostDialog = autoplayHost
			
    if hostDialog == -1:
        progressDialog.close()
        control.execute('dialog.close(okdialog)')
        return

    hostname = videos[hostDialog]['name']		
    hostlink = videos[hostDialog]['url']
    hostquality = videos[hostDialog]['quality']
    embed_id = videos[hostDialog]['embed_id']

    progressDialog.update(75, line1=l1, line3="Loading video.")
	
    #Resolve Links
    mp4 = getdirect(hostname, hostlink, hostquality, embed_id)
    progressDialog.close()
    MAPlayer().run(anime_id, ep_id, mp4)

class MAPlayer(xbmc.Player):
    def __init__(self):
        xbmc.Player.__init__(self)
        self.anime_id = 0
        self.episode_id = 0

    def run(self, anime_id, ep_id, url):
        control.sleep(200)

        self.anime_id = int(anime_id)
        self.episode_id = int(ep_id)

        item = control.item(path=url)

        try:
            c = cache.get(masterani.get_anime_details, 3, self.anime_id)

            ctype = c['type']
            ctype = 'video' if int(ctype) is 2 else 'episode'

            tvshowtitle = c['title']
            poster = c['poster']
            print poster
            genre = c['genre']
            print genre
			
            coverlink = "http://cdn.masterani.me/poster/" + poster
            print coverlink

            item.setArt({'icon': coverlink, 'thumb': coverlink, 'poster': coverlink, 'tvshow.poster': coverlink, 'season.poster': coverlink})

            e = c['episodes'][self.episode_id]
            title = e['info']['title']
            season = 1
            if season is None: season = 1
            episode = e['info']['episode']
            if ctype is 'video': title = c['title']
            if title is None: title = "Episode %s" % episode
			
            year = e['info']['aired']
            year = year.split("-", 1)[0]
            print year

            plot = e['info']['description']
            print plot

            item.setInfo(type="video",
                         infoLabels={'tvshowtitle': title, 'title': tvshowtitle, 'episode': int(episode),
                                     'season': int(season), 'mediatype': ctype, 'genre': genre,
                                     'year': year, 'plot': plot})

        except:
            pass

        item.setProperty('Video', 'true')
        item.setProperty('IsPlayable', 'true')

        self.play(url, item)

        self.playback_checker()

        pass

    def playback_checker(self):
        for i in range(0, 300):
            if self.isPlaying():
                break
            xbmc.sleep(100)

        while self.isPlaying():
            try:
                if (self.getTime() / self.getTotalTime()) >= .8:
                    Watched().mark(self.anime_id, self.episode_id)
            except:
                pass
            xbmc.sleep(1000)

    def onPlayBackStarted(self):
        control.execute('Dialog.Close(all,true)')
        control.setSetting("anime.lastvisited", str(self.anime_id))
        pass

    def onPlayBackEnded(self):
        self.onPlayBackStopped()
        pass

    def onPlayBackStopped(self):
        control.refresh()
        pass
