#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
search_movie.py
Usage: search_movie "movie title"
Search for the given title and print the results.

pip install IMDbPY pandas tabulate
"""

import sys
import webbrowser

import json
import pandas as pd
from io import StringIO
from tabulate import tabulate

# FROM PROJECT
import utils

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


def SearchFilm(query: str, kind_filter='movie'):
    """
    manages ambiguity by CLI user input
    :param query:
    :return:
    """
    try:
        # Do the search, and get the results (a list of Movie objects).
        results = ia.search_movie(query)
    except imdb.IMDbError as e:
        print("Probably you're not connected to Internet.  Complete error report:")
        print(e)
        sys.exit(3)

    # Print the results.
    print('\n' + '*' * 80 + '\n' + fg['yellow'] + query + fg['white'] + ' (%s result%s)' % (len(results),
                                                                                            ('', 's')[
                                                                                                len(results) != 1]))

    new_table = []
    # Extracting information
    for index, movie in enumerate(results):
        # movie.movieID movie.keys
        id = movie.movieID
        if id != ia.get_imdbID(movie):
            print(fg['red'] + 'ERROR ' * 100 + fg['white'])

        # filter
        kind = movie['kind']
        if not kind_filter or kind == kind_filter:  # filter out non movies
            year = movie.get('year', '')
            new_table.append([id, year, kind, movie['title'], ia.get_imdbURL(movie)])

    if new_table:
        df = pd.DataFrame(new_table, columns=headings)

        # the chances are high for the first film to be the one we're looking for
        # so, show more info about the first item
        first_id = df.iloc[0]['ID']
        data = FillData(first_id)
        print('\nFirst movie info:')
        df_first = pd.DataFrame([{'Year': data['year'],
                                  'Directors': ", ".join(data['directors']),
                                  'Actors': ", ".join(data['actors'])
                                  }])
        print(tabulate(df_first, headers='keys', tablefmt='psql'))

        # we launch the first item webpage in order to allow informed confirmation by the user
        first_movie = ia.get_movie(str(first_id))
        # webbrowser.open(ia.get_imdbURL(first_movie), new=2)

        # show all
        print()
        print(tabulate(df, headers='keys', tablefmt='psql'))

        indices = df.index.to_list()

        selection = None
        while selection not in indices:
            answer = input('Choose (ENTER for first one, the one shown in web browser): ')
            if not answer.strip():
                selection = 0
                break
            try:
                selection = int(answer)
            except:
                print(fg['red'] + "it's not a valid number" + fg['white'])

        selectedId = df.iloc[selection]['ID']
        data = FillData(selectedId)
        return data


def FillData(id, directors_max=2, actors_max=4):
    movie = ia.get_movie(str(id))
    # critical conditions:
    assert movie.get('cast'), "No actors found"
    # assert 'director' in movie and movie['director'], "No directors found"
    directors = movie.get('director', [])

    return {'id': id,
            'url': ia.get_imdbURL(movie),
            'rating': movie.get('rating'),
            'year': movie.get('year'),
            'title': movie.get('title'),  # english title
            'original title': movie.get('original title'),
            'directors': [_['name'] for _ in directors[:directors_max]],
            'actors': [_['name'] for _ in movie['cast'][:actors_max]],
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

    print('QUERY: ' + utils.fg['yellow'] + sys.argv[1] + utils.fg['white'] + '\n')
    query = sys.argv[1]
    data = SearchFilm(query)
    print(json.dumps(data, indent=3))
