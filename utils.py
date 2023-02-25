from pathlib import Path

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
# '.ogg',

def error_message(message, value=''):
    print(fg['red'] + message.upper() + ':\t' + fg['white'] + value)


def search_files_in_folder(input_path: Path, suffixes: list):
    assert input_path.exists(), f'folder {str(input_path)} not found'
    assert input_path.is_dir(), f'path {str(input_path)} is not a folder'

    # recursive search
    files_compilation = [_ for _ in input_path.glob(r'**/*') if _.is_file() and _.suffix in suffixes]
    # Collecting into a set prevents storing duplicates
    return set(files_compilation)


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

    # glob and regex cannot be used because the files use special charactersles []
    for item in file_path.parent.iterdir():  # iterate folder files
        if item.is_file() and item.name.startswith(stem):
            new_file_name = new_stem_name + item.name[len(stem):]
            rename(item, new_file_name)

