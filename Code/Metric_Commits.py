"""
main.py passes over an object as argument of class Repository

returns commits and their attached message
"""


def commits(repo_obj, auth_obj):
    commits_obj = repo_obj.get_commits()
    page_counter = 1
    for commits in commits_obj:
        if page_counter == 31:
            if auth_obj.get_rate_limit().core.remaining >= 1:
                page_counter = 1
                continue
            else:
                break   # alternative action for just breaking like sending out error message and
                        # stopping until the rate limit is back
        else:
            print(page_counter, commits.author, '\t', commits.commit.message)
            page_counter += 1
