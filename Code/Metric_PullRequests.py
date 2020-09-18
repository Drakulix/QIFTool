"""
main.py passes over an object as argument of class Repository
"""

import sys


class PullRequests:
    def __init__(self, pulls_list, keywords, labels, total_count):
        self.pulls_list = pulls_list
        self.keywords = keywords
        self.labels = labels
        self.total_count = total_count


class Pull:
    def __init__(self, repo_id, id, url, title, number, keywords, labels, comments_total_count, commits_total_count, additions,
                 deletions, created_at, closed_at):
        self.repo_id = repo_id
        self.id = id
        self.url = url
        self.title = title
        self.number = number
        self.keywords = keywords
        self.labels = labels
        self.comments_totalCount = comments_total_count
        self.commits_totalCount = commits_total_count
        self.additions = additions
        self.deletions = deletions
        self.created_at = created_at
        self.closed_at = closed_at


def pull_requests(repo, auth, keywords):
    """
    uses a list of keywords to look for in each pull request title, its content and comments
    :param repo: the repository object that contains the issues
    :param auth: the authentication object that is used to access the current rate-limit
    :param keywords: list of keywords to look for. this is read out of a config file
    :return: returns a list of keywords as strings that were found in the issues and its comments
    """
    try:
        from main import reset_sleep
        pull_request_list = []
        unique_keywords_in_pull_request = []
        unique_labels_in_pull_request = []
        pull_request_obj = repo.get_pulls()
        counter = 0
        if auth.get_rate_limit().core.remaining <= 0:
            reset_sleep(auth)
        for pull in pull_request_obj:
            counter += 1
            if auth.get_rate_limit().core.remaining <= 0:
                reset_sleep(auth)
            pull_result = read_pull(keywords, pull, auth, repo.id)
            if pull_result is not None:
                pull_request_list.append(pull_result)
                for keyword in pull_result.keywords:
                    if keyword not in unique_keywords_in_pull_request:
                        unique_keywords_in_pull_request.append(keyword)
                for label in pull_result.labels:
                    if label not in unique_labels_in_pull_request:
                        unique_labels_in_pull_request.append(label)
        if not pull_request_list:
            return PullRequests(pulls_list=None, keywords=None, labels=None, total_count=pull_request_obj.totalCount)
        else:
            return PullRequests(pulls_list=pull_request_list, keywords=unique_keywords_in_pull_request,
                                labels=unique_labels_in_pull_request, total_count=pull_request_obj.totalCount)
    except Exception as e:
        print('Exception inside Metrics_PullRequests.pull_requests() on line {}:'.format(sys.exc_info()[-1].tb_lineno),
              e.with_traceback(e.__traceback__))


def read_pull(keywords, pull, auth, repo_id):
    """
    checks for each title, body and comments in the given pull request for the given keywords
    if a keyword was found it is written inside a list
    :param repo_id: id of the current repository to be filled inside the pull_request table as reference
    :param auth: authentication object to access the rate-limits
    :param keywords: words to look for inside the issue
    :param pull: the issue to be looked into
    :return: the corresponding issue ID, the amount of comments the issue has and keywords_in_issue
    """
    try:
        from main import reset_sleep
        keywords_in_pull_request = []
        label_list = []
        for label in pull.labels:
            label_list.append(label.name)

        for keyword in keywords:
            if keyword.casefold() in pull.title.casefold():
                keywords_in_pull_request.append(keyword)
            elif keyword.casefold() in pull.body.casefold():
                keywords_in_pull_request.append(keyword)
        temp_keywords = []
        if auth.get_rate_limit().core.remaining <= 0:
            reset_sleep(auth)
        for pull_comment in pull.get_comments():
            if auth.get_rate_limit().core.remaining <= 0:
                reset_sleep(auth)
            if len(keywords) == len(temp_keywords):
                break
            else:
                for keyword in keywords:
                    if keyword.casefold() in pull_comment.body.casefold():
                        keywords_in_pull_request.append(keyword)
                        temp_keywords.append(keyword)
        if not keywords_in_pull_request:
            return None
        else:
            if pull.closed_at is None:
                return Pull(repo_id=repo_id, id=pull.id, url=pull.url, title=pull.title, number=pull.number,
                            keywords=keywords_in_pull_request, labels=label_list, comments_total_count=pull.comments,
                            commits_total_count=pull.commits, additions=pull.additions, deletions=pull.deletions,
                            created_at=pull.created_at.strftime(str(pull.created_at.date())), closed_at='NA')
            else:
                return Pull(repo_id=repo_id, id=pull.id, url=pull.url, title=pull.title, number=pull.number,
                            keywords=keywords_in_pull_request, labels=label_list, comments_total_count=pull.comments,
                            commits_total_count= pull.commits, additions=pull.additions, deletions=pull.deletions,
                            created_at=pull.created_at.strftime(str(pull.created_at.date())),
                            closed_at=pull.closed_at.strftime(str(pull.closed_at.date())))
    except Exception as e:
        print('Exception inside Metrics_PullRequests.read_pull() on line {}:'.format(sys.exc_info()[-1].tb_lineno),
              e.with_traceback(e.__traceback__))
