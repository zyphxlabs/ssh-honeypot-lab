# Public dataset: CyberLab honeynet

Label: PUBLIC DATASET. This is data collected by other people and it is not from my lab.

## What it is

So this is the CyberLab honeynet dataset and it holds everything that a Cowrie honeypot saw on about 50 nodes at universities and companies in the EU and the US from May 2019 to February 2020. The number of nodes moved around during the experiment so it was not always 50. I wanted it because my own lab data is simulated and I wanted some real attacker traffic to test my analysis on.

## Where it comes from

| Item | Value |
|---|---|
| Name | CyberLab honeynet dataset |
| Page | https://zenodo.org/records/3687527 |
| DOI | 10.5281/zenodo.3687527 |
| Collected by | Sedlar, Kren, Štefanič Južnič and Volk at the University of Ljubljana Faculty of Electrical Engineering |
| Published | February 29 2020 version 1.0 |
| License | CC BY 4.0 so I can reuse it if I give credit |
| Date range | files from 2019-05-13 to 2020-02-29 |
| Total size | 10.0 GB |
| Format | one `.json.gz` file per day |

## What I downloaded

I did not want 10 GB so I started with the smallest day `cyberlab_2019-05-13.json.gz` just to look at the format. That one day had 8860 connect events. After I saw it was fine I downloaded 1 to 7 November 2019 which is about 205 MB. I picked those days on purpose because before 8 November 2019 the honeypot ran as default low-interaction Cowrie 1.6.0 which is the same kind as my lab. After that date they put real Linux instances behind it so the traffic is not comparable. I also checked the md5 code of all 8 files against the Zenodo page and every single one matched.

## What is inside

Each file is one day starting at midnight UTC and it holds sessions and every session holds a list of events. The typed commands are not in an `input` field like in my own logs. They sit in the `message` field as `Command found:` and then the command. There is also a `hassh` field. The attacker IPs are pseudonymized so I cannot look them up later and I think I will need a small converter because the field names are different from my logs.

## Safety

It is text only. I never opened a link from inside it and I never ran anything from it. It sits in `data/public/` which is git-ignored so it never gets committed.

## Credit

Sedlar, U., Kren, M., Štefanič Južnič, L., & Volk, M. (2020). CyberLab honeynet dataset (Version 1.0) [Dataset]. Zenodo. https://doi.org/10.5281/zenodo.3687527
