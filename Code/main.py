"""
installed packages: apt install cURL
                    apt install python3-pip
                    pip3 install PyGithub
"""

import urllib.request
import json
import time
import sqlite3
from sqlite3 import Error
from github import Github
import Metric_StatsCodeFrequency  # metric file for StatsCodeFrequency
import Metric_Contributors  # metric file for Contributors
import Metric_Issues  # metric file for Issues
import Metric_Commits  # metric file for Commits

# authentication of REST API v3

auth = Github("c2c1d13983cbb8c1d9ce7845c20d7937ba7c25a0", per_page=1000)

file = open('database.txt', 'a')


# ----------------------------------------------------------------------------------------------- #

def create_connection(db_file):
    """
    create a database connection to the SQLite database specified by db_file
    :param db_file: database file
    :return: Connection object or None
    """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except Error as e:
        print(e)
    return conn


def create_table(conn, create_table_statement):
    """
    create the table for all the repositories
    :param create_table_statement: create table statement
    :param conn: connection object
    :return: False
    """
    try:
        cursor = conn.cursor()
        cursor.execute(create_table_statement)
    except Error as e:
        print(e)


def create_database():
    """
    creates the databse file and tables
    :return: False
    """
    # choose path for the database to be created at or none if you want the database to be created in
    # the current directory
    database = r"/home/robert/OSCTool/Code/OSCTool.db"
    repository_table_statement = """ CREATE TABLE IF NOT EXISTS repositories (
                                        repo_id integer NOT NULL,
                                        repo_name text NOT NULL,
                                        repo_creator_name text NOT NULL,
                                        code_frequency integer,
                                        commits text,
                                        contributors integer,
                                        issues text
                                        ); """
    # create the database connection
    conn = create_connection(database)

    # create the repositories table if it does not exist yet
    if conn is not None:
        create_table(conn, repository_table_statement)
    else:
        print('Error! Cannot create database connection.')


def test_input():
    try:
        database = r"/home/robert/OSCTool/Code/OSCTool.db"
        conn = create_connection(database)
        cursor = conn.cursor()
        with conn:
            input_test = (1, 'testrepo', 'testcreator', 999, 'refactor', 100, 'new')
            insert_statement = """INSERT INTO repositories VALUES (?, ?, ?, ?, ?, ?, ?) """
            cursor.execute(insert_statement, input_test)
    except Error as e:
        print(e)


# ------------------------------------------------------------------------------------------------ #

def testhub():
    repo = auth.get_repo("PyGithub/PyGithub")
    print(repo.get_topics())


def search():
    """
    repo = auth.search_repositories(query='spotify')
    for i in range(0, 15):
        print(Metric_Contributors.contributors_count(repo[i]), '\t',
              Metric_StatsCodeFrequency.stats_code_frequency(repo[i]),
              '\t', repo[i].full_name,
              repo[i].get_issues_events()[0].issue.get_comments())
    """
    # repo = auth.search_repositories(query='ytmdesktop')
    print(auth.get_rate_limit().search)
    print(auth.get_rate_limit())
    print('\n')
    repo = auth.search_repositories(query='size:500..1000')
    counter = 1
    repo_list = []
    for rep in repo:
        print(counter, '- remaining: ', auth.get_rate_limit().search.remaining, 'limit: ',
              auth.get_rate_limit().search.limit, rep.name)
        repo_list.append(rep.name)
        counter += 1
        if counter % 100 == 0:
            print(auth.get_rate_limit())
            break

    repo2 = auth.search_repositories(query='size:500..1000', order='asc')
    boolean = False
    for rep2 in repo2:
        if rep2.name in repo_list:
            boolean = True
        else:
            boolean = False
        print(counter, '- remaining: ', auth.get_rate_limit().search.remaining, 'limit: ',
              auth.get_rate_limit().search.limit, rep2.name, 'repo inside list: ', boolean)
        counter += 1
    repo_first = repo[0]


def query():
    repo_count = 0
    for i in range(1, 5):
        repo = auth.search_repositories(query='size:>500')
        for rep in repo:
            repo_count += 1
            file.write(rep.name+'\n')
            print(repo_count, rep.size, rep.name)
            if repo_count % 100 == 0:
                # time.sleep(0.5)
                print(auth.get_rate_limit().search, auth.get_rate_limit())


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    create_database()
    test_input()
    # query()
