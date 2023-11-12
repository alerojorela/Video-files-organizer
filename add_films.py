#! /usr/bin/python3
# -*- coding: utf-8 -*-
import sys
from datetime import date
from pathlib import Path

import re
import pandas as pd
import logging

##################################
# FROM PROJECT
##################################
import file_utils
import query_imdb
import parse_folder


logging.basicConfig(format='%(asctime)s %(message)s')
logger = logging.getLogger(__name__)




# Preparado para presentación de colores en consola. Basado en:
# https://stackoverflow.com/questions/27265322/how-to-print-to-console-in-color
fg = {'black': '\033[30m', 'red': '\033[31m', 'green': '\033[32m', 'yellow': '\033[33m', 'blue': '\033[34m',
      'magenta': '\033[35m', 'cyan': '\033[36m', 'white': '\033[37m'}
bg = {'black': '\033[40m', 'red': '\033[41m', 'green': '\033[42m', 'yellow': '\033[43m', 'blue': '\033[44m',
      'magenta': '\033[45m', 'cyan': '\033[46m', 'white': '\033[47m'}

default_output_file = Path('./output.tsv')


def query_dict(properties: dict, kind_filter='movie', lazy=False):
    """
    :param name:
    :return: dictionary
    """
    data = query_imdb.SearchFilm(properties, lazy=lazy)  # CLI disambiguation
    if data:
        # format new filename
        new_name = '%s  %s %s - %s [VO]' % (
            data['title'] if data['original title'] is None else data['original title'],
            data['year'], ", ".join(data['directors']), ", ".join(data['actors']))
        # new_name = f"{data['title']}  {data['year']} {', '.join(data['directors'])} - {', '.join(data['actors'])} [VO]"

        # organize information
        return {
            # filter
            'id': data['id'],
            'url': data['url'],
            'rating': str(data['rating']),
            'year': str(data['year']),
            'title': data['title'],

            # convert to string
            'directors': ", ".join(data['directors']),
            'actors': ", ".join(data['actors']),

            'updated': str(date.today()),  # external data
            'original_name': properties.get('original_name'),  # external data
            'new_name': new_name}  # external data
    else:
        logger.warning('NO IMDB RESULTS for %s', properties)


def read_dataframe(data_file: Path):
    headings = ['updated', 'id', 'url', 'rating', 'year', 'title', 'directors', 'actors',
                'original_name', 'new_name']
    if data_file.exists():  # append mode
        df = pd.read_csv(str(data_file), sep='\t')

        # check there are no NA on critical data
        parts = df[['id', 'year', 'title']]
        if any(parts.isna().any(axis=1)):
            print(parts[parts.isna().any(axis=1)])
            raise ValueError('database has NA on id or year fields')

        # parse data type correctly
        df = df.astype({'id': str, 'year': int})
    else:
        print('DUMPING DATA TO: ' + fg['yellow'] + str(data_file.absolute()) + fg['white'])
        df = pd.DataFrame(columns=headings)
    return df


def from_folder(input_folder: Path, output_file: Path=default_output_file):
    print('INPUT FOLDER: ' + fg['yellow'] + str(input_folder) + fg['white'])
    print('OUTPUT DATA TO: ', output_file.absolute(), '\n')
    df = read_dataframe(output_file)

    files_compilation = file_utils.search_files_in_folder(input_folder, file_utils.video_suffixes)
    # parse files
    for file_path in files_compilation:
        properties = parse_folder.parse(file_path.name)
        if properties:
            data = query_dict(properties)
            if data:
                # remove ':'
                new_name = re.sub(r'[:]', '', data['new_name'])
                print(new_name, data)
                # append to df
                # df.loc[len(df)] = data
                df = pd.concat([df, pd.DataFrame([data])], ignore_index=True)

                file_utils.rename_file_group(file_path, new_name)
            else:
                logger.error('ERROR: %s', file_path.name)
        else:
            logger.error('Unable to extract labels from item: %s', file_path.name)


    # print(df)
    df.to_csv(str(output_file), sep='\t', index=False)


def from_txt(input_file: Path, output_file: Path=default_output_file):
    print('INPUT FILE: ' + fg['yellow'] + str(input_file) + fg['white'])
    print('OUTPUT DATA TO: ', output_file.absolute(), '\n')
    df = read_dataframe(output_file)

    with input_file.open() as f:
        data = f.read()

    for title in data.splitlines():
        # properties = parse_folder.parse(title)
        if title.strip():
            properties = {"title": title}
            if properties:
                data = query_dict(properties)
                if data:
                    # remove ':'
                    new_name = re.sub(r'[:]', '', data['new_name'])
                    print(new_name, data)
                    # append to df
                    # df.loc[len(df)] = data
                    df = pd.concat([df, pd.DataFrame([data])], ignore_index=True)

                else:
                    logger.error('ERROR: %s', title)
            else:
                logger.error('Unable to extract labels from item: %s', title)

    print(df)
    df.to_csv(str(output_file), sep='\t', index=False)




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
    if input_path.is_file():
        from_txt(input_path)
    elif input_path.is_dir():
        from_folder(input_path, output_file)
    else:
        raise ValueError('Invalid argument, must be a list file or a folder')


