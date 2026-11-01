# make_sample.py - picks 50 sessions for me to label by hand
# usage: python tools/make_sample.py
# it reads the sessions csv and the labels csv and writes a sample csv
# it does NOT put the classifier label in the sample so i label blind

import csv
import random

# same pick every run
random.seed(1)

sessions_file = "data/cyber_may13_sessions.csv"
labels_file = "data/cyber_may13_labels.csv"
out_file = "data/cyber_may13_sample.csv"

# the 5 groups that exist on this day and how many sessions from each
groups = ["ssh_key_persist", "download_and_run", "login_then_exit", "password_guess_fail", "connect_only"]
per_group = 10

# step 1: read the labels into a dictionary (session id -> label)
labels = {}
f = open(labels_file, "r", encoding="utf-8")
for row in csv.DictReader(f):
    labels[row["session"]] = row["label"]
f.close()

# step 2: read the sessions into a dictionary (session id -> whole row)
# order keeps the ids in file order
sessions = {}
order = []
f = open(sessions_file, "r", encoding="utf-8")
for row in csv.DictReader(f):
    sessions[row["session"]] = row
    order.append(row["session"])
f.close()

# step 3: pick sessions group by group
picked = []
for group in groups:

    # all ids with this label
    ids = []
    for sid in order:
        if labels.get(sid) == group:
            ids.append(sid)

    chosen = []

    # for download_and_run take one session per different command list first
    # so the rare bots are in the sample too
    if group == "download_and_run":
        seen_texts = []
        for sid in ids:
            text = sessions[sid]["commands"]
            if text not in seen_texts and len(chosen) < per_group:
                seen_texts.append(text)
                chosen.append(sid)

    # fill the rest at random
    rest = []
    for sid in ids:
        if sid not in chosen:
            rest.append(sid)
    random.shuffle(rest)
    for sid in rest:
        if len(chosen) < per_group:
            chosen.append(sid)

    print(group, "found", len(ids), "picked", len(chosen))

    for sid in chosen:
        picked.append(sid)

# step 4: mix the order so the groups are not together
random.shuffle(picked)

# step 5: write the sample csv with an empty my_label column
out = open(out_file, "w", newline="", encoding="utf-8")
w = csv.writer(out)
w.writerow(["session", "fail_count", "success_count", "command_count", "commands", "my_label"])
for sid in picked:
    r = sessions[sid]
    w.writerow([sid, r["fail_count"], r["success_count"], r["command_count"], r["commands"][:300], ""])
out.close()

print("wrote", len(picked), "sessions to", out_file)