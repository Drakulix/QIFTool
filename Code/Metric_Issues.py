"""
main.py passes over an object as argument of class Repository
"""


def issues(repo_obj):
    issues_obj = repo_obj.get_issues(state='all')
    for iss in issues_obj:
        print(iss.number, '\t', iss.title)
        for iss_comment in iss.get_comments():
            print('\t\t\t', iss_comment.body)
        print(iss.number, '\t', iss.title)
    return issues_obj
