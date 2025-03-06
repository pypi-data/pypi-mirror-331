import shutil
from terragit.terragrunt import *  # type: ignore
import gitlab


class bcolors:
    HEADER = "\033[95m"
    OKBLUE = "\033[94m"
    OKCYAN = "\033[96m"
    OKGREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"


pathList = []
failedloglist = []
logsFolder = ""
printLogs = False


class mr_changes:
    def __init__(self):
        self.bcolor = bcolors

    def plan_ci(self):
        global printLogs
        git_url = "https://gitlab.com"
        if len(sys.argv) > 1:
            git_url = sys.argv[1]
        logsFolder = pathlib.Path("logs").absolute().as_posix()
        failedlogsFolder = pathlib.Path("failedlogs").absolute().as_posix()
        idMr = str(os.environ.get("CI_MERGE_REQUEST_IID"))
        idProject = int(str(os.environ.get("CI_PROJECT_ID")))
        gitlab_token = str(os.environ.get("gitlab_token"))

        ci_commit_title = str(os.environ.get("CI_COMMIT_TITLE"))

        gl = gitlab.Gitlab(
            url="https://gitlab.com", private_token=gitlab_token
        )

        project = gl.projects.get(idProject)

        mr = project.mergerequests.get(idMr)
        folderList = []
        mrchange = mr.changes()
        changes = mrchange["changes"]  # type: ignore

        if len(changes) == 0:
            if not isdir(pathlib.Path(ci_commit_title).absolute().as_posix()):
                print(
                    bcolors.FAIL + ci_commit_title + " is not valid path" + bcolors.ENDC
                )
                failedloglist.append(ci_commit_title)
            else:
                ci_mr_titlePath = pathlib.Path(ci_commit_title).absolute().as_posix()
                printLogs = True
                self.tg_plan(ci_mr_titlePath, logsFolder, printLogs)
        else:
            for change in changes:
                newPath = change["new_path"]
                if not ("live/") in newPath:
                    print(
                        pathlib.Path(newPath).absolute().as_posix()
                        + bcolors.WARNING
                        + " OUT of SCOPE"
                        + bcolors.ENDC
                    )
                else:
                    pathh = pathlib.Path(newPath).parent.absolute().as_posix()
                    folderList.append(pathh)
        mylist = list(dict.fromkeys(folderList))
        if os.environ.get("TG_OUTPUT_LIMIT"):
            TG_OUTPUT_LIMIT = int(str(os.environ.get("TG_OUTPUT_LIMIT")))
        else:
            TG_OUTPUT_LIMIT = 3
        if len(mylist) <= TG_OUTPUT_LIMIT:
            printLogs = True
        for path in mylist:
            if isdir(path):
                self.tg_plan(path, logsFolder, printLogs)
        if failedloglist:
            for message in failedloglist:
                logfileName = message.split("live/")[1].replace("/", "_")
                os.chdir(failedlogsFolder)
                shutil.move(
                    logsFolder + "/" + logfileName + ".log",
                    "failed_" + logfileName + ".log",
                )
            sys.exit(1)

    def tg_plan(self, path, logsFolder, printLogs):
        if path in pathList:
            return
        else:
            pathList.append(path)
            only_tf_files = [
                f
                for f in sorted(listdir(path))
                if not isdir(join(path, f)) and f.endswith(".tf")
            ]
            if len(only_tf_files) == 0:
                onlyDirectories = [
                    d
                    for d in sorted(listdir(path))
                    if isdir(join(path, d))
                    and d != ".terraform"
                    and d != ".terragrunt-cache"
                ]
                if len(onlyDirectories) > 0:
                    for i in range(0, len(onlyDirectories)):
                        self.tg_plan(
                            path + "/" + onlyDirectories[i], logsFolder, printLogs
                        )
                return
            os.chdir(path)
            logfileName = path.split("live/")[1].replace("/", "_")

            state_list = (
                "terragrunt plan -no-color 2>&1 | tee "
                + logsFolder
                + "/"
                + logfileName
                + ".log"
            )
            popen = subprocess.Popen(
                state_list, stdout=subprocess.PIPE, shell=True, encoding="utf8"
            )
            lines = popen.stdout.readlines()  # type: ignore
            popen.stdout.close()  # type: ignore
            print(bcolors.OKBLUE + path + ":" + bcolors.ENDC)
            for line in lines:
                if printLogs:
                    print(line)
                else:
                    if "will be updated in-place" in line:
                        print(line.replace("\n", ""))
                    if "will be created" in line:
                        print(line.replace("\n", ""))
                    if "must be replaced" in line:
                        print(line.replace("\n", ""))

                        lint = lines[(lines.index(line)) : (len(lines))]
                        lin = lint[0 : (lint.index("\n"))]
                        for l in lin:
                            if "forces replacement" in l:
                                print(l.replace("\n", ""))
                                print(lin[(lin.index(l)) + 1])
                    if "will be destroyed" in line:
                        print(line.replace("\n", ""))
                    if line.startswith("Error"):
                        lint = lines[(lines.index(line)) : (len(lines))]
                        for l in lint:
                            print(l.replace("\n", ""))
                        print(bcolors.FAIL + " COULDNT PROCESS" + bcolors.ENDC)
                        failedloglist.append(path)
                        return
                if "No changes. Infrastructure is up-to-date." in line:
                    print(
                        bcolors.OKGREEN
                        + "  : No changes. Infrastructure is up-to-date."
                        + bcolors.ENDC
                    )
                    return
                if "Plan:" in line:
                    print(bcolors.WARNING + line + bcolors.ENDC)
                    return
            print(bcolors.FAIL + " COULDNT PROCESS" + bcolors.ENDC)
            failedloglist.append(path)
