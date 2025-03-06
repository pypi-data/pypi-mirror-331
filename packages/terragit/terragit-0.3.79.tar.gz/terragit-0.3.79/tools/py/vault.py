import os
from argparse import ArgumentParser

import requests

try:
    from tqdm import tqdm
except ModuleNotFoundError:
    os.system(
        "pip install tqdm > /dev/null 2>&1 || pip install tqdm --break-system-packages"
    )
    from tqdm import tqdm


def export_env_vars_from_vault(path):
    VAULT_TOKEN = os.getenv("VAULT_TOKEN")
    VAULT_ADDR = "https://vault.allence.cloud"
    headers = {"X-Vault-Token": VAULT_TOKEN}
    url = f"{VAULT_ADDR}/v1/{str(path)}"
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()["data"]["data"]
        with open(output_file, "a") as script_file:
            for key, value in data.items():
                os.environ[key] = value
                script_file.write(f"export {key}='{value}'\n")


def get_secrets_path(input_str):
    l = []
    parts = input_str.strip("/").split("/")
    if "builds" in parts:
        index = parts.index("builds")
        for i in range(index + 1, len(parts)):
            os.environ[f"{chr(ord('A') + i - index - 1)}"] = parts[i]
            l.append(parts[i])
    return l


if __name__ == "__main__":
    output_file = "env_vars.sh"
    input_str = os.getenv("CI_PROJECT_DIR")
    result = get_secrets_path(input_str)

    parser = ArgumentParser(description="Get Vault variables path from user")
    parser.add_argument(
        "-p",
        "--path",
        default="variables",
        type=str,
        help="set vault variables path",
    )
    args = parser.parse_args()

    if len(result) >= 2:
        char_list = [chr(65 + i) for i in range(len(result))]  # Generates ['A', 'B']
        base_path = f"{os.environ.get(char_list[0])}/data"
        path_parent_group = f"{os.environ.get(char_list[0])}/data/{args.path}"
        export_env_vars_from_vault(path_parent_group)
        print(f"\nExtracting variables from base path: {path_parent_group}")
        for var in tqdm(char_list[1:]):
            base_path += f"/{os.environ.get(var)}"
            if var == char_list[len(char_list) - 1]:
                export_env_vars_from_vault(base_path)
            else:
                export_env_vars_from_vault(f"{base_path}/{args.path}")
