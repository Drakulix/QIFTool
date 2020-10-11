from googleapiclient.discovery import build
from github import Github
from time import time
from datetime import datetime
from sqlite3 import Error
import configparser
import sqlite3
import sys
import os


# ---------------------------------------------------------------------------------------------------------------------#
# class and functions for handling the configuration file

class Config:
    def __init__(self, path_of_database, path_of_download, github_api_key, google_api_key, google_cse_id,
                 keywords, issue_comments, repo_contributors):
        self.path_of_database = path_of_database
        self.path_of_download = path_of_download
        self.github_api_key = github_api_key
        self.google_api_key = google_api_key
        self.google_cse_id = google_cse_id
        self.keywords = keywords
        self.issue_comments = issue_comments
        self.repo_contributors = repo_contributors


def create_config():
    """
    creates the config file if it does not exist yet to allow the user not to cope with writing inside the code and also
    security of data like keys
    :return: True or False depending whether the file already existed or not
    """
    config = configparser.ConfigParser()
    config['DEFAULT'] = {'path_of_database': 'current',
                         'path_of_download': 'current',
                         }
    config['credentials'] = {'github_api_key': '',
                             'google_api_key': '',
                             'google_cse_id': ''
                             }
    config['metrics'] = {'keywords': '',
                         'issue_comments': '',
                         'repo_contributors': ''
                         }
    if not (os.path.isfile('config.ini')):
        with open('config.ini', 'w') as config_file:
            config.write(config_file)
            return True
    else:
        return False


def read_config():
    """
    function to read out the config file for further usage
    :return: Config_object with all attributes filled
    """
    config = configparser.ConfigParser()
    config.read('config.ini')
    values = Config(path_of_database=config['DEFAULT']['path_of_database'],
                    path_of_download=config['DEFAULT']['path_of_download'],
                    github_api_key=config['credentials']['github_api_key'],
                    google_api_key=config['credentials']['google_api_key'],
                    google_cse_id=config['credentials']['google_cse_id'],
                    keywords=config['metrics']['keywords'],
                    issue_comments=config['metrics']['issue_comments'],
                    repo_contributors=config['metrics']['repo_contributors'])
    return values

# ---------------------------------------------------------------------------------------------------------------------#
# functions to for handling the database


def create_connection(path):
    """
    create a database connection to the SQLite database specified by db_file
    :param path: database file
    :return: Connection object or None
    """
    if path == 'current':
        database = os.getcwd() + '/QIFTool.db'
    else:
        database = path + '/QIFTool.db'
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
        issues_table_statement = """ CREATE TABLE IF NOT EXISTS issues (repo_id integer,
                                                                        issue_id integer PRIMARY KEY,
                                                                        issue_url text,
                                                                        issue_htmlurl text,
                                                                        issue_title text,
                                                                        issue_number integer,
                                                                        score integer,
                                                                        notes text,
                                                                        amount_of_comments integer,
                                                                        relevance integer,
                                                                        keywords text,
                                                                        labels text,
                                                                        linked_issues integer,
                                                                        create_date text,
                                                                        closed_date text,

                                                                        FOREIGN KEY (repo_id) 
                                                                        REFERENCES repositories (repo_id),
            
                                                                        UNIQUE(repo_id, issue_id, issue_url, 
                                                                                issue_htmlurl, issue_title, 
                                                                                issue_number, score, notes, 
                                                                                amount_of_comments, relevance, 
                                                                                keywords, labels, linked_issues,
                                                                                create_date, closed_date) 
                                                                            ON CONFLICT IGNORE
                                                                        ); """

        repositories_table_statement = """ CREATE TABLE IF NOT EXISTS repositories (repo_id integer PRIMARY KEY,
                                                                                    repo_url text,
                                                                                    repo_htmlurl text,
                                                                                    repo_about text,
                                                                                    repo_creator text,
                                                                                    repo_name text,
                                                                                    repo_size integer,
                                                                                    languages text,
                                                                                    
                                                                                    contributors integer,
                                                                                    
                                                                                    issues_amount integer,
                                                                                    issues_keywords text,
                                                                                    issues_labels text,
                                        
                                                                                    code_frequency_additions integer,
                                                                                    code_frequency_deletions integer,
                                                                                    code_frequency_ratio real,
                                        
                                                                                    UNIQUE(repo_id, repo_url, 
                                                                                            repo_htmlurl, 
                                                                                            repo_about, 
                                                                                            repo_creator, 
                                                                                            repo_name, repo_size, 
                                                                                            languages,
                                                                                            contributors, issues_amount,
                                                                                            issues_keywords, 
                                                                                            issues_labels, 
                                                                                            code_frequency_additions, 
                                                                                            code_frequency_deletions, 
                                                                                            code_frequency_ratio) 
                                                                                            ON CONFLICT IGNORE
                                                                                    ); """

        # create the database connection
        conn = create_connection(path)

        # create the tables if they do not exist yet
        create_table(conn, issues_table_statement)
        create_table(conn, repositories_table_statement)
        conn.close()
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
    if table == 'issues':
        insert_statement = """INSERT INTO issues (repo_id, issue_id, issue_url, issue_htmlurl,
                                                    issue_title, issue_number, score, notes, 
                                                    amount_of_comments, relevance, keywords, labels, 
                                                    linked_issues, create_date, closed_date) 
                                                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?); """

    elif table == 'repositories':
        insert_statement = """INSERT INTO repositories (repo_id, repo_url, repo_htmlurl, repo_about, 
                                                        repo_creator, repo_name, repo_size, languages, contributors, 
                                                        issues_amount, issues_keywords, issues_labels, 
                                                        code_frequency_additions, code_frequency_deletions, 
                                                        code_frequency_ratio) 
                                                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?); """
    with conn:
        try:
            if insert_statement is not None:
                # print(list(vars(values).values()))
                cursor.execute(insert_statement, list(vars(values).values()))
            else:
                print('table selection went wrong!')
        except Exception as e:
            print('Exception inside insert on line {}:'.format(sys.exc_info()[-1].tb_lineno),
                  e.with_traceback(e.__traceback__))


def redundancy_check(conn, table, issue_or_repo_id, title_or_name, relevance, keywords):
    try:
        with conn:
            cursor = conn.cursor()
            if table == 'issues':
                check_statement = """SELECT issue_id FROM issues WHERE issue_id = ?;"""
            elif table == 'repositories':
                check_statement = """SELECT repo_id FROM repositories WHERE repo_id = ?;"""
            cursor.execute(check_statement, [issue_or_repo_id])
            db_entry = cursor.fetchall()
            cursor.close()
            if db_entry:
                if table == 'issues':
                    rel_values = relevance_check(conn, issue_or_repo_id, relevance)
                    keywords_values = keywords_check(conn, issue_or_repo_id, keywords)
                    if rel_values.result and keywords_values.result:
                        print('\t\t', title_or_name, issue_or_repo_id, 'already in database '
                                                                       'but relevance changed from',
                                                                        rel_values.old, 'to', rel_values.new,
                                                                       'and\n', 'keywords changed from'.rjust(24),
                                                                        keywords_values.old_keywords, 'to',
                                                                        keywords_values.new_keywords)
                    elif rel_values.result:
                        print('\t\t', title_or_name, issue_or_repo_id, 'already in database '
                                                                       'but relevance changed from',
                                                                        rel_values.old, 'to', rel_values.new)
                    elif keywords_values.result:
                        print('\t\t', title_or_name, issue_or_repo_id, 'already in database '
                                                                       'but keywords changed from',
                                                                        keywords_values.old_keywords, 'to',
                                                                        keywords_values.new_keywords)
                return True
            else:
                return False
    except Exception as e:
        print('Exception inside insert on line {}:'.format(sys.exc_info()[-1].tb_lineno),
              e.with_traceback(e.__traceback__))


class RelevanceValues:
    def __init__(self, result, old=None, new=None):
        self.result = result
        self.old = old
        self.new = new


def relevance_check(conn, issue_id, relevance):
    """
    function to check an issues relevance whenever it occurs in the search again if its relevance is lower than the one
    stored in the database
    :return:
    """
    try:
        with conn:
            cursor = conn.cursor()
            check_statement = """SELECT relevance FROM issues WHERE issue_id = ?;"""
            cursor.execute(check_statement, [issue_id])
            db_entry = cursor.fetchall()
            if db_entry:
                if db_entry[0][0] > relevance:
                    update_statement = """UPDATE issues SET relevance = ? WHERE issue_id = ?;"""
                    cursor.execute(update_statement, [relevance, issue_id])
                    cursor.close()
                    return RelevanceValues(result=True, old=db_entry[0][0], new=relevance)
            return RelevanceValues(result=False)
    except Exception as e:
        print('Exception inside relevance_check() on line {}:'.format(sys.exc_info()[-1].tb_lineno),
              e.with_traceback(e.__traceback__))


class KeywordsValues:
    def __init__(self, result=False, old_keywords='', current_keywords='', new_keywords=''):
        self.result = result
        self.old_keywords = old_keywords
        self.current_keywords = current_keywords
        self.new_keywords = new_keywords


def keywords_check(conn, issue_id, keywords):
    try:
        with conn:
            cursor = conn.cursor()
            check_statement = """SELECT keywords FROM issues WHERE issue_id = ?;"""
            cursor.execute(check_statement, [issue_id])
            db_entry = cursor.fetchall()
            if db_entry:
                keywords_values = KeywordsValues()
                keywords_values.old_keywords = db_entry[0][0]
                keywords_values.current_keywords = keywords.split('\t')
                for word in keywords_values.current_keywords:
                    if word not in db_entry[0][0].split(', '):
                        keywords += '\t' + word
                keywords_values.new_keywords = db_keywords(keywords)
                update_statement = """UPDATE issues SET keywords = ? WHERE issue_id = ?;"""
                cursor.execute(update_statement, [keywords_values.new_keywords, issue_id])
                cursor.close()
                if keywords_values.new_keywords not in keywords_values.old_keywords:
                    keywords_values.result = True
            return keywords_values
    except Exception as e:
        print('Exception inside keywords_check() on line {}:'.format(sys.exc_info()[-1].tb_lineno),
              e.with_traceback(e.__traceback__))


# ---------------------------------------------------------------------------------------------------------------------#
# class and function for metric: StatsCodeFrequency


class SCF:
    def __init__(self, additions=0, deletions=0, ratio=0.0):
        self.additions = additions
        self.deletions = deletions
        self.ratio = ratio

    def get_adds(self):
        return self.additions

    def get_dels(self):
        return self.deletions

    def get_ratio(self):
        return self.ratio


def stats_code_frequency(repo, auth):
    """
    gets a repository object and counts the additions and deletions on a weekly basis together
    :param repo: the repository object that contains the stats code frequency
    :param auth: the authentication object that is used to access the current rate-limit
    :return: returns an SCF-object
    """
    try:
        from main import reset_sleep
        if auth.get_rate_limit().core.remaining <= 0:
            reset_sleep(auth)
        scf_obj = repo.get_stats_code_frequency()
        scf = SCF()
        for add_del in scf_obj:
            scf.additions += add_del.additions
            scf.deletions += add_del.deletions.__abs__()
        scf.ratio = scf.deletions/scf.additions
        return scf
    except Exception as e:
        print('Exception inside Metrics_StatsCodeFrequency.stats_code_frequency() on line {}:'
              .format(sys.exc_info()[-1].tb_lineno), e.with_traceback(e.__traceback__))


# ---------------------------------------------------------#
# class and function for metric: Contributors


class Contributors:
    def __init__(self, size):
        self.size = size

    def get_size(self):
        return self.size


def contributors(repo, auth):
    """
    gets a repository and returns the amount of contributors on that repository
    :param repo: the repository object that contains the contributors
    :param auth: the authentication object that is used to access the current rate-limit
    :return: returns an Contributors-object
    """
    try:
        from main import reset_sleep
        if auth.get_rate_limit().core.remaining <= 0:
            reset_sleep(auth)
        contributor = Contributors(size=repo.get_contributors().totalCount)
        return contributor
    except Exception as e:
        print('Exception inside Metrics_Contributors.contributors() on line {}:'.format(sys.exc_info()[-1].tb_lineno),
              e.with_traceback(e.__traceback__))


# ---------------------------------------------------------------------------------------------------------------------#


def reset_sleep(auth):
    """
    function that sleeps for a given time to await the next rate-limit reset which is calculated by taking the reset
    date and subtracting the current date to get a date difference
    :param auth: auth object to access the rate-limits
    :return: Nothing
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


class RepoObj:
    def __init__(self, id, url, html_url, about, creator, name, size, languages, contributors,
                 issues_amount, issues_keywords, issues_labels,
                 code_frequency_additions, code_frequency_deletions, code_frequency_ratio):
        self.id = id
        self.url = url
        self.html_url = html_url
        self.about = about
        self.creator = creator
        self.name = name
        self.size = size
        self.languages = languages
        self.contributors = contributors
        self.issues_amount = issues_amount
        self.issues_keywords = issues_keywords
        self.issues_labels = issues_labels
        self.code_frequency_additions = code_frequency_additions
        self.code_frequency_deletions = code_frequency_deletions
        self.code_frequency_ratio = code_frequency_ratio


class IssueObj:
    def __init__(self, repo_id, id, url, html_url, title, number, score, notes, amount_of_comments,
                 relevance, keywords, labels, linked_issues, create_date, closed_date):
        self.repo_id = repo_id
        self.id = id
        self.url = url
        self.html = html_url
        self.title = title
        self.number = number
        self.score = score
        self.notes = notes
        self.amount_of_comments = amount_of_comments
        self.relevance = relevance
        self.keywords = keywords
        self.labels = labels
        self.linked_issues = linked_issues
        self.create_date = create_date
        self.closed_date = closed_date


class IssueDates:
    def __init__(self, created_at='NA', closed_at='NA'):
        self.created_at = created_at
        self.closed_at = closed_at


def db_keywords(keywords):
    """
    function to make a suitable string out of the given keywords to insert into the database
    :param keywords: string of keywords extracted from the config file
    :return: the changed string to fit into the database
    """
    try:
        keywords_str = ''
        keywords_list = keywords.split('\t')
        if len(keywords_list) >= 1:
            for keyword in keywords_list[:-1]:
                keywords_str += keyword + ', '
            keywords_str += keywords_list[-1]
        return keywords_str
    except Exception as e:
        print('Exception inside issue_print() on line {}:'.format(sys.exc_info()[-1].tb_lineno),
              e.with_traceback(e.__traceback__))


def get_labels(issue):
    """
    function to get the labels of an issue
    :param issue: the issue of the labels to extract
    :return: a string suitable for an insert into the database
    """
    try:
        labels_str = ''
        labels = issue.get_labels()
        for label in labels:
            labels_str += label.name + ', '
        labels_str = labels_str[:-2]
        return labels_str
    except Exception as e:
        print('Exception inside get_labels() on line {}:'.format(sys.exc_info()[-1].tb_lineno),
              e.with_traceback(e.__traceback__))


def get_languages(repo):
    try:
        languages_str = ''
        languages = repo.get_languages()
        for lang in languages:
            languages_str += lang + ', '
        languages_str = languages_str[:-2]
        return languages_str
    except Exception as e:
        print('Exception inside get_languages() on line {}:'.format(sys.exc_info()[-1].tb_lineno),
              e.with_traceback(e.__traceback__))


def linked_issue(repo, issue_number):
    """
    function to get teh linked issue
    :param repo: repository of the issues involved
    :param issue_number: number of the issue to be gotten
    :return: linked issue-object
    """
    try:
        issue = repo.get_issue(issue_number)
        return issue
    except Exception as e:
        return None


def get_linked_issues(repo, issue):
    """
    TODO this is a funtion that has a concept of extracting linked issues insdie issues but is not consistent due to
    \linked issues being possible to embedded inside text
    :param repo: repository object of all linked issues
    :param issue: current issue where linked issues shall be found
    :return:
    """
    linked_issues_list = []
    for comment in issue.get_comments():
        split_list = comment.split('#')
        for linked_issue in split_list:
            temp_issue = linked_issue(repo, linked_issue[:6])
            if temp_issue is not None:
                linked_issues_list.append([linked_issue[:6], temp_issue.html_url])

    # TODO
    linked_issues = ''
    return linked_issues


def get_issue_dates(issue):
    """
    function to return the issue dates of when they have been created and possibly been closed at
    :param issue: issue-object
    :return: IssueDates-object
    """
    try:
        if issue.closed_at is None:
            return IssueDates(created_at=issue.created_at.strftime(str(issue.created_at.date())))
        else:
            return IssueDates(created_at=issue.created_at.strftime(str(issue.created_at.date())),
                              closed_at=issue.closed_at.strftime(str(issue.closed_at.date())))
    except Exception as e:
        print('Exception inside get_issue_dates() on line {}:'.format(sys.exc_info()[-1].tb_lineno),
              e.with_traceback(e.__traceback__))


def metric_check(conn, config_issue_comments, config_repo_contributors, issue_id, repo_id):
    """
    function to prefilter results that are shown to the user. uses the config metrics to determine.
    :param conn: conenction-object to the database
    :param config_issue_comments: config metric attribute
    :param config_repo_contributors: config metric attribute
    :param issue_id: id of the issue
    :param repo_id: id of the repo
    :return: a bool to either print the result or not depending
    whether the result is greater than or equal to the metric set in the config file
    """
    try:
        with conn:
            if config_issue_comments == '' and config_repo_contributors == '':
                return True
            elif config_issue_comments != '' and config_repo_contributors != '':
                cursor = conn.cursor()
                check_statement = """SELECT amount_of_comments FROM issues WHERE issue_id = ?;"""
                cursor.execute(check_statement, [issue_id])
                db_issue_comments = cursor.fetchall()[0][0]
                check_statement = """SELECT contributors FROM repositories WHERE repo_id = ?;"""
                cursor.execute(check_statement, [repo_id])
                db_repo_contributors = cursor.fetchall()[0][0]
                if db_issue_comments >= config_issue_comments and db_repo_contributors >= config_repo_contributors:
                    return True
            elif config_issue_comments != '' and config_repo_contributors == '':
                cursor = conn.cursor()
                check_statement = """SELECT amount_of_comments FROM issues WHERE issue_id = ?;"""
                cursor.execute(check_statement, [issue_id])
                db_issue_comments = cursor.fetchall()[0][0]
                cursor.close()
                if db_issue_comments >= config_issue_comments:
                    return True
            elif config_repo_contributors != '' and config_issue_comments == '':
                cursor = conn.cursor()
                check_statement = """SELECT contributors FROM repositories WHERE repo_id = ?;"""
                cursor.execute(check_statement, [repo_id])
                db_repo_contributors = cursor.fetchall()[0][0]
                cursor.close()
                if db_repo_contributors >= config_repo_contributors:
                    return True
            return False
    except Exception as e:
        print('Exception inside metric_check() on line {}:'.format(sys.exc_info()[-1].tb_lineno),
              e.with_traceback(e.__traceback__))


class IssuePrint:
    def __init__(self, repo_name, repo_about, issue_id, issue_htmlurl,
                 issue_title, score, relevance, linked_issues, notes):
        self.repo_name = repo_name
        self.repo_about = repo_about
        self.issue_id = issue_id
        self.issue_htmlurl = issue_htmlurl
        self.issue_title = issue_title
        self.score = score
        self.relevance = relevance
        self.linked_issues = linked_issues
        self.notes = notes


def issue_print(conn, issue_id):
    try:
        with conn:
            cursor = conn.cursor()
            check_statement = """SELECT r.repo_name, r.repo_about, i.issue_id, i.issue_htmlurl, 
                                i.issue_title, i.score, i.relevance, i.linked_issues, i.notes
                                FROM issues AS i INNER JOIN repositories AS r ON i.repo_id = r.repo_id
                                WHERE issue_id = ?;"""
            cursor.execute(check_statement, [issue_id])
            db_entry = cursor.fetchall()[0]
            cursor.close()
            if not db_entry:
                print('something went wrong')
            else:
                issue_print = IssuePrint(repo_name=db_entry[0], repo_about=db_entry[1],
                                         issue_id=db_entry[2], issue_htmlurl=db_entry[3], issue_title=db_entry[4],
                                         score=db_entry[5], relevance=db_entry[6], linked_issues=db_entry[7],
                                         notes=db_entry[8])
                print('-----------------------------------------------------------------------------------------------')
                print('repo_name:'.rjust(17), issue_print.repo_name)
                print('repo_about:'.rjust(17), issue_print.repo_about)
                print('html_url:'.rjust(17), issue_print.issue_htmlurl)
                print('issue_id:'.rjust(17), issue_print.issue_id)
                print('issue_title:'.rjust(17), issue_print.issue_title)
                print('score:'.rjust(17), issue_print.score)
                print('relevance:'.rjust(17), issue_print.relevance)
                print('linked_issues:'.rjust(17), issue_print.linked_issues)
                print('notes:'.rjust(17), issue_print.notes)
                print('-----------------------------------------------------------------------------------------------')
    except Exception as e:
        print('Exception inside issue_print() on line {}:'.format(sys.exc_info()[-1].tb_lineno),
              e.with_traceback(e.__traceback__))


def google_search(query, google_api_key, google_cse_id, start, **kwargs):
    """
    function that uses a search query to look for in the web using google as a search engine
    :param query: read from an outside file that contains keywords to filter by
    :param google_api_key: read from an outside file to use the custom search engine
    :param google_cse_id: read from an outside file to use the search engine
    :param start: offset to tell google what results to deliver since the max of results given at a time is 10
    :param kwargs:
    :return: returns a dict-object with the 10 results found with this query
    """
    try:
        service = build(serviceName='customsearch', version='v1', developerKey=google_api_key)
        result = service.cse().list(q=query, cx=google_cse_id, exactTerms='comments', start=start, **kwargs).execute()
        return result
    except Exception as e:
        if e.args[0]['status'] == '429':
            return None
        else:
            print('Exception inside googl_search() on line {}:'.format(sys.exc_info()[-1].tb_lineno),
                  e.with_traceback(e.__traceback__))


def query_maker(keywords):
    """
    function to build the search query with the desired keywords
    :param keywords: string of keywords extracted from the config file
    :return: string of the final query
    """
    query = 'inurl:issues '
    for keyword in keywords.split('\t'):
        if ' ' in keyword:
            keyword = '"' + keyword + '"'
        query += 'intext:' + keyword + ' '
    return query


def page_iterator(auth, keywords, issue_comments, repo_contributors, google_api_key, google_cse_id, path_db):
    try:
        relevance = 0
        query = query_maker(keywords)
        conn = create_connection(path_db)
        print('Used Keywords: '.rjust(37) + keywords)
        print('Used minimum amount of comments:'.rjust(37), issue_comments)
        print('Used minimum amount of contributors:'.rjust(37), repo_contributors, '\n')
        for offset in range(0, 100, 10):
            res_page = google_search(query=query, google_api_key=google_api_key,
                                     google_cse_id=google_cse_id, start=offset)
            if res_page is None:
                print('\nDaily rate-limit of 100 query searches reached.\n')
                break
            elif res_page['searchInformation']['totalResults'] == '0':
                print('Finished iterating through', relevance, 'results\n')
                break
            for res in res_page['items']:
                relevance += 1
                repo_id = int(res['pagemap']['metatags'][0]['octolytics-dimension-repository_id'])
                issue_num = int(res['link'].split('issues/')[1])

                # check ob repo und issue bereits in der datenbank vorhanden sind
                repo = auth.get_repo(repo_id)
                issue = repo.get_issue(issue_num)
                if redundancy_check(conn, 'issues', issue.id, issue.title, relevance, keywords):
                    if metric_check(conn, issue_comments, repo_contributors, issue.id, repo_id):
                        issue_print(conn, issue.id)
                    continue
                else:
                    if auth.get_rate_limit().core.remaining <= 0:
                        reset_sleep(auth)
                    issue_dates = get_issue_dates(issue)
                    scf = stats_code_frequency(repo, auth)
                    cons = contributors(repo, auth)
                    issue_obj = IssueObj(repo_id=repo.id, id=issue.id, url=issue.url, html_url=issue.html_url,
                                         title=issue.title, number=issue.number, score=0, notes='',
                                         amount_of_comments=issue.get_comments().totalCount, relevance=relevance,
                                         keywords=db_keywords(keywords), labels=get_labels(issue),
                                         linked_issues='',
                                         create_date=issue_dates.created_at, closed_date=issue_dates.closed_at)
                    insert(conn, 'issues', issue_obj)
                    print('Issue:'.rjust(11), issue.title, issue.id, 'has been inserted into the database')
                    if redundancy_check(conn, 'repositories', repo_id, repo.full_name, relevance, keywords):
                        if metric_check(conn, issue_comments, repo_contributors, issue.id, repo_id):
                            issue_print(conn, issue.id)
                        continue
                    else:
                        repo_obj = RepoObj(id=repo.id, url=repo.url, html_url=repo.html_url,
                                           about=repo.description,
                                           creator=repo.full_name.split('/')[0], name=repo.full_name.split('/')[1],
                                           size=repo.size, languages=get_languages(repo), contributors=cons.get_size(),
                                           issues_amount=repo.get_issues().totalCount,
                                           issues_keywords=db_keywords(keywords),
                                           issues_labels=get_labels(issue),
                                           code_frequency_additions=scf.get_adds(),
                                           code_frequency_deletions=scf.get_dels(),
                                           code_frequency_ratio=scf.ratio)
                        insert(conn, 'repositories', repo_obj)
                        print('Repository:', repo.full_name, repo.id, 'has been inserted into the database')
                if metric_check(conn, issue_comments, repo_contributors, issue.id, repo_id):
                    issue_print(conn, issue.id)
    except Exception as e:
        print('Exception inside page_iterator() on line {}:'.format(sys.exc_info()[-1].tb_lineno),
              repr(e))


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


def download_repo(init, repo_id):
    """
    function to download the repo as it is seen in github with the folder structure intact
    :param init: init object for extracting the path of download from
    :param auth: authentication object to perform necessary calls
    :param repo: repository object to download
    :return: False
    """
    auth = init.auth
    folder = create_download_folder(init.config.path_of_download)
    repo = auth.get_repo(repo_id)
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


# ---------------------------------------------------------------------------------------------------------------------#

def input_handler(init):
    conn = create_connection(init.config.path_of_database)
    print('-----------------------------------------------------------------------------------------------')
    print('sq\t'.rjust(35), 'to use the query created by the config '
                       'and give out each result for further inspection and entry into the database')
    print('sn<tab><issue_id><tab><message>\t'.rjust(35), 'to set notes for a certain issue')
    print('ss<tab><issue_id><tab><score>\t'.rjust(35), 'to set the score for a certain issue')
    print('giws<tab><operator><tab><score>\t'.rjust(35), 'to get all issues stored in the database '
                                                                      'where the score fulfills the condition')
    print('giwm\t'.rjust(35), 'to get all issues stored in the database where the metainformation fulfill '
                              'the metrics set inside the configfile')
    print('dr<tab>repo_id\t'.rjust(35), "to download the repository's files into a folder set "
                                                 'by the configuration file')
    print('quit\t'.rjust(35), 'to terminate this program')
    func_input = input('\nplease choose one of the stated functions by writing it down and '
                       'press the enter key afterwards\n')
    print('-----------------------------------------------------------------------------------------------')
    if func_input.split('\t')[0] == 'sq':
        page_iterator(auth=init.auth, keywords=init.config.keywords, issue_comments=int(init.config.issue_comments),
                      repo_contributors=int(init.config.repo_contributors),
                      google_api_key=init.config.google_api_key, google_cse_id=init.config.google_cse_id,
                      path_db=init.config.path_of_database)
    elif func_input.split('\t')[0] == 'sn':
        issue_id = func_input.split('\t')[1]
        message = func_input.split('\t')[2]
        set_notes_to_issue(issue_id, message, conn)
    elif func_input.split('\t')[0] == 'ss':
        issue_id = func_input.split('\t')[1]
        score = func_input.split('\t')[2]
        set_score_of_issue(issue_id, score, conn)
    elif func_input.split('\t')[0] == 'giws':
        operator = func_input.split('\t')[1]
        score = func_input.split('\t')[2]
        get_issues_where_score(conn, operator, score)
    elif func_input.split('\t')[0] == 'giwm':
        get_issues_where_metrics(conn=conn, keywords=init.config.keywords,
                                 issue_comments=int(init.config.issue_comments),
                                 repo_contributors=int(init.config.repo_contributors))
    elif func_input.split('\t')[0] == 'dr':
        repo_id = func_input.split('\t')[1]
        download_repo(init, repo_id)
    elif func_input.split('\t')[0] == 'quit':
        quit()
    input_handler(init)


def set_notes_to_issue(issue_id, message, conn):
    try:
        with conn:
            cursor = conn.cursor()
            update_statement = """UPDATE issues SET notes = ? WHERE issue_id = ?;"""
            cursor.execute(update_statement, [message, issue_id])

            check_statement = """SELECT notes FROM issues WHERE issue_id = ?;"""
            cursor.execute(check_statement, [issue_id])
            db_entry = cursor.fetchall()[0]
            if not db_entry:
                print('Note was failed to add.')
            else:
                print('Note was successfully added')
            cursor.close()
    except Exception as e:
        print('Exception inside set_notes_to_issue() on line {}:'.format(sys.exc_info()[-1].tb_lineno),
              e.with_traceback(e.__traceback__))


def set_score_of_issue(issue_id, score, conn):
    try:
        with conn:
            cursor = conn.cursor()
            update_statement = """UPDATE issues SET score = ? WHERE issue_id = ?;"""
            cursor.execute(update_statement, [int(score), issue_id])

            check_statement = """SELECT score FROM issues WHERE issue_id = ?;"""
            cursor.execute(check_statement, [issue_id])
            db_entry = cursor.fetchall()[0]
            if not db_entry:
                print('Score was failed to add.')
            else:
                print('Score was successfully set to ' + str(db_entry[0]))
            cursor.close()
    except Exception as e:
        print('Exception inside set_score_of_issue() on line {}:'.format(sys.exc_info()[-1].tb_lineno),
              e.with_traceback(e.__traceback__))


def get_issues_where_score(conn, operator, score):
    try:
        with conn:
            cursor = conn.cursor()
            select_statement = """SELECT issue_id FROM issues WHERE score """ + operator + """ ? ORDER BY score DESC;"""
            cursor.execute(select_statement, [score])
            db_entry = cursor.fetchall()[0]
            for entry in db_entry:
                issue_print(conn, entry)
            cursor.close()
    except Exception as e:
        print('Exception inside get_issues_where_score() on line {}:'.format(sys.exc_info()[-1].tb_lineno),
              e.with_traceback(e.__traceback__))


def get_issues_where_metrics(conn, keywords, issue_comments, repo_contributors):
    try:
        print('Used Keywords:'.rjust(37), keywords)
        print('Used minimum amount of comments:'.rjust(37), issue_comments)
        print('Used minimum amount of contributors:'.rjust(37), repo_contributors, '\n')
        with conn:
            cursor = conn.cursor()
            select_statement = """SELECT i.issue_id, i.keywords FROM issues AS i INNER JOIN repositories AS r 
                                    ON i.repo_id = r.repo_id WHERE amount_of_comments >= ? 
                                    AND contributors >= ? ORDER BY score DESC;"""
            cursor.execute(select_statement, [issue_comments, repo_contributors])
            db_entry = cursor.fetchall()
            for entry in db_entry:
                print_issue = True
                for keyword in keywords.split('\t'):
                    if keyword not in entry[1]:
                        print_issue = False
                if print_issue:
                    issue_print(conn, entry[0])
            cursor.close()
    except Exception as e:
        print('Exception inside get_issues_where_metrics() on line {}:'.format(sys.exc_info()[-1].tb_lineno),
              e.with_traceback(e.__traceback__))

# ---------------------------------------------------------------------------------------------------------------------#


class Init:
    def __init__(self, auth=None, config=None):
        self.auth = auth
        self.config = config


def init():
    """
    function to initialize this program
    :return: Init-object
    """
    if create_config():
        sys.exit("The configuration file was just created. "
                 "Please open the file 'config.ini' located in the same folder as this program and "
                 "fill it out as instructed in the documentation. Then run this program again. "
                 "\nProgram successfully terminated.")
    init = Init()
    init.config = read_config()
    init.auth = Github(login_or_token=init.config.github_api_key, per_page=100)
    create_database(init.config.path_of_database)
    return init


# site:github.com inurl:issues OR inurl:pulls intext:"technical debt" intext:refactoring intext:cost
if __name__ == '__main__':
    init = init()
    input_handler(init)

