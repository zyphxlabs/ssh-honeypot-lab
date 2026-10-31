# Attack scenarios

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
