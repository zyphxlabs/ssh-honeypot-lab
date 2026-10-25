# Concepts

## Honeypot

A honeypot is a fake computer environment to attract the attacker and record their behaviour and techniques so we get familiar with their ways. The things the attacker does are logged in `cowrie.json`. As there is no real system in a honeypot anyone who is there is suspicious.

Next come 3 types. The first is low where we give only fake services. The second is medium where we allow them to run commands but nothing is real. Cowrie is medium and I am going to use it in this project. The third is high where we give them a real system and this is dangerous too as the attacker may manipulate it to use against us.
