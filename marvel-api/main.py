"""
This module contains the main program that generates an HTML file
based on information received from the Marvel API. The HTML file
is generated through the Jinja2 Templating engine. Requests to the
Marvel API are managed by the ApiRequest class, contained in the
api_request.py module. The program can operate in two distinct modes. 

In the first, the user gives as parameter the unique ID of a specific
story from the Marvel API, and the program will generate the HTML file
for that story. To access this mode, the user must inform the
"--id <story_id>" in the program command line.

In the second mode, the user gives the name of a character, and the program
will try to find all of his/her stories and will randomly chose one to
generate the HTML file. To access this mode, the user must inform the
"--name <character_name>". The second operation mode will be considerably
slow if a popular character is given as parameter due to the high number
of stories he/she appears on.

@author: Rodolfo S. Antunes <rsantunes@inf.ufrgs.br>
"""

import random
import argparse
import sys
import traceback
from api_request import ApiRequest, ApiCommunicationError
from jinja2 import Environment, FileSystemLoader

class Main:
    """ Main program class
    
    This class contains the main entry point of the program in its constructor.
    It also contains the methods that parse the JSON information recovered from
    calls to the Marvel API and the methods to generate the output HTML file
    through Jinja2 templates.
    """
    def __init__(self):
        """ Main program routine
        
        This method specifies the restrictions to the program command line arguments.
        In summary, it guarantees that the user only chooses one of the two available
        operation modes, selected by the "--name" or "--id" parameters. It also calls
        the additional parsing methods depending on the selected operation mode.
        """
        # First defines the CLI parser to process the program options
        parser = argparse.ArgumentParser(description='Generate HTML pages from Marvel comic Stories.')
        group = parser.add_mutually_exclusive_group(required=True)
        group.add_argument('--name', help='Randomly selects a comic from a given character')
        group.add_argument('--id', type=int, help='Selects a specific story ID from Marvel API')
        args = parser.parse_args()

        self.api = ApiRequest()
        # If the user uses the "--name" option, then look for all
        # the stories of one character and selects one randomly.
        if args.name != None:
            print('Looking for a comic from {}...'.format(args.name))
            print('This may take a while for popular characters!')
            story_id = self.getRandomStoryId(args.name)
        # If the user uses the "--id" option, then just use the id
        # informed as parameter.
        else:
            story_id = args.id
        print('Generating HTML...')
        # Invoke the method to generate the HTML file.
        self.generateStoryHtml(story_id, 'out.html')
        print('Done!')
        return


    def getRandomStoryId(self, character_name):
        """ Method to randomly select a story from a character.
        
        This method invokes the API calls to, firstly, look for the
        unique ID of a character given his/her name. Then, it tries to
        obtain all the available stories of the character. Finally,
        the method randomly selects the unique ID of one of the available
        stories. If the character name does not exist or no stories are found,
        the program if finished with an error.
        
        Parameters:
        character_name: string
            The name of the character from which one story will be
            randomly selected.
        
        Returns:
            An integer containing the unique ID of a randomly selected story.
        """
        try:
            char_id = self.api.getCharacterId(character_name)
            char_stories = self.api.getCharacterStories(char_id)
        except ApiCommunicationError as exc:
            print('ERROR: {}'.format(exc))
            traceback.print_exc()
            sys.exit(1)            
        return random.choice(char_stories)

    def generateStoryHtml(self, story_id, html_file):
        """ Method to retrieve story information and generate the HTML output.
        
        This method executes two main functions. First, it requests from the
        Marvel API all the information about a story given as parameter.
        The recovered information is parsed by additional methods. Second,
        It invokes the Jinja2 template engine to generate the HTML output
        using the data recovered from the API. If any of the API calls raises
        an exception (usually due to connection problems), the program
        finishes with an error.
        
        The method assumes that the file "templates/story.html" file exists
        and it contains the Jinja2 HTML template that will be used to generate
        the final HTML file containing the information obtained from
        the Marvel API.
        
        Parameters:
        story_id: int
            Unique ID of the story to be recovered from the API.
        html_file: string
            Name of the output file that will contain the information about
            the story recovered from the API.
        """
        print('Generating HTML for Story {}'.format(story_id))
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
        """ Method to prepare story information for the HTML template
        
        This method receives the raw JSON from the Marvel API and
        processes it prior to use in the Jinja2 HTML template. The
        method basically removes unnecessary fields from the JSON
        structure and concatenates different lists into a "pretty"
        string that can be presented to the template.
        
        Parameters:
        story_data: dict
            Raw JSON structure received from the Marvel API containing
            story information.
        
        Return:
            A dictionary with the story information required by the
            HTML template.
        """
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
        """ Method to prepare character information for the HTML template
        
        This method receives the raw JSON from the Marvel API and
        processes it prior to use in the Jinja2 HTML template. The
        method basically removes unnecessary fields from the JSON
        structure and concatenates different lists into a "pretty"
        string that can be presented to the template.
        
        Parameters:
        character_data: dict
            Raw JSON structure received from the Marvel API containing
            character information.
        
        Return:
            A dictionary with the character information required by the
            HTML template.
        """
        res = dict()
        res['name'] = character_data['name']
        res['description'] = character_data['description']
        res['image_url'] = '{}.{}'.format(character_data['thumbnail']['path'], character_data['thumbnail']['extension'])
        return res

if __name__ == '__main__':
    Main()