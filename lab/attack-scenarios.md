# Attack scenarios

# Attack scenarios

## Scenario 1: connect-only scan

This one happened right at the start of the lab while I was just testing the connection from my attacker VM Kali to my honeypot. I did not plan it as a scenario so I did not note the time or the command and I only found it later when I went looking in the `Cowrie log`. I think I used nc to just touch port 2222 and close it with no login and no typing but I do not remember the exact command so I am marking it as a guess.

Command I think I used:` nc -vz <vm-ip> 2222`

In the log I found session `de4f6c6abbeb` coming from my attacker VM Kali to port `2222` and it has only `2 `events. The first is the connect at`2026-10-31T00:31:18Z`in Cowrie log time and the second is the closed event about `4 milliseconds `later. The closed event itself says the connection was lost after `2 milliseconds`. There is no client version event and no login and no command so nothing happened except the knock on the door. I think this fits nc because a real ssh client would send its version first but that is only my guess and I have not checked it.

I did not note the true UTC time for this one. The Cowrie log time has the same` 5 hour shift` as the other scenarios so my calculation says it was about `2026-10-30T19:31` in true UTC but that is calculated and not noted.

Now if I try to map this to `MITRE ATT&CK` the number would be` T1595 (Active Scanning)` means a connection that only touches the port to see if it is open Label: SIMULATED.

---
