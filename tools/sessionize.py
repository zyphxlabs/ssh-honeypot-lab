# sessionize.py - reads a cowrie style log and makes one row per session
# it works on my fake logs (SYNTHETIC) and on real logs
# usage: python tools/sessionize.py <file or folder> <out.csv>

import sys
import os
import json
import csv
from datetime import datetime

# ---------- step 1: read the arguments ----------

# sys.argv is the list of words i typed after python
# sys.argv[0] is the script name. [1] is the log. [2] is the csv i want
if len(sys.argv) < 3:
    print("usage: python tools/sessionize.py <file or folder> <out.csv>")
    sys.exit()

path_in = sys.argv[1]
path_out = sys.argv[2]

# the second csv with one row per ip gets its name from the first one
path_ips = path_out.replace(".csv", "_ips.csv")

# ---------- step 2: find the log files ----------

# if i give a folder i read every file that starts with cowrie.json
# cowrie rotates the log so the old days sit in files like cowrie.json.2026-10-29
files = []
if os.path.isdir(path_in):
    for name in sorted(os.listdir(path_in)):
        if name.startswith("cowrie.json"):
            files.append(os.path.join(path_in, name))
else:
    files.append(path_in)

# ---------- step 3: read every line ----------

events = []
skipped = 0

for filename in files:
    f = open(filename, "r", encoding="utf-8", errors="replace")
    for line in f:
        line = line.strip()
        # an empty line is not an error. i just go on
        if line == "":
            continue
        # json.loads turns the text line into a python dict
        # a broken line makes it fail. i count it and skip it
        # i do not crash because one bad line should not kill the whole run
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            skipped = skipped + 1
            continue
        # a line that is valid json but has no session is no use to me
        if not isinstance(event, dict) or "session" not in event:
            skipped = skipped + 1
            continue
        events.append(event)
    f.close()

print("good events:", len(events))
print("skipped lines:", skipped)

# ---------- step 4: group the events by session ----------

# sessions is a dict. the key is the session id. the value is a small dict with my numbers
sessions = {}

for event in events:
    sid = event["session"]

    # first time i see this session i make an empty box for it
    # i check this by hand. that is the job of defaultdict in the starter script
    if sid not in sessions:
        sessions[sid] = {"session": sid, "src_ip": "", "first_time": "", "last_time": "",
                         "fail_count": 0, "success_count": 0, "commands": [],
                         "command_times": [], "version": "", "hassh": "", "duration_ms": "", "has_close": "no"}

    s = sessions[sid]
    eventid = event.get("eventid", "")
    when = event.get("timestamp", "")

    # the ip comes from the first event that has one
    if s["src_ip"] == "":
        s["src_ip"] = event.get("src_ip", "")

    # keep the earliest and the latest time. the iso time text sorts like time
    if when != "":
        if s["first_time"] == "" or when < s["first_time"]:
            s["first_time"] = when
        if when > s["last_time"]:
            s["last_time"] = when

    # count what this event is
    # i never save the password. i only count the logins
    if eventid == "cowrie.login.failed":
        s["fail_count"] = s["fail_count"] + 1
    elif eventid == "cowrie.login.success":
        s["success_count"] = s["success_count"] + 1
    elif eventid == "cowrie.command.input":
        s["commands"].append(event.get("input", ""))
        s["command_times"].append(when)
    elif eventid == "cowrie.client.version":
        s["version"] = event.get("version", "")
    elif eventid == "cowrie.client.kex":
        s["hassh"] = event.get("hassh", "")
    elif eventid == "cowrie.session.closed":
        s["has_close"] = "yes"
        s["duration_ms"] = event.get("duration_ms", "")

# ---------- step 5: timing between commands ----------

# turns the time text into a real time so i can subtract two times
def to_time(text):
    return datetime.fromisoformat(text.replace("Z", "+00:00"))

# the average wait between commands helps later to tell a bot from a human
# a bot types fast. a human waits. with less than 2 commands there is no gap
for sid in sessions:
    s = sessions[sid]
    s["avg_gap_sec"] = ""
    if len(s["command_times"]) >= 2:
        total = 0
        count = 0
        for n in range(1, len(s["command_times"])):
            gap = to_time(s["command_times"][n]) - to_time(s["command_times"][n - 1])
            total = total + gap.total_seconds()
            count = count + 1
        s["avg_gap_sec"] = round(total / count, 2)

# ---------- step 6: write one row per session ----------

columns = ["session", "src_ip", "first_time", "last_time", "duration_ms", "has_close",
           "fail_count", "success_count", "command_count", "avg_gap_sec", "version", "hassh", "commands"]

out = open(path_out, "w", newline="", encoding="utf-8")
writer = csv.writer(out)
writer.writerow(columns)
for sid in sessions:
    s = sessions[sid]
    writer.writerow([s["session"], s["src_ip"], s["first_time"], s["last_time"], s["duration_ms"], s["has_close"],
                     s["fail_count"], s["success_count"], len(s["commands"]), s["avg_gap_sec"],
                     s["version"], s["hassh"], " ; ".join(s["commands"])])
out.close()

print("sessions:", len(sessions))

# ---------- step 7: one row per ip ----------

# first_seen and last_seen for every attacker ip
ips = {}
for sid in sessions:
    s = sessions[sid]
    ip = s["src_ip"]
    if ip not in ips:
        ips[ip] = {"sessions": 0, "first_seen": s["first_time"], "last_seen": s["last_time"]}
    ips[ip]["sessions"] = ips[ip]["sessions"] + 1
    if s["first_time"] < ips[ip]["first_seen"]:
        ips[ip]["first_seen"] = s["first_time"]
    if s["last_time"] > ips[ip]["last_seen"]:
        ips[ip]["last_seen"] = s["last_time"]

out = open(path_ips, "w", newline="", encoding="utf-8")
writer = csv.writer(out)
writer.writerow(["src_ip", "sessions", "first_seen", "last_seen"])
for ip in ips:
    writer.writerow([ip, ips[ip]["sessions"], ips[ip]["first_seen"], ips[ip]["last_seen"]])
out.close()

print("ips:", len(ips))