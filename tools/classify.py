# classify.py - gives every session a label using simple rules
# it reads the csv from sessionize.py and writes a new csv with a label column
# usage: python tools/classify.py <sessions.csv> <out.csv> [ground_truth.csv]

import sys
import csv

# ---------- step 1: read the arguments ----------

if len(sys.argv) < 3:
    print("usage: python tools/classify.py <sessions.csv> <out.csv> [ground_truth.csv]")
    sys.exit()

path_in = sys.argv[1]
path_out = sys.argv[2]

# the third word is optional. it is my file with the right answers
path_truth = ""
if len(sys.argv) > 3:
    path_truth = sys.argv[3]

# ---------- step 2: the rules ----------

# gets one row of the sessions csv and gives back one label
# the order matters. the first rule that fits wins
def get_label(row):
    fails = int(row["fail_count"])
    success = int(row["success_count"])
    text = row["commands"]

    # the sessionizer joined the commands with " ; " so i cut them apart again
    commands = []
    if text != "":
        commands = text.split(" ; ")

    # exit is not a real command. a session with only exit counts as no commands
    real_commands = []
    for c in commands:
        if c.strip() != "exit":
            real_commands.append(c)

    # the average wait between commands. empty means less than 2 commands
    gap = 0
    if row["avg_gap_sec"] != "":
        gap = float(row["avg_gap_sec"])

    # no good login
    if success == 0 and fails == 0:
        return "connect_only"
    if success == 0:
        return "password_guess_fail"

    # good login but nothing real typed
    if len(real_commands) == 0:
        return "login_then_exit"

    # miner before download. the miner session has curl and xmrig together
    if "xmrig" in text:
        return "miner_download"
    # where the last wget or curl is in the text. find gives the first place of a word and rfind the last place. -1 means it is not there
    # a bare word like "wget;" is only a probe. a real download has a space after the word
    last_download = text.rfind("wget ")
    if text.rfind("curl ") > last_download:
        last_download = text.rfind("curl ")
    # wipe before download. a delete that comes before the last download
    wipe_at = text.find("rm -rf")
    if wipe_at != -1 and wipe_at < last_download:
        return "wipe_then_download"
    if last_download != -1:
        return "download_and_run"
    if "authorized_keys" in text:
        return "ssh_key_persist"
    if "crontab" in text.replace("crontab -l", ""):
        return "cron_persist"

    # one command with a ; inside is a one liner
    if len(real_commands) == 1 and ";" in real_commands[0]:
        return "fast_oneliner"

    # the commands look the same now so the client and the timing decide
    if "paramiko" in row["version"]:
        return "paramiko_client_whoami"
    if len(real_commands) == 1 and real_commands[0].strip() == "whoami":
        return "ssh_client_whoami"

    # my guess is that 10 seconds is the line between bot and human
    if gap >= 10:
        return "slow_human"

    return "system_recon"

# ---------- step 3: label every session ----------

f = open(path_in, "r", encoding="utf-8", newline="")
rows = list(csv.DictReader(f))
f.close()

counts = {}
labels = {}
for row in rows:
    label = get_label(row)
    row["label"] = label
    labels[row["session"]] = label
    if label not in counts:
        counts[label] = 0
    counts[label] = counts[label] + 1

out = open(path_out, "w", encoding="utf-8", newline="")
writer = csv.writer(out)
writer.writerow(["session", "label"])
for row in rows:
    writer.writerow([row["session"], row["label"]])
out.close()

print("sessions labeled:", len(rows))
for label in sorted(counts):
    print(label, counts[label])

# ---------- step 4: compare with the right answers ----------

if path_truth != "":
    truth = {}
    f = open(path_truth, "r", encoding="utf-8", newline="")
    for row in csv.DictReader(f):
        truth[row["session"]] = row["label"]
    f.close()

    total = 0
    correct = 0
    right = {}
    said = {}
    real = {}
    misses = []

    for sid in truth:
        # sessions that have no label in my file or no row here are skipped
        if sid not in labels:
            continue
        total = total + 1
        t = truth[sid]
        p = labels[sid]
        if t not in real:
            real[t] = 0
        if p not in said:
            said[p] = 0
        real[t] = real[t] + 1
        said[p] = said[p] + 1
        if t == p:
            correct = correct + 1
            if t not in right:
                right[t] = 0
            right[t] = right[t] + 1
        else:
            misses.append(sid + " truth=" + t + " classifier=" + p)

    print("")
    print("sessions with a right answer:", total)
    print("correct:", correct)
    print("wrong:", total - correct)

    # precision = of all i called x how many were really x
    # recall = of all that really were x how many did i find
    print("")
    print("label / real / said / right / precision / recall")
    all_labels = sorted(set(list(real.keys()) + list(said.keys())))
    for label in all_labels:
        r = real.get(label, 0)
        s = said.get(label, 0)
        ok = right.get(label, 0)
        precision = "-"
        recall = "-"
        if s > 0:
            precision = round(ok / s, 2)
        if r > 0:
            recall = round(ok / r, 2)
        print(label, r, s, ok, precision, recall)

    print("")
    print("misses:")
    for m in misses:
        print(m)