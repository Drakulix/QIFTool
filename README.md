# QIFTool

QIFTool  or  Query  Issue  Finder-Tool  is  a  project  created  as  a  bachelor’s  thesis.It  aims to  help  in the  quality  research field  of technical  debt  by provoding  relevant discussions regarding these debts. The discussion are presented in form of issues from github.  The tool uses keywords and additional metrics to find potentially interesting issues. Although it is meant for the field of techincal debt the tool can be also be used to return all different kind of issues’ topics.

The documentation can also be found here: [Documentation](QIFTool___Documentation.pdf)


## Table of contents

- [Workflow](#workflow)
- [How to run the program](#how_to)
- [Configuration file](#config)
- [Interactive mode](#interactive_mode)
  - [Functions](#im_functions)
- [SQLite - Database](#sqlite)
  - [Repositories](#sqlite_repositories)
  - [Issues](#sqlite_issues)
- [Expanding the tool](#expanding)
  - [Metrics](#ex_metrics)
  - [SQLite commands](#ex_sqlite)

## Workflow

QIFTool is written in Python(3.8) and uses [Google’s Custom Search JSON API](https://developers.google.com/custom-search/v1/overview) in conjunction with [Google’s Custom Search Engine](https://developers.google.com/custom-search) to filter issues directly on Github. Keywords will be read out of a configuration file to determine which issues should be prefiltered. All prefiltered issues found by the engine will be inserted for research and caching purposes into a SQLite database. Afterwards it uses the official Github API ([PyGithub](https://pygithub.readthedocs.io/en/latest/index.html)) to look through the available pieces of metainformation inside each found issue and compares them to the other metrics set in the configuration file to only show the issues that match the requirements.

## How to run the program

1. Download the `qiftool.py`  and `requirements.txt` files from the repository
1. Place both files in the desired location
1. Open the terminal and navigate to the files’ location
1. Install all dependencies by running `pip3 install -r /path/to/requirements.txt` or just `pip install -r /path/to/requirements.txt` depending on your python version
1. Run the program by using `python3 qiftool.py`
1. By running it for the very first time the tool should have created a `config.ini` file inside the tool’s folder. Fill out the necessary parameters following the instructions in [Configuration file](#config)
1. With the `config.file` filled out run the programm again just like in step 5
1. The tool should now operate properly and an interactive mode will be seen.
Follow [Interactive mode](#interactive_mode) for further instructions

## Configuration file

This file is created by running the program for the very first time. It is used to give
the user a space to use their own parameters used by the tool. The file contains three
sections for the user to fill out.

`[DEFAULT]
  path_of_database = current
  path_of_download = current
[credentials]
  github_api_key = randomnumberandlettersinlowercase
  google_api_key = randomlettersinuppderandlowercaseandsymbols
  google_cse_id = randomleterandnumbersinlowercase
[metrics]
  keywords = technical debt refactor rewrite
  issue_comments = 5
  repo_contributors = 50`
