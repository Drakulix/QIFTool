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
import sys

from sqlite3 import Error
from github import Github
import Metric_StatsCodeFrequency  # metric file for StatsCodeFrequency
import Metric_Contributors  # metric file for Contributors
import Metric_Issues  # metric file for Issues
import Metric_Commits  # metric file for Commits
import Metric_PullRequests  # metric file for Pull Requests


# -------------------------------------------------------------------------------------------------------------------- #
# the following block of code deals with the creation and reading of the config file


def create_config():
    config = configparser.ConfigParser()
    config['DEFAULT'] = {'path_of_database': 'current',
                         'path_of_download': 'current',
                         'loops_of_1000s': '1',
                         'size': "0..10000"
                         }
    config['manual'] = {'path_of_database': r"/home/robert/OSCTool/Code",
                        'path_of_download': r"/home/robert/OSCTool/Code",
                        'loops_of_1000s': '1',
                        'size': '500'
                        }
    config['mode'] = {'use_default_values': 'yes'
                      }
    config['metric_values'] = {'commits': '',
                               'issues': '',
                               'pull_requests': ''
                               }
    if not (os.path.isfile('config.ini')):
        with open('config.ini', 'w') as config_file:
            config.write(config_file)


def read_config():
    values = {
        'loops_of_1000s': '',
        'size': '',
        'issues': '',
        'commits': '',
        'pull_requests': '',
        'contributors': '',
    }
    config = configparser.ConfigParser()
    config.read('config.ini')
    config_mode = read_config_mode(config)
    values['loops_of_1000s'] = config[config_mode]['loops_of_1000s']
    values['size'] = config[config_mode]['size']
    values['issues'] = config['metric_values']['issues'].split('\t')
    values['commits'] = config['metric_values']['commits'].split('\t')
    values['pull_requests'] = config['metric_values']['pull_requests'].split('\t')
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
# the following block of code is part of the database interaction


def create_connection(path):
    """
    create a database connection to the SQLite database specified by db_file
    :param path: database file
    :return: Connection object or None
    """
    if path == 'current':
        database = os.getcwd() + '/OSCTool.db'
    else:
        database = path + '/OSCTool.db'
    try:
        conn = sqlite3.connect(database)
        return conn
    except Exception as e:
        print('Exception inside create_connection on line {}:'.format(sys.exc_info()[-1].tb_lineno),
              e.with_traceback(e.__traceback__))
    return None


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
        print('Exception inside create_table on line {}:'.format(sys.exc_info()[-1].tb_lineno),
              e.with_traceback(e.__traceback__))


def create_database(path):
    """
    creates the database file and tables
    :return: False
    """
    # choose path for the database to be created at or none if you want the database to be created in
    # the current directory of the main.py
    try:
        repositories_table_statement = """ CREATE TABLE IF NOT EXISTS repositories (
                                            repo_id integer PRIMARY KEY,
                                            repo_creator text,
                                            repo_name text,
                                            repo_size integer,
                                            downloaded boolean,
                                            last_access text,
                                            
                                            code_frequency_additions integer,
                                            code_frequency_deletions integer,
                                            code_frequency_difference real,
                                            
                                            contributors integer,
                                            
                                            commits_amount integer,
                                            commits_keywords text,
                                            
                                            issues_amount integer,
                                            issues_keywords text,
                                            issues_labels text,
                                            
                                            pull_requests_amount integer,
                                            pull_requests_keywords text,
                                            pull_requests_labels text,
                                            
                                            UNIQUE(repo_id, repo_creator, repo_name, repo_size, downloaded, last_access,
                                                    code_frequency_additions, code_frequency_deletions,
                                                    code_frequency_difference,
                                                    contributors, commits_amount, commits_keywords, 
                                                    issues_amount, issues_keywords,
                                                    pull_requests_amount, pull_requests_keywords) ON CONFLICT IGNORE
                                            ); """

        commits_table_statement = """ CREATE TABLE IF NOT EXISTS commits (
                                                                    repo_id integer,
                                                                    commit_id text PRIMARY KEY,
                                                                    keywords text,
                                                                    commit_author_id integer,
                                                                    commit_author_name text,
                                                                    commit_additions integer,
                                                                    commit_deletions integer,

                                                                    FOREIGN KEY (repo_id) REFERENCES 
                                                                    repositories (repo_id),

                                                                    UNIQUE(repo_id,commit_id, keywords, 
                                                                    commit_author_id, commit_author_name, 
                                                                    commit_additions, commit_deletions) 
                                                                    ON CONFLICT IGNORE
                                                                    ); """

        issues_table_statement = """ CREATE TABLE IF NOT EXISTS issues (
                                                    repo_id integer,
                                                    issue_id integer PRIMARY KEY,
                                                    issue_number integer,
                                                    keywords text,
                                                    labels text,
                                                    amount_of_comments integer,
                                                    create_date text,
                                                    closed_date text,
                                                    
                                                    FOREIGN KEY (repo_id) REFERENCES repositories (repo_id),

                                                    UNIQUE(repo_id, issue_id, keywords, issue_number, labels, 
                                                    amount_of_comments, create_date, closed_date) ON CONFLICT IGNORE
                                                    ); """

        pull_requests_table_statement = """ CREATE TABLE IF NOT EXISTS pull_requests (
                                                            repo_id integer,
                                                            pull_request_id integer PRIMARY KEY,
                                                            pull_request_number integer,
                                                            keywords text,
                                                            labels text,
                                                            amount_of_comments integer,
                                                            amount_of_commits integer,
                                                            pull_request_additions integer,
                                                            pull_request_deletions integer,
                                                            create_date text,
                                                            closed_date text,

                                                            FOREIGN KEY (repo_id) REFERENCES repositories (repo_id),

                                                            UNIQUE(repo_id, pull_request_id, keywords, 
                                                                    pull_request_number, labels, 
                                                                    amount_of_comments, amount_of_commits, 
                                                                    create_date, closed_date) ON CONFLICT IGNORE
                                                            ); """
        # create the database connection
        conn = create_connection(path)

        # create the tables if they do not exist yet
        create_table(conn, repositories_table_statement)
        create_table(conn, issues_table_statement)
        create_table(conn, pull_requests_table_statement)
        create_table(conn, commits_table_statement)
    except Error as e:
        print('Exception inside create_database: on line {}:'.format(sys.exc_info()[-1].tb_lineno),
              e.with_traceback(e.__traceback__))


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
                                                        code_frequency_difference, contributors, 
                                                        commits_amount, commits_keywords, 
                                                        issues_amount, issues_keywords, issues_labels, 
                                                        pull_requests_amount, pull_requests_keywords, 
                                                        pull_requests_labels) 
                                                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 
                                                                ?, ?, ?, ?, ?, ?, ?, ?, ?); """
    # ---------------------------------------------------------------------------------------------------------------- #
    elif table == 'commits':
        insert_statement = """INSERT INTO commits (repo_id, commit_id, keywords, commit_author_id, 
                                                    commit_author_name, commit_additions, commit_deletions) 
                                                    VALUES (?, ?, ?, ?, ?, ?, ?); """
    # ---------------------------------------------------------------------------------------------------------------- #
    elif table == 'issues':
        insert_statement = """INSERT INTO issues (repo_id, issue_id, issue_number, keywords, labels,
                                                    amount_of_comments, create_date, closed_date) 
                                                    VALUES (?, ?, ?, ?, ?, ?, ?, ?); """
    # ---------------------------------------------------------------------------------------------------------------- #
    elif table == 'pull_requests':
        insert_statement = """INSERT INTO pull_requests (repo_id, pull_request_id, pull_request_number, 
                                                            keywords, labels, amount_of_comments, amount_of_commits,
                                                            pull_request_additions, pull_request_deletions, 
                                                            create_date, closed_date) 
                                                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?); """
    # ---------------------------------------------------------------------------------------------------------------- #
    with conn:
        try:
            if insert_statement is not None:
                cursor.execute(insert_statement, values)
            else:
                print('table selection went wrong!')
        except Exception as e:
            print('Exception inside insert on line {}:'.format(sys.exc_info()[-1].tb_lineno),
                  e.with_traceback(e.__traceback__))
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
    :param folder: path of the folder where the repository will be downloaded in
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
                print('Exception inside download_repo on line {}:'.format(sys.exc_info()[-1].tb_lineno),
                      e.with_traceback(e.__traceback__))


# -------------------------------------------------------------------------------------------------------------------- #


def metric_search(auth, repo):
    """
    gets a repository and searches all the metadata of the given metrics
    :param auth: authentication object to access the rate-limit
    :param repo: repository object to get the metadata from
    :return: list of all found metadata results
    """
    try:
        config_values = read_config()
        commits_keywords = config_values['commits']
        issues_keywords = config_values['issues']
        pull_requests_keywords = config_values['pull_requests']

        print(datetime.datetime.now(), '- working on ', repo.full_name, 'with',
              auth.get_rate_limit().core.remaining, 'requests remaining')
        print('\tworking on commits for', repo.full_name)
        if not commits_keywords == '':
            commits_results = Metric_Commits.commits(repo, auth, commits_keywords)
        else:
            commits_results = None
        print('\tworking on issues for', repo.full_name)
        if not issues_keywords == '':
            issues_results = Metric_Issues.issues(repo, auth, issues_keywords)
        else:
            issues_results = None
        print('\tworking on pull requests for', repo.full_name)
        if not pull_requests_keywords == '':
            pull_requests_results = Metric_PullRequests.pull_requests(repo, auth, pull_requests_keywords)
        else:
            pull_requests_results = None
        print('\tworking on contributors for', repo.full_name)
        contributors_results = Metric_Contributors.contributors(repo, auth)
        print('\tworking on statscodefrequency for', repo.full_name)
        scf_results = Metric_StatsCodeFrequency.stats_code_frequency(repo, auth)

        return commits_results, issues_results, pull_requests_results, contributors_results, scf_results
    except Exception as e:
        print('Exception inside metric_search on line {}:'.format(sys.exc_info()[-1].tb_lineno),
              e.with_traceback(e.__traceback__))


def repo_search(auth, database, loops_of_1000s, size):
    """
    very bottom layer of searching for repositories and getting their metadata and inserts them into the database
    :param loops_of_1000s: the number of iterations of random repository searches. Each iteration outputs 1000 repos.
    :param size: size of found repositories (in kB).
                 Can be a range for random repositories or a single value for fixed order of found repositories
    :param auth: authentication object to access the api
    :param database: path to the database to know where to insert information to
    :return:
    """
    # TODO build rate limit robustness
    if ".." not in size:
        loops_of_1000s = 1
    repo_counter = 0
    for i in range(int(loops_of_1000s)):
        repositories = auth.search_repositories(query='size:' + size)  # (query='pelle/oauth')
        for repo in repositories:
            repo_counter += 1
            # readout the metadata for the repository itself
            repo_id = repo.id
            repo_creator = repo.full_name.split('/')[0]
            repo_name = repo.full_name.split('/')[1]
            repo_size = repo.size
            downloaded = False
            last_access = str(datetime.datetime.now().date())

            try:
                # insert found metadata into the tables of the database
                # create the connection to the database
                conn = create_connection(database)
                # readout the metadata of the repo
                print('\n')
                print('# -------------------------------------------------'
                      '-------------------------------------------------- #')
                print('repository:', repo_counter)
                metric_results = metric_search(auth, repo)

                # insert the metadata of commits  -------------------------------------------------------------------- #
                contributors_results = metric_results[3]
                statscodefrequency_results_adds = metric_results[4][0]
                statscodefrequency_results_dels = metric_results[4][1]
                commits_results = metric_results[0]
                if isinstance(commits_results, int):
                    commits_repo_keywords = ''
                    commits_repo_amount = commits_results
                else:
                    commits_repo_keywords = ''
                    commits_repo_amount = commits_results[2]

                    # keywords and labels inside table repositories
                    for keyword in commits_results[1][:-1]:
                        commits_repo_keywords += keyword + ', '
                    commits_repo_keywords += commits_results[1][-1]

                    # insert into the table commits
                    for commit in commits_results[0]:
                        # keywords and labels inside table commits
                        commit_repo_key_str = ''
                        for keyword in commit[2][:-1]:
                            commit_repo_key_str += keyword + ', '
                        commit_repo_key_str += commit[2][-1]
                        commit[2] = commit_repo_key_str

                        insert(conn, 'commits', commit)

                # insert the metadata of issues ---------------------------------------------------------------------- #
                issues_results = metric_results[1]
                if isinstance(issues_results, int):
                    issues_repo_keywords = ''
                    issues_repo_labels = ''
                    issues_repo_amount = issues_results
                else:
                    issues_repo_keywords = ''
                    issues_repo_amount = issues_results[3]

                    # keywords and labels inside table repositories
                    for keyword in issues_results[1][:-1]:
                        issues_repo_keywords += keyword + ', '
                    issues_repo_keywords += issues_results[1][-1]

                    issues_repo_labels = ''
                    if issues_results[2]:
                        for label in issues_results[2][:-1]:
                            issues_repo_labels += label + ', '
                        issues_repo_labels += issues_results[2][-1]

                    # insert into the table issues
                    for issue in issues_results[0]:
                        # keywords and labels inside table issues
                        issue_repo_key_str = ''
                        for keyword in issue[3][:-1]:
                            issue_repo_key_str += keyword + ', '
                        issue_repo_key_str += issue[3][-1]
                        issue[3] = issue_repo_key_str

                        issue_repo_label_str = ''
                        if issue[4]:
                            for label in issue[4][:-1]:
                                issue_repo_label_str += label + ', '
                            issue_repo_label_str += issue[4][-1]
                        issue[4] = issue_repo_label_str

                        insert(conn, 'issues', issue)

                # insert the metadata of pull requests --------------------------------------------------------------- #
                pull_requests_results = metric_results[2]
                if isinstance(pull_requests_results, int):
                    pull_requests_repo_keywords = ''
                    pull_requests_repo_labels = ''
                    pull_requests_repo_amount = pull_requests_results
                else:
                    pull_requests_repo_keywords = ''
                    pull_requests_repo_amount = pull_requests_results[3]

                    # keywords and labels inside table repositories
                    for keyword in pull_requests_results[1][:-1]:
                        pull_requests_repo_keywords += keyword + ', '
                    pull_requests_repo_keywords += pull_requests_results[1][-1]
                    pull_requests_repo_labels = ''
                    if pull_requests_results[2]:
                        for label in pull_requests_results[2][:-1]:
                            pull_requests_repo_labels += label + ', '
                        pull_requests_repo_labels += pull_requests_results[2][-1]
                    # insert into the table pull_requests
                    for pull in pull_requests_results[0]:
                        # keywords and labels inside table pull_requests
                        pull_repo_key_str = ''
                        for keyword in pull[3][:-1]:
                            pull_repo_key_str += keyword + ', '
                        pull_repo_key_str += pull[3][-1]
                        pull[3] = pull_repo_key_str

                        pull_repo_label_str = ''
                        if pull[4]:
                            for label in pull[4][:-1]:
                                pull_repo_label_str += label + ', '
                            pull_repo_label_str += pull[4][-1]
                        pull[4] = pull_repo_label_str

                        insert(conn, 'pull_requests', pull)

                # ---------------------------------------------------------------------------------------------------  #

                insert(conn, 'repositories', (repo_id, repo_creator, repo_name, repo_size, downloaded, last_access,
                                              statscodefrequency_results_adds, statscodefrequency_results_dels,
                                              statscodefrequency_results_dels / statscodefrequency_results_adds,
                                              contributors_results, commits_repo_amount, commits_repo_keywords,
                                              issues_repo_amount, issues_repo_keywords, issues_repo_labels,
                                              pull_requests_repo_amount, pull_requests_repo_keywords,
                                              pull_requests_repo_labels))
                conn.close()
                print('insert for', repo.full_name, 'complete')
                print('# -------------------------------------------------'
                      '-------------------------------------------------- #')
            except Exception as e:
                print('Exception inside repo_search on line {}:'.format(sys.exc_info()[-1].tb_lineno),
                      e.with_traceback(e.__traceback__))


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
        print('Exception inside reset_sleep on line {}:'.format(sys.exc_info()[-1].tb_lineno),
              e.with_traceback(e.__traceback__))
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
    loops_of_1000s = config.get(config_mode, 'loops_of_1000s')
    size = config.get(config_mode, 'size')

    # create the database if it does not exist yet with the given path from the config file
    create_database(database_path)
    # create the folder structure for the repositories to download if it does not exist yet
    # with the given path from the config file
    create_download_folder(download_path)
    return auth, database_path, download_path, loops_of_1000s, size


# ---------------------------------------------------------------------------------------------------------------------#

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    init = initialize()
    auth = init[0]
    database_path = init[1]
    download_path = init[2]
    loops_of_1000s = init[3]
    size = init[4]
    print(database_path)
    print(size)
    # repo = auth.get_repo('ytmdesktop/ytmdesktop')
    # repo.get_issue(234234).created_at.strftime(str)
    # repo = auth.get_repo('PyGithub/PyGithub')
    # pulls = repo.get_pulls()
    # for pull in pulls
    #     pull_get_comments = pull.get_comments()
    #     pull_comments = pull_get_comments.totalCount
    # metric_search(auth, repo)
    repo_search(auth, database_path, loops_of_1000s, size)
