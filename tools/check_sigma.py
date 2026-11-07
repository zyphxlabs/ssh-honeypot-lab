# check_sigma.py - runs my small sigma rules on my session csv files
# it only knows my own rule shape: contains and endswith on the commands field
# the condition can be one block, blocks joined with or, or blocks joined with and
# usage: python tools/check_sigma.py

import os
import csv

# ---------- step 1: where things are ----------

rule_folder = "detections/sigma"

# the csv files i test on. the first word is just a name for the print
data_files = [
    ("nov1 PUBLIC", "data/cyber_nov01_sessions.csv"),
    ("lab SIMULATED", "data/lab_sessions.csv"),
    ("synth SYNTHETIC", "data/synth_sessions.csv"),
    ("benign SYNTHETIC", "data/benign_sessions.csv"),
]

# ---------- step 2: read one rule file ----------

# gives back the title, the condition and the blocks
# a block has a name and two lists of words. one for contains and one for endswith
def read_rule(path):
    f = open(path, "r", encoding="utf-8")
    lines = f.read().split("\n")
    f.close()

    title = ""
    condition = ""
    blocks = {}
    current = ""

    i = 0
    while i < len(lines):
        line = lines[i].strip()

        if line.startswith("title:"):
            title = line[6:].strip()

        if line.startswith("condition:"):
            condition = line[10:].strip()

        # a new block starts with a name like selection or selection_end
        if (line.startswith("selection") or line.startswith("filter")) and line.endswith(":"):
            current = line[:-1]
            blocks[current] = {"contains": [], "endswith": []}

        # check both kinds of match line
        for mod in ["contains", "endswith"]:
            key = "commands|" + mod + ":"
            if line.startswith(key):
                rest = line[len(key):].strip()
                found = []
                if rest != "":
                    # one word on the same line
                    found.append(rest[1:-1])
                else:
                    # a list of words on the next lines
                    i = i + 1
                    while i < len(lines) and lines[i].strip().startswith("- "):
                        item = lines[i].strip()[2:]
                        found.append(item[1:-1])
                        i = i + 1
                    i = i - 1
                blocks[current][mod] = blocks[current][mod] + found
        i = i + 1

    return title, condition, blocks

# ---------- step 3: count matches ----------

# my checker can run one block, blocks joined with or, or blocks joined with and
# it can not run not, and it can not mix and with or
def can_run(condition):
    words = condition.split(" ")
    if "not" in words:
        return False
    if "and" in words and "or" in words:
        return False
    return True

# true if one block fits the text
def block_hit(text, block):
    for w in block["contains"]:
        if w in text:
            return True
    for w in block["endswith"]:
        if text.endswith(w):
            return True
    return False

# true if the whole condition fits the text
def rule_hit(text, blocks, condition):
    words = condition.split(" ")
    results = []
    for w in words:
        if w != "or" and w != "and":
            results.append(block_hit(text, blocks[w]))
    if "and" in words:
        for r in results:
            if not r:
                return False
        return True
    for r in results:
        if r:
            return True
    return False

# counts the sessions where the rule fits the commands
def count_matches(csv_path, blocks, condition):
    f = open(csv_path, "r", encoding="utf-8", newline="")
    count = 0
    for row in csv.DictReader(f):
        if rule_hit(row["commands"], blocks, condition):
            count = count + 1
    f.close()
    return count

# ---------- step 4: run every rule on every file ----------

for name in sorted(os.listdir(rule_folder)):
    if not name.endswith(".yml"):
        continue

    title, condition, blocks = read_rule(rule_folder + "/" + name)
    print(name)

    if not can_run(condition):
        print("  skipped. condition is", condition)
        continue

    print("  condition:", condition)
    for label, csv_path in data_files:
        print("  ", label, count_matches(csv_path, blocks, condition))

# ---------- step 5: compare the matches with my truth labels ----------

# reads a truth file into a dict. the key is the session id and the value is the label
def read_truth(path):
    truth = {}
    f = open(path, "r", encoding="utf-8", newline="")
    for row in csv.DictReader(f):
        truth[row["session"]] = row["label"]
    f.close()
    return truth

# gives back how many matched sessions have each label
def label_counts(csv_path, truth, blocks, condition):
    counts = {}
    f = open(csv_path, "r", encoding="utf-8", newline="")
    for row in csv.DictReader(f):
        if rule_hit(row["commands"], blocks, condition):
            label = "not_in_truth"
            if row["session"] in truth:
                label = truth[row["session"]]
            if label in counts:
                counts[label] = counts[label] + 1
            else:
                counts[label] = 1
    f.close()
    return counts

truth_files = [
    ("lab SIMULATED", "data/lab_sessions.csv", "data/ground_truth.csv"),
    ("synth SYNTHETIC", "data/synth_sessions.csv", "data/synth_truth.csv"),
]

print("")
print("---------- labels of the matched sessions ----------")
for name in sorted(os.listdir(rule_folder)):
    if not name.endswith(".yml"):
        continue
    title, condition, blocks = read_rule(rule_folder + "/" + name)
    if not can_run(condition):
        continue
    print(name)
    for label, csv_path, truth_path in truth_files:
        truth = read_truth(truth_path)
        print("  ", label, label_counts(csv_path, truth, blocks, condition))
