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


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    testhub()
