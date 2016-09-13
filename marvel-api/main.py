'''
@author: Rodolfo S. Antunes <rsantunes@inf.ufrgs.br>
'''

import random
import argparse
import sys
import traceback
from api_request import ApiRequest, ApiCommunicationError
from jinja2 import Environment, FileSystemLoader

class Main:
    def __init__(self):
        parser = argparse.ArgumentParser(description='Generate HTML pages from Marvel comic Stories.')
        group = parser.add_mutually_exclusive_group(required=True)
        group.add_argument('--name', help='Randomly selects a comic from a given character')
        group.add_argument('--id', type=int, help='Selects a specific story ID from Marvel API')
        args = parser.parse_args()

        self.api = ApiRequest()
        if args.name != None:
            print('Looking for a comic from {}...'.format(args.name))
            print('This may take a while for popular characters!')
            story_id = self.getRandomStoryId(args.name)
        else:
            story_id = args.id
        print('Generating HTML...')
        self.generateStoryHtml(story_id, 'out.html')
        print('Done!')
        return


    def getRandomStoryId(self, character_name):
        try:
            char_id = self.api.getCharacterId(character_name)
            char_stories = self.api.getCharacterStories(char_id)
        except ApiCommunicationError as exc:
            print('ERROR: {}'.format(exc))
            traceback.print_exc()
            sys.exit(1)            
        return random.choice(char_stories)

    def generateStoryHtml(self, story_id, html_file):
        try:
            raw_data = self.api.getStoryData(story_id)
        except ApiCommunicationError as exc:
            print('ERROR: {}'.format(exc))
            traceback.print_exc()
            sys.exit(1)
        story_data = self.parseStoryData(raw_data)
        character_data = list()
        for itchar in raw_data['characters']['items']:
            raw_char = self.api.getCharacterInfoFromUrl(itchar['resourceURI'])
            character_data.append( self.parseCharacterData(raw_char) )
        env = Environment(loader=FileSystemLoader('templates'))
        template = env.get_template('story.html')
        output_from_template = template.render(story_data=story_data, character_data=character_data)
        with open(html_file, 'wb') as arq:
            arq.write(output_from_template.encode('ascii', 'xmlcharrefreplace'))
        return       

    def parseStoryData(self, story_data):
        res = dict()
        res['title'] = story_data['title']
        res['description'] = story_data['description']
        res['attributionHTML'] = story_data['attributionHTML']
        res['authors'] = ''
        for it in story_data['creators']['items']:
            res['authors'] += '{} ({}), '.format(it['name'], it['role'])
        res['authors'] = res['authors'][:-2]
        res['series'] = ''
        for it in story_data['series']['items']:
            res['series'] += '{}, '.format(it['name'])
        res['series'] = res['series'][:-2]
        res['events'] = ''
        for it in story_data['events']['items']:
            res['events'] += '{}, '.format(it['name'])
        res['events'] = res['events'][:-2]
        return res

    def parseCharacterData(self, character_data):
        res = dict()
        res['name'] = character_data['name']
        res['description'] = character_data['description']
        res['image_url'] = '{}.{}'.format(character_data['thumbnail']['path'], character_data['thumbnail']['extension'])
        return res

if __name__ == '__main__':
    Main()