"""
main.py passes over an object as argument of class Repository
"""

import sys


class Issues:
    def __init__(self, issues_list, keywords, labels, total_count):
        self.issues_list = issues_list
        self.keywords = keywords
        self.labels = labels
        self.total_count = total_count


class Issue:
    def __init__(self, repo_id, id, url, title, number, keywords, labels, comments_total_count, created_at, closed_at):
        self.repo_id = repo_id
        self.id = id
        self.url = url
        self.title = title
        self.number = number
        self.keywords = keywords
        self.labels = labels
        self.comments_totalCount = comments_total_count
        self.created_at = created_at
        self.closed_at = closed_at


def issues(repo, auth, keywords):
    """
    uses a list of keywords to look for in each issue title and its comments
    :param repo: the repository object that contains the issues
    :param auth: the authentication object that is used to access the current rate-limit
    :param keywords: list of keywords to look for. this is read out of a config file
    :return: returns a list of keywords as strings that were found in the issues and its comments
    """
    try:
        from main import reset_sleep
        issues_list = []
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
            issue_result = read_issue(keywords, issue, auth, repo.id)
            if issue_result is not None:
                issues_list.append(issue_result)
                for keyword in issue_result.keywords:
                    if keyword not in unique_keywords_in_issues:
                        unique_keywords_in_issues.append(keyword)
                for label in issue_result.labels:
                    if label not in unique_labels_in_issues:
                        unique_labels_in_issues.append(label)
        if not issues_list:
            return Issues(issues_list=None, keywords=None, labels=None, total_count=issues_obj.totalCount)
        else:
            return Issues(issues_list=Issues, keywords=unique_keywords_in_issues, labels=unique_labels_in_issues,
                          total_count=issues_obj.totalCount)
    except Exception as e:
        print('Exception inside Metrics_Issues.issues() on line {}:'.format(sys.exc_info()[-1].tb_lineno),
              e.with_traceback(e.__traceback__))


def read_issue(keywords, issue, auth, repo_id):
    """
    checks for each comment in the given issue if the given keywords are found. Also inside the title
    if a keyword was found it is written inside a list
    :param repo_id: id of the current repository to be filled inside the issue table as reference
    :param auth: the authentication object that is used to access the current rate-limit
    :param keywords: list of words to look for inside the issue
    :param issue: the issue to be looked into
    :return: the corresponding issue ID, the amount of comments the issue has and keywords_in_issue
    """
    try:
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
                return Issue(repo_id=repo_id, id=issue.id, url=issue.url, title=issue.title, number=issue.number,
                             keywords=keywords_in_issue, labels=label_list, comments_total_count=issue.comments,
                             created_at=issue.created_at.strftime(str(issue.created_at.date())), closed_at='NA')
            else:
                return Issue(repo_id=repo_id, id=issue.id, url=issue.url, title=issue.title, number=issue.number,
                             keywords=keywords_in_issue, labels=label_list, comments_total_count=issue.comments,
                             created_at=issue.created_at.strftime(str(issue.created_at.date())),
                             closed_at=issue.closed_at.strftime(str(issue.closed_at.date())))
    except Exception as e:
        print('Exception inside Metrics_Issues.read_issue() on line {}:'.format(sys.exc_info()[-1].tb_lineno),
              e.with_traceback(e.__traceback__))
