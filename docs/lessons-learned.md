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

---

---

---

## Incident 2: `rm` with `&&` and a missing command

### What I ran

I was cleaning my test logs so I typed `rm` with the path to `cowrie.json*`, then `&&`, then the path to `cowrie.log*` without another `rm` in front of it because I thought `rm` would carry over to the second part and I put the `*` at the end of both names so that any other files I might have missed would be cleared too.

### Error

`Permission denied`

### Why it failed

`&&` joins two full commands so the second part needs its own command name and mine was only a file path which made bash treat the first file that `cowrie.log*` matched as a program to run and since a log file is not executable it said `Permission denied`.

### Fix

`rm` takes both paths in one command with a space between them, like `rm cowrie.json* cowrie.log*`, and I use `&&` only when both sides are full commands.

### Lesson

`&&` needs a command on both sides and a file name alone is not a command and because `*` can match more files than I expect I check a wildcard command before I press Enter.

---

## Failure 4: my first search found 6 download sessions and there were 50

### What I ran

I wanted to list the download servers in the CyberLab Nov 1 data. I ran `grep -c http` on `cyber_nov01_sessions.csv` and it said 6. Then I ran `grep -cE 'wget|curl|tftp'` on the same file and it said 50.

### Error

No error message. The two numbers did not match and that was the problem.

### Why it failed

Searching for `http` only finds downloads that have a full web address. About 40 of the 50 sessions had a bare `wget;` with no host after it. They looked like a bot checking if the tool exists. Some real downloads also had no `http`, like `wget -q 54.37.70.249/rp`. A bare IP has no `http://` in front of it. My first version of `extract_downloads.py` missed that host too.

### Fix

I added a second check for `wget` with a word that starts with a digit and has a slash in it. After that the host `54.37.70.249` showed up with a count of 10. The number matches the 5 `.satan` and 5 `rp` commands I saw before.

### Lesson

One search is not a proof. I count the same thing in two different ways and I trust the number only when both agree. The counts are commands and not attacks.

---

## Finding 1: I cannot look up the CyberLab IPs

### What I ran

I planned to enrich the IPs with reputation services. First I looked at the data with `head -5 data/cyber_nov01_sessions_ips.csv`.

### What I saw

The `src_ip` column does not hold IPs. Each value is a 64 character code. One code had 1610 sessions and another had 569.

### Why it matters

The data owners hid the real IPs. No reputation service knows these codes. My own lab IPs are private addresses so a lookup on them means nothing either. IP reputation does not work on any of my data.

### What I did instead

I wrote `extract_downloads.py`. It reads the commands and pulls out the host of every download. It tags each host as public, private or domain with the `ipaddress` module. The hosts are real because only the attacker IP was hidden. It writes them to a csv. It needs no internet and no account and it never opens an address.

### Result

In the Nov 1 data 50 sessions use `wget`, `curl` or `tftp`. The tool found 5 hosts. 4 are public IPs and 1 is a domain. This is a tiny sample out of about 59000 sessions so it only shows that the method works. The csv also drops the port of `103.219.112.66:8000`. That is a small loss.

### Lesson

I check what my data really holds before I plan around it. The data was pseudonymized and my first plan did not fit it. Data origin: PUBLIC DATASET, CyberLab Nov 1 2019.

## Failure 5: my first cron rule matched nothing

### What I built

A Sigma rule for cron persistence. It looked for `crontab` in the commands but skipped any session with `crontab -l`.

### What I expected

On the Nov 1 data `crontab` shows up on 1091 lines. After the filter only 1 was left. I thought the filter removed a listing habit and kept the real attacks.

### What I saw

The rule matched 0 sessions in my lab data and 0 in my synthetic data. I had already committed it before I tested it.

### Why it happened

The attacks in my lab and synthetic sessions start with `crontab -l`, then add the job with `crontab -`. My filter dropped every one of them.

### How I fixed it

I removed the `crontab -l` filter. The rule now looks for the text `crontab -` in the middle or at the end of the commands.

### Lesson

I test a rule on data where I know the answer before I commit it. A rule that matches 0 is not safe. It can mean the rule is broken.

## Failure 6: my grep count was wrong

### What I did

I tested my cron rule with grep on the sessions CSV. On the synthetic data grep found 0 matches for a command that ends with `crontab -`.

### What I saw

My checker found 12 matches on the same synthetic data.

### Why it happened

In the CSV the commands column ends with a closing quote. Grep counted that quote as part of the command. My checker reads the file with the csv module and sees the text without the quote. So grep looked for something that was not there.

### Lesson

A grep count on a CSV file can be wrong when a field ends with a quote. I check a count with the tool that reads the data the right way. Only the checker showed me the truth.

## Finding 2: my ATT&CK IDs were out of date

### What I did

I wrote the technique IDs and tactics for my first rules from memory.

### What I found

I checked them on the web. 3 of my 7 IDs or tactics were out of date. T1496 now has sub-techniques, so I use T1496.001. ATT&CK v19 split Defense Evasion into Stealth and Defense Impairment, so T1070.004 moved to Stealth. T1562.003 was revoked and replaced by T1690. I fixed rules 3, 6 and 8.

### Not checked yet

One source says ATT&CK v20 came out in October 2026. I did not check if it changed any of my IDs. I also did not verify the Sigma tag spellings for the two new tactics.

### Lesson

I do not trust an ID from memory. I check it on the official site before it goes into a rule.

## Finding 3: 172 out of 172 does not cover everything

### What I found

My lab has 182 sessions. My truth file has 172. 10 lab sessions are not in it.

### What it means

The 172 out of 172 result covers only the sessions in my truth file. It says nothing about the other 10. I do not know why they are missing from the file.

### Lesson

When I report an accuracy number I also say how many sessions it covers and how many it leaves out.
