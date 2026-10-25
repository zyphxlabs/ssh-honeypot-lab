# Threat Model

## What am I protecting?

I am protecting my own network and my own accounts and my own VM and my host PC and all my other stuff.

## What could go wrong?

**Malware**
I may download malware and run it or push it to GitHub. It may damage my VM. My host can also be damaged as the VM and the host are linked in some way.

**Network exposure**
If I allow the VM to have internet or put it on the bridged network a real attacker can come scanning and get into my network and get me in trouble.

**Leaked secrets**
I can commit an API key or an env file. That may hold something important like my passwords or my public IP which an attacker can use to track me and hunt me. An attacker can take over my GitHub account this way too.

**Attacking something I don't own**
I may run an attack on something I don't own.

**Breaking the VM**
The VM may break. I may lock myself out while setting up the honeypot or making SSH configuration changes.

## What stops each risk?

- **Malware:** I only look at downloaded samples as hashes and text. I never run or open them.
- **Network exposure:** After the install the VM only uses a host-only network. It never uses a bridged network or the internet. I am not going to do this as I am a beginner still learning and evolving so let's keep it safe first.
- **Leaked secrets:** I set up `.gitignore` before any data exists so keys and env files and downloads stay out of the repo.
- **Attacking something I don't own:** I only attack my own honeypot VM. I double check things in this kind of work and labs.
- **Breaking the VM:** I take VM snapshots before big changes. My two snapshots are `clean-install` and `cowrie-working`.
