"""
installed packages: apt install cURL
                    apt install python3-pip
                    pip3 install PyGithub
"""

import time
import sqlite3
import os
import configparser
import datetime

from sqlite3 import Error
from github import Github
import Metric_StatsCodeFrequency  # metric file for StatsCodeFrequency
import Metric_Contributors  # metric file for Contributors
import Metric_Issues  # metric file for Issues
import Metric_Commits  # metric file for Commits
import Metric_PullRequests # metric file for Pull Requests


# -------------------------------------------------------------------------------------------------------------------- #
# the following block of code is part of the database interaction


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


def create_database(path):
    """
    creates the database file and tables
    :return: False
    """
    # choose path for the database to be created at or none if you want the database to be created in
    # the current directory of the main.py
    try:
        if path == 'current':
            database = os.getcwd() + '/OSCTool.db'
        else:
            database = path + '/OSCTool.db'
        repositories_table_statement = """ CREATE TABLE IF NOT EXISTS repositories (
                                            repo_id integer NOT NULL PRIMARY KEY,
                                            repo_creator text NOT NULL,
                                            repo_name text NOT NULL,
                                            repo_size integer NOT NULL,
                                            downloaded boolean NOT NULL,
                                            last_access text NOT NULL,
                                            
                                            code_frequency_additions integer,
                                            code_frequency_deletions integer,
                                            code_frequency_difference real,
                                            
                                            contributors integer,
                                            
                                            commits_keywords text,
                                            
                                            issues_keywords text,
                                            
                                            pull_requests_keywords text,
                                            
                                            UNIQUE(repo_id, repo_creator, repo_name, repo_size, downloaded, last_access,
                                                    code_frequency_additions, code_frequency_deletions,
                                                    code_frequency_difference,
                                                    contributors, commits_keywords, issues_keywords,
                                                    pull_requests_keywords) ON CONFLICT IGNORE
                                            ); """

        commits_table_statement = """ CREATE TABLE IF NOT EXISTS commits (
                                                                    repo_id integer NOT NULL,
                                                                    commit_id integer NOT NULL PRIMARY KEY,
                                                                    keywords text NOT NULL,
                                                                    commit_author_id integer NOT NULL,
                                                                    commit_author_name text NOT NULL,
                                                                    commit_additions integer NOT NULL,
                                                                    commit_deletions integer NOT NULL,

                                                                    FOREIGN KEY (repo_id) REFERENCES 
                                                                    repositories (repo_id),

                                                                    UNIQUE(repo_id,commit_id, keywords, 
                                                                    commit_author_id, commit_author_name, 
                                                                    commit_additions, commit_deletions) 
                                                                    ON CONFLICT IGNORE
                                                                    ); """

        issues_table_statement = """ CREATE TABLE IF NOT EXISTS issues (
                                                    repo_id integer NOT NULL,
                                                    issue_id integer NOT NULL PRIMARY KEY,
                                                    keywords text NOT NULL,
                                                    issue_number integer NOT NULL,
                                                    labels text NOT NULL,
                                                    amount_of_comments integer NOT NULL,
                                                    create_date text NOT NULL,
                                                    closed_date text NOT NULL,
                                                    
                                                    FOREIGN KEY (repo_id) REFERENCES repositories (repo_id),

                                                    UNIQUE(repo_id, issue_id, keywords, issue_number, labels, 
                                                    amount_of_comments, create_date, closed_date) ON CONFLICT IGNORE
                                                    ); """

        pull_requests_table_statement = """ CREATE TABLE IF NOT EXISTS pull_requests (
                                                            repo_id integer NOT NULL,
                                                            pull_request_id integer NOT NULL PRIMARY KEY,
                                                            keywords text NOT NULL,
                                                            pull_request_number integer NOT NULL,
                                                            labels text NOT NULL,
                                                            amount_of_comments integer NOT NULL,
                                                            amount_of_commits integer NOT NULL,
                                                            create_date text NOT NULL,
                                                            closed_date text NOT NULL,

                                                            FOREIGN KEY (repo_id) REFERENCES repositories (repo_id),

                                                            UNIQUE(repo_id, pull_request_id, keywords, 
                                                                    pull_request_number, labels, 
                                                                    amount_of_comments, amount_of_commits, 
                                                                    create_date, closed_date) ON CONFLICT IGNORE
                                                            ); """
        # create the database connection
        conn = create_connection(database)

        # create the tables if they do not exist yet
        create_table(conn, repositories_table_statement)
        create_table(conn, issues_table_statement)
        create_table(conn, pull_requests_table_statement)
        create_table(conn, commits_table_statement)
    except Error as e:
        print(e.with_traceback(e.__traceback__))


def insert(conn, table, values):
    """
    insert function to write the given values inside the database table 'repositories'
    :param table: string code of the table and column that should be written into
    :param conn: the connection made of the database
    :param values: the values to be written inside the table
    :return: False
    """
    cursor = conn.cursor()
    insert_statement = None
    if table == 'repositories':
        insert_statement = """INSERT INTO repositories (repo_id, repo_creator, repo_name, repo_size, downloaded, 
                                                        last_access, code_frequency_additions, code_frequency_deletions,
                                                        code_frequency_difference, contributors) 
                                                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?); """
    elif table == 'repositories_commits':
        insert_statement = """INSERT INTO repositories (commits_keywords) VALUES (?); """
    elif table == 'repositories_issues':
        insert_statement = """INSERT INTO repositories (issues_keywords) VALUES (?); """
    elif table == 'repositories_pull_requests':
        insert_statement = """INSERT INTO repositories (pull_requests_keywords) VALUES (?); """
    # ---------------------------------------------------------------------------------------------------------------- #
    elif table == 'commits':
        insert_statement = """INSERT INTO commits (repo_id, issue_id, amount_of_comments, 
                                                    issue_number, create_date, closed_date) 
                                                    VALUES (?, ?, ?, ?, ?, ?); """
    elif table == 'commits_keywords':
        insert_statement = """INSERT INTO commits (keywords) VALUES (?); """
    elif table == 'commits_labels':
        insert_statement = """INSERT INTO commits (labels) VALUES (?); """
    # ---------------------------------------------------------------------------------------------------------------- #
    elif table == 'issues':
        insert_statement = """INSERT INTO issues (repo_id, issue_id, issue_number, amount_of_comments,
                                                    create_date, closed_date) 
                                                    VALUES (?, ?, ?, ?, ?, ?); """
    elif table == 'issues_keywords':
        insert_statement = """INSERT INTO issues (keywords) VALUES (?); """
    elif table == 'issues_labels':
        insert_statement = """INSERT INTO issues (labels) VALUES (?); """
    # ---------------------------------------------------------------------------------------------------------------- #
    elif table == 'pull_requests':
        insert_statement = """INSERT INTO pull_requests (repo_id, pull_request_id, pull_request_number, 
                                                        amount_of_comments, amount_of_commits, create_date, closed_date) 
                                                        VALUES (?, ?, ?, ?, ?, ?, ?); """
    elif table == 'pull_requests_keywords':
        insert_statement = """INSERT INTO pull_requests (keywords) VALUES (?); """
    elif table == 'pull_requests_labels':
        insert_statement = """INSERT INTO pull_requests (labels) VALUES (?); """
    # ---------------------------------------------------------------------------------------------------------------- #
    with conn:
        try:
            if insert_statement is not None:
                for value in values:
                    cursor.execute(insert_statement, value)
            else:
                print('table selection went wrong!')
        except Exception as e:
            print(e.with_traceback(e.__traceback__))
    # TODO write when to close and commit changes into the database


# -------------------------------------------------------------------------------------------------------------------- #
# the following block of code deals with the folder structure and the downloading of the repositories


def create_download_folder(path):
    """
    creates the folder structure the repositories will be written to
    :param path: path for the folder to be created at
    :return: path of the created folder
    """
    if path == 'current':
        path = os.getcwd() + '/repositories'
    if not os.path.exists(path):
        os.makedirs(path)
    return path


def download_repo(auth, repo, folder):
    """
    function to download the repo as it is seen in github with the folder structure intact
    :param auth: authentication object to perform necessary calls
    :param repo: repository object to download
    :param folder: path of the folder where the repository will be dowloaded in
    :return: False
    """
    repo = auth.get_repo(repo)
    repo_creator = repo.full_name.split('/')[0]
    os.chdir(folder)
    folder_name = os.getcwd() + '/' + repo_creator + '_' + repo.name + '_' + repo.id
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)
    os.chdir(folder_name)

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
            except Exception as e:
                file = open(file_content.path, 'w')
                file.write('could not write file because of unsupported decoding')
                print(e.with_traceback())


# -------------------------------------------------------------------------------------------------------------------- #
# the following block of code deals with the creation and reading of the config file


def create_config():
    config = configparser.ConfigParser()
    config['DEFAULT'] = {'path_of_database': 'current',
                         'path_of_download': 'current',
                         'loops_of_1000s': '1'
                         }
    config['manual'] = {'path_of_database': r"/home/robert/OSCTool/Code",
                        'path_of_download': r"/home/robert/OSCTool/Code",
                        'loops_of_1000s': '1',
                        }
    config['mode'] = {'use_default_values': 'yes'
                      }
    config['metric_values'] = {'commits': '',
                               'issues': '',
                               'pull_requests': '',
                               'contributors': '0',
                               'statscodefrequency_additions': '0',
                               'statscodefrequency_deletions': '0',
                               'statscodefrequency_difference': '0'
                        }
    if not (os.path.isfile('config.ini')):
        with open('config.ini', 'w') as config_file:
            config.write(config_file)


def read_config():
    values = {
        'loops_of_1000s': '',
        'issues': '',
        'commits': '',
        'pull_requests': '',
        'contributors': '',
        'statscodefrequency_additions': '',
        'statscodefrequency_deletions': '',
        'statscodefrequency_difference': ''
    }
    config = configparser.ConfigParser()
    config.read('config.ini')
    config_mode = read_config_mode(config)
    values['loops_of_1000s'] = config[config_mode]['loops_of_1000s']
    values['issues'] = config['metric_values']['issues'].split('\t')
    values['commits'] = config['metric_values']['commits'].split('\t')
    values['pull_requests'] = config['metric_values']['pull_requests'].split('\t')
    values['contributors'] = config['metric_values']['contributors']
    values['statscodefrequency_additions'] = config['metric_values']['statscodefrequency_additions']
    values['statscodefrequency_deletions'] = config['metric_values']['statscodefrequency_deletions']
    values['statscodefrequency_difference'] = config['metric_values']['statscodefrequency_difference']
    return values


def read_config_mode(config):
    """
    function to read out which section should be used for the following instructions
    :param config: config object used to access the config file
    :return:
    """
    use_default_values = config.get('mode', 'use_default_values')
    if use_default_values == 'yes':
        return 'DEFAULT'
    elif use_default_values == 'no':
        return 'manual'
    else:
        print('config.ini uses a wrong syntax. Please refer to the documentation for a valid config.ini')
        quit()


# -------------------------------------------------------------------------------------------------------------------- #


def testhub(auth, repo):
    repo_values = []
    config_values = read_config()
    commits_keywords = config_values['commits']
    issues_keywords = config_values['issues']
    pull_requests_keywords = config_values['pull_requests']

    print(commits_keywords)
    print(issues_keywords)
    print(pull_requests_keywords)

    # commits_results = Metric_Commits.commits(repo, auth, commits_keywords)
    issues_results = Metric_Issues.issues(repo, auth, issues_keywords)
    pull_requests_results = Metric_PullRequests.pull_requests(repo, auth, pull_requests_keywords)

    # print(commits_results)
    print('# ------------------------------------------------------------------------------------------------------- #')
    print(issues_results)
    print('# ------------------------------------------------------------------------------------------------------- #')
    print(pull_requests_results)
    print('# ------------------------------------------------------------------------------------------------------- #')


def search(auth):
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


def query(auth):
    """
    test function to see what repositories will be looked up by searching for it
    :return:
    """
    repo_count = 0
    values = []
    repos = auth.search_repositories(query='size:>500')
    for repo in repos:
        repo_count += 1
        print(repo_count, repo.size, repo.name, repo.downloads_url)
        values.append(repo.id)  # repo_id
        values.append(repo.full_name.split('/')[0])  # repo_creator
        values.append(repo.name)  # repo_name
        values.append(repo.size)  # repo_size
        values.append('False')  # downloaded
        values.append(datetime.date(datetime.now()))  # last_access
        scf = Metric_StatsCodeFrequency.stats_code_frequency()
        values.append(scf[0])  # code_frequency_additions
        values.append(scf[1])  # code_frequency_deletions
        values.append(scf[1] / scf[0])  # # code_frequency_difference
        values.append(Metric_Contributors.contributors())  # contributors

        # repo_creator = values[1]
        # repo_name = values[2]
        # repo_size = values[3]
        # downloaded = values[4]
        # last_access = values[5]
        # code_frequency_additions = values[6]
        # code_frequency_deletions = values[7]
        # code_frequency_difference = values[8]
        # contributors = values[9]
        commits = values[10]
        issues = values[11]
        if repo_count % 100 == 0:
            # time.sleep(0.5)
            print(auth.get_rate_limit().search, auth.get_rate_limit())
            break


# ---------------------------------------------------------------------------------------------------------------------#


def reset_sleep(auth):
    """
    function that sleeps for a given time to await the next rate-limit reset which is calculated by taking the reset
    date and subtracting the current date to get a date difference
    :param auth: auth object to access the rate-limits
    :return: False
    """
    try:
        waiting_sec = int((auth.get_rate_limit().core.reset - datetime.datetime.utcnow()).total_seconds()) + 1
        local_reset_time = datetime.datetime.fromtimestamp(float(auth.get_rate_limit().core.reset.strftime("%s")),
                                                           datetime.datetime.now().astimezone().tzinfo)

        print('OSCTool waits', waiting_sec,
              'seconds for the next rate-limit reset and will be done at around', local_reset_time)
        time.sleep(waiting_sec)
    except Exception as e:
        print(str(e))
        print('Please make sure your time is set correct on your local machine '
              '(timezone does not matter) and run the script again')
        quit()


# ---------------------------------------------------------------------------------------------------------------------#


def initialize():
    """
    function that creates all mandatory infrastructure for the tool to work
    :return: the auth
    """
    # authentication of REST API v3
    auth = Github("c2c1d13983cbb8c1d9ce7845c20d7937ba7c25a0", per_page=100)
    # create the config file if it does not exist yet to base on all following instructions
    create_config()
    # read out necessary metadata off the config file
    config = configparser.ConfigParser()
    config.read('config.ini')
    config_mode = read_config_mode(config)
    database_path = config.get(config_mode, 'path_of_database')
    download_path = config.get(config_mode, 'path_of_download')
    # create the database if it does not exist yet with the given path from the config file
    create_database(database_path)
    # create the folder structure for the repositories to download if it does not exist yet
    # with the given path from the config file
    create_download_folder(download_path)
    return auth


# ---------------------------------------------------------------------------------------------------------------------#

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    auth = initialize()
    repo = auth.get_repo('ytmdesktop/ytmdesktop')
    # repo.get_issue(234234).created_at.strftime(str)
    # repo = auth.get_repo('PyGithub/PyGithub')

    testhub(auth, repo)
