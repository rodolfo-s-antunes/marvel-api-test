# Marvel API Simple Test

This project contains a simple Python script that recovers data from the Marvel Comic API. It obtains data about a story and generates a corresponding HTML file that contains the story description and a list of characters with the respective pictures provided by Marvel.

## Installation

The script requires **Python 3**. Also, you will need to install the following modules:

* jinja2
* urllib3

If you use **pip**, simple run the command `pip install jinja2 urllib3`

To install the program, you can directly download the files from Github or you can use Git:

`git clone https://github.com/rodolfo-s-antunes/marvel-api-test.git`

## Running the Program

To run the program, run the `main.py` script using the python interpreter. The script is located in the `marvel-api` directory. The program has two modes of operation, which can be selected through its command line parameters.

### Mode 1: Generate a description from a randomly selected story of a given character

In this mode, the program requires the name of a character as parameter. It will query the Marvel API for all the available stories on the character and randomly select one to produce its HTML description. To use this mode, use the `--name` parameter. For example:

`python3 main.py --name "Iron Man"`

**Important:** This program will take a long time to finish if this mode is used with a popular character with a long list of stories. To try it out, use characters that appear on less Marvel stories, such as Dum Dum Dugan

`python3 main.py --name "Dum Dum Dugan"`

### Mode 2: Generate a description from a specific Marvel story

In this mode, the program requires the unique ID of a story. It will then query the API for information on it and generate the corresponding HTML description. To use this mode, use the `--id` parameter. For example:

`python3 main.py --id 51906`

If the provided ID does not exist in the comic database, the program will return an error.

### Output file name

The program also allows the user to specify the name of the resulting HTML file. To change it, use the `--out` parameter. The default name of the output file is `out.html`. For example:

`python3 main.py --id 51906 --out "comic.html"` 