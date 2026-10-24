# I. Cowrie

Cowrie is a fake computer that gives fake SSH and Telnet access to an attacker. It has three modes.

**Medium interaction:** it is made in Python and mimics a real system but it is not actually a real system.

**High interaction (proxy mode):** Cowrie sits between the attacker and a real system, and watches everything that goes through and note attacker behaviour and tactics

**LLM mode:** an AI gives responses based on what the attacker does. For example suppose if they type `ls` in the terminal to list things it shows them an `ls` response.

### Features

- It has a fake filesystem. The `createfs` tool can be used to create your own.
- It logs files the attacker downloads with `wget` or anything else an attacker may host a web server and try to pull a script into the SSH session so Cowrie lets them do this but keep the copy and logs it.
- Every attempt the attacker makes is saved in the JSON file.

### The two logs

- `cowrie.log` is Cowrie's own log it holds things like start stop and errors.
- `cowrie.json` is the log of the attacker's attempts.

---

# II. MITRE ATT&CK

## Brute force (MITRE ATT&CK T1110)

Brute force means guessing a password by trying one after another on a system or service. Its ID in MITRE ATT&CK is T1110, and it has four sub-techniques.

- **T1110.001 (Password Guessing):** trying many passwords to get into a system.
- **T1110.002 (Password Cracking):** the attacker gets password hashes and tries to crack them offline on their own system to recover the real password for someone's account.
- **T1110.003 (Password Spraying):** Trying one password on many accounts for example 123456 on root admin and other users. It stays under lockout limits because each account only sees one failure.
- **T1110.004 (Credential Stuffing):** Using username and password pairs from data breaches and trying them on another system as people may reuse the same password everywhere so someone with QWERTY123 on Instagram probably has it on Gmail and Facebook too.

---

## T1078 Valid Accounts

The MITRE ATT&CK gave this the T1078 number and its name is Valid Accounts. In this the attacker has the credentials either from a data breach, cracked passwords or valid passwords that are purchased from another adversary so they use it to sneak in to the system.

**Why it's hard to catch:** The system finds it hard to flag this as danger as it is normal behaviour.

### Tactics (the attacker's goals)

- **Initial Access:** getting in.
- **Persistence:** it will come back whenever they want, like they will have the key to come back.
- **Privilege Escalation:** This is the tactic where the attacker gets more power for example going from a normal user to an admin user.
- **Defense Evasion:** In this the attacker stays undetected as they are using password to get in like a person walking in from front door in house using keys so it does not look suspicious at all.

### Sub-techniques (the type of account)

- **T1078.001 (Default Accounts):** they enter default unchanged credentials like for CCTV cameras and Wi-Fi routers it's mostly admin admin for Kali Linux it's kali kali.
- **T1078.002 (Domain Accounts):** the account managed by a company like Active Directory where one password works on multiple systems.
- **T1078.003 (Local Accounts):** In this kind of sub technique the attacker gets the password to one machine, which gives access to that specific machine for example the root account on one Linux server. If an attacker gets the root password for that server he controls that server. The same password doesn't work on the company's other servers.
- **T1078.004 (Cloud Accounts):** An account for a cloud service like AWS or Google Cloud.
  Cloud has many things stored on it for example different VMs. If attacker got the cloud account password access they can control those configured VMs.

### Difference from T1110 Brute Force

Now if i try to differentiate it from Brute force the brute force is trying 500 keys one by one to open the door.
In short brute force is like getting the keys and valid account is like using that key.
