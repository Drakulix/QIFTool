"""
main.py passes over an object as argument of class Repository
"""

import sys


class SCF:
    def __init__(self, additions, deletions, ratio):
        self.additions = additions
        self.deletions = deletions
        self.ratio = ratio


def stats_code_frequency(repo, auth):
    """
    gets a repository object and counts the additions and deletions on a weekly basis together
    :param repo: the repository object that contains the stats code frequency
    :param auth: the authentication object that is used to access the current rate-limit
    :return: returns a tuple with the first item being the accumulated additions
            and the second the accumulated deletions
    """
    try:
        from main import reset_sleep
        if auth.get_rate_limit().core.remaining <= 0:
            reset_sleep(auth)
        scf_obj = repo.get_stats_code_frequency()
        scf = SCF(additions=0, deletions=0, ratio=0.0)
        for add_del in scf_obj:
            scf.additions += add_del.additions
            scf.deletions += add_del.deletions.__abs__()
        scf.ratio = scf.deletions/scf.additions
        return scf
    except Exception as e:
        print('Exception inside Metrics_StatsCodeFrequency.stats_code_frequency() on line {}:'
              .format(sys.exc_info()[-1].tb_lineno), e.with_traceback(e.__traceback__))
