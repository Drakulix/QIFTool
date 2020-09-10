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
import Metric_PullRequests # metric file for Pull Requests


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
        print('Exception inside create_connection:', e.with_traceback(e.__traceback__))
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
        print('Exception inside create_table:', e.with_traceback(e.__traceback__))


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
                                                    keywords text,
                                                    issue_number integer,
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
                                                            keywords text,
                                                            pull_request_number integer,
                                                            labels text,
                                                            amount_of_comments integer,
                                                            amount_of_commits integer,
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
        print('Exception inside create_database:', e.with_traceback(e.__traceback__))


def insert(conn, table, values, repo_id):
    """
    insert function to write the given values inside the database table 'repositories'
    :param repo_id: id of the current repository for other insert to have a reference repo
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
    elif table == 'repositories_metrics_repo_id':
        insert_statement = """UPDATE repositories SET commits_amount = ?, 
                                                        issues_amount = ?, 
                                                        pull_requests_amount = ? 
                                                        WHERE repo_id = ?; """
    elif table == 'repositories_commits_keywords':
        insert_statement = """UPDATE repositories SET commits_keywords = ? 
                                                        WHERE repo_id = ?; """
    elif table == 'repositories_issues_keywords':
        insert_statement = """UPDATE repositories SET issues_keywords = ? 
                                                        WHERE repo_id = ?; """
    elif table == 'repositories_pull_requests_keywords':
        insert_statement = """UPDATE repositories SET pull_requests_keywords = ?
                                                        WHERE repo_id = ?; """
    # ---------------------------------------------------------------------------------------------------------------- #
    elif table == 'commits':
        insert_statement = """INSERT INTO commits (repo_id, commit_id, commit_author_id, 
                                                    commit_author_name, commit_additions, commit_deletions) 
                                                    VALUES (?, ?, ?, ?, ?, ?); """
    elif table == 'commits_keywords':
        insert_statement = """UPDATE commits SET keywords = ?
                                                    WHERE repo_id = ?; """
    # ---------------------------------------------------------------------------------------------------------------- #
    elif table == 'issues':
        insert_statement = """INSERT INTO issues (repo_id, issue_id, issue_number, 
                                                    amount_of_comments, create_date, closed_date) 
                                                    VALUES (?, ?, ?, ?, ?, ?); """
    elif table == 'issues_keywords':
        insert_statement = """UPDATE issues SET keywords = ?
                                                WHERE repo_id = ?; """
    elif table == 'issues_labels':
        insert_statement = """UPDATE issues SET labels = ?
                                                WHERE repo_id = ?; """
    # ---------------------------------------------------------------------------------------------------------------- #
    elif table == 'pull_requests':
        insert_statement = """INSERT INTO pull_requests (repo_id, pull_request_id, pull_request_number,
                                                            amount_of_comments, amount_of_commits,
                                                            create_date, closed_date) 
                                                        VALUES (?, ?, ?, ?, ?, ?, ?); """
    elif table == 'pull_requests_keywords':
        insert_statement = """UPDATE pull_requests SET keywords = ?
                                                        WHERE repo_id = ?; """
    elif table == 'pull_requests_labels':
        insert_statement = """UPDATE pull_requests SET labels = ? 
                                                        WHERE repo_id = ?; """
    # ---------------------------------------------------------------------------------------------------------------- #
    with conn:
        try:
            if insert_statement is not None:
                if 'keywords' in table or 'labels' in table:
                    for value in values:
                        print(value, values)
                        print('KEYWORDS OR LABELS with', insert_statement)
                        cursor.execute(insert_statement, [value, repo_id])
                elif 'metrics' in table:
                    print('METRICS with', insert_statement)
                    cursor.execute(insert_statement, [values, repo_id])
                else:
                    print(values)
                    print('TABLE INSERT with', insert_statement)
                    cursor.execute(insert_statement, values)
            else:
                print('table selection went wrong!')
        except Exception as e:
            print('Exception inside insert:', e.with_traceback(e.__traceback__))
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
                print('Exception inside download_repo:', e.with_traceback())


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

        print('# ------------------------------------------------------------------------------------------------------- #')
        print(auth.get_rate_limit())
        print('working on commits for', repo.full_name)
        if not commits_keywords == '':
            commits_results = Metric_Commits.commits(repo, auth, commits_keywords)
        else:
            commits_results = None
        # print(commits_results)
        print('# ------------------------------------------------------------------------------------------------------- #')
        print(auth.get_rate_limit())
        print('working on issues for', repo.full_name)
        if not issues_keywords == '':
            issues_results = Metric_Issues.issues(repo, auth, issues_keywords)
        else:
            issues_results = None
        # print(issues_results)
        print('# ------------------------------------------------------------------------------------------------------- #')
        print(auth.get_rate_limit())
        print('working on pull requests for', repo.full_name)
        if not pull_requests_keywords == '':
            pull_requests_results = Metric_PullRequests.pull_requests(repo, auth, pull_requests_keywords)
        else:
            pull_requests_results = None
        # print(pull_requests_results)
        print('# ------------------------------------------------------------------------------------------------------- #')
        print(auth.get_rate_limit())
        print('working on contributors for', repo.full_name)
        contributors_results = Metric_Contributors.contributors(repo, auth)
        # print(contributors_results)
        print('# ------------------------------------------------------------------------------------------------------- #')
        print(auth.get_rate_limit())
        print('working on statscodefrequency for', repo.full_name)
        scf_results = Metric_StatsCodeFrequency.stats_code_frequency(repo, auth)
        # print(scf_results)
        print('# ------------------------------------------------------------------------------------------------------- #')

        return commits_results, issues_results, pull_requests_results, contributors_results, scf_results
    except Exception as e:
        print('Exception inside metric_search:', e.with_traceback(e.__traceback__))


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
    for i in range(int(loops_of_1000s)):
        repositories = auth.search_repositories(query=size)  # (query='size:'+size)
        for repo in repositories:
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
                metric_results = metric_search(auth, repo)
                # insert the metadata of commits
                contributors_results = metric_results[3]
                statscodefrequency_results_adds = metric_results[4][0]
                statscodefrequency_results_dels = metric_results[4][1]
                # print(type(repo_id), repo_id)
                # print(type(repo_creator), repo_creator)
                # print(type(repo_name), repo_name)
                # print(type(repo_size), repo_size)
                # print(type(downloaded), downloaded)
                # print(type(last_access), last_access)
                # print(type(statscodefrequency_results_adds), statscodefrequency_results_adds)
                # print(type(statscodefrequency_results_dels), statscodefrequency_results_dels)
                # print(type(statscodefrequency_results_dels/statscodefrequency_results_adds),
                #            statscodefrequency_results_dels/statscodefrequency_results_adds)
                # print(type(contributors_results), contributors_results)
                insert(conn, 'repositories', (repo_id, repo_creator, repo_name, repo_size, downloaded, last_access,
                                              statscodefrequency_results_adds, statscodefrequency_results_dels,
                                              statscodefrequency_results_dels / statscodefrequency_results_adds,
                                              contributors_results), repo_id)
                commits_results = metric_results[0]
                if commits_results is int:
                    commits_amount = commits_results
                else:
                    print('COMMITS')
                    for commit in commits_results[0]:
                        commits_results_keywords = commit[2]
                        commit.remove(commits_results_keywords)
                        print(commit)
                        insert(conn, 'commits', commit, repo_id)
                        insert(conn, 'commits_keywords', commits_results_keywords, repo_id)
                    commits_repo_keywords = commits_results[1]
                    commits_amount = commits_results[2]
                    insert(conn, 'repositories_commits_keywords', commits_repo_keywords, repo_id)

                # insert the metadata of issues
                issues_results = metric_results[1]
                if issues_results is int:
                    issues_amount = issues_results
                else:
                    print('ISSUES')
                    for issue in issues_results[0]:
                        issues_results_keywords = issue[2]
                        issues_results_labels = issue[3]
                        issue.remove(issues_results_keywords).remove(issues_results_labels)
                        insert(conn, 'issues', issue, repo_id)
                        insert(conn, 'issues_keywords', issues_results_keywords, repo_id)
                        insert(conn, 'issues_labels', issues_results_labels, repo_id)
                    issues_repo_keywords = issues_results[1]
                    issues_repo_labels = issues_results[2]
                    issues_amount = issues_results[3]
                    insert(conn, 'repositories_issues_keywords', issues_repo_keywords, repo_id)
                    insert(conn, 'repositories_issues_labels', issues_repo_labels, repo_id)

                # insert the metadata of pull requests
                pull_requests_results = metric_results[2]
                if pull_requests_results is int:
                    pull_requests_amount = pull_requests_results
                else:
                    print('PULL REQUEST')
                    for pull in pull_requests_results[0]:
                        pull_request_results_keywords = pull[2]
                        pull_request_results_labels = pull[3]
                        pull.remove(pull_request_results_keywords).remove(pull_request_results_labels)
                        insert(conn, 'pull_requests', pull, repo_id)
                        insert(conn, 'pull_requests_keywords', pull_request_results_keywords, repo_id)
                        insert(conn, 'pull_requests_labels', pull_request_results_labels, repo_id)
                    pull_repo_keywords = pull_requests_results[1]
                    pull_repo_labels = pull_requests_results[2]
                    pull_requests_amount = pull_requests_results[3]
                    insert(conn, 'repositories_pull_requests_keywords', pull_repo_keywords, repo_id)
                    insert(conn, 'repositories_pull_requests_labels', pull_repo_labels, repo_id)
                insert(conn, 'repositories_metrics_repo_id',
                       [commits_amount, issues_amount, pull_requests_amount], repo_id)
                conn.close()
                print('insert for', repo.full_name, ' complete\n')
            except Exception as e:
                print('Exception inside repo_search:', e.with_traceback(e.__traceback__))


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
    repos = auth.search_repositories(size='size:>500')
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
        print('Exception inside reset_sleep:', e.with_traceback(e.__traceback__))
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
    #     pull_commments = pull_get_comments.totalCount
    # metric_search(auth, repo)
    repo_search(auth, database_path, loops_of_1000s, size)
