# Google sheet dependancies----------------------------------------
from __future__ import print_function
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
#------------------------------------------------------------------
import pandas as pd
import numpy as np
import re as re
import time
import itertools
import requests
import mysql.connector
import pymysql
import plotly.graph_objects as go
import chart_studio.plotly as py
import plotly.offline as py
import warnings
import os
import pickle
import psycopg2
# -- NEW --
import json
#----------
from sqlalchemy import create_engine
from datetime import datetime, timedelta, date


#-------------------------------------------------------------------
#translation of special characters
special_characters={r',':'', r';':'', r'.':'', r':':'', r'%':'',
                    r'@':'', r'$':'', r')':'', r'(':'', r'!':'',
                    r'*':'', r'/':'', r"'":'', r'-':'', r'_':'',
                    r']':'', r'[':'', r'|':'', r'#':'', r'&':'and'}
trans_table = r",;.:%@$)(!*/'-_][|#&".maketrans(special_characters)
#-------------------------------------------------------------------
#NOTEBOOK FUNCTIONS
def daterange(date1, date2):
    for n in range(int ((date2 - date1).days)+1):
        yield date1 + timedelta(n)

def textFilter(string, substr):
    '''
    Intended process:
        Extract elements from argument [string] list if any of the elements in [substr] list is in it.
        Then returns a list of the filtered elements from [string]

    Arguments:
        string: list type
            (mandatory) list of string type elements.
        substr: list type
            (mandatory) list of string type elements.

    Return: list type
        A list of string types
    '''
    return [str for str in string if
             any(sub in str for sub in substr)]
#------------------------------------------------------------------
def fileName(text, upperLimit=1000, lowerLimit=0):
    #find one or more alphanumerical characters followed by "." and a max of 3 more characters
    try:
        regex = re.compile(r'[\w]+\.[a-z]{3}')
        found = regex.findall(text)
        found = found[0]
        found = found[lowerLimit:upperLimit]
    except AttributeError:
        found = 'no_name'
    return found
#------------------------------------------------------------------
def sql_engine(un, pw, host, port, db, close={'bool':False,'dispose':None}):
    '''
    Intended process:
        Establishes/Closes a single mysql engine database
        (Requieres 'from sqlalchemy import create_engine' library)

    Arguments:
        un: str type
            (mandatory) username for logging in to the database.
        pw: str type
            (mandatory) password for logging in to the database.
        host: str type
            (mandatory) host ip for logging in to the database.
        port: str type
            (mandatory) port for logging in to the database.
        db: str type
            (mandatory) name of database inside the mysql connection to use.
        close: dict type
            (optional) dictionary used to close connections or engine
                + 'bool' key: If TRUE, you are asking to close a connection/engine
                + 'dispose' key: you should provide the object that you want to close

    Return:
        A engine object (from sqlalchemy library) that holds the connection to a datase

    References:
        1. https://gist.github.com/stefanthoss/364b2a99521d5bb76d51
        2. https://pythontic.com/pandas/serialization/mysql
    '''
    if close['bool']==True:
        if not(isinstance(close['dispose'], type(None))):
            return close['dispose'].dispose()
        else:
            return print('A sqlalchemy engine type object must be provided to be closed')
    else:
        engine_str = f'mysql+pymysql://{un}:{pw}@{host}:{port}/{db}'
        engine = create_engine(engine_str)
        return engine

def sql_connection(engine, close={'bool':False,'dispose':None}):
    '''
    Intended process:
        Establishes/Closes a single connection to a mysql database
        (Requieres 'from sqlalchemy import create_engine' library)

    Arguments:
        engine: str type
            (mandatory) engine which the connection is going to get established to
        close: dict type
            (optional) dictionary used to close connections or engine
                + 'bool' key: If TRUE, you are asking to close a connection/engine
                + 'dispose' key: you should provide the object that you want to close

    Return:
        A connection object (from sqlalchemy library) that holds the connection to a datase

    References:
        1. https://gist.github.com/stefanthoss/364b2a99521d5bb76d51
        2. https://pythontic.com/pandas/serialization/mysql
    '''
    if close['bool']==True:
        if not(isinstance(close['dispose'], type(None))):
            return close['dispose'].close()
        else:
            return print('A sqlalchemy connection type object must be provided to be closed')
    else:
        db_connection = engine.connect()
        return db_connection

def readMysql(un, pw, host, port, db, query, parameters=None, col_to_date=None, load_size=None):
    '''
    Intended process:
        Read a table from a MySQL database with given credentials [un, pw, host, , port, db] and speficit query. It can be a parameterized query.
        (Requieres 'from sqlalchemy import create_engine' library)

    Arguments:
        un: str type
            (mandatory) username for logging in to the database.
        pw: str type
            (mandatory) password for logging in to the database.
        host: str type
            (mandatory) host ip for logging in to the database.
        port: str type
            (mandatory) port for logging in to the database.
        query: str type
            (mandatory) stadard query following mysql structure. It can be parameterized under PEP 249 guidances. More information on reference 2.
        parameters: array-like
            (optional) parameters to be set when using a parameterized query. More information on reference 1.
        col_to_date: array-like
            (optional) list of columns to be parse as dates. More information on reference 1.
        load_size: int
            (optional) allows the function to behave iteratively, loading a set number of rows instead of the whole table until gets loaded completly
                       More information on reference 1.

    Return:
        A dataframe exactly as the query was written for MySQL

    References:
        1.https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.read_sql_query.html
        2.https://www.psycopg.org/docs/usage.html#passing-parameters-to-sql-queries
        3.https://gist.github.com/stefanthoss/364b2a99521d5bb76d51
        4.https://stackoverflow.com/questions/1633332/how-to-put-parameterized-sql-query-into-variable-and-then-execute-in-python
        5.https://pythontic.com/pandas/serialization/mysql
    '''

    engine_str = f'mysql+pymysql://{un}:{pw}@{host}:{port}/{db}'
    engine = create_engine(engine_str)
    dbConnection = engine.connect()
    df_output = pd.read_sql_query(sql=query, con=dbConnection, params=parameters, parse_dates=col_to_date, chunksize=load_size)
    dbConnection.close()

    return df_output
#------------------------------------------------------------------
def readPostgresql(un, pw, host, port, db, query, parameters=None, col_to_date=None, load_size=None):
    '''
    Intended process:
        Read a table from a MySQL database with given credentials [un, pw, host, , port, db] and speficit query. It can be a parameterized query.
        (Requieres 'from sqlalchemy import create_engine' library)

    Arguments:
        un: str type
            (mandatory) username for logging in to the database.
        pw: str type
            (mandatory) password for logging in to the database.
        host: str type
            (mandatory) host ip for logging in to the database.
        port: str type
            (mandatory) port for logging in to the database.
        query: str type
            (mandatory) stadard query following Postgresql structure. It can be parameterized under PEP 249 guidances. More information on reference 2 of function readMysql.
        parameters: array-like
            (optional) parameters to be set when using a parameterized query. More information on reference 1 of function readMysql.
        col_to_date: array-like
            (optional) list of columns to be parse as dates. More information on reference 1 of function readMysql.
        load_size: int
            (optional) allows the function to behave iteratively, loading a set number of rows instead of the whole table until gets loaded completly
                       More information on reference 1.

    Return:
        A dataframe exactly as the query was written for Postgresql

    References:
        1.All references realted to function readMysql apply here as well
        2.https://stackoverflow.com/questions/9353822/connecting-postgresql-with-sqlalchemy
        3.https://docs.sqlalchemy.org/en/14/core/engines.html#postgresql
    '''

    engine_str = f'postgresql+psycopg2://{un}:{pw}@{host}:{port}/{db}'
    engine = create_engine(engine_str)
    dbConnection = engine.connect()
    df_output = pd.read_sql_query(sql=query, con=dbConnection, params=parameters, parse_dates=col_to_date, chunksize=load_size)
    dbConnection.close()

    return df_output
#------------------------------------------------------------------
def get_google_sheets(sheed_id, range_name,
                      scopes = ['https://www.googleapis.com/auth/spreadsheets.readonly']):
    '''
    Intended process:
        Read a table a google sheet owned/shared by/to you given a worksheed and a sheed range
    '''
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', scopes)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'client_secret.json', scopes)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    service = build('sheets', 'v4', credentials=creds)

    # Call the Sheets API
    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=sheed_id,
                                range=range_name).execute()
    values = result.get('values', [])
    
    if not values:
        print('No data found')
    else:
        output = pd.DataFrame(values[1:],columns=values[0])
        output = output.replace({'': None})
        return output
#------------------------------------------------------------------
def writeMysql(un, pw, host, port, db, query, values, mode='many'):
    '''
    For values use a list of columns of a dataframe:
        list(zip(df.column1,df.column2,df.column3))

    References:
        1. https://pynative.com/python-mysql-update-data/
    '''
    try:
        connection = mysql.connector.connect(host=host,
                                             port=port,
                                             database=db,
                                             user=un,
                                             password=pw)
        cursor = connection.cursor()

        if mode=='single':
            cursor.execute(query,values)
        elif mode=='many':
            cursor.executemany(query,values)

        connection.commit()
        print(f'{cursor.rowcount} were affected successfully')
    except mysql.connector.Error as error:
        print("Failed to affect records into MySQL table {}".format(error))
    finally:
        if (connection.is_connected()):
            cursor.close()
            connection.close()
        return

#------------------------------------------------------------------
#leading zeroes handling
def column_forceInt(df, column, re_str=None):
    '''
    Intended process:
        Update a [column] from DataFrame [df] with string values after transforming then to int to str, avoiding str that match substring [re_str].
        It will always avoid values which can not be transform to int.

    Arguments:
        df: DataFrame type
            (mandatory) DataFrame from which the column will be parsed.
            (Requieres pandas library as pd)
        column: str type
            (mandatory) name of the column to be parsed from the DataFrame.
        re_str: str (raw)
            (optional) regular expresion str to be avoided during parsing of int values.
            (Requieres regular expresion library as re)
                - example: r'^0+$' will prevent values with only zeros to be transform to int. So '000000' will not be transform to '0'.

    Return:
        Not actual return. Function applies changes on the input DataFrame and saves the result in the parsed column.

    References:
        https://jakevdp.github.io/WhirlwindTourOfPython/14-strings-and-regular-expressions.html
    '''
    if re_str != None:
        df_temp = df[df[column].str.contains(re_str)==False]
        series = df_temp[df_temp[column].str.isdigit()==True][column]
    else:
        series = df[df[column].str.isdigit()==True][column]

    series = series.apply(lambda x: (str(int(x))))
    return df.update(series)
#------------------------------------------------------------------
def str_translation(df,columns,translation={'road':'rd','street':'st',
                                             'suite':'ste','drive':'dr',
                                             'avenue':'ave','highway':'hwy',
                                             'north':'n','south':'s',
                                             'east':'e','west':'w',
                                             'northwest':'nw','northeast':'ne',
                                             'southwest':'sw','southeast':'se'},
                     case_sensitive=False,greedy=False):
    '''
    Intended process:
        Update strings of 1 or more [columns] of a dataframe [df_original], doing whole word
        translation according to a dictionary [translation]

    Arguments:
        df: DataFrame type
            (mandatory) DataFrame from which the column will be parsed.
            (Requieres pandas library as pd)
        column: array type
            (mandatory) name of the column or columns to be parsed from the DataFrame. Must be an iterable.
        translation: dictionary type
            (mandatory) Dictionary that contains the words to do translation on. Non-case senstivie.
            (Requieres pandas library as pd)
            - example: if dictionary = {'road':'rd','north':'n'} then this will happen:
                       '1234 north road drive' -> '1234 n rd drive'.
        case_sensitive: bool type
            (mandatory) Dictates whether the function will treat the dictionary [translation] as case senstivie or not
        greedy: bool type
            (mandatory) Changes the behaviour of the function:
            + False: default
                The function will only translate whole words, not substrings.
            + True:
                The function will translate any matching string or substring according to the dictionary [translation]
                    - example: if dictionary = {'ham':'h','north':'n'} then this will happen:
                               'hamster north road' -> 'hster n road'.

    Return:
        Not actual return. Function applies changes on the input columns of the given DataFrame.
    '''
    regex_dictionary={}
    modifier = '' if case_sensitive==True else '(?i)'
    if isinstance(translation, dict):
        if greedy==True:
            for key, value in translation.items():
                regex_dictionary[f'{modifier}{key}'] = f'{value}'
        else:
            for key, value in translation.items():
                regex_dictionary[f'{modifier}^{key}\W+'] = f'{value} '
                regex_dictionary[f'{modifier}\W+{key}\W+'] = f' {value} '
                regex_dictionary[f'{modifier}\W+{key}$'] = f' {value}'

        for each in columns:
            df[each] = df[each].replace(regex_dictionary,regex=True)
    return
#------------------------------------------------------------------