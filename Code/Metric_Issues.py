"""
main.py passes over an object as argument of class Repository
"""

import datetime

def issues(repo, auth, keywords):
    """
    uses a list of keywords to look for in each issue title and its comments
    :param repo: the repository object that contains the issues
    :param auth: the authentication object that is used to access the current rate-limit
    :param keywords: list of keywords to look for. this is read out of a config file
    :return: returns a list of keywords as strings that were found in the issues and its comments
    """
    from main import reset_sleep
    found_keywords_in_issues = []
    unique_keywords_in_issues = []
    issues_obj = repo.get_issues(state='all')
    if auth.get_rate_limit().core.remaining <= 0:
        reset_sleep(auth)
    for issue in issues_obj:
        if auth.get_rate_limit().core.remaining <= 0:
            reset_sleep(auth)
        else:
            issue_result = read_issue(keywords, issue)
            if issue_result is not None:
                found_keywords_in_issues.append(issue_result)
                print(issue_result)
                for keyword in issue_result[1]:
                    if keyword not in unique_keywords_in_issues:
                        unique_keywords_in_issues.append(keyword)
    return found_keywords_in_issues, unique_keywords_in_issues


def read_issue(keywords, issue):
    """
    checks for each comment in the given issue if the given keywords are found. Also inside the title
    if a keyword was found it is written inside a list
    :param keywords: words to look for inside the issue
    :param issue: the issue to be looked into
    :return: the corresponding issue ID, the amount of comments the issue has and keywords_in_issue
    """
    keywords_in_issue = []
    label_list = []
    for label in issue.labels:
        label_list.append(label.name)
    for keyword in keywords:
        if keyword.casefold() in issue.title.casefold():
            keywords_in_issue.append(keyword)
        else:
            for issue_comment in issue.get_comments():
                if keyword.casefold() in issue_comment.body.casefold():
                    keywords_in_issue.append(keyword)
                    break
    if not keywords_in_issue:
        return None
    else:
        return issue.id, keywords_in_issue, label_list, issue.comments, issue.number, issue.created_at, issue.closed_at
