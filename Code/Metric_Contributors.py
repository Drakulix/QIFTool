"""
main.py passes over an object as argument of class Repository
"""


def contributors(repo, auth):
    """
    gets a repository and returns the amount of contributors on that repository
    :param repo: the repository object that contains the contributors
    :param auth: the authentication object that is used to access the current rate-limit
    :return: returns the amount of contributors as an int
    """
    from main import reset_sleep
    if auth.get_rate_limit().core.remaining <= 0:
        reset_sleep(auth)
    con = repo.get_contributors().totalCount
    return con
