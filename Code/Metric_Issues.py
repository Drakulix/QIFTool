"""
main.py passes over an object as argument of class Repository
"""

import time
import datetime


def issues(repo, auth, keywords):
    """
    uses a list of keywords to look for in each issue title and its comments
    :param repo: the repository object that contains the issues
    :param auth: the authentication object that is used to access the current rate-limit
    :param keywords: list of keywords to look for. this is read out of a config file
    :return: returns a list of keywords as strings that were found in the issues and its comments
    """
    found_keywords = []
    issues_obj = repo.get_issues(state='all')
    while True:
        if auth.get_rate_limit().core.remaining >= 1:
            for issue in issues_obj:
                if auth.get_rate_limit().core.remaining >= 1:
                    # checks if the given list of keywords are all found and then returns immediately
                    # thus improving runtime and rate_limit usage
                    if not keywords:
                        return found_keywords
                    else:
                        # checks for each comment if the given words are found. Also inside the title
                        # if a keyword was found it is removed from the list since it does not have to be found again
                        # thus also improving runtime for each additional message
                        found_keywords = read_issues(keywords, found_keywords, issue)
                else:
                    if (auth.get_rate_limit().core.reset - datetime.datetime.utcnow()).total_seconds() < 0:
                        print('Please make sure your time is set correct on your local machine '
                              '(timezone does not matter) and run the script again')
                        quit()
                    else:
                        time.sleep(int((auth.get_rate_limit().core.reset -
                                        datetime.datetime.utcnow()).total_seconds()) + 1)
                        if auth.get_rate_limit().core.remaining >= 1:
                            found_keywords = read_issues(keywords, found_keywords, issue)
            break
        else:
            if (auth.get_rate_limit().core.reset - datetime.datetime.utcnow()).total_seconds() < 0:
                print('Please make sure your time is set correct on your local machine '
                      '(timezone does not matter) and run the script again')
                quit()
            else:
                time.sleep(int((auth.get_rate_limit().core.reset - datetime.datetime.utcnow()).total_seconds()) + 1)
    return found_keywords


def read_issues(keywords, found_keywords, issue):
    for keyword in keywords:
        print(issue.title)
        if keyword.casefold() in issue.title.casefold():
            found_keywords.append(keyword)
            keywords.remove(keyword)
        for issue_comment in issue.get_comments():
            print(issue_comment.body)
            if keyword.casefold() in issue_comment.body.casefold():
                found_keywords.append(keyword)
                keywords.remove(keyword)
    return found_keywords
