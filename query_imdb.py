#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
search_movie.py
Usage: search_movie "movie title"
Search for the given title and print the results.

pip install IMDbPY pandas tabulate


IMDbPY is now cinemagoer

This package has been renamed. Use pip install cinemagoer instead.
"""

import sys
import re
import webbrowser

import json
import pandas as pd
from io import StringIO
from tabulate import tabulate

# FROM PROJECT
import file_utils

# Import the IMDbPY package.
try:
    import imdb
except ImportError:
    print("""You need to install the IMDbPY package!
    pip install IMDbPY""")
    sys.exit(1)

ia = imdb.IMDb()

# Preparado para presentación de colores en consola. Basado en:
# https://stackoverflow.com/questions/27265322/how-to-print-to-console-in-color
fg = {'black': '\033[30m', 'red': '\033[31m', 'green': '\033[32m', 'yellow': '\033[33m', 'blue': '\033[34m',
      'magenta': '\033[35m', 'cyan': '\033[36m', 'white': '\033[37m'}
bg = {'black': '\033[40m', 'red': '\033[41m', 'green': '\033[42m', 'yellow': '\033[43m', 'blue': '\033[44m',
      'magenta': '\033[45m', 'cyan': '\033[46m', 'white': '\033[47m'}

headings = ['ID', 'YEAR', 'KIND', 'NAME', 'URL']


def get_url(movie):
    # def get_url(id: int):
    # url = ia.get_imdbURL(movie)
    return f'https://www.imdb.com/title/tt{movie.movieID}'


def search_movie(query):
    try:
        # Do the search, and get the results (a list of Movie objects).
        results = ia.search_movie(query)
        return results
    except imdb.IMDbError as e:
        print("Probably you're not connected to Internet.  Complete error report:")
        print(e)
        sys.exit(3)


def id_from_url(url):
    match = re.search(r'/tt(\d+)/?', url)
    if match:
        return match.group(1)


def SearchFilm(properties: str, kind_filter: str=None, lazy=False):
    """
    manages ambiguity by CLI user input
    :param query:
    :return:
    """

    # filter attributes
    # 1)
    """
    select_properties = ['year', 'director']
    # filtered_properties = {key: value for key, value in properties.items() if key in select_properties and value}
    # query = ' '.join([str(_) for _ in filtered_properties.values()])
    query = ' '.join([str(value) for key, value in properties.items() if key in select_properties and value])
    results = search_movie(query)
    """
    results = None
    # 2)
    if not results:
        select_properties = ['year', 'title']  # IMPORTANT: Order
        # query = ' '.join([str(properties.get(key)) for key in select_properties])
        query = ' '.join([str(properties[key]) for key in select_properties if properties.get(key)])
        # query = ' '.join([str(value) for key, value in properties.items() if key in select_properties and value])
        results = search_movie(query)
    # 3) MANUAL

    if not results:
        if lazy:
            return
        id = None
        while not id:
            answer = input(fg['yellow'] + "SEARCH UNSUCCESSFULL (write 'pass' to ignore; or insert imdb url: " + fg['white'])
            if answer.lower() == 'pass':
                print(fg['red'] + "PASS" + fg['white'])
                return
            # todo pass
            id = id_from_url(answer)
        print('id:', id)            
        data = FillData(id)
        return data

    # Print the results.
    print('*' * 80 + '\n' + fg['yellow'] + query + fg['white'] + ' (%s result%s)' % (
        len(results), ('', 's')[int(bool(results))]))

    new_table = []
    # Extracting information
    for movie in results:
        # movie.movieID movie.keys
        # filter
        kind = movie['kind']
        if not kind_filter or kind_filter == kind:  # filter out non movies
            year = movie.get('year', '')
            url = get_url(movie)

            if not new_table:  # first item
                # the chances are high for the first film to be the one we're looking for
                # so, launch webbrowser in order to allow informed confirmation by the user
                # this won't work from a different environment
                # webbrowser.open_new_tab(url)

                # show first movie detailed info
                # first_item = df.iloc[0]
                # data = FillData(first_item['ID'])
                data = FillData(movie.movieID)
                df_first = pd.DataFrame([{'Year': data['year'],
                                          'Directors': ", ".join(data['directors']),
                                          'Actors': ", ".join(data['actors'])
                                          }])

                if data['directors']:
                    directors = ', '.join(data['directors'])
                    print(data['year'], directors, 'VS.')
                    print(properties.get('year'), properties.get('director'))
                    # if data['year'] == properties.get('year') and data['directors'] and data['directors'][0] == properties.get('director'):
                    if data['year'] == properties.get('year') and directors == properties.get('director'):                    
                        print('🥳🥳 SAME YEAR & DIRECTORS 🥳🥳')
                        return data

                print('\nFirst movie info:')
                print(tabulate(df_first, headers='keys', tablefmt='psql'))
                if not lazy:
                    webbrowser.open_new_tab(url)

            new_table.append([movie.movieID, year, kind, movie['title'], url])

        if lazy:
            return  # lazy: avoid disambiguation of films

    if new_table:
        df = pd.DataFrame(new_table, columns=headings)

        # show all short info
        print()
        print(tabulate(df, headers='keys', tablefmt='psql'))

        indices = df.index.to_list()
        selection = None
        while selection not in indices:
            answer = input("Choose (ENTER for first one, the one shown in web browser; 'pass' to ignore; or a imdb url): ").strip()
            if answer:
                if answer.lower() == 'pass':
                    print(fg['red'] + "PASS" + fg['white'])
                    return None
                elif id_from_url(answer):
                    selectedId = id_from_url(answer)
                    return FillData(selectedId)
                else:
                    try:
                        selection = int(answer)
                        selectedId = df.iloc[selection]['ID']
                    except:
                        print(fg['red'] + "it's not a valid number" + fg['white'])
            else:  # empty string '' just enter
                selection = 0
                selectedId = df.iloc[selection]['ID']
                # break
        
        data = FillData(selectedId)
        return data


def FillData(id, directors_max=2, actors_max=4):
    movie = ia.get_movie(str(id))
    # critical conditions:
    # sometimes the first item has no actors (some episodes...)
    # assert movie.get('cast'), "No actors found"
    # assert 'director' in movie and movie['director'], "No directors found"
    directors = movie.get('director', [])
    actors = movie.get('cast', [])

    return {'id': id,
            'url': get_url(movie),
            'rating': movie.get('rating'),
            'year': movie.get('year'),
            'title': movie.get('title'),  # english title
            'original title': movie.get('original title'),
            'directors': [_['name'] for _ in directors[:directors_max]],
            'actors': [_['name'] for _ in actors[:actors_max]],
            }


'''

['title', 'kind', 'year', 'cover url', 'canonical title', 'long imdb title', 'long imdb canonical title', 'smart canonical title', 'smart long imdb canonical title', 'full-size cover url']
cast | genres | runtimes | countries | country codes | language codes | color info | aspect ratio | sound mix | box office | certificates | original air date | rating | votes | cover url | plot outline | languages | title | year | kind | directors | writers | producers | composers | cinematographers | editors | editorial department | casting directors | production designers | art directors | set decorators | costume designers | make up department | production managers | assistant directors | art department | sound department | special effects | visual effects | stunts | camera department | casting department | costume departmen | location management | music department | script department | transportation department | miscellaneous | thanks | akas | writer | director | production companies | distributors | special effects companies | other companies | plot | synopsis | canonical title | long imdb title | long imdb canonical title | smart canonical title | smart long imdb canonical title | full-size cover url

for i in ia.get_movie_infoset():
    print(i)


airing
akas
alternate versions
awards
connections
crazy credits
critic reviews
episodes
external reviews
external sites
faqs
full credits
goofs
keywords
locations
main
misc sites
news
official sites
parents guide
photo sites
plot
quotes
release dates
release info
reviews
sound clips
soundtrack
synopsis
taglines
technical
trivia
tv schedule
video clips
vote details

'''

# De esta forma, el archivo se puede ejecutar desde el exterior.
if __name__ == "__main__":
    if len(sys.argv) != 2:
        print('One argument missing: ')
        print('  %s "movie title"' % sys.argv[0])
        sys.exit(2)

    print('QUERY: ' + file_utils.fg['yellow'] + sys.argv[1] + file_utils.fg['white'] + '\n')
    query = sys.argv[1]
    data = SearchFilm(query)
    print(json.dumps(data, indent=3))
