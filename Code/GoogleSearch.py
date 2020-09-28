from googleapiclient.discovery import build
from github import Github
from time import time
from datetime import datetime
from sqlite3 import Error
import configparser
import sqlite3
import sys
import os

api_key = "api_key"
cse_id = "cse_di"


# ---------------------------------------------------------------------------------------------------------------------#
# class and functions for handling the configuration file

class Config:
    def __init__(self, path_of_database, path_of_download, github_api_key, google_api_key, google_cse_id,
                 keywords, issue_comments, repo_contributors, repo_additions, repo_deletions, repo_ratio):
        self.path_of_database = path_of_database
        self.path_of_download = path_of_download
        self.github_api_key = github_api_key
        self.google_api_key = google_api_key
        self.google_cse_id = google_cse_id
        self.keywords = keywords
        self.issue_comments = issue_comments
        self.repo_contributors = repo_contributors
        self.repo_additions = repo_additions
        self.repo_deletions = repo_deletions
        self.repo_ratio = repo_ratio


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
                         'repo_contributors': '',
                         'repo_additions': '',
                         'repo_deletions': '',
                         'repo_ratio': ''
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
                    repo_contributors=config['metrics']['repo_contributors'],
                    repo_additions=config['metrics']['repo_additions'],
                    repo_deletions=config['metrics']['repo_deletions'],
                    repo_ratio=config['metrics']['repo_ratio'])
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
                cursor.execute(insert_statement, list(vars(values).values()))
            else:
                print('table selection went wrong!')
        except Exception as e:
            print('Exception inside insert on line {}:'.format(sys.exc_info()[-1].tb_lineno),
                  e.with_traceback(e.__traceback__))


class RelevanceValues:
    def __init__(self, result, old=None, new=None):
        self.result = result
        self.old = old
        self.new = new


def redundancy_check(conn, table, issue_or_repo_id, title_or_name, relevance):
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
                    if rel_values.result:
                        print('\t\t', title_or_name, issue_or_repo_id, 'already in database '
                                                                       'but relevance changed from',
                                                                        rel_values.old, 'to', rel_values.new)
                return True
            else:
                return False
    except Exception as e:
        print('Exception inside insert on line {}:'.format(sys.exc_info()[-1].tb_lineno),
              e.with_traceback(e.__traceback__))


def relevance_check(conn, issue_id, relevance):
    """
    function to check an issues relevance whenever it occours in the search again if its relevance is lower than the one
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
        print('Exception inside insert on line {}:'.format(sys.exc_info()[-1].tb_lineno),
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
        print('Exception inside Metrics_Contributors.contributors() on line {}:'.format(sys.exc_info()[-1].tb_lineno),
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


def db_keywords(keywords):
    """
    function to make a suitable string out of the given keywords to insert into the database
    :param keywords: string of keywords extracted from the config file
    :return: the changed string to fit into the database
    """
    keywords_str = ''
    keywords_list = keywords.split('\t')
    if len(keywords_list) == 1:
        return keywords_str
    elif len(keywords_list) > 1:
        for keyword in keywords_list[:-1]:
            keywords_str += keyword + ', '
        keywords_str += keywords[-1]
    return keywords_str


def get_labels(issue):
    """
    function to get the labels of an issue
    :param issue: the issue of the labels to extract
    :return: a string suitable for an insert into the database
    """
    labels_str = ''
    for label in issue.get_labels():
        labels_str += label.name + ', '
    return labels_str


def get_languages(repo):
    languages_str = ''
    for lang in repo.get_languages():
        languages_str += lang + ', '
    return languages_str


def get_linked_issues(issue):
    # TODO
    linked_issues = ''
    return linked_issues


def get_issue_dates(issue):
    """
    function to return the issue dates of when they have been created and possibly been closed at
    :param issue: issue-object
    :return: IssueDates-object
    """
    if issue.closed_at is None:
        return IssueDates(created_at=issue.created_at.strftime(str(issue.created_at.date())))
    else:
        return IssueDates(created_at=issue.created_at.strftime(str(issue.created_at.date())),
                          closed_at=issue.closed_at.strftime(str(issue.closed_at.date())))


def page_iterator(auth, keywords, google_api_key, google_cse_id, path_db):
    try:
        relevance = 0
        query = query_maker(keywords)
        print(query)
        for offset in range(1, 100, 10):
            res_page = google_search(query=query, google_api_key=google_api_key, google_cse_id=google_cse_id, start=offset)
            print(res_page.keys)
            for res in res_page['items']:
                relevance += 1
                repo_id = int(res['pagemap']['metatags'][0]['octolytics-dimension-repository_id'])
                issue_num = int(res['link'].split('issues/')[1])

                # check ob repo und issue bereits in der datenbank vorhanden sind
                repo = auth.get_repo(repo_id)
                issue = repo.get_issue(issue_num)
                conn = create_connection(path_db)
                if redundancy_check(conn, 'issues', issue.id, issue.title, relevance):
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
                                         linked_issues=get_linked_issues(issue),
                                         create_date=issue_dates.created_at, closed_date=issue_dates.closed_at)
                    insert(conn, 'issues', issue_obj)
                    if redundancy_check(conn, 'repositories', repo_id, repo.full_name, relevance):
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
                issue_print(conn, issue.id)
    except Exception as e:
        print('Exception inside page_iterator() on line {}:'.format(sys.exc_info()[-1].tb_lineno),
              repr(e))


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


# ---------------------------------------------------------------------------------------------------------------------#

def input_handler(init):
    # wait for keyboard input
    conn = create_connection(init.config.path_of_database)
    func_input = input('\nplease choose one of the following functions\n'
                       '\tsq<enter key>\tto use the query created by the config '
                       'and give out each result for further inspection and entry into the database\n'
                       '\tsn<tab><issue_id><tab><message><enter key>\tto set notes for a certain issue\n'
                       '\tss<tab><issue_id><tab><score><enter key>\tto set the score for a certain issue\n'
                       '\tgiws<tab><operator(<, >, =, ...)><tab><score><enter key>\t '
                       'to get all issues stored in the database '
                       'where the score fulfills the condition\n'
                       '\tquit<enter key>\tto terminate this program\n\n')
    if func_input.split('\t')[0] == 'sq':
        page_iterator(auth=init.auth, keywords=init.config.keywords,
                      google_api_key=init.config.google_api_key, google_cse_id=init.config.google_cse_id,
                      path_db=init.config.path_of_database)
    elif func_input.split('\t')[0] == 'sn':
        issue_id = func_input.split('\t')[1]
        message = func_input.split('\t')[2]
        print(message)
        set_notes_to_issue(issue_id, message, conn)
    elif func_input.split('\t')[0] == 'ss':
        issue_id = func_input.split('\t')[1]
        score = func_input.split('\t')[2]
        set_score_of_issue(issue_id, score, conn)
    elif func_input.split('\t')[0] == 'giws':
        operator = func_input.split('\t')[1]
        score = func_input.split('\t')[2]
        get_issues_where_score(conn, operator, score)
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
        print('Exception inside issue_print() on line {}:'.format(sys.exc_info()[-1].tb_lineno),
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

