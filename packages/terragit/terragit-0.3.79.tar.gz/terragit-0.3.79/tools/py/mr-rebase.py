import os

import requests

gitlab_token = os.environ["gitlab_token"]
headers = {"PRIVATE-TOKEN": gitlab_token}
project_id = os.environ["CI_PROJECT_ID"]
base_url = "https://gitlab.allence.cloud/api/v4/projects/" + str(project_id)

req_mrs = requests.get(
    f"{base_url}/merge_requests?state=opened", headers=headers
).json()

for mr in req_mrs:
    request = requests.put(
        f"{base_url}/merge_requests/{mr['iid']}/rebase", headers=headers
    )
    print(f"MR {mr['iid']} is rebased with status: {request.status_code}")
    last_commit = requests.get(
        f"{base_url}/repository/commits/{mr['sha']}", headers=headers
    ).json()
    print(last_commit)
