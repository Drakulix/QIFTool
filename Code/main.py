"""
installed packages: apt install cURL
                    apt install python3-pip
                    pip3 install PyGithub
"""

import urllib.request, json
from github import Github
import Metric_StatsCodeFrequency    # metric file for StatsCodeFrequency
import Metric_Contributors          # metric file for Contributors
import Metric_Issues                # metric file for Issues
import Metric_Commits               # metric file for Commits

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
    repo = auth.search_repositories(query='ytmdesktop')
    repo_first = repo[0]
    print(code_pattern(repo_first, auth))
    print(auth.get_rate_limit().core.remaining)


def code_pattern(repo_obj, auth):
    # print(repo_obj.get_contents("main.js").decoded_content)
    print(repo_obj.contents_url[:-7])
    with urllib.request.urlopen(repo_obj.contents_url[:-7]) as url:
        json_obj = json.load(url)
        for data in json_obj:
            # if data['path'][-3:] == *repos language* dann gehe hinein und schaue weiter
            print(data["path"][-3:])



# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    search()
