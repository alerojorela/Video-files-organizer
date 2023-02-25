#! /usr/bin/python3
# -*- coding: utf-8 -*-
import sys
from datetime import date
from pathlib import Path

import re
import pandas as pd

# FROM PROJECT
import utils
import query_imdb
from parse_folder import *

# Preparado para presentación de colores en consola. Basado en:
# https://stackoverflow.com/questions/27265322/how-to-print-to-console-in-color
fg = {'black': '\033[30m', 'red': '\033[31m', 'green': '\033[32m', 'yellow': '\033[33m', 'blue': '\033[34m',
      'magenta': '\033[35m', 'cyan': '\033[36m', 'white': '\033[37m'}
bg = {'black': '\033[40m', 'red': '\033[41m', 'green': '\033[42m', 'yellow': '\033[43m', 'blue': '\033[44m',
      'magenta': '\033[45m', 'cyan': '\033[46m', 'white': '\033[47m'}


def format(name: str):
    """
    :param name:
    :return: dictionary
    """
    query_dict = parse(name)
    if query_dict:
        query = ' '.join((query_dict.get('year'), query_dict.get('title')))
        if query.strip():

            data = query_imdb.SearchFilm(query)  # CLI disambiguation
            if data:

                # format new filename
                new_name = '%s  %s %s - %s [VO]' % (
                    data['title'] if data['original title'] is None else data['original title'],
                    data['year'], ", ".join(data['directors']), ", ".join(data['actors']))
                # new_name = f"{data['title']}  {data['year']} {', '.join(data['directors'])} - {', '.join(data['actors'])} [VO]"

                # organize information
                return {
                    'id': data['id'],
                    'url': data['url'],
                    'rating': str(data['rating']),
                    'year': str(data['year']),
                    'title': data['title'],
                    # convert to string
                    'directors': ", ".join(data['directors']),
                    'actors': ", ".join(data['actors']),

                    'updated': str(date.today()),  # external data
                    'original_name': name,  # external data
                    'new_name': new_name}  # external data

            else:
                utils.error_message('NO IMDB RESULTS', name)
        else:
            utils.error_message('Unable to extract labels from file name', name)
    else:
        utils.error_message('Unable to extract labels from file name', name)


if __name__ == "__main__":

    # ARGUMENTS
    # 1 folder
    # 2 data base (OPTIONAL)
    if len(sys.argv) != 3:
        print('Some argument missing: ')
        print('  %s folder dump_file.tsv' % sys.argv[0])
        sys.exit(1)

    input_path = Path(sys.argv[1])
    output_file = Path(sys.argv[2])
    print('INPUT FOLDER: ' + fg['yellow'] + str(input_path) + fg['white'])
    print('OUTPUT DATA TO: ', output_file.absolute(), '\n')
    """
    input_path = Path('/home/targa/Downloads/NEW')
    output_file = Path('./filmslog.tsv')
    """

    headings = ['id', 'url', 'rating', 'year', 'title', 'directors', 'actors',
                'updated', 'original_name', 'new_name']
    if output_file.exists():  # append mode
        print('APPENDING DATA TO: ' + fg['yellow'] + str(output_file.absolute()) + fg['white'])
        df = pd.read_csv(str(output_file), sep='\t')

        # check there are no NA on critical data
        parts = df[['id', 'year', 'title']]
        if any(parts.isna().any(axis=1)):
            print(parts[parts.isna().any(axis=1)])
            # no NA
            raise ValueError('database has NA on id or year fields')

        # parse data type correctly
        data_types_dict = {'id': str, 'year': int}
        df = df.astype(data_types_dict)
    else:
        print('DUMPING DATA TO: ' + fg['yellow'] + str(output_file.absolute()) + fg['white'])
        df = pd.DataFrame(columns=headings)

    files_compilation = utils.search_files_in_folder(input_path, utils.video_suffixes)
    # parse files
    for file_path in files_compilation:
        data = format(file_path.name)
        if data:
            # remove ':'
            new_name = re.sub(r'[:]', '', data['new_name'])
            print(new_name, data)
            # append to df
            df.loc[len(df)] = data
            utils.rename_file_group(file_path, new_name)
        else:
            print(fg['red'] + 'ERROR ' + fg['white'] + file_path.name)

    # print(df)
    df.to_csv(str(output_file), sep='\t', index=False)
