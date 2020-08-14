"""
main.py passes over an object as argument of class Repository
"""


def contributors(repo_obj):
    con_obj = repo_obj.get_contributors().totalCount
    return con_obj

