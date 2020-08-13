"""
installed packages: apt install cURL
                    apt install python3-pip
                    pip3 install PyGithub
"""

from github import Github
import Metric_StatsCodeFrequency    # metric file for StatsCodeFrequency
import Metric_Contributors          # metric file for Contributors

# authentication of REST API v3

auth = Github("c2c1d13983cbb8c1d9ce7845c20d7937ba7c25a0")


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
    repo = auth.search_repositories(query='nuclear')
    repo_first = repo[0]
    print(repo_first.full_name, '\t', repo_first.get_issues(state='all')[1].get_comments()[0].body)
    print(auth.get_rate_limit())


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    search()
