'''
@author: Rodolfo S. Antunes <rsantunes@inf.ufrgs.br>
'''

import sys
import urllib3
import time
import hashlib
import json
import math
from configuration import Configuration

class ApiRequest:

    def __init__(self):
        self.conf = Configuration()
        self.http = urllib3.PoolManager()
        return

    def __addAuthParms(self, request_parms):
        ts = str(time.time())
        hashbase = ts+self.conf.getParm("private_key")+self.conf.getParm("public_key")
        hashdigest = hashlib.md5(hashbase.encode('ascii')).hexdigest()
        res = {'ts': ts, 'hash': hashdigest, 'apikey': self.conf.getParm("public_key")}
        for it in request_parms:
            res[it] = request_parms[it]
        return res
    
    def __apiRequest(self, url, parms={}):
        authparms = self.__addAuthParms(parms);
        request = self.http.request('GET', url, fields=authparms)
        if request.status != 200:
            print("ERROR: Failed to retrieve data from Marvel, HTTP Status {}".format(request.status))
            sys.exit(1)
        else:
            return json.loads( request.data.decode('utf-8') )

    def getCharacterId(self, character_name):
        result = self.__apiRequest('http://gateway.marvel.com/v1/public/characters', {'name': character_name})
        if result['data']['count'] < 1:
            print("ERROR: No character with the name {} found on Marvel".format(character_name))
            sys.exit(1)
        else:
            return result['data']['results'][0]['id']
    
    def getCharacterInfo(self, character_id):
        result = self.__apiRequest('http://gateway.marvel.com/v1/public/characters/{}'.format(character_id))
        return result['data']['results'][0]
    
    def getCharacterInfoFromUrl(self, char_url):
        result = self.__apiRequest(char_url)
        return result['data']['results'][0]

    def getCharacterStories(self, character_id):
        story_ids = list()
        parms = {'limit': '100'}
        result = self.__apiRequest('http://gateway.marvel.com/v1/public/characters/{}/stories'.format(character_id), parms)
        total_stories = int(result['data']['total'])
        total_steps = math.ceil(total_stories/100)
        for it in range(total_steps):
            for sit in result['data']['results']:
                story_ids.append(sit['id'])
            parms = {'limit': '100', 'offset': str((it+1)*100)}
            result = self.__apiRequest('http://gateway.marvel.com/v1/public/characters/{}/stories'.format(character_id), parms)
        return story_ids
    
    def getStoryData(self, story_id):
        result = self.__apiRequest('http://gateway.marvel.com/v1/public/stories/{}'.format(story_id))
        story_data = result['data']['results'][0]
        story_data['attributionHTML'] = result['attributionHTML']
        return story_data
