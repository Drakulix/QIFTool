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

## How to run the program <a name="how_to"/>


1. Download the `qiftool.py`  and `requirements.txt` files from the repository
1. Place both files in the desired location
1. Open the terminal and navigate to the files’ location
1. Install all dependencies by running `pip3 install -r /path/to/requirements.txt` or just `pip install -r /path/to/requirements.txt` depending on your python version
1. Run the program by using `python3 qiftool.py`
1. By running it for the very first time the tool should have created a `config.ini` file inside the tool’s folder. Fill out the necessary parameters following the instructions in [Configuration file](#config)
1. With the `config.file` filled out run the programm again just like in step 5
1. The tool should now operate properly and an interactive mode will be seen.
Follow [Interactive mode](#interactive_mode) for further instructions

## Configuration file <a name="config"/>

This file is created by running the program for the very first time. It is used to give
the user a space to use their own parameters used by the tool. The file contains three
sections for the user to fill out.

```python
[DEFAULT]
  path_of_database = current
  path_of_download = current
[credentials]
  github_api_key = randomnumberandlettersinlowercase
  google_api_key = randomlettersinuppderandlowercaseandsymbols
  google_cse_id = randomleterandnumbersinlowercase
[metrics]
  keywords = technical debt refactor rewrite
  issue_comments = 5
  repo_contributors = 50
```
1. `[DEFAULT]` this section contains the path for the database and downloaded repositories to be stored in. The user is able to create their own path with the location of the ’qiftool.py”s as a pivot. These can be changed by providiung a valid path on your machine.

1. `[credentials]` this section contains the corresponding credentials necessary to run the used APIs
    1. `[github_api_key]`
        1. register on github
        1. [use this link](https://github.com/settings/tokens) and click on ’generate new token’ to create a new key
        1. paste the key as a parameter
    1. `[google_api_key]`
        1. register on google
        1. [use this link](https://developers.google.com/custom-search/v1/introduction) and click on ’Get a Key’ to create a new key
        1. either choose a project or create a new one
        1. follow the instructions and paste the key as a parameter
    1. `[google_cse_id]`
        1. login to the google account created in the prior step
        1. [use this link](https://cse.google.com/cse/all) and click on the project you used to create the google key with
        1. look for the ’Search engine ID’ and paste the ID as a parameter
1. `[metrics]` These contain the metrics used for the google search. For further details for understanding each metric please refer to the tables in [SQLite Database](#sqlite).
    1. `[keywords]` - string of characters with each element separated by a tabulator. Note that the keywords will be used to find patterns that exactly match. So ’refactor’ will find ’refactoring’ but not vice versa. In addition the keywords are connected with a logical and.
    1. `[issue_comments]` - an integer over 0. It will show issues that have at least the amount of comments set in this metric. So 5 will yield issues with 5 or more comments.
    1. `[repo_contributors]` - an integer over 0. It will show issues that have at least the amount of contributors working on the corresponding repository. So 5 will yield issues with more 5 or more contributors working on its repository.

## Interactive Mode <a name="interactive_mode"/>

Once you successfully configered the configuration file in 3 an interactive mode will be seen on the console after running it. In this mode the program will wait for the user to simply type a desired function into the console and confirming it by pressing enter. After being done with a function the program goes back to displaying the interactive mode as it loops itself around it.

![interactive mode](/interactive_mode_large.png)

### Functions

Function | Description
---------|------------
sq | (search query) - start the google search. The metrics set in the configuration file will be used to determine what results will be found and shown.
sn<tab><issue_id><tab><message> | (set notes) - sets a note for a certain issue inside the database issue_id - a string of numbers. Found within the issue_id field in either the ouput or database of the issue. message - a string of characters that will be inserted into the notes field inside the database.
