# QIFTool

QIFTool or Query Issue Finder-Tool is a project created as a bachelor's thesis. 
It aims to help in the quality research field of technical debt by provoding relevant discussions regarding these debts of issues from github itself.
Although it is meant for the field of techincal debt the tool can be also be used to return all different kind of issues' topics.

## How to run the programm
1. Download the 'qiftool.py' file from the repository
2. Install all dependencies by running 'cmd'
3. Navigate to the file's location via the 'cd' command
4. Run the program by using 'python3 qiftool.py'
5. By running it for the very first time, the tool should have created a 'config.ini' file inside the tool's folder. Fill out the necessary parameters following the \ref to config.ini file
6. With the 'config.file' filled out run the programm again just like in step 4
7. The tool should now operate properly and follow the program's instructions for further details

## Configuration file - config.ini
This file is created by running the program for the very first time. It is used to give the user a space to use their own parameters used by the tool.
The file contains three sections for the user to fill out.

1. [DEFAULT] - this section contains the path for the database and downloaded repositories to be stored in. As the name suggests these contain default values with 'current' meaning that both the database and the repositories (inside an additonal folder) will be stored in the same location as the 'qiftool.py'.
These can be changed by providiung a valid path on your machine. <br/>e.g path_of_database = current >>> path_of_database = ~/Desktop <br/>BUG: right now they only create a set path with the 'qiftool.py''s location as a pivot.

2. [credentials] - this section contains the corresponding credentials necessary to run the used APIs<br/>
github_api_key -  
<ol type="a">
  <li>register on github</li>
  <li> [use this link](https://github.com/settings/tokens) and click on 'generate new token' to create a new key</li>
  <li>paste the key as a parameter</li>
  <li>e.g github_api_key = '' >>> github_api_key = randomnumbersandlettersinlowercaseandnoquotationsmarks</li>
</ol>

google_api_key- 
<ol type="a">
  <li>register on google</li>
  <li> [use this link](https://developers.google.com/custom-search/v1/introduction) and click on 'Get a Key' to create a new key</li>
  <li/>either choose a project or create a new one</li>
  <li>follow the instructions and paste the key as a parameter</li>
  <li>e.g google_api_key = '' >>> google_api_key = randomnumbersandlettersinupperandlowercaseandnoquotationsmarks</li>
</ol>

google_cse_id- 
<ol type="a">
  <li>login to the google account created in the prior step</li>
  <li> [use this link](https://cse.google.com/cse/all) and click on the project you used to create the google key with</li>
  <li/>look for the 'Search engine ID' and paste the ID as a parameter</li>
  <li>e.g google_cse_id = '' >>> google_cse_id = randomnumbersandlettersinlowercaseandnoquotationsmarks</li>
</ol>

3. [metrics] - this section contains the metrics used by the tool to determine what topics are looked for. Note that the metrics are seen as verundet.
keywords - put in significant keywords that should be found in the issues' content by spacing them using tabs
e.g keywords = '' >>> keywords = technical debt refactor  rewrite
note that keywords like 'technical debt' are seen as one since they are spaced using a simple whitespace

issue_comments - put in a number. this will only show issues that have at least this number amount of comments
e.g issue_comments = '' >>> issue_comments = 5

repo_contributors - put in a number. this will only show issues that have at least this number amount of contributors in their whole repository
e.g repo_contributors = '' >>> repo_contributors = 250

