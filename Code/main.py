"""
installed packages: apt install cURL
                    apt install python3-pip
                    pip3 install PyGithub
"""

from github import Github

# authentication of REST API v3

auth = Github("c2c1d13983cbb8c1d9ce7845c20d7937ba7c25a0")


def testhub():
    repo = auth.get_repo("PyGithub/PyGithub")
    print(repo.get_topics())


def search():
    repo = auth.search_repositories(query='ytmdesktop')
    #repo = auth.search_repositories(query='youtube')
    repo0 = repo[0]
    compurl = repo0.compare('master@{all}', 'master')
    scf = repo0.get_stats_code_frequency()

    diff = compurl.get__repr__(compurl.raw_data)
    scf1 = scf[0].deletions
    additions = 0
    deletions = 0
    for add_del in scf:
        additions += add_del.additions
        deletions += add_del.deletions
        print(add_del.additions, add_del.deletions, add_del.week, '\n')
    print(additions, deletions)

    print(repo0, scf1, len(scf), diff)


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    search()
