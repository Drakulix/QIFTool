"""
installed packages: apt install cURL
                    apt install python3-pip
                    pip3 install PyGithub
"""

import urllib.request
import json
import time
from github import Github
import Metric_StatsCodeFrequency  # metric file for StatsCodeFrequency
import Metric_Contributors  # metric file for Contributors
import Metric_Issues  # metric file for Issues
import Metric_Commits  # metric file for Commits

# authentication of REST API v3

auth = Github("c2c1d13983cbb8c1d9ce7845c20d7937ba7c25a0", per_page=1000)

file = open('database.txt', 'a')


def testhub():
    repo = auth.get_repo("PyGithub/PyGithub")
    print(repo.get_topics())


def search():
    """
    repo = auth.search_repositories(query='spotify')
    for i in range(0, 15):
        print(Metric_Contributors.contributors_count(repo[i]), '\t',
              Metric_StatsCodeFrequency.stats_code_frequency(repo[i]),
              '\t', repo[i].full_name,
              repo[i].get_issues_events()[0].issue.get_comments())
    """
    # repo = auth.search_repositories(query='ytmdesktop')
    print(auth.get_rate_limit().search)
    print(auth.get_rate_limit())
    print('\n')
    repo = auth.search_repositories(query='size:500..1000')
    counter = 1
    repo_list = []
    for rep in repo:
        print(counter, '- remaining: ', auth.get_rate_limit().search.remaining, 'limit: ',
              auth.get_rate_limit().search.limit, rep.name)
        repo_list.append(rep.name)
        counter += 1
        if counter % 100 == 0:
            print(auth.get_rate_limit())
            break

    repo2 = auth.search_repositories(query='size:500..1000', order='asc')
    boolean = False
    for rep2 in repo2:
        if rep2.name in repo_list:
            boolean = True
        else:
            boolean = False
        print(counter, '- remaining: ', auth.get_rate_limit().search.remaining, 'limit: ',
              auth.get_rate_limit().search.limit, rep2.name, 'repo inside list: ', boolean)
        counter += 1
    repo_first = repo[0]


def query():
    repo_count = 0
    for i in range(1, 5):
        repo = auth.search_repositories(query='size:>500')
        for rep in repo:
            repo_count += 1
            file.write(rep.name+'\n')
            print(repo_count, rep.size, rep.name)
            if repo_count % 100 == 0:
                # time.sleep(0.5)
                print(auth.get_rate_limit().search, auth.get_rate_limit())


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    query()
