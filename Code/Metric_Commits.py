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
    found_keywords_in_commits = []
    unique_keywords_in_commits = []
    commits_obj = repo.get_commits()
    if auth.get_rate_limit().core.remaining <= 0:
        reset_sleep(auth)
    for commit in commits_obj:
        if auth.get_rate_limit().core.remaining <= 0:
            reset_sleep(auth)
        else:
            commit_result = read_commit(keywords, commit)
            if commit_result is not None:
                found_keywords_in_commits.append(commit_result)
                print(commit_result)
                for keyword in commit_result[1]:
                    if keyword not in unique_keywords_in_commits:
                        unique_keywords_in_commits.append(keyword)
    return found_keywords_in_commits, unique_keywords_in_commits


def read_commit(keywords, commit):
    keywords_in_commit = []
    for keyword in keywords:
        if keyword.casefold() in commit.commit.message.casefold():
            keywords_in_commit.append(keyword)
    if not keywords_in_commit:
        return None
    else:
        if commit.author is not None:
            return commit.sha, keywords_in_commit, commit.author.id, commit.author.login, \
                   commit.stats.additions, commit.stats.deletions
        else:
            return commit.sha, keywords_in_commit, 0, 'NA', \
                   commit.stats.additions, commit.stats.deletions