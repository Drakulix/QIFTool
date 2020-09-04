"""
main.py passes over an object as argument of class Repository
"""


def commits(repo, auth, keywords):
    """
    uses a list of keywords to look for in each commit message
    :param repo: the repository object that contains the commits
    :param auth: the authentication object that is used to access the current rate-limit
    :param keywords: list of keywords to look for. this is read out of a config file
    :return: returns a list of keywords as strings that were found in the commits
    """
    from main import reset_sleep
    commits_list = []
    commits_obj = repo.get_commits()
    if auth.get_rate_limit().core.remaining <= 0:
        reset_sleep(auth)
    for commit in commits_obj:
        if auth.get_rate_limit().core.remaining <= 0:
            reset_sleep(auth)
        else:
            commits_list.append(read_commit(keywords, commit))
    return commits_list


def read_commit(keywords, commit):
    keywords_in_commit = []
    for keyword in keywords:
        if keyword.casefold() in commit.commit.message.casefold():
            keywords_in_commit.append(keyword)
    return commit.sha, keywords_in_commit, commit.author.id, commit.author.login, \
           commit.stats.additions, commit.stats.deletions
