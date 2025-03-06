# terragit

terragit is a Python package allow access to the GitLab server API , in order to perform terraform/git operations

#### precondition
install python-gitlab package:
``pip install python-gitlab``
#### Installation
``pip install terragit``
#### Start-up 
#### terragit config

before using any of the bellow commands you will need to run terragit config command to initialise terragit:\
you will be asked to enter the following information : 

gitlab_token : gitlab token allows you to access remotely to your gitlab account\
keybase : terragit use keybase mainly to decrypt IAM credentials\
gitlab_user : your gitlab username

after running terragit config successfully it will create a file called ./terragit in your home directory\
after that you can run the commands bellow

##### terragit {switch}

.Allows you to switch between groups/project present in .terragit file and use the project/group information \
when executing some terragit commands like terragit plan or apply in this case the command is going to use IAM account credentials \
.Creates a ~/.terragit_profile file with  corresponding environment variables
{-g} {--group_id} : group/project id of the group/project that you want to switch to
{-gn} {--group_name} : group/project name of the group/project that you want to switch to
.Please run source ~/.terragit_profile when success
.Add aws profiles to ~/.aws/credentials file (you should have aws-cli installed)
##### terragit {compare}
Allows you to compare two infrastructures by giving source and destination local tf states in json format.\
.Creates terragit-compare folder, where you can see:\
    
State_list.csv file: comparison between 2 infrastructure different states \
S_list{State_name}.csv: Detailed properties' comparison of each common state \
{-I}: local path for source infra \
{-N}: local path for destination infra
##### terragit {validate}
Allows you to validate a terraform module by giving the local path or project id and path of the target
folder from content root \ 
{-p}: local path \
{-P}: path of the target folder from content root in case of remote project \
{-prId}: git/gitlab  project id 
##### terragit {plan|validate|changes|apply|output}

you must switch to a project before using this command if you intend to use it with AWS services  \
in order to get IAM credentials from .terragit file 

{-d} {--destroy}: to indicate if it is destroy  make plan a plan destroy and make apply a destroy\
{-c} {--commit_id}: commit id\
{-mrid} { --mr_id}: merge id\
{-dir} {--directory}: directory\
{-p} {--project_id}: project id\
{-v} {-verbose}: to indicate if output will exit on the console  and in log folder too\

##### terragit {docs}

{-p} {--project_id}: project id\
{-m} {--module} : for docs module\
{-l} {--live} : for live infra\
{-o} {--output} : output path : default {"./"}\

##### terragit {clone}

Allows you to clone a project or the entire projects of a specific group(projects of subgroups included),\
check if you have an aws account, and if you have one, this feature is going to decrypt your credentials\
and add group information to .terragit file

{-g} {--group_id}: provide group id if you want to clone a group, if not, don't use this argument\
{-p} {--project_id}: provide project id if you want to clone a project, if not, don't use this argument\
{-ip} {--infra_project_id}: your infrastructure project id in case you are cloning a group to check if you have \
{--path}: the path to clone the project in \

##### terragit {adduser}

Using this command, you can add a user to a gitlab group or project and create an AWS account for him.\
first this command is going to check if a user exists or not in gitlab group or project.Then based \
on the search result it will either add user to repository, create AWS account for the user or do both.

{-g} {--group_id}: provide group id if you want to add user to a group, if not, don't use this argument\
{-p} {--project_id}: provide project id if you want to add user to a project, if not, don't use this argument\
{-ip} {--gitlab_username}: gitlab username of the user you want to add \
{-lvl} {--access_level} : access level of the user you want to add, possible values (guest, reporter, developer, maintainer or owner)\


##### terragit {clean}

Allows you to delete old merge requests, branches or both of a project or group.
{-g} {--group_id}: provide group id if you want to clean a group. if not, don't use this argument\
{-p} {--project_id}: provide project id if you want to clean a project. if not, don't use this argument\
{-t} {--time}: provide time(number of days) to delete branches/merge-requests older then time provided \
Example :if you provide 10 it will delete all branches/merge-requests older then 10 days. \
provide 0 if you want to delete all branches/merge-requests\
{-mr} {--mr}: set it to true if you want to delete Merge requests else false \
{-b} {--branches}: set it to true if you want to delete branches else false \

##### terragit {list}

list projects/groups in .terragit file 

##### terragit {currentProject}

get selected project/group (you can select project/group using terragit switch command)  

##### terragit {status}

this command executes terragit status on all git projects inside a given directory

{-dir} {--directory}: directory\

##### terragit {project-list}

Allows you to list all groups in clients-acp group and clone the entire projects of a specific group

{-dir} {--directory}: directory where to make the clone \
