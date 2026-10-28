# Lessons Learned

---

## Failure 1: Cowrie would not start from the wrong folder

### What I ran

I turned on the vm and logged in as my main user `zyphex`(me) which have sudo privileges. Then I switched with `sudo -su cowrie` and ran `source ~/my-honeypot/cowrie-env/bin/activate` and the prompt changed. Then I ran `cowrie start` from `/home/zyphex`.

### Error

`PermissionError: (Errno 13) Permission denied: 'etc/cowrie.cfg'`

### Why it failed

I never did `cd ~/my-honeypot` and I was in the wrong directory. `sudo -su cowrie` opens a cowrie shell but it keeps me in the folder I was in. The folder was `/home/zyphex`. Its permissions are `drwx------`. The `d` means it is a directory. The owner `zyphex` has read, write and execute. The group and others have no permission. A dash means that permission is off. The cowrie user is not the owner and not in the group so it counts as others. On a folder `x` means permission to enter it. Without `x` cowrie cannot even look inside. That is why it showed Permission denied. Cowrie needs the `etc` and `var` folders to run. The `etc` folder has all the configuration and settings of cowrie like the `/etc` on a normal system. The `var` folder has the logs.

The error names `etc/cowrie.cfg` because the cowrie settings live there. The path is short with no full path in front. So Cowrie looks for it inside the folder I am standing in. It only works from `~/my-honeypot` because `cowrie init` made `etc` and `var` there.

### Fix

`cd ~/my-honeypot`

`sudo su - cowrie` changes me to `/home/cowrie`. `sudo -su cowrie` does not. It just opens the prompt in `/home/zyphex`.

The path `source ~/my-honeypot/cowrie-env/bin/activate` works from any folder. A short path like `source cowrie-env/bin/activate` only works if I am already inside `my-honeypot`.

Cowrie started because I switched to the right folder that has the cowrie things in it. I typed `cowrie start` command which started it and `cowrie status` command printed `cowrie is running (pid:1016)`. `cowrie stop` said `stopping cowrie....` and then status said `cowrie is not running`.

---

## Failure 2: Cowrie would not start as root

### What I ran

I opened a root shell with `sudo -i`. I activated the venv with the full path `/home/cowrie/my-honeypot/cowrie-env/bin/activate` and went to `/home/cowrie/my-honeypot`. Then I ran `cowrie start`.

### Error

`ERROR: You must not run cowrie as root!`

### Why it failed

Cowrie checks which user is running it. If the user is root it stops on purpose. If an attacker breaks out of the fake shell, he gets the rights of the user running Cowrie. If that is root, he is the owner of everything in the VM and can do whatever he wants. That is the worst nightmare for a SOC team.

### Fix

I run Cowrie only as the `cowrie` user.

### Side problem I hit on the way

The first `source` command failed with `No such file or directory`. I typed the wrong venv folder name. It is `cowrie-env` and I left out `-env`. Then I put `~/` in front of a full path and bash looked in `/root/home/...`. A full path starts with `/` and needs no `~` in front. `~` means the home of whoever I am right now. As root that is `/root`, not `/home/cowrie`.

---

## Failure 3: Cowrie would not start with a broken config

### What I ran

I went to `/home/cowrie/my-honeypot` and made a backup of `etc/cowrie.cfg` with the `cp` command, so I could restore it if anything went wrong. I confirmed the backup with `ls -l`. Then I added a bad line at the end of the file with `echo` and `>>`. The line was `broken by zyphex`. I checked the last 3 lines with `tail` to confirm that it really changed. Then I ran `cowrie start` and saved the output to `out.txt`.

### Error

`configparser.ParsingError: Source contains parsing errors: 'etc/cowrie.cfg'`. Python also printed the bad line, line 1415. The last line of the output was: `twistd: Unknown command: cowrie`

### Why it failed

Cowrie did not start. Nothing was written to `cowrie.log`. The real error was only in `out.txt`. My first tries with `head` and `tail` missed it. Saving the whole output to a file and using `grep` found it.

The error chain was:

1. Bad line in the config.
2. `ParsingError`.
3. The cowrie plugin fails to load.
4. `twistd: Unknown command: cowrie`.

"Unknown command: cowrie" is only the symptom. The `ParsingError` is the cause. I proved it because the same `cowrie start` worked with a good config.

### Fix

I restored the backup with `cp` and ran `cowrie start` again. It worked. `grep -c` showed 0 bad lines left.

---

---

## Incident 1: I typed my real password at the Cowrie prompt

### What I ran

I logged in as `zyphex` and switched to the `cowrie` user. I initialized Cowrie and ran it on port 2222. Then I tested it with SSH to port 2222.

### What went wrong

When it asked me to type the password, I entered the real password of my `zyphex` account, the one that is in the sudoers file. After a minute I realized that I made a mistake. I stopped Cowrie and went to check the files. I found my password in `cowrie.json`.

### Fix

I cleaned all the files to clear the record. I also checked my password and it is fine.

### Lesson

Cowrie logs every password it sees. I never write my password or a hint of it in the repo.
