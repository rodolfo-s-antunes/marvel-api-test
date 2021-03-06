""" Module to control the communication with the Marvel comic API

This module contains the ApiRequest class, which exports methods to
request information from the Marvel API. Various methods assume that
the data returned from the calls will follow the format described in
the Marvel API documentation (http://developer.marvel.com/docs).

The module also exports the ApiCommunicationError class, used to manage
various exceptions that may occur while obtaining data from the API.
Exceptions that may occur will not be treated  by the methods in the
ApiRequest class. They will be raised and must be treated by the callers
that import this module. 

@author: Rodolfo S. Antunes <rsantunes@inf.ufrgs.br>
"""

import urllib3
import time
import hashlib
import json
import math
from configuration import Configuration

class ApiCommunicationError(Exception):
    """ Simple exception class to catch API Errors
    
    This is a simple class that encapsulates the exceptions that
    occur when communicating with the Marvel API. The class contains a
    string parameter with a descriptive text from the exception. This
    can be used to provide the user with useful information about the
    communication error prior to terminating execution.
    """

    def __init__(self, message):
        self.message = message
        return

    def __str__(self):
        return self.message

class ApiRequest:
    """ Marvel API Communication management class
    
    This class controls all requests to obtain data from the Marvel API.
    The urllib3 module is used to abstract the HTTP connection management.
    Most methods on the class abstract the endpoints exported by the Marvel
    API, which will be required to obtain story and character information.
    """

    def __init__(self):
        # Instantiate the class that contains the configuration file parameters
        self.conf = Configuration()
        # Instantiate the connection pool manager from the urllib3 module
        self.http = urllib3.PoolManager()
        return

    def __addAuthParms(self, request_parms):
        """ Method to generate authentication parameters for API calls
        
        This method generates a dictionary containing the authentication
        parameters required to authenticate calls to the Marvel API. In
        summary, these parameters are:
        
        -- ts: a random string that uniquely identifies calls to the API.
           This value is generated by simply obtaining the current system time
           in seconds.
        -- apikey: the public key obtained when registering with the Marvel API.
           this key is stored in the "public_key" parameter of the configuration
           file.
        -- hash: the MD5 digest from the concatenation of the ts parameter with
           the API private and public keys (ts+public_key+private_key). The ts and
           public_key parameters are the same as above described. The private_key,
           in turn, is also stored in the configuration file, with the
           "private_key" parameter.
        
        Parameters:
        request_parms: dict
            A dictionary with additional parameters that must be added sent with
            the API request. These parameters vary depending on the API endpoint.
            They will be added to the dictionary returned by this method.
        
        Returns:
            A dictionary containing the parameters to be sent with the API
            request, including those passed to the method and the ones required
            to authenticate the request.
        """
        ts = str(time.time())
        hashbase = ts+self.conf.getParm("private_key")+self.conf.getParm("public_key")
        hashdigest = hashlib.md5(hashbase.encode('ascii')).hexdigest()
        res = {'ts': ts, 'hash': hashdigest, 'apikey': self.conf.getParm("public_key")}
        for it in request_parms:
            res[it] = request_parms[it]
        return res
    
    def __apiRequest(self, url, parms={}):
        """ Method for actually requesting data from the API through urllib3
        
        This method uses the urllib3 module to send HTTP requests to the
        Marvel API. It will check the request status to guarantee that
        the request was successful prior to returning the data to its caller.
        If an error occurred in the request (that is, its status is different
        from 200), the method will raise an ApiCommunicationError that must be
        handled by the caller. We assume that the API will return a JSON data
        structure since this is the case for all methods exported by the
        Marvel API.
        
        Parameters:
        url: string
            The URL of the API endpoint which should be called through HTTP.
        parms: dict
            A dictionary containing the parameters required by the API endpoint
            to be called.
        
        Returns:
            A parsed JSON structure containing the data received from the API.
        """
        authparms = self.__addAuthParms(parms);
        request = self.http.request('GET', url, fields=authparms)
        if request.status != 200:
            raise ApiCommunicationError('Failed to retrieve data from Marvel, HTTP Status {}'.format(request.status))
        else:
            return json.loads( request.data.decode('utf-8') )

    def getCharacterId(self, character_name):
        """ Method to obtain the unique ID from a character based on his/her full name
        
        Parameters:
        character_name: string
            The full name of the character from whih the unique ID must be recovered
            (eg: "Iron Man")
        
        Returns:
            The integer value of the unique ID from the character. If a character
            with the name sent as parameter is not found, the method will raise
            an ApiCommunicationException to inform the caller.
        """
        try:
            result = self.__apiRequest('http://gateway.marvel.com/v1/public/characters', {'name': character_name})
        except ApiCommunicationError:
            raise
        if result['data']['count'] < 1:
            raise ApiCommunicationError('No character with the name {} found'.format(character_name))
        else:
            return result['data']['results'][0]['id']
        
    def getCharacterInfoFromUrl(self, char_url):
        """ Method to obtain character information from a given character URI
        
        This method is required to obtain further information about the characters
        contained in a story. A story returned by the API will contain the full URI
        of the data of each participating character. This URI is received as
        parameter by this method, which returns the necessary information about
        the character. The method assumes that just one character will be
        returned by the method, as specified in the Marvel API documentation.
        Additional parsing of the information is left to the caller.
        
        Parameters:
        char_url: string
            The URI of the API endpoint that contains the required character
            information. The method assume that the URI passed as parameter
            is a valid URI that contains character information as described
            in the API docs.
        
        Returns:
            A JSON structure with the full information about a character.
        """
        try:
            result = self.__apiRequest(char_url)
        except ApiCommunicationError:
            raise
        return result['data']['results'][0]

    def getCharacterStories(self, character_id):
        """ Method to obtain the unique IDs from all stories from a character
        
        This method send consecutive requests to the API to obtain a list of
        all stories available of a character informed as parameter. Multiple
        requests are necessary because the API limits the number of responses
        to a call to 100.
        
        The idea of this method is to recover all story IDs so that one can
        be randomly chosen by the user. This method should be used with
        caution: a popular character might appear in thousands of stories,
        resulting in a very lengthy execution time.
        
        Parameters:
        character_id: int
            The unique ID of the character from which the stories should be
            recovered.
            
        Return:
            A list with the unique IDs from all the stories of this character.
            If the API does not return stories, an ApiCommuncationException is
            raised to inform the caller.
        """
        story_ids = list()
        parms = {'limit': '100'}
        try:
            result = self.__apiRequest('http://gateway.marvel.com/v1/public/characters/{}/stories'.format(character_id), parms)
        except ApiCommunicationError:
            raise
        total_stories = int(result['data']['total'])
        if total_stories < 1:
            raise ApiCommunicationError('The character ID {} did not return any stories'.format(character_id))
        else:
            total_steps = math.ceil(total_stories/100)
            for it in range(total_steps):
                for sit in result['data']['results']:
                    story_ids.append(sit['id'])
                parms = {'limit': '100', 'offset': str((it+1)*100)}
                try:
                    result = self.__apiRequest('http://gateway.marvel.com/v1/public/characters/{}/stories'.format(character_id), parms)
                except ApiCommunicationError:
                    raise
                return story_ids
    
    def getStoryData(self, story_id):
        """ Returns information about a specific story from the API
        
        This method returns the JSON information about a specific story.
        Additionally, it will return the attribution HTML with the Marvel
        Copyright information, which should be added to the program output.
        The method assumes that just one story will be returned by the method,
        as specified in the Marvel API documentation. Additional parsing of
        the information is left to the caller.
        
        Parameters:
        story_id: int
            The unique ID of the story to be requested.
        
        Return:
            A JSON structure containing the information about the requested
            story. If the API does not return information, an ApiCommunicationError
            is raised to inform the caller.
        """
        try:
            result = self.__apiRequest('http://gateway.marvel.com/v1/public/stories/{}'.format(story_id))
        except ApiCommunicationError:
            raise
        if int(result['data']['count']) < 1:
            raise ApiCommunicationError('The story ID {} does not exist'.format(story_id))
        else:
            story_data = result['data']['results'][0]
            story_data['attributionHTML'] = result['attributionHTML']
            return story_data
