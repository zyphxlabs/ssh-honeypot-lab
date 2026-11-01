# test_sessionize.py - tests for tools/sessionize.py
# run them from the repo folder with: python -m pytest tests -v
# the test data is made up in this file. no real log is used

import os
import sys
import json
import csv
import subprocess

# the script i test sits in the tools folder one level up from this file
here = os.path.dirname(os.path.abspath(__file__))
script = os.path.join(here, "..", "tools", "sessionize.py")

# makes one fake event as a dict. extra is a dict with more fields
def make_event(session, eventid, time, extra):
    event = {"session": session, "eventid": eventid, "timestamp": time, "src_ip": "ip-one"}
    for key in extra:
        event[key] = extra[key]
    return event

# writes the lines into a log file, runs sessionize.py on it and reads the csv it made
# it gives back the rows, the text the script printed and the path of the csv
def run_script(tmp_path, lines):
    log_path = os.path.join(str(tmp_path), "cowrie.json")
    out_path = os.path.join(str(tmp_path), "out.csv")

    f = open(log_path, "w", encoding="utf-8")
    f.write("\n".join(lines))
    f.close()

    # subprocess.run starts the script like i would in the terminal
    result = subprocess.run([sys.executable, script, log_path, out_path], capture_output=True, text=True)
    assert result.returncode == 0, result.stderr

    f = open(out_path, "r", encoding="utf-8", newline="")
    rows = list(csv.DictReader(f))
    f.close()
    return rows, result.stdout, out_path

# ---------- test 1: an empty file ----------

def test_empty_file(tmp_path):
    rows, printed, out_path = run_script(tmp_path, [])
    # no events and no sessions. the csv has only the header line
    assert rows == []
    assert "good events: 0" in printed
    assert "sessions: 0" in printed

# ---------- test 2: bad lines ----------

def test_bad_lines_are_skipped(tmp_path):
    lines = [
        json.dumps(make_event("s1", "cowrie.session.connect", "2026-10-31T10:00:00.000000Z", {})),
        "{this is broken",
        json.dumps({"eventid": "cowrie.session.connect"}),
        json.dumps(make_event("s1", "cowrie.session.closed", "2026-10-31T10:00:05.000000Z", {"duration_ms": 5000})),
    ]
    rows, printed, out_path = run_script(tmp_path, lines)
    # one broken line and one line without a session are skipped. the other two are good
    assert "skipped lines: 2" in printed
    assert "good events: 2" in printed
    assert len(rows) == 1
    assert rows[0]["has_close"] == "yes"
    assert rows[0]["duration_ms"] == "5000"

# ---------- test 3: a session with no close event ----------

def test_session_without_close(tmp_path):
    lines = [
        json.dumps(make_event("s1", "cowrie.session.connect", "2026-10-31T10:00:00.000000Z", {})),
        json.dumps(make_event("s1", "cowrie.login.success", "2026-10-31T10:00:01.000000Z", {})),
        json.dumps(make_event("s1", "cowrie.command.input", "2026-10-31T10:00:02.000000Z", {"input": "whoami"})),
    ]
    rows, printed, out_path = run_script(tmp_path, lines)
    assert len(rows) == 1
    assert rows[0]["has_close"] == "no"
    # no close event means no duration
    assert rows[0]["duration_ms"] == ""
    assert rows[0]["success_count"] == "1"
    assert rows[0]["command_count"] == "1"

# ---------- test 4: the password is never saved ----------

def test_password_is_never_saved(tmp_path):
    lines = [
        json.dumps(make_event("s1", "cowrie.session.connect", "2026-10-31T10:00:00.000000Z", {})),
        json.dumps(make_event("s1", "cowrie.login.failed", "2026-10-31T10:00:01.000000Z",
                              {"username": "someuser", "password": "notarealpassword"})),
    ]
    rows, printed, out_path = run_script(tmp_path, lines)
    # the failed login is counted
    assert rows[0]["fail_count"] == "1"

    # the password must not be in the sessions csv and not in the ip csv
    ips_path = out_path.replace(".csv", "_ips.csv")
    for path in [out_path, ips_path]:
        f = open(path, "r", encoding="utf-8")
        text = f.read()
        f.close()
        assert "notarealpassword" not in text