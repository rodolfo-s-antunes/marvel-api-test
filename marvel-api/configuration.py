""" Module to load configuration variables from a JSON file.

This module contains a simple class that loads configuration parameters from a
JSON file. The class expects the file to be named "config.json".
 
@author: Rodolfo S. Antunes <rsantunes@inf.ufrgs.br>
"""

import json

class Configuration(object):
    """ Simple configuration file class
    
    This class simply loads configuration variables from a file named
    "config.json". As the name implies, the file is expected to be in
    the JSON format.
    """
    
    CONF_FILE_NAME = 'config.json'
    __inst = None
    
    def __init__(self):
        with open(self.CONF_FILE_NAME) as arq:
            self.__parms = json.load(arq)
        return
    
    def getParm(self, parm):
        """ Return the value from a configuration parameter
        
        This method returns the value of a configuration parameter.
        
        Parameters:
        parm : string
            The parameter name for which the configuration value should be returned
               
        Returns:
            If the named parameter exists in the configuration file, its value is returned.
            Otherwise, the method returns None.
        """
        if parm in self.__parms:
            return self.__parms[parm]
        else:
            return None
