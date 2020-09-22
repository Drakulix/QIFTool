from googleapiclient.discovery import build
from github import Github

api_key = "api_key"
cse_id = "cse_di"


def google_search(query, api_key, cse_id, start, **kwargs):
    service = build(serviceName='customsearch', version='v1', developerKey=api_key)
    result = service.cse().list(q=query, cx=cse_id, exactTerms='comments', num=10, start=start, **kwargs).execute()
    return result


def init():
    auth = Github("c2c1d13983cbb8c1d9ce7845c20d7937ba7c25a0", per_page=100)
    return auth


# ---------------------------------------------------------------------------------------------------------------------#


class RepoObj:
    def __init__(self, id, url, html_url, creator, name, size):
        self.id = id
        self.url = url
        self.html_url = html_url
        self.creator = creator
        self.name = name
        self.size = size
        """
        add lots of more metrics to filter by like contributors etc
        """


class IssueObj:
    def __init__(self, repo_id, id, title, number, url, html_url):
        self.repo_id = repo_id
        self.id = id
        self.title = title
        self.number = number
        self.url = url
        self.html = html_url


def page_iterator(query, api_key, cse_id):
    for offset in range(1, 100, 10):
        res_page = google_search(query=query, api_key=api_key, cse_id=cse_id, start=offset)
        for res in res_page['items']:
            repo_id = int(res['pagemap']['metatags'][0]['octolytics-dimension-repository_id'])
            issue_num = int(res['link'].split('issues/')[1])

            # check ob repo und issue bereits in der datenbank vorhanden sind

            repo = auth.get_repo(repo_id)
            issue = repo.get_issue(issue_num)

            issue_obj = IssueObj(repo_id=repo.id, id=issue.id, title=issue.title, number=issue.number, url=issue.url,
                                 html_url=issue.html_url)
            repo_obj = RepoObj(id=repo.id, url=repo.url, html_url=repo.html_url, creator=repo.full_name.split('/')[0],
                               name=repo.full_name.split('/')[1], size=repo.size)



            print(offset, issue)


# ---------------------------------------------------------------------------------------------------------------------#

#
# site:github.com inurl:issues OR inurl:pulls intext:"technical debt" intext:refactoring intext:cost
if __name__ == '__main__':
    auth = init()
    page_iterator('inurl:issues intext:"technical debt" intext:refactoring intext:cost', api_key, cse_id)

