# convert_cyberlab.py - turns cyberlab files into my own log shape
# cyberlab is PUBLIC DATASET. it is not from my lab
# my sessionizer and classifier stay the way they are. this script makes the data fit them
# usage: python tools/convert_cyberlab.py <out.json> <file1.json.gz> [file2.json.gz ...]

import sys
import gzip
import json

# ---------- step 1: read the arguments ----------

if len(sys.argv) < 3:
    print("usage: python tools/convert_cyberlab.py <out.json> <file1.json.gz> [file2.json.gz ...]")
    sys.exit()

path_out = sys.argv[1]
path_files = sys.argv[2:]

# ---------- step 2: how one cyberlab event becomes one of my events ----------

# gets one cyberlab event and gives back one event in my shape
# the differences i found in the real file:
# session_id becomes session
# src_ip_identifier becomes src_ip (it is a hash, not a real ip)
# the typed command sits in message as "Command found: ..." and goes to input
# the duration is in seconds and goes to duration_ms
# ssh_client_version goes to version
def convert_event(old):
    new = {}
    new["eventid"] = old.get("eventid", "")
    new["session"] = old.get("session_id", "")
    new["src_ip"] = old.get("src_ip_identifier", "")
    new["timestamp"] = old.get("timestamp", "")
    new["sensor"] = "cyberlab"

    eventid = new["eventid"]
    message = old.get("message", "")

    # the commands. cyberlab uses three event names for a command
    # cowrie.command.success and cowrie.command.failed in may and cowrie.command.input in november
    # my tools only know cowrie.command.input so i rename all three to it
    # the text after the first ": " is the command (may has "Command found: <text>" and november has "CMD: <text>")
    # i have not seen a failed command message yet. my guess is that it has the same shape
    if eventid == "cowrie.command.success" or eventid == "cowrie.command.failed" or eventid == "cowrie.command.input":
        new["eventid"] = "cowrie.command.input"
        if ": " in message:
            new["input"] = message.split(": ", 1)[1]
        else:
            new["input"] = ""

    # the client version. only this event has it filled
    elif eventid == "cowrie.client.version":
        new["version"] = old.get("ssh_client_version") or ""

    # the fingerprint. it can be null. then i leave it empty
    elif eventid == "cowrie.client.kex":
        new["hassh"] = old.get("hassh") or ""

    # the length of the session. cyberlab has seconds and i need milliseconds
    # null means no duration so i skip it and do not crash
    elif eventid == "cowrie.session.closed":
        seconds = old.get("duration")
        if seconds is not None:
            new["duration_ms"] = int(seconds * 1000)

    # i do not copy the username and the password of the logins
    # the sessionizer only counts the logins
    return new

# ---------- step 3: read the files ----------

out = open(path_out, "w", encoding="utf-8")
sessions_seen = 0
events_written = 0
skipped = 0

for path in path_files:
    f = gzip.open(path, "rt", encoding="utf-8", errors="replace")
    for line in f:
        line = line.strip()

        # the file is one big list. each line holds one session
        # the first line starts with [ and the lines end with a comma
        # the last line should end with ]
        # i cut those characters off so that one line is one json object
        line = line.rstrip(",")
        if line.startswith("["):
            line = line[1:]
        if line.endswith("}]"):
            line = line[:-1]
        if line == "" or line == "]":
            continue

        # a broken line is counted and skipped. same as in my sessionizer
        try:
            box = json.loads(line)
        except json.JSONDecodeError:
            skipped = skipped + 1
            continue
        if not isinstance(box, dict):
            skipped = skipped + 1
            continue

        # the box looks like {"6c70d195": [event, event, ...]}
        for sid in box:
            sessions_seen = sessions_seen + 1
            for old in box[sid]:
                if not isinstance(old, dict):
                    continue
                out.write(json.dumps(convert_event(old)) + "\n")
                events_written = events_written + 1
    f.close()

out.close()

print("files read:", len(path_files))
print("sessions seen:", sessions_seen)
print("events written:", events_written)
print("skipped lines:", skipped)