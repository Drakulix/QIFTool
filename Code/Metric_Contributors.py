"""
main.py passes over an object as argument of class Repository
"""

import time
import datetime


def contributors(repo, auth):
    """
    gets a repository and returns the amount of contributors on that repository
    :param repo: the repository object that contains the contributors
    :param auth: the authentication object that is used to access the current rate-limit
    :return: returns the amount of contributors as an int
    """
    while True:
        if auth.get_rate_limit().core.remaining >= 1:
            con = repo.get_contributors().totalCount
            break
        else:
            if (auth.get_rate_limit().core.reset - datetime.datetime.utcnow()).total_seconds() < 0:
                print('Please make sure your time is set correct on your local machine '
                      '(timezone does not matter) and run the script again')
                quit()
            else:
                time.sleep(int((auth.get_rate_limit().core.reset - datetime.datetime.utcnow()).total_seconds()) + 1)
    return con
