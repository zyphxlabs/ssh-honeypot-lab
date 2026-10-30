# Setup Notes

This file shows how to build my lab from nothing so that anyone can repeat it even without any experience. It contains no passwords and no keys and no details about my real machine. Everything runs inside virtual machines and nothing is ever opened to the internet.

---

## 1. What you need

You need a Windows PC with at least 8 GB of RAM and about 50 GB of free disk space and an internet connection for the downloads. You need three downloads and all of them are free. The first is VMware Workstation Pro which you get from the official Broadcom site and you must check the current page for the free personal use terms because they change. The second is the Debian 12 ISO from the official site `debian.org` and you pick the small network install or the full installer image for 64 bit PCs. The third is Kali Linux from the official site `kali.org` and you pick the pre-built VMware image because it is ready to open and needs no install. Always download from the official sites only and never from mirrors you do not know.

## 2. Tools and tech in this lab

| Tool                   | What it does in my lab                                                          | Where it runs |
| ---------------------- | ------------------------------------------------------------------------------- | ------------- |
| VMware Workstation Pro | runs the virtual machines and the private network                               | Windows host  |
| Git Bash and Git       | runs my Git commands and connects to the VMs with SSH                           | Windows host  |
| VS Code                | where I write my notes                                                          | Windows host  |
| Debian 12              | the operating system of the honeypot VM                                         | honeypot VM   |
| Cowrie                 | the honeypot that pretends to be an SSH server on port 2222 and logs everything | honeypot VM   |
| Python and venv        | Cowrie lives in its own Python environment                                      | honeypot VM   |
| Kali Linux             | the attacker VM                                                                 | attacker VM   |
| Hydra                  | guesses passwords for my brute force scenarios                                  | attacker VM   |
| nc and ssh             | test a port and log in by hand                                                  | attacker VM   |
| Python 3 and paramiko  | scripted SSH connections for later scenarios                                    | attacker VM   |

The lab has three machines. The Windows host is my desk. The honeypot VM is the target. The attacker VM is the only machine that attacks and it only attacks the honeypot.

## 3. Network rules of the lab

These rules protect me and my real network. All lab traffic stays on the private Host-only network. I never aim anything at my real network. The honeypot VM has only a Host-only adapter. The attacker VM keeps its old Bridged adapter but I disconnect it before I start any attack and I connect it again later. The small web server for the attack files is bound to the Host-only address only and never to the Bridged side.

---

# PART 1: The host

## 4. Install VMware Workstation Pro

Run the installer and accept the defaults. Restart the PC if it asks. Open VMware once to check that it starts. I do not install VMware Tools in any VM on purpose so copy and paste between my PC and the VMs stays off and I type every command by hand.

## 5. Check the Host-only network

Open VMware and go to Edit then Virtual Network Editor. Look for a network of the type Host-only. This is a private network that only connects your PC and your VMs and it has no route to the internet. If there is none you add one. Do not change anything else here.

---

# PART 2: The honeypot VM (defender)

## 6. Create the honeypot VM

Make a new virtual machine from the Debian 12 ISO and give it 1 CPU core and 1024 MB of RAM and a 20 GB disk. Follow the Debian installer and make one admin user with sudo rights. While you install set the network adapter to NAT so the VM can download packages. When the install is done take a snapshot named `clean-install` so you can always go back to a fresh system.

## 7. Install Cowrie

These commands run inside the Debian VM. First install the system packages that Cowrie needs.

```bash
sudo apt-get update && sudo apt-get install -y python3-pip python3-venv libssl-dev libffi-dev build-essential libpython3-dev python3-minimal authbind
```

Then make a separate user that only runs the honeypot. It has no password so nobody can log in as it directly.

```bash
sudo adduser --disabled-password cowrie
```

Switch to that user with a dash so you land in its own home folder.

```bash
sudo su - cowrie
```

Make the state folder and a Python virtual environment inside it and install Cowrie there.

```bash
mkdir ~/my-honeypot && cd ~/my-honeypot && python3 -m venv cowrie-env && source cowrie-env/bin/activate && python -m pip install --upgrade pip && python -m pip install cowrie
```

The last step creates the `etc` folder with the configuration and the `var` folder with the logs.

```bash
cowrie init
```

## 8. Test Cowrie

Cowrie must always be started as the `cowrie` user and from inside `~/my-honeypot` with the virtual environment active. To turn on the virtual environment from any folder as the `cowrie` user I use the full path `source ~/my-honeypot/cowrie-env/bin/activate`. Cowrie listens on port 2222.

```bash
cowrie start && cowrie status
```

From inside the VM connect to the fake shell.

```bash
ssh -p 2222 root@localhost
```

At the password prompt always type a fake password because Cowrie writes every password it sees into its log in clear text. Run a few harmless commands like `ls` and `whoami` and then `exit`. Then read the last events in the log and stop Cowrie.

```bash
tail -n 20 var/log/cowrie/cowrie.json
```

```bash
cowrie stop
```

## 9. Cut the internet

Shut the VM down and open its settings in VMware and change the network adapter from NAT to Host-only. Boot it again and find its address with `ip a`. It is a private address and I write it as `<vm-ip>` in my notes. This ping must fail because the VM has no internet now.

```bash
ping 8.8.8.8 -c 4
```

Start Cowrie again and connect from the host to `<vm-ip>` on port 2222 with a fake password to prove that the host can still reach the fake shell.

```bash
ssh -p 2222 root@<vm-ip>
```

When both checks pass take a snapshot named `cowrie-working-isolated`.

## 10. Decide who can log in

In my version Cowrie had no `userdb.txt` file in its `etc` folder. The only file I found was `userdb.example` inside the program folder. Its last line lets any name in with any password, so almost every login would succeed. That is no good for a brute force that must fail. So I copied the example into `etc` as my own `userdb.txt`, made a backup of it and then replaced the content with two lines. Cowrie reads the file from the top and the first matching line decides. Cowrie must be stopped while you do this.

```bash
cp ~/my-honeypot/etc/userdb.txt ~/my-honeypot/etc/userdb.txt.bak
```

The two lines look like this. The name and the password are fake lab values and the passwords of these two accounts never go into my wordlists.

```
<user-one>:x:<fake-password-one>
<user-two>:x:<fake-password-two>
```

Then I started Cowrie again and tested it from Kali with `ssh -p 2222 <name>@<vm-ip>`. A name that is not in the file was refused with a wrong password. One of the two accounts got in and the fake prompt showed the name I had used.

---

# PART 3: The attacker VM (Kali)

## 11. Add the Host-only adapter

The attacker VM is Kali Linux and it only ever attacks my own honeypot. I use my existing Kali VM and I shut it down completely before I change anything. Then I take a snapshot named `kali-before-lab` so I can undo any mistake. I keep the adapter that Kali already has and I add a second adapter set to Host-only so Kali sits on the same private network as the honeypot. The first adapter stays as it was. After booting I check the addresses with `ip -4 a`. The second adapter gets its own private address and I write it as `<kali-ip>` in my notes.

```bash
ip -4 a
```

## 12. Check the connection

To prove that the two machines can talk I ping the honeypot from Kali and the answer comes back with no loss.

```bash
ping -c 3 <vm-ip>
```

With Cowrie running I also test the port from Kali. The port is open and Cowrie logs the visit as a connect event and a closed event with a very short duration. The warning about the inverse host lookup is harmless because my lab has no DNS.

```bash
nc -vz <vm-ip> 2222
```

## 13. Check the tools

I check that the tools I need are already there. Hydra and nc and ssh and python3 are all present and paramiko imports without an error, so I install nothing.

```bash
which hydra nc ssh python3 && python3 -c "import paramiko"
```

## 14. Attack material and wordlists

I keep my attack material in a folder called `~/honeypot` in Kali. Inside it is a folder called `fileserver` that will later hold a harmless script for the file server. The script has two lines and it only prints a message. I never run it in Kali. The wordlists live in `~/honeypot` and not inside `fileserver` because a web server shows everything inside the folder it serves.

The wordlists are `users.txt` with 20 common user names and `pass.txt` with 100 fake or very common passwords. None of them is a real password. Both lists stay away from the two accounts that can really log in to my honeypot so that the brute force scenario fails on purpose.

## 15. Snapshot the attacker

When everything works I shut Kali down again and take a second snapshot named `kali-attacker-ready`.

---

## 16. Problems to expect

If `cowrie start` says that Cowrie is not initialized or a file is not found then you are in the wrong folder and you must `cd ~/my-honeypot`. If it refuses to run then you are probably root and you must switch to the `cowrie` user. If it says `twistd: Unknown command: cowrie` then the virtual environment is not active or the config file has a syntax error and the real error is in the full output so save it to a file and search it with `grep`. My own failures and fixes are in `docs/lessons-learned.md`.
