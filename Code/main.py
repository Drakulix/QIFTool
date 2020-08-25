"""
installed packages: apt install cURL
                    apt install python3-pip
                    pip3 install PyGithub
"""

import urllib.request
import json
import time
import sqlite3
import os
from sqlite3 import Error
from github import Github
import Metric_StatsCodeFrequency  # metric file for StatsCodeFrequency
import Metric_Contributors  # metric file for Contributors
import Metric_Issues  # metric file for Issues
import Metric_Commits  # metric file for Commits

# authentication of REST API v3

auth = Github("c2c1d13983cbb8c1d9ce7845c20d7937ba7c25a0", per_page=100)

# creates a .txt file in the current directory of the .py file
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
    except Exception as e:
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
    except Exception as e:
        print(e)


def create_database():
    """
    creates the database file and tables
    :return: False
    """
    # choose path for the database to be created at or none if you want the database to be created in
    # the current directory
    try:
        database = r"/home/robert/OSCTool/Code/OSCTool.db"
        repository_table_statement = """ CREATE TABLE IF NOT EXISTS repositories (
                                            id integer NOT NULL PRIMARY KEY,
                                            repo_id integer NOT NULL,
                                            repo_creator text NOT NULL,
                                            repo_name text NOT NULL,
                                            downloaded boolean NOT NULL,
                                            
                                            code_frequency_additions_metric integer,
                                            code_frequency_deletions_metric integer,
                                            code_frequency_difference_metric real,
                                            code_frequency_additions_value integer,
                                            code_frequency_deletions_value integer,
                                            code_frequency_difference_value real,
                                            
                                            commits_metric text,
                                            commits_value text,
                                            
                                            contributors_metric integer,
                                            contributors_value integer,
                                            
                                            issues_metric text,
                                            issues_value text,
                                            
                                            UNIQUE(repo_id, repo_creator, repo_name, downloaded, 
                                                    code_frequency_additions_metric, code_frequency_deletions_metric,
                                                    code_frequency_difference_metric, 
                                                    code_frequency_additions_value, code_frequency_deletions_value,
                                                    code_frequency_difference_value,
                                                    
                                                    commits_metric, commits_value, 
                                                    contributors_metric, contributors_value, 
                                                    
                                                    issues_metric, issues_value) ON CONFLICT IGNORE
                                            ); """
        # create the database connection
        conn = create_connection(database)
    except Error as e:
        print(e)

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
            input_test = (1, 'testcreator', 'testrepo', False,
                          999, 800,  0.2,
                          808, 559, 0.18,
                          'refactor, debt', 'refactor, debt',
                          100, 97,
                          'new, bad, old', 'new, bad, old')
            input_test2 = (1, 'testcreator', 'testrepo', True,
                          800, 500, 0.1,
                          808, 559, 0.18,
                          'refactor, debt, technical', 'refactor, debt, technical',
                          80, 97,
                          'new, bad, old, frequent', 'new, bad, old, frequent')
            insert_statement = """INSERT INTO repositories (repo_id, repo_creator, repo_name, downloaded, 
                                                    code_frequency_additions_metric, code_frequency_deletions_metric,
                                                    code_frequency_difference_metric, 
                                                    code_frequency_additions_value, code_frequency_deletions_value,
                                                    code_frequency_difference_value,
                                                    
                                                    commits_metric, commits_value, 
                                                    contributors_metric, contributors_value, 
                                                    
                                                    issues_metric, issues_value) 
                                                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?); """
            cursor.execute(insert_statement, input_test)
            cursor.execute(insert_statement, input_test2)
            select_statement = """SELECT downloaded, commits_value FROM repositories WHERE downloaded=False;"""
            commits = cursor.execute(select_statement).fetchall()
            for com in commits[0][1].split(', '):
                print(com)
            print(commits)
    except Exception as e:
        print(e)
    # TODO write when to close and commit changes into the database


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
    """
    test function to see what repositories will be looked up by searching for it
    :return:
    """
    repo_count = 0
    for i in range(1, 5):
        repo = auth.search_repositories(query='size:>500')
        for rep in repo:
            repo_count += 1
            file.write(rep.name+'\n')
            print(repo_count, rep.size, rep.name, rep.downloads_url)
            if repo_count % 100 == 0:
                # time.sleep(0.5)
                print(auth.get_rate_limit().search, auth.get_rate_limit())


def create_folder(path):
    """
    creates the folder structure the repositories will be written to
    :param path: TODO make it work via read parameter out of .txt file
                    if path is None the current directory will be used to create a folder inside
    :return: path of the created folder
    """
    if path is None:
        path = os.getcwd() + '/Repositories'
    if not os.path.exists(path):
        os.makedirs(path)
    return path


def download_repo(repo, folder):
    repo = auth.get_repo(repo)
    os.chdir(folder)
    if not os.path.exists(os.getcwd() + '/' + repo.name):
        os.makedirs(os.getcwd() + '/' + repo.name)
    os.chdir(os.getcwd() + '/' + repo.name)

    contents = repo.get_contents("")
    while contents:
        file_content = contents.pop(0)
        print(file_content.type)
        if file_content.type == 'dir':
            print(file_content)
            os.makedirs(file_content.path)
            contents.extend(repo.get_contents(file_content.path))
        else:
            print(file_content)
            try:

                file = open(file_content.path, 'wb')
                file.write(file_content.decoded_content)
            except:
                file = open(file_content.path, 'wb')
                file.write('could not write file because of unsupported decoding')


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    folder = create_folder(None)
    # create_database()
    # test_input()
    # query()
    download_repo('ytmdesktop/ytmdesktop', folder)
