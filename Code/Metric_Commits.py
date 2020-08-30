"""
main.py passes over an object as argument of class Repository
"""

import time
import datetime


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
    while True:
        if auth.get_rate_limit().core.remaining >= 1:
            for commit in commits_obj:
                if auth.get_rate_limit().core.remaining >= 1:
                    # checks if the given list of keywords are all found and then returns immediately
                    # thus improving runtime and rate_limit usage
                    if not keywords:
                        return found_keywords
                    else:
                        # checks for each message if the given words are found.
                        # if a word was found it is removed from the list since it does not have to be found again
                        # thus also improving runtime for each additional message
                        found_keywords = read_commits(keywords, found_keywords, commit)
                else:
                    if (auth.get_rate_limit().core.reset - datetime.datetime.utcnow()).total_seconds() < 0:
                        print('Please make sure your time is set correct on your local machine '
                              '(timezone does not matter) and run the script again')
                        quit()
                    else:
                        time.sleep(int((auth.get_rate_limit().core.reset -
                                        datetime.datetime.utcnow()).total_seconds()) + 1)
                        if auth.get_rate_limit().core.remaining >= 1:
                            found_keywords = read_commits(keywords, found_keywords, commit)
            break
        else:
            if (auth.get_rate_limit().core.reset - datetime.datetime.utcnow()).total_seconds() < 0:
                print('Please make sure your time is set correct on your local machine '
                      '(timezone does not matter) and run the script again')
                quit()
            else:
                time.sleep(int((auth.get_rate_limit().core.reset -
                                datetime.datetime.utcnow()).total_seconds()) + 1)
    return found_keywords


def read_commits(keywords, found_keywords, commit):
    for word in keywords:
        if word.casefold() in commit.commit.message.casefold():
            found_keywords.append(word)
            keywords.remove(word)
    return found_keywords
