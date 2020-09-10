"""
main.py passes over an object as argument of class Repository
"""


def pull_requests(repo, auth, keywords):
    """
    uses a list of keywords to look for in each pull request title, its content and comments
    :param repo: the repository object that contains the issues
    :param auth: the authentication object that is used to access the current rate-limit
    :param keywords: list of keywords to look for. this is read out of a config file
    :return: returns a list of keywords as strings that were found in the issues and its comments
    """
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
            for keyword in pull_result[2]:
                if keyword not in unique_keywords_in_pull_request:
                    unique_keywords_in_pull_request.append(keyword)
            for label in pull_result[3]:
                if label not in unique_labels_in_pull_request:
                    unique_labels_in_pull_request.append(keyword)
    if not pull_request_list:
        return pull_request_obj.totalCount
    else:
        return [pull_request_list, unique_keywords_in_pull_request, unique_labels_in_pull_request,
                pull_request_obj.totalCount]


def read_pull(keywords, pull, auth, repo_id):
    """
    checks for each title, body and comments in the given pull request for the given keywords
    if a keyword was found it is written inside a list
    :param auth: authentication object to access the rate-limits
    :param keywords: words to look for inside the issue
    :param pull: the issue to be looked into
    :return: the corresponding issue ID, the amount of comments the issue has and keywords_in_issue
    """
    from main import reset_sleep
    keywords_in_pull_request = []
    label_list = []
    for label in pull.labels:
        label_list.append(label)

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
            return [repo_id, pull.id, keywords_in_pull_request, label_list, pull.number, pull.comments, pull.commits,
                    pull.additions, pull.deletions, pull.created_at.strftime(str(pull.created_at.date())), 'NA']

        else:
            return [repo_id, pull.id, keywords_in_pull_request, label_list, pull.number, pull.comments, pull.commits,
                    pull.additions, pull.deletions, pull.created_at.strftime(str(pull.created_at.date())),
                    pull.closed_at.strftime(str(pull.closed_at.date()))]
