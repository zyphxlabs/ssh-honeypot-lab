## Cowrie

Cowrie is a fake computer that gives fake SSH and Telnet access to an attacker. It has three modes.

**Medium interaction:** it is made in Python and mimics a real system but it is not actually a real system.

**High interaction (proxy mode):** Cowrie sits between the attacker and a real system, and watches everything that goes through and note attacker behaviour and tactics

**LLM mode:** an AI gives responses based on what the attacker does. For example suppose if they type `ls` in the terminal to list things it shows them an `ls` response.

### Features

- It has a fake filesystem. The `createfs` tool can be used to create your own.
- It logs files the attacker downloads with `wget` or anything else an attacker may host a web server and try to pull a script into the SSH session so Cowrie lets them do this but keep the copy and logs it.
- Every attempt the attacker makes is saved in the JSON file.

### The two logs

- `cowrie.log` is Cowrie's own log it holds things like start stop and errors.
- `cowrie.json` is the log of the attacker's attempts.
