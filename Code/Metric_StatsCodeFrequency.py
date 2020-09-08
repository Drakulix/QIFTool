"""
main.py passes over an object as argument of class Repository
"""


def stats_code_frequency(repo, auth):
    """
    gets a repository object and counts the additions and deletions on a weekly basis together
    :param repo: the repository object that contains the stats code frequency
    :param auth: the authentication object that is used to access the current rate-limit
    :return: returns a tuple with the first item being the accumulated additions
            and the second the accumulated deletions
    """
    from main import reset_sleep
    if auth.get_rate_limit().core.remaining <= 0:
        reset_sleep(auth)
    scf_obj = repo.get_stats_code_frequency()
    additions = 0
    deletions = 0
    for add_del in scf_obj:
        additions += add_del.additions
        deletions += add_del.deletions
    return additions, deletions.__abs__()
