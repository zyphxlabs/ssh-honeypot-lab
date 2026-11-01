# make_charts.py - makes 6 charts from one sessions csv and its labels csv
# usage: python tools/make_charts.py <sessions.csv> <labels.csv> <out_folder> <name> <source text>
# example: python tools/make_charts.py data/cyber_nov01_sessions.csv data/nov_new.csv analysis/charts nov01 "PUBLIC DATASET: CyberLab Nov 1 2019"
# only use it on the public dataset files. the source text goes into every chart title

import sys
import os
import pandas as pd
import matplotlib

# Agg means draw into picture files and open no window
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# ---------- step 1: read the arguments ----------

if len(sys.argv) < 6:
    print("usage: python tools/make_charts.py <sessions.csv> <labels.csv> <out_folder> <name> <source text>")
    sys.exit()

path_sessions = sys.argv[1]
path_labels = sys.argv[2]
out_folder = sys.argv[3]
name = sys.argv[4]
source = sys.argv[5]

# ---------- step 2: read the two files and join them ----------

# the session id and the ip are read as text so pandas does not turn them into numbers
sessions = pd.read_csv(path_sessions, dtype={"session": str, "src_ip": str})
labels = pd.read_csv(path_labels, dtype={"session": str})

# an empty commands cell is read as missing. i make it an empty text again
sessions["commands"] = sessions["commands"].fillna("")

# merge puts the label next to every session. it matches on the session column
df = sessions.merge(labels, on="session", how="left")
df["label"] = df["label"].fillna("no_label")

print("sessions read:", len(df))
print("sessions without a label:", (df["label"] == "no_label").sum())

os.makedirs(out_folder, exist_ok=True)

# ---------- step 3: two helpers that draw and save a picture ----------

# bars lying down. names are the words on the left. values are the numbers
def draw_bars(names, values, title, xlabel, path, use_log):
    plt.figure(figsize=(9, 5))
    plt.barh(names, values)
    # the number is written at the end of every bar
    for i in range(len(values)):
        plt.text(values[i], i, " " + str(values[i]), va="center")
    top = max(values)
    if use_log:
        plt.xscale("log")
        plt.xlim(0.5, top * 4)
    else:
        plt.xlim(0, top * 1.15)
    # the first name goes on top
    plt.gca().invert_yaxis()
    plt.title(title + "\n" + source)
    plt.xlabel(xlabel)
    plt.tight_layout()
    plt.savefig(path, dpi=150)
    plt.close()

# a histogram counts how many values fall into each box
def draw_hist(values, title, xlabel, path):
    plt.figure(figsize=(9, 5))
    plt.hist(values, bins=50)
    plt.yscale("log")
    plt.title(title + "\n" + source)
    plt.xlabel(xlabel)
    plt.ylabel("sessions (log scale)")
    plt.tight_layout()
    plt.savefig(path, dpi=150)
    plt.close()

# ---------- chart 1: sessions per label ----------

label_counts = df["label"].value_counts()
draw_bars(label_counts.index.tolist(), label_counts.values.tolist(),
          "sessions per label (log scale)", "sessions",
          os.path.join(out_folder, name + "_1_labels.png"), True)

# ---------- chart 2: how long a session lasts ----------

seconds = pd.to_numeric(df["duration_ms"], errors="coerce") / 1000
seconds = seconds.dropna()
draw_hist(seconds, "how long a session lasts", "session length in seconds",
          os.path.join(out_folder, name + "_2_duration.png"))

# ---------- chart 3: commands per session ----------

command_counts = pd.to_numeric(df["command_count"], errors="coerce")
command_counts = command_counts[command_counts > 0]
draw_hist(command_counts, "commands per session (only sessions with commands)",
          "commands in one session",
          os.path.join(out_folder, name + "_3_commands.png"))

# ---------- chart 4: sessions per hour of the day ----------

# the time looks like 2019-11-01T06:58:44.806364Z so the hour is the characters 11 and 12
hours = pd.to_numeric(df["first_time"].str[11:13], errors="coerce").dropna().astype(int)
per_hour = hours.value_counts()

hour_names = []
hour_values = []
for h in range(24):
    hour_names.append(h)
    if h in per_hour.index:
        hour_values.append(int(per_hour[h]))
    else:
        hour_values.append(0)

plt.figure(figsize=(9, 5))
plt.bar(hour_names, hour_values)
plt.xticks(hour_names)
plt.title("sessions per hour of the day\n" + source)
plt.xlabel("hour of the day as logged")
plt.ylabel("sessions")
plt.tight_layout()
plt.savefig(os.path.join(out_folder, name + "_4_hours.png"), dpi=150)
plt.close()

# ---------- chart 5: top 10 source ids ----------

# in this dataset the source address is already a hash. i show only the first 8 characters
top_ips = df["src_ip"].value_counts().head(10)
short_names = []
for ip in top_ips.index:
    short_names.append(str(ip)[:8])
draw_bars(short_names, top_ips.values.tolist(),
          "top 10 source ids by sessions", "sessions",
          os.path.join(out_folder, name + "_5_top_ips.png"), False)

# ---------- chart 6: top 10 first words of commands ----------

# the sessionizer joined the commands with " ; " so i cut them apart again
word_counts = {}
for text in df["commands"]:
    if text == "":
        continue
    for c in text.split(" ; "):
        words = c.strip().split(" ")
        first = words[0]
        # some bots put LC_ALL=C in front so i take the next word
        if first.startswith("LC_ALL") and len(words) > 1:
            first = words[1]
        if first == "":
            continue
        # a very long word is a blob or a key and not a command name so i skip it
        if len(first) > 20:
            continue
        if first not in word_counts:
            word_counts[first] = 0
        word_counts[first] = word_counts[first] + 1

# i put the count first so sort puts the biggest count first
pairs = []
for word in word_counts:
    pairs.append((word_counts[word], word))
pairs.sort(reverse=True)

word_names = []
word_values = []
for pair in pairs[:10]:
    word_values.append(pair[0])
    word_names.append(pair[1])
draw_bars(word_names, word_values,
          "top 10 first words of commands (every command counted)", "commands",
          os.path.join(out_folder, name + "_6_first_words.png"), False)

print("6 pictures saved in", out_folder)