"""
main.py passes over an object as argument of class Repository
"""


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
    unique_labels_in_issues = []
    issues_obj = repo.get_issues(state='all')
    if auth.get_rate_limit().core.remaining <= 0:
        reset_sleep(auth)
    counter = 1
    for issue in issues_obj:
        counter += 1
        if auth.get_rate_limit().core.remaining <= 0:
            reset_sleep(auth)
        issue_result = read_issue(keywords, issue, auth)
        if issue_result is not None:
            found_keywords_in_issues.append(issue_result)
            for keyword in issue_result[1]:
                if keyword not in unique_keywords_in_issues:
                    unique_keywords_in_issues.append(keyword)
            for label in issue_result[2]:
                if label not in unique_labels_in_issues:
                    unique_labels_in_issues.append(keyword)
    return found_keywords_in_issues, unique_keywords_in_issues, unique_labels_in_issues


def read_issue(keywords, issue, auth):
    """
    checks for each comment in the given issue if the given keywords are found. Also inside the title
    if a keyword was found it is written inside a list
    :param auth: the authentication object that is used to access the current rate-limit
    :param keywords: list of words to look for inside the issue
    :param issue: the issue to be looked into
    :return: the corresponding issue ID, the amount of comments the issue has and keywords_in_issue
    """
    from main import reset_sleep
    keywords_in_issue = []
    label_list = []
    for label in issue.labels:
        label_list.append(label.name)

    for keyword in keywords:
        if keyword.casefold() in issue.title.casefold():
            keywords_in_issue.append(keyword)
    temp_keywords = []
    if auth.get_rate_limit().core.remaining <= 0:
        reset_sleep(auth)
    for issue_comment in issue.get_comments():
        if auth.get_rate_limit().core.remaining <= 0:
            reset_sleep(auth)
        if len(keywords) == len(temp_keywords):
            break
        else:
            for keyword in keywords:
                if keyword.casefold() in issue_comment.body.casefold():
                    keywords_in_issue.append(keyword)
                    temp_keywords.append(keyword)
    if not keywords_in_issue:
        return None
    else:
        if issue.closed_at is None:
            return issue.id, keywords_in_issue, label_list, issue.comments, issue.number, \
                   issue.created_at.strftime(str(issue.created_at.date())), 'NA'
        else:
            return issue.id, keywords_in_issue, label_list, issue.comments, issue.number, \
                   issue.created_at.strftime(str(issue.created_at.date())), \
                   issue.closed_at.strftime(str(issue.closed_at.date()))
