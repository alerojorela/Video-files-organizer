This is a simple script for organizing a movie collection consisting of video files inside some folder.

What it does:

1. Looks recursively into a folder
2. Tries to extract year and title info from filename
3. Queries **IMDb** with previous info
4. Asks user if needed in order to disambiguate films with similar names

And takes some actions:

5. renames files (and files sharing the file stem) to an standard format (change it if you want it in `add_films.py`):

```
title  year directors - actors [VO]
```

6. fills a `.tsv` file (creates it or appends info) with movie info extracted from IMDb

## Requirements

```
import pandas tabulate IMDbPY
```

## Usage

| file            | action                                                       | arguments                |
| --------------- | ------------------------------------------------------------ | ------------------------ |
| query_imdb.py   | for getting IMDb info                                        | 1: movie name            |
| parse_folder.py | for parsing files names                                      | 1: folder                |
| add_films.py    | renames and fills some database (implemented only for `.tsv`) | 1: folder 2: output file |

```BASH
python3 query_imdb.py Manhattan
python3 parse_folder.py ~/Downloads/NEW
python3 add_films.py ~/Downloads/NEW films_collection.tsv
```

