"""
main.py passes over an object as argument of class Repository
"""

import sys


def commits(repo, auth, keywords):
    """
    uses a list of keywords to look for in each commit message
    :param repo: the repository object that contains the commits
    :param auth: the authentication object that is used to access the current rate-limit
    :param keywords: list of keywords to look for. this is read out of a config file
    :return: returns a list of keywords as strings that were found in the commits
    """
    try:
        from main import reset_sleep
        commits_list = []
        unique_keywords_in_commits = []
        commits_obj = repo.get_commits()
        if auth.get_rate_limit().core.remaining <= 0:
            reset_sleep(auth)
        counter = 1
        for commit in commits_obj:
            counter += 1
            if auth.get_rate_limit().core.remaining <= 0:
                reset_sleep(auth)
            commit_result = read_commit(keywords, commit, repo.id)
            if commit_result is not None:
                commits_list.append(commit_result)
                for keyword in commit_result[2]:
                    if keyword not in unique_keywords_in_commits:
                        unique_keywords_in_commits.append(keyword)
        if not commits_list:
            return commits_obj.totalCount
        else:
            return [commits_list, unique_keywords_in_commits, commits_obj.totalCount]
    except Exception as e:
        print('Exception inside Metrics_Commits.commits() on line {}:'.format(sys.exc_info()[-1].tb_lineno),
              e.with_traceback(e.__traceback__))


def read_commit(keywords, commit, repo_id):
    """
    checks for each message in the given commit if the given keywords are found.
    :param keywords: list of words to look for inside the issue
    :param commit: the commit object to look into
    :param repo_id: id of the current repository to be filled inside the commit table as reference
    :return: list of all meta data of the commit that will be written inside the table
    """
    try:
        keywords_in_commit = []
        for keyword in keywords:
            if keyword.casefold() in commit.commit.message.casefold():
                keywords_in_commit.append(keyword)
        if not keywords_in_commit:
            return None
        else:
            if commit.author is None:
                return [repo_id, commit.sha, keywords_in_commit, 0, 'NA',
                        commit.stats.additions, commit.stats.deletions]

            else:
                return [repo_id, commit.sha, keywords_in_commit, commit.author.id, commit.author.login,
                        commit.stats.additions, commit.stats.deletions]
    except Exception as e:
        print('Exception inside Metrics_Commits.read_commit() on line {}:'.format(sys.exc_info()[-1].tb_lineno),
              e.with_traceback(e.__traceback__))
