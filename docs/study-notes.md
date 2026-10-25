# Study Notes

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

---

## T1059.004 Unix Shell

The parent technique T1059 is called Command and Scripting Interpreter. The command is the instruction to execute the thing and scripting is writing commands or instructions in sequence so they run one after another. An interpreter is the one that takes the command and does the work.

The .004 is the Unix shell. Systems like Linux and macOS are called Unix systems. The shell is the interactive command line where we type commands. It has the same idea as the GUI but it works by typing plain text commands.

### Tactic

**Execution:** It is the goal of the attacker. He writes and runs commands on the victim machine to make the system do things. The shell is the place where he types those commands.

### How attackers use it

- **Reverse shell:** The victim machine connects out to the attacker and that outgoing connection gives the attacker his shell. So this often gets past the firewalls as they block connections coming in but allow connections going out.
- **Running malware scripts:** They run the script. For example there could be a script to create a crontab desired by the attacker or download the crypto miner malware that will be used to mine crypto for the attacker on the victim's system.

### How it fits the chain

First the attacker did T1110 to get the password. Then they used T1078 to use that password and get into the system. Now it is T1059.004 running commands on the machine.

### In my honeypot

The attacker will type the commands and they will be stored in `cowrie.json`. If they run or download malware its copy will be saved in Cowrie's downloads folder. That's why I kept `downloads/` in the `.gitignore` file so I don't accidentally publish the malware and it doesn't harm somebody's system.

---

## T1105 Ingress Tool Transfer

T1105 is Ingress Tool Transfer. Ingress means coming in and the opposite of it is "egress" (going out). T1105 has no sub-techniques.

The attacker uses this to get a specialized tool like a crypto miner onto the victim machine. They can do it by the wget command or curl or they may use a server that they are controlling and download the malware from there onto the victim machine.

### Tactic

**Command and Control:** The C2 means the attacker commands and controls the victim system. Basically it is the line of contact to the attacker through which they keep the system under their control and use the machine to send the commands and bring files.

### Difference from T1059.004

It is different from T1059.004 as T1059.004 does the execution of commands and T1105 gets the files from outside.

### How it fits the chain

Till now T1110 gets the password. T1078 logs in with that password. T1059.004 types commands and now T1105 downloads the tools using those commands.

### In my honeypot

When an attacker runs wget or curl inside a Cowrie honeypot to bring their things onto the system by downloading, the downloaded file is caught and saved inside the `downloads` folder. The commands they typed to get that file are recorded in `cowrie.json`.

---

## SSH Account Manipulation and Persistence (T1098.004)

### Technique and sub-technique

The number for this technique is T1098 and its name is Account Manipulation. In this the attacker modifies a compromised account's settings to keep access or get higher access and those changes can be to the credentials (password or keys) or to the permissions (groups). The sub-technique for this in my project is T1098.004 which is named SSH Authorized Keys.

### Where the key goes

So the attacker adds their public key to the `authorized_keys` of the SSH. This is the file that keeps the keys that are authorized to get in. Every user has their own file inside their home folder and the full path is `~/.ssh/authorized_keys`. It keeps one public key per line.

### Public and private key

Public key and private key are a concept of asymmetric cryptography where there are 2 keys. One is private and the other is public. Let's suppose the public key is like a lock that anyone can see and copy and the private key is the only key that opens that lock. The server keeps the public key lock. So when logging in, the attacker proves he has the matching private key and the private key itself never goes to the server.

### Why it is dangerous

By using this pair the attacker can get into the system without a password too. This is why it is dangerous as a password reset won't help or stop the attacker. The password reset only changes the password, but the key login does not use the password at all so the attacker's key keeps working anyway.

### Tactics

The tactics are persistence and privilege escalation. Persistence is when the attacker can get back as they wish. Privilege escalation is when the attacker can give themselves higher permission for example a root login. If they put their key into root's `.ssh` folder at `/root/.ssh/authorized_keys`, they can log in straight as root.

### sshd_config

There is also a file called `sshd_config` which is the settings file of the SSH server, and it lives at `/etc/ssh/sshd_config`. It does not keep keys, but the attacker might change two settings inside it:

- `PubkeyAuthentication yes` to allow login with keys.
- `PermitRootLogin yes` to allow root to log in over SSH.

The attacker changes them so his key works and he can get root access.

### Mitigation

Mitigation is to disable the SSH if the system doesn't need any SSH connection.

### Detection

To detect this watch for processes that modify the `authorized_keys` file or the `/etc/ssh/sshd_config` file.

### In my honeypot

It could show up in my honeypot as the attacker can try to add his key to the SSH so he can get back as he wants. The attacker might type commands like `mkdir -p ~/.ssh` to make the folder, and then `echo "ssh-rsa AAAA... attacker" >> ~/.ssh/authorized_keys` to append his key, and maybe use `chmod` on it. Everything he types will be logged in the `cowrie.json` file and we can find it by searching the log for the word `authorized_keys`.

---

## Cron Scheduled Task (T1053.003)

### Technique and sub-technique

The parent technique T1053 is called Scheduled Task/Job in which the attacker uses the system's scheduling feature to make commands or programs run automatically without having to start them manually every time. The sub-technique for this in my project is T1053.003 which is named Cron.

Cron is the time-based job scheduler of Linux it is used to run commands at a particular time or repeatedly as desired inshort a crontab is the file that keeps the scheduled jobs for a user.

### Tactics (the attacker's goals)

- **Execution:** getting his program or malicious code to run.
- **Persistence:** it keeps running on a scheduled basis or after a reboot so he keeps access.
- **Privilege Escalation:** the attacker gets more power. If the job is made in root's crontab it runs as root so it gives him more power.

### Mitigation

Cron permissions are controlled by the `/etc/cron.allow` and `/etc/cron.deny` files. The `cron.deny` file lists specific users who are not allowed to use cron. If neither file exists, only the superuser can use cron.

### Detection

To detect this you have to watch for processes that create or modify cron jobs via `crontab` or the `/etc/cron.*` directories. Normal software installs and admin work also create them so you have to compare the changes with what is normal for your system. We can also review cron execution logs in the `/var/log` directory.

### In my honeypot

It could show up in my honeypot because after planting a key with T1098.004 an attacker may also plant a cron job so his program restarts or pulls down a crypto miner. When they run commands to edit or echo things into the crontab those commands are caught and stored in `cowrie.json`. We can find it by searching the log file for words like `crontab` or `cron`. The log only shows what Cowrie recorded during the session so it does not prove the cron job was installed or ran.

---

## T1496 Resource Hijacking

### Technique

The ID given by MITRE ATT&CK for this is T1496. Hijacking means using the victim's system to get work done for the attacker's own benefit. The victim pays the cost and the attacker enjoys the profit. For example a crypto miner on the victim's system. It impacts the system performance and availability. The system may stop working if the load of the work is too much and it won't even do basic tasks for the victim's daily routine.

### Sub-techniques

It has 4 sub-techniques.

- **T1496.001 (Compute Hijacking):** It means using the CPU and GPU. The most usual example is a crypto miner.
- **T1496.002 (Bandwidth Hijacking):** It means using the network of the victim. It can be used to create a botnet or to sell it as a proxy to proxy companies.
- **T1496.003 (SMS Pumping):** The attacker abuses the SMS forms that send codes. They may send multiple messages and the victim's bill will go high as a result.
- **T1496.004 (Cloud Service Hijacking):** Examples are email and SMS and AI models. The attacker uses them for their own benefit like using an AI model for free and the victim will be charged for this.

### Tactic

Tactic means the attacker's goal. In this case it is Impact. The attacker harms or disrupts the system. This is usually a late step as the attacker first gets in and then gets the profit.

### Mitigation

Mitigation for this is hard compared to other techniques.

### Detection

Checking CPU and GPU use. If they are high for a long time even with no task going on then it may be compromised by it. Looking for connections to a mining pool. We can also detect by noticing unusual containers or cloud instances.

### Honeypot

In my honeypot the attacker can't really do this even if they try. They can see that things are working and that they succeeded but in reality this is a Cowrie honeypot so their actions will be captured in `cowrie.json` and their whole working process can be found there.
