"""
main.py passes over an object as argument of class Repository
"""

import Reset_sleep


def commits(repo, auth, keywords):
    """
    uses a list of keywords to look for in each commit message
    :param repo: the repository object that contains the commits
    :param auth: the authentication object that is used to access the current rate-limit
    :param keywords: list of keywords to look for. this is read out of a config file
    :return: returns a list of keywords as strings that were found in the commits
    """
    found_keywords = []
    commits_obj = repo.get_commits()
    if auth.get_rate_limit().core.remaining <= 0:
        Reset_sleep.reset_sleep(auth)
    for commit in commits_obj:
        if auth.get_rate_limit().core.remaining <= 0:
            Reset_sleep.reset_sleep(auth)
        if not keywords:
            # checks if the given list of keywords are all found and then returns immediately
            # thus improving runtime and rate_limit usage
            return found_keywords, commits_obj.totalCount
        else:
            found_keywords = read_commits(keywords, found_keywords, commit)
    return found_keywords, commits_obj.totalCount


def read_commits(keywords, found_keywords, commit):
    for word in keywords:
        if word.casefold() in commit.commit.message.casefold():
            found_keywords.append(word)
            keywords.remove(word)
    return found_keywords
