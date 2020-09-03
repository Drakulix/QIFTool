"""
main.py passes over an object as argument of class Repository
"""

import Reset_sleep


def issues(repo, auth, keywords):
    """
    uses a list of keywords to look for in each issue title and its comments
    :param repo: the repository object that contains the issues
    :param auth: the authentication object that is used to access the current rate-limit
    :param keywords: list of keywords to look for. this is read out of a config file
    :return: returns a list of keywords as strings that were found in the issues and its comments
    """
    longest_issue = 0
    keywords_in_issue = []
    found_keywords = []
    issues_obj = repo.get_issues(state='all')
    if auth.get_rate_limit().core.remaining <= 0:
        Reset_sleep.reset_sleep(auth)
    for issue in issues_obj:
        if auth.get_rate_limit().core.remaining <= 0:
            Reset_sleep.reset_sleep(auth)
        if not keywords:
            # checks if the given list of keywords are all found and then returns immediately
            # thus improving runtime and rate_limit usage
            return found_keywords, issues_obj.totalCount
        else:
            found_keywords = read_issues(keywords, found_keywords, issue, longest_issue)
    return found_keywords


def read_issues(keywords, found_keywords, issue, longest_issue, keywords_in_issue):
    """
    checks for each comment in the given issue if the given keywords are found. Also inside the title
    if a keyword was found it is removed from the list since it does not have to be found again
    thus also improving runtime for each iteration
    :param keywords: words to look for inside the issue
    :param found_keywords: list of keywords that have been found
    :param issue: the issue to be looked into
    :return: a list consisting of the words that have been found by now
    """
    for keyword in keywords:
        print(issue.title)
        if keyword.casefold() in issue.title.casefold():
            found_keywords.append(keyword)
            keywords.remove(keyword)
        for issue_comment in issue.get_comments():
            longest_issue += 1
            print(issue_comment.body)
            if keyword.casefold() in issue_comment.body.casefold():
                found_keywords.append(keyword)
                keywords.remove(keyword)
    return found_keywords


def read_issues(keywords, issue, longest_issue, keywords_in_issue):
    """
    checks for each comment in the given issue if the given keywords are found. Also inside the title
    if a keyword was found it is removed from the list since it does not have to be found again
    thus also improving runtime for each iteration
    :param keywords: words to look for inside the issue
    :param found_keywords: list of keywords that have been found
    :param issue: the issue to be looked into
    :return: a list consisting of the words that have been found by now
    """
    for keyword in keywords:
        if keyword.casefold() in issue.title.casefold():
            keywords_in_issue.append(keyword, issue.id, issue.comments)
        for issue_comment in issue.get_comments():
            if keyword.casefold() in issue_comment.body.casefold():
                if keyword not in keywords_in_issue:
                    keywords_in_issue.append(keyword, issue.id, issue.comments)
    return keywords_in_issue
