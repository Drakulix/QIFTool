"""
main.py passes over an object as argument of class StatsCodeFrequency
"""


def stats_code_frequency(repo_obj):
    repo_obj_scf = repo_obj.get_stats_code_frequency()
    additions = 0
    deletions = 0
    for add_del in repo_obj_scf:
        additions += add_del.additions
        deletions += add_del.deletions
        # print(add_del.additions, add_del.deletions, add_del.week)
    return additions, deletions
