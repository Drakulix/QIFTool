"""
main.py passes over an object as argument of class Repository
"""


def contributors_count(repo_obj):
    repo_obj_con = repo_obj.get_contributors().totalCount
    return repo_obj_con
