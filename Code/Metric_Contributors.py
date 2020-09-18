"""
main.py passes over an object as argument of class Repository
"""

import sys


class Contributors:
    def __init__(self, size):
        self.size = size


def contributors(repo, auth):
    """
    gets a repository and returns the amount of contributors on that repository
    :param repo: the repository object that contains the contributors
    :param auth: the authentication object that is used to access the current rate-limit
    :return: returns the amount of contributors as an int
    """
    try:
        from main import reset_sleep
        if auth.get_rate_limit().core.remaining <= 0:
            reset_sleep(auth)
        contributor = Contributors(size=repo.get_contributors().totalCount)
        return contributor
    except Exception as e:
        print('Exception inside Metrics_Contributors.contributors() on line {}:'.format(sys.exc_info()[-1].tb_lineno),
              e.with_traceback(e.__traceback__))
