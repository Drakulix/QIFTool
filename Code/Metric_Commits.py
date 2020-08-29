"""
main.py passes over an object as argument of class Repository

returns commits and their attached message
"""

import time
import datetime


def commits(repo_obj, auth_obj, words):
    print(datetime.datetime.now().astimezone().tzinfo)
    found_words = []
    commits_obj = repo_obj.get_commits()
    page_counter = 1
    for commit in commits_obj:
        if page_counter == 101:
            print(auth_obj.get_rate_limit().core.reset)
            print('local utc time: ' + str(datetime.datetime.utcnow()))
            print(int((auth_obj.get_rate_limit().core.reset - datetime.datetime.utcnow()).total_seconds()))
            if auth_obj.get_rate_limit().core.remaining >= 1:
                page_counter = 1
                continue
            else:
                while True:
                    if auth_obj.get_rate_limit().core.remaining >= 1:
                        break
                    else:
                        time.sleep(int(
                            (auth_obj.get_rate_limit().core.reset - datetime.datetime.utcnow()).total_seconds()) + 1)
        else:
            # checks if the given list of words are all found and then returns thus improving runtime and rate_limit
            if not words:
                return found_words
            else:
                # checks for each message if the given words are found. if a word was found it is removed from the list
                # since it does not have to be found again thus also improving runtime for each additional message
                for word in words:
                    if word.casefold() in commit.commit.message.casefold():
                        found_words.append(word)
                        words.remove(word)
            print(page_counter, commit.author, '\t', commit.commit.message)
            page_counter += 1
    return found_words
