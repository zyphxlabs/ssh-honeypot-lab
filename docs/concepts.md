# Concepts

## Honeypot

A honeypot is a fake computer environment to attract the attacker and record their behaviour and techniques so we get familiar with their ways. The things the attacker does are logged in `cowrie.json`. As there is no real system in a honeypot anyone who is there is suspicious.

Next come 3 types. The first is low where we give only fake services. The second is medium where we allow them to run commands but nothing is real. Cowrie is medium and I am going to use it in this project. The third is high where we give them a real system and this is dangerous too as the attacker may manipulate it to use against us.

---

## Brute Force vs Credential Stuffing

Brute force means guessing a password by trying one after another on a system or service.

Credential stuffing means using username and password pairs from data breaches and trying them on another system. People may reuse the same password everywhere so someone with QWERTY123 on Instagram probably has it on Gmail and Facebook too.

---

## Botnet and Mirai

A botnet is a network of hijacked computers controlled by an attacker through command and control (C2). It is used in DDoS attacks. The most common examples are the Mirai and Mozi botnets where IoT devices like cameras and routers are hacked and added to the botnet.

The Mirai source code was leaked and later used by many to make copy botnets. Mozi was peer to peer with no single C2 so every bot works as an equal peer. Mirai spreads through weak Telnet passwords and Mozi through weak Telnet passwords and common vulnerabilities.

Then come cryptominer botnets. They mine crypto and it is the T1496.001 Compute Hijacking part.

---

## IOC

IOC is an indicator of compromise. It means a sign that a system was attacked or compromised.

There are 4 common types. The first is the IP where the attack came from. The second is the domain the attacker used to host the malware. The third is the file hash. Every file has a unique hash that is very hard to fake. Two files that are the same except for a single dot still have different hashes. The fourth is the URL which is the whole web address they typed with wget to get the malware.

In the modern era the domain and IP can be changed but if the malware is the same the file hash stays the same.
