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
    found_keywords_in_pull_request = []
    unique_keywords_in_pull_request = []
    pull_request_obj = repo.get_pulls()
    if auth.get_rate_limit().core.remaining <= 0:
        reset_sleep(auth)
    for pull in pull_request_obj:
        if auth.get_rate_limit().core.remaining <= 0:
            reset_sleep(auth)
        else:
            pull_result = read_pull(keywords, pull)
            if pull_result is not None:
                found_keywords_in_pull_request.append(pull_result)
                print(pull_result)
                for keyword in pull_result[1]:
                    if keyword not in unique_keywords_in_pull_request:
                        unique_keywords_in_pull_request.append(keyword)
    return found_keywords_in_pull_request, unique_keywords_in_pull_request


def read_pull(keywords, pull):
    """
    checks for each title, body and comments in the given pull request for the given keywords
    if a keyword was found it is written inside a list
    :param keywords: words to look for inside the issue
    :param pull: the issue to be looked into
    :return: the corresponding issue ID, the amount of comments the issue has and keywords_in_issue
    """
    keywords_in_pull_request = []
    label_list = []
    for label in pull.label:
        label_list.append(label)
    for keyword in keywords:
        if keyword.casefold() in pull.title.casefold():
            keywords_in_pull_request.append(keyword)
        elif keyword.casefold() in pull.body.casefold():
            keywords_in_pull_request.append(keyword)
        else:
            for pull_comment in pull.get_comments():
                if keyword.casefold() in pull_comment.body.casefold():
                    keywords_in_pull_request.append(keyword)
                    break
    if not keywords_in_pull_request:
        return None
    else:
        return pull.id, keywords_in_pull_request, pull.number, label_list, pull.comments, pull.commits, \
               pull.created_at, pull.closed_at, pull.additions, pull.deletions
