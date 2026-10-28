# Setup Notes

This file shows how to build my lab from nothing so that anyone can repeat it even without any experience. It contains no passwords and no keys and no details about my real machine. Everything runs inside virtual machines and nothing is ever opened to the internet.

---

## 1. What you need

You need a Windows PC with at least 8 GB of RAM and about 50 GB of free disk space and an internet connection for the downloads. You need three downloads and all of them are free. The first is VMware Workstation Pro which you get from the official Broadcom site and you must check the current page for the free personal use terms because they change. The second is the Debian 12 ISO from the official site `debian.org` and you pick the small network install or the full installer image for 64 bit PCs. The third is Kali Linux from the official site `kali.org` and you pick the pre-built VMware image because it is ready to open and needs no install. Always download from the official sites only and never from mirrors you do not know.

## 2. Install VMware Workstation Pro

Run the installer and accept the defaults. Restart the PC if it asks. Open VMware once to check that it starts. I do not install VMware Tools in any VM on purpose so copy and paste between my PC and the VMs stays off and I type every command by hand.

## 3. Check the Host-only network

Open VMware and go to Edit then Virtual Network Editor. Look for a network of the type Host-only. This is a private network that only connects your PC and your VMs and it has no route to the internet. If there is none you add one. Do not change anything else here and never connect any lab VM to a Bridged network.

## 4. Create the honeypot VM

Make a new virtual machine from the Debian 12 ISO and give it 1 CPU core and 1024 MB of RAM and a 20 GB disk. Follow the Debian installer and make one admin user with sudo rights. While you install set the network adapter to NAT so the VM can download packages. When the install is done take a snapshot named `clean-install` so you can always go back to a fresh system.

## 5. Install Cowrie

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

## 6. Test Cowrie

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

## 7. Cut the internet

Shut the VM down and open its settings in VMware and change the network adapter from NAT to Host-only. Boot it again and find its address with `ip a`. It is a private address and I write it as `<vm-ip>` in my notes. This ping must fail because the VM has no internet now.

```bash
ping 8.8.8.8 -c 4
```

Start Cowrie again and connect from the host to `<vm-ip>` on port 2222 with a fake password to prove that the host can still reach the fake shell.

```bash
ssh -p 2222 root@<vm-ip>
```

When both checks pass take a snapshot named `cowrie-working-isolated`.

## 8. Attacker VM (Kali)

Note: this part is the plan and I will correct it after I build it for real.

The attacker VM is Kali Linux and it only ever attacks my own honeypot. I open the pre-built Kali image in VMware and check that it boots. Then I shut it down completely and take a snapshot named `kali-before-lab` so I can undo any mistake. I keep the adapter that Kali already has and I add a second adapter set to the same Host-only network as the honeypot. After booting I check the new private address with `ip -4 a` and I test that Kali can reach the honeypot.

```bash
ping -c 4 <vm-ip>
```

With Cowrie running I also test the port from Kali.

```bash
nc -vz <vm-ip> 2222
```

I will add the tools check and the harmless file server and the wordlists here after I build them.

## 9. Problems to expect

If `cowrie start` says that Cowrie is not initialized or a file is not found then you are in the wrong folder and you must `cd ~/my-honeypot`. If it refuses to run then you are probably root and you must switch to the `cowrie` user. If it says `twistd: Unknown command: cowrie` then the virtual environment is not active or the config file has a syntax error and the real error is in the full output so save it to a file and search it with `grep`. My own failures and fixes are in `docs/lessons-learned.md`.
