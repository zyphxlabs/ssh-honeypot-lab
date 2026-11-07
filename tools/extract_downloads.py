# extract_downloads.py
# bots in my honeypot often try to download a file with wget, curl or tftp.
# i want to list the servers they download from. this is the first small step.
# it only reads text. i never open or fetch any address.
# data: PUBLIC DATASET (CyberLab, Nov 1 2019)
# usage: python tools/extract_downloads.py data/cyber_nov01_sessions.csv

import sys

path = sys.argv[1]

# ---------- part 1: count the sessions that use a download tool ----------

total = 0
hits = 0

f = open(path, "r", encoding="utf-8", errors="replace")
for line in f:
    total = total + 1
    # one line is one session. i check if it has one of the three tools
    if "wget" in line or "curl" in line or "tftp" in line:
        hits = hits + 1
f.close()

print("lines:", total)
print("lines with a download tool:", hits)


# ---------- part 2: pull the host out of every http:// address ----------

# hosts is a dict. the key is the host. the value is how often i saw it
hosts = {}

f = open(path, "r", encoding="utf-8", errors="replace")
for line in f:
    # my commands are joined with " ; " so i cut every line at that
    for piece in line.split(" ; "):
        if "http://" in piece:
            # i keep the text after http:// and cut it at the first slash
            after = piece[piece.find("http://") + 7:]
            host = after.split("/")[0]
            if host not in hosts:
                hosts[host] = 0
            hosts[host] = hosts[host] + 1
                    # a wget with a bare ip has no http://. the host is a word that starts with a digit and has a slash
        elif "wget " in piece:
            for word in piece.split(" "):
                if word != "" and word[0].isdigit() and "/" in word:
                    host = word.split("/")[0]
                    if host not in hosts:
                        hosts[host] = 0
                    hosts[host] = hosts[host] + 1
f.close()

print("--- hosts ---")
for host in hosts:
    print(host, hosts[host])