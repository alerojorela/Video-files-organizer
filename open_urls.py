#! /usr/bin/python3
# -*- coding: utf-8 -*-
import sys
from datetime import date
from pathlib import Path

import re
import pandas as pd
import logging
import webbrowser

import fire

##################################
# FROM PROJECT
##################################
from add_films import read_dataframe



def run(data_path: Path,rating_mappings:list=None):
    rating_mappings = [1,2,3,4,5,6,7,8,9,10,10]
    data_path = Path(data_path)

    df = read_dataframe(data_path)

    print(df)
    # "rated on site" values: update, updated
    subset = df[df['rated on site'] == 'update']
    print(subset)
    for index, row in subset.iterrows():
        # TODO: float
        personal_rating = int(row['MY RATING'])
        if rating_mappings:
            personal_rating2 = rating_mappings[personal_rating]
            print(personal_rating2, '<-', personal_rating, row.year, row.title)
        else:
            print(personal_rating, row.year, row.title)
        webbrowser.open_new_tab(row.url)

if __name__ == '__main__':
    # mappings = [0,1,2,3,4,5,6,7,8,9,10]
    fire.Fire(run)

