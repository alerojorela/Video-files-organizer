#! /usr/bin/python3
# -*- coding: utf-8 -*-
import sys
from pathlib import Path
import os
from os.path import dirname, realpath

import json
import re

# from urllib.parse import urlparse, quote
import urllib
import webbrowser

# FROM PROJECT
import utils

# formatted_regex = r"^([a-zA-Z1-9. ]+)(\([a-zA-Z1-9. ]+\))?\s*((?:19|20)[0-9]{2})"
# formatted_regex = r"^([a-záéíóúüñA-ZÁÉÍÓÚÜÑ1-9., '\-]+)  ((?:19|20)[0-9]{2})"
formatted_regex = r"^([a-zA-ZáéíóúüñÁÉÍÓÚÜÑêÊ1-9., '\-]+)(?:.+)((?:19|20)[0-9]{2}) (?:([^-]+) )?"

# unformatted_regex = r"^([a-zA-Z1-9. '\-]+)?(?:.*)\W?((?:19|20)[0-9]{2})\W?"
# regex = r"^([a-zA-Z1-9. ]+)(\([a-zA-Z1-9. ]+\))?\s*((?:19|20)[0-9]{2})"
# named groups
unformatted_regex = r"^(?P<title>[a-zA-Z1-9. '\-]+)?(?:.*)\W?(?P<year>(?:19|20)[0-9]{2})\W?"


def parse_formatted_name(name: str):
    """
    """
    m = re.match(formatted_regex, name)
    if m:
        title, year, director = m.groups()

        quoted_title = urllib.parse.quote(title.replace(' ', '+'))
        search_url = 'https://www.imdb.com/parsed/title/?title=%s&release_date=%s' % (quoted_title, year)
        return {
            'year': year,
            'title': title,
            'director': director,
            'imdb_search_url': search_url,
        }


def parse_unformatted_file_name(name: str):
    """
    :param name:
    :return: parsed data
    """
    m = re.match(unformatted_regex, name)
    if m:
        parsed = m.groupdict()
        parsed['title'] = parsed['title'].replace('.', ' ').strip()
        return parsed


def parse(name):
    parsed = parse_formatted_name(name)
    if parsed:
        print(utils.fg['green'] + json.dumps(parsed, indent=3) + utils.fg['white'])
    else:  # alternative: unformatted file name
        parsed = parse_unformatted_file_name(name)
        if parsed:
            print(json.dumps(parsed, indent=3))
        else:
            print(utils.fg['red'] + 'PARSING ERROR ' + utils.fg['white'] + name)
    return parsed


if __name__ == "__main__":
    if len(sys.argv) != 2:  # [program.py, folder]
        # input_path = Path(os.path.dirname(os.path.realpath(__file__)))
        print('One argument missing: ')
        print('  %s path' % sys.argv[0])
        sys.exit(2)

    input_path = Path(sys.argv[1])
    print('INPUT FOLDER: ' + utils.fg['yellow'] + str(input_path) + utils.fg['white'] + '\n')

    files_compilation = utils.search_files_in_folder(input_path, utils.video_suffixes)
    results = {}
    # parse file
    for file in files_compilation:
        name = file.name
        parsed = parse(name)
        if parsed:
            results[str(file.absolute())] = parsed
            # webbrowser.open(parsed['imdb_search_url'], new=2)

    # print(json.dumps(results, indent=3))
