# check_sigma.py - runs my small sigma rules on my session csv files
# it only knows my own rule shape: contains and endswith on the commands field
# the condition can be one block or blocks joined with or. nothing else
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
]

# ---------- step 2: read one rule file ----------

# gives back the title, the condition and two lists of words
# one list for contains and one list for endswith
def read_rule(path):
    f = open(path, "r", encoding="utf-8")
    lines = f.read().split("\n")
    f.close()

    title = ""
    condition = ""
    contains_words = []
    endswith_words = []

    i = 0
    while i < len(lines):
        line = lines[i].strip()

        if line.startswith("title:"):
            title = line[6:].strip()

        if line.startswith("condition:"):
            condition = line[10:].strip()

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
                if mod == "contains":
                    contains_words = contains_words + found
                else:
                    endswith_words = endswith_words + found
        i = i + 1

    return title, condition, contains_words, endswith_words

# ---------- step 3: count matches ----------

# counts the sessions where any contains word is inside the text
# or the text ends with any endswith word
def count_matches(csv_path, contains_words, endswith_words):
    f = open(csv_path, "r", encoding="utf-8", newline="")
    count = 0
    for row in csv.DictReader(f):
        text = row["commands"]
        hit = False
        for w in contains_words:
            if w in text:
                hit = True
        for w in endswith_words:
            if text.endswith(w):
                hit = True
        if hit:
            count = count + 1
    f.close()
    return count

# ---------- step 4: run every rule on every file ----------

for name in sorted(os.listdir(rule_folder)):
    if not name.endswith(".yml"):
        continue

    title, condition, contains_words, endswith_words = read_rule(rule_folder + "/" + name)
    print(name)

    # my checker can only do a single block or blocks joined with or
    if " and " in condition or "not" in condition:
        print("  skipped. condition is", condition)
        continue

    print("  contains:", contains_words, " endswith:", endswith_words)
    for label, csv_path in data_files:
        print("  ", label, count_matches(csv_path, contains_words, endswith_words))

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
def label_counts(csv_path, truth, contains_words, endswith_words):
    counts = {}
    f = open(csv_path, "r", encoding="utf-8", newline="")
    for row in csv.DictReader(f):
        text = row["commands"]
        hit = False
        for w in contains_words:
            if w in text:
                hit = True
        for w in endswith_words:
            if text.endswith(w):
                hit = True
        if hit:
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
    title, condition, contains_words, endswith_words = read_rule(rule_folder + "/" + name)
    if " and " in condition or "not" in condition:
        continue
    print(name)
    for label, csv_path, truth_path in truth_files:
        truth = read_truth(truth_path)
        print("  ", label, label_counts(csv_path, truth, contains_words, endswith_words))
