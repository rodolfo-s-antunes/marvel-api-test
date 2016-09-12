'''
@author: Rodolfo S. Antunes <rsantunes@inf.ufrgs.br>
'''

import json

class Configuration(object):
    CONF_FILE_NAME = 'config.json'
    __inst = None
    
    def __init__(self):
        with open(self.CONF_FILE_NAME) as arq:
            self.__parms = json.load(arq)
        return
    
    def getParm(self, parm):
        return self.__parms[parm]
