"""
installed packages: apt install cURL
                    apt install python3-pip
                    pip3 install PyGithub
"""

from github import Github
import Metric_StatsCodeFrequency    # metric file for StatsCodeFrequency
import Metric_Contributors          # metric file for Contributors
import Metric_Issues                # metric file for Issues

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
    print(issues(repo_first))
    print(auth.get_rate_limit())

def issues(repo_obj):
    issues_obj = repo_obj.get_issues(state='all')
    for iss in issues_obj:
        print(iss.number, '\t', iss.title)
        for iss_comment in iss.get_comments():
            print('\t\t\t', iss_comment.body)
        print(iss.number, '\t', iss.title)
    return issues_obj

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    search()
