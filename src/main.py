import os
import multiprocessing as mp
import configparser

from git import Repo


class Scram(object):
    def __init__(self, repo: str, user: dict, path: str = ""):
        repo = repo.strip()
        self.path = os.path.join(os.getcwd(), path.strip())
        _ = {"ssh": "", "name": "nobody", "email": "nobody@mail.com"}
        _.update(user)
        user = _

        if not os.path.isfile(user["ssh"]):
            raise Exception(
                f'Missing SSH key file: {user["ssh"]}\n'
                "Please generate a new SSH key and add it to your GitHub account.\n"
                "https://help.github.com/en/github/authenticating-to-github/generating-a-new-ssh-key-and-adding-it-to-the-ssh-agent"
            )

        os.environ["GIT_SSH"] = user["ssh"]

        if os.path.isdir(self.path) and os.listdir(self.path):
            self.repo = Repo(self.path)
            print(
                f'Fetching updates for : {os.path.basename(self.path[:-1]):19} Diff : {self.repo.git.pull("origin", "main")}\n'
            )
        else:
            if not os.path.exists(self.path):
                os.makedirs(self.path)
            print(
                f"Cloning repository: {repo} to {self.path}"
            )  # The added print statement
            self.repo = Repo.clone_from(repo, self.path, env={"GIT_SSH": user["ssh"]})
            self.repo.config_writer().set_value("user", "name", user["name"]).release()
            self.repo.config_writer().set_value(
                "user", "email", user["email"]
            ).release()

    def commit(self, branch: str = "main", message: str = "Auto commit"):
        has_changes = False
        for file in self.repo.untracked_files:
            print(
                f"Adding untracked file : {file} {os.path.basename(self.path[:-1])}\n"
            )
            self.repo.git.add(file)
            has_changes = True

        if self.repo.is_dirty():
            for file in self.repo.git.diff(None, name_only=True).split("\n"):
                if file == "":
                    continue
                print(
                    f"Adding modified file : {file} {os.path.basename(self.path[:-1])}\n"
                )
                self.repo.git.add(file)
                has_changes = True

        return has_changes

    @staticmethod
    def remote_repos(output_queue, input_queue, remote_repo, path_repo, user_config):
        repository = Scram(repo=remote_repo, user=user_config, path=path_repo)
        if repository.commit():
            output_queue.put(
                f"\nINPUT: Write commit msg for , {os.path.basename(path_repo.rstrip(os.sep))} = "
            )
            result = input_queue.get()
            repository.repo.git.commit("-m", result)
            repository.repo.git.push("origin", "main")
        output_queue.put("DONE")

    @staticmethod
    def run():
        process = configparser.ConfigParser()
        __location__ = os.path.realpath(
            os.path.join(os.getcwd(), os.path.dirname(__file__))
        )
        process.read(os.path.join(__location__, "./static/repos.ini"))

        # Read user config here and pass it to the remote_repos
        user = configparser.ConfigParser()
        user.read(os.path.join(__location__, "./static/user.ini"))
        user_config = dict(user.items("user_id"))

        processes = []
        input_queues = []
        output_queues = []

        # Start processes for each repo
        for i, name in enumerate(process):
            if name == "DEFAULT":
                continue
            iq = mp.Queue()
            oq = mp.Queue()
            input_queues.append(iq)
            output_queues.append(oq)

            p = mp.Process(
                target=Scram.remote_repos,
                args=(
                    oq,
                    iq,
                    process.get(name, "repo"),
                    process.get(name, "path"),
                    user_config,
                ),
            )
            p.start()
            processes.append(p)

        while processes:
            # Monitor output queues
            for i, oq in enumerate(output_queues):
                while not oq.empty():
                    req = oq.get()
                    if "INPUT" in req:
                        res = input(req.split(":")[1])
                        input_queues[i].put(res)
                    elif "DONE" in req:
                        processes[i].join()  # Make sure process has finished
                        processes.pop(i)
                        input_queues.pop(i)
                        output_queues.pop(i)
                        break
                    else:
                        print(req)

        print("\nCompleted all updates")


if __name__ == "__main__":
    Scram.run()
