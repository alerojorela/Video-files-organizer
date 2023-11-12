import os
from pathlib import Path
import difflib
import re
import pandas as pd

import logging
logger = logging.getLogger(__name__)

# https://stackoverflow.com/questions/27265322/how-to-print-to-console-in-color
fg = {'black': '\033[30m', 'red': '\033[31m', 'green': '\033[32m', 'yellow': '\033[33m', 'blue': '\033[34m',
      'magenta': '\033[35m', 'cyan': '\033[36m', 'white': '\033[37m'}
bg = {'black': '\033[40m', 'red': '\033[41m', 'green': '\033[42m', 'yellow': '\033[43m', 'blue': '\033[44m',
      'magenta': '\033[45m', 'cyan': '\033[46m', 'white': '\033[47m'}

suffixes_black_list = ['.srt', '.sup', '.py', '.idx', '.sub', '.ssa', '.zip', '.nfo', '.txt']
# video_suffixes = ['.mkv', '.mp4', '.avi', '.mov', '.mpg', '.wmv', '.iso', '.ogm']
# https://en.wikipedia.org/wiki/Video_file_format
video_suffixes = ['.3g2', '.3gp', '.amv', '.asf', '.avi', '.drc', '.flv', '.flv', '.flv', '.f4v', '.f4p', '.f4a',
                  '.f4b', '.m4v', '.mkv', '.mng', '.mov', '.qt', '.mp4', '.m4p', '.m4v', '.mpg', '.mp2', '.mpeg',
                  '.mpe', '.mpv', '.mpg', '.mpeg', '.m2v', '.MTS', '.M2TS', '.TS', '.mxf', '.nsv', '.ogv',
                  '.rm', '.rmvb', '.roq', '.svi', '.vob', '.webm', '.wmv', '.yuv',
                  '.iso']


# OGG is suitable for audio, video, text (captions), and metadata;
# ambiguous = ['.ogg']

# def error_message(message, value=''):
#    print(fg['red'] + message.upper() + ':\t' + fg['white'], value)


def search_files_in_folder(input_path: Path, suffixes: list = None):
    assert input_path.exists(), f'folder {str(input_path)} not found'
    assert input_path.is_dir(), f'path {str(input_path)} is not a folder'

    # recursive search
    files_compilation = [_ for _ in input_path.glob(r'**/*') if _.is_file() and (not suffixes or _.suffix in suffixes)]
    # Collecting into a set prevents storing duplicates
    return set(files_compilation)


def get_files_with_same_start_on_folder(file_path: Path):
    # on the same folder
    # 70% length, [:0.7]
    # glob and regex cannot be used because the files use special characters []
    stem = file_path.stem
    # iterate same folder files
    output = [file for file in file_path.parent.iterdir()
              if file.is_file() and file.name.startswith(stem)]
    return output


def get_similar_files_on_folder(folder: Path, stem: str, ratio=0.85):
    # on the same folder
    output = []
    for file in folder.iterdir():  # iterate folder files
        if file.is_file():
            matcher = difflib.SequenceMatcher(None, stem, file.stem)
            # print('>>', matcher.ratio(), stem)
            if matcher.ratio() > ratio:
                output.append(file)
    return output


def create_instructions_df(files: list, source_folder,
                           flat_copy: bool = False, filename=None):
    # source file size
    df = pd.DataFrame(files, columns=['source'])
    if flat_copy:
        df['relative_folder'] = '.'
    else:  # mantains source folder structure on target
        df['relative_folder'] = df.source.apply(lambda file: file.parent.relative_to(source_folder))
        # file_target_folder = Path(target_folder, file.parent.relative_to(source_folder))
    # file_target_folder.mkdir(parents=True, exist_ok=True)

    df['file'] = df.source.apply(lambda file: file.name)
    df['size'] = df.source.apply(lambda file: os.path.getsize(file))
    # df['hash'] =
    total_size = df['size'].sum()
    print(total_size / 1024 ** 4, 'TB')

    if filename:
        df.to_csv(filename, sep='\t')
    return df


def df_move(df, target_folder):
    for index, row in df.iterrows():
        print(target_folder, row.relative_folder, row.source)
        if Path(row.source).exists():
            # invalid chars
            filename = re.sub(r':', ' - ', row.file)
            target_file = Path(target_folder, row.relative_folder, filename)
            target_file.parent.mkdir(parents=True, exist_ok=True)

            print('...MOVING')
            print('\t· ', row.source)
            print('\t ·', target_file)

            os.rename(str(row.source), str(target_file))

            # copyfile(row.source, str(target_file))
            # shutil.move(row.source, str(target_file))
        else:
            logger.warning('File does not exist')


def rename(file_path: Path, new_file_name: str):
    new_file_path = Path(file_path.parent, new_file_name)
    file_path.rename(new_file_path)

    print('\n' + fg['magenta'] + str(file_path.parent) + '/' + fg['yellow'] + file_path.name + fg['white'] + ' =====> ')
    print(fg['magenta'] + str(new_file_path.parent) + '/' + fg['yellow'] + new_file_path.name + fg['white'])


def rename_file_group(file_path: Path, new_stem_name: str):
    '''
    renames a file and associated files (same or extended filename)
        myfilm.mkv myfilm.en.srt myfilm.es.srt
        to
        summerfilm.mkv summerfilm.en.srt summerfilm.es.srt
    '''
    stem = file_path.stem
    # glob and regex cannot be used because the files use special characters []
    for item in get_files_with_same_start_on_folder(file_path):
        new_file_name = new_stem_name + item.name[len(stem):]
        rename(item, new_file_name)
