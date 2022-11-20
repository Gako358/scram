# scram
A "A simple git wrapper to help you keep your git history clean" 
Update local and remote git repositories easy

## Installation

*For nix users*
run: `nix run`

### Other systems

src/static/repos.ini
```
[nameofrepo]
repo = git@github.com:username/reponame.git
path = /home/user/location/for/repo

[nameofother]
repo = git@github.com:username/reponame.git
path = /home/user/location/for/repo
```

src/static/user.ini
```
[user_id]
ssh     = /home/user/path/to/scram/src/static/git.ssh
name    = git username
email   = git email
```

### Create a file
inside src/static create a new file, `git.ssh`
```
#!/usr/bin/env bash
ssh -i /home/user/.ssh/id_rsa -oIdentitiesOnly=yes -oStrictHostKeyChecking=no -oUserKnownHostsFile=/dev/null "$@"
```
run: `chmod +x git.ssh` after creating the file and adding the content.
