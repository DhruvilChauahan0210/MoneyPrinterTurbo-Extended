#!/usr/bin/env python3
"""Jev (TypeSafe System One) toolkit for the football-shorts channel.

Jev is text-only: it judges, it does not write, count or see frames. Every tool here
is a semantic judgment over text; Python owns all arithmetic and policy.

  python jev_tools.py dedup  "topic text"            # already covered? (vs batch_*.json)
  python jev_tools.py topics headlines.txt           # rank candidate topics (1 per line)
  python jev_tools.py screen script.txt              # claim / copyright / sensitivity risks
  python jev_tools.py comments comments.txt          # triage comments (1 per line)
"""
import glob
import json
import os
import re
import sys
from concurrent.futures import ThreadPoolExecutor

from typesafe_sdk import Choice, Noul, TypeSafeClient

ROOT = os.path.dirname(os.path.abspath(__file__))


def _load_key():
    p = os.path.join(ROOT, ".env")
    if os.environ.get("TYPESAFE_API_KEY") or not os.path.isfile(p):
        return
    for line in open(p):
        k, _, v = line.strip().partition("=")
        if k.strip() == "TYPESAFE_API_KEY":
            os.environ["TYPESAFE_API_KEY"] = v.strip().strip("\"'")


_load_key()
_client = TypeSafeClient()


def ask(state, questions):
    return _client.system_one(state=state, questions=questions).answers


def pmap(fn, items, workers=8):
    with ThreadPoolExecutor(max_workers=workers) as p:
        return list(p.map(fn, items))


# ---------------------------------------------------------------- corpus ----
def corpus(exclude_file=None):
    """Every topic we have already built: [{file, subject}] (minus `exclude_file`)."""
    out = []
    for f in sorted(glob.glob(os.path.join(ROOT, "batch_*.json"))):
        if exclude_file and os.path.basename(f) == os.path.basename(exclude_file):
            continue
        try:
            d = json.load(open(f))
        except Exception:
            continue
        for v in d.get("videos", []):
            s = (v.get("video_subject") or "").strip()
            if s:
                out.append({"file": os.path.basename(f)[6:-5], "subject": s})
    return out


_STOP = set("the a an of in on at to and or for with his her their he she it was is as by from that this "
            "after before when who which into over than then have has had been not but are were".split())


def _toks(s):
    return {w for w in re.findall(r"[a-z0-9]+", s.lower()) if w not in _STOP and len(w) > 2}


def shortlist(topic, docs, k=30):
    """Deliberately WIDE: Jev cannot pick a candidate the shortlist omitted."""
    t = _toks(topic)
    scored = sorted(docs, key=lambda d: -len(t & _toks(d["subject"] + " " + d["file"].replace("_", " "))))
    return scored[:k]


# ----------------------------------------------------------------- dedup ----
def dedup(topic, k=30, exclude_file=None):
    docs = shortlist(topic, corpus(exclude_file), k)

    def judge(d):
        a = ask({"new_topic": topic, "existing_short": d["subject"][:700]}, {
            "same_story": Noul(instructions=(
                "Is `existing_short` about the same specific story, incident or claim as "
                "`new_topic`, so that a viewer would feel they had already seen this video? "
                "Same player but a different incident is NO.")),
            "same_angle": Noul(instructions=(
                "Do `new_topic` and `existing_short` make essentially the same narrative "
                "point about the same moment, even if worded differently?")),
        })
        return {**d, "same": a["same_story"].noul, "angle": a["same_angle"].noul}

    res = sorted(pmap(judge, docs), key=lambda r: -max(r["same"], r["angle"]))
    return res


# ---------------------------------------------------------------- topics ----
TOPIC_Q = {
    "drama": Noul(instructions=(
        "Does this topic carry personal drama, conflict, controversy, a snub, a feud, "
        "a family or emotional story, or a shocking reveal -- rather than merely a "
        "statistic or a routine record?")),
    "curiosity_gap": Noul(instructions=(
        "Can this be framed so the viewer must keep watching to learn the outcome or "
        "reason (an open loop), instead of the headline giving everything away?")),
    "famous_star": Noul(instructions=(
        "Is the main subject a globally famous current-era superstar footballer?")),
    "filmable": Noul(instructions=(
        "Is the core event something that was actually filmed on camera in a match, "
        "ceremony, press conference or public moment (so real broadcast footage plausibly "
        "exists), rather than a private, off-camera or purely statistical matter?")),
    "debate": Noul(instructions=(
        "Would football fans split into two sides arguing in the comments about this?")),
}


def rank_topics(topics):
    docs = corpus()

    def one(t):
        a = ask({"topic": t}, TOPIC_Q)
        j = {k: a[k].noul for k in TOPIC_Q}
        dd = dedup(t, k=15)
        j["dup"] = max([max(r["same"], r["angle"]) for r in dd] or [0])
        j["dup_with"] = dd[0]["file"] if dd else ""
        # Hard gates first, then rank: filmable footage and non-duplicate are non-negotiable.
        j["ok"] = j["filmable"] >= 0.5 and j["dup"] < 0.5
        j["score"] = round(0.35 * j["drama"] + 0.25 * j["curiosity_gap"] + 0.15 * j["famous_star"]
                           + 0.25 * j["debate"], 3)
        return {"topic": t, **j}

    return sorted(pmap(one, topics, 4), key=lambda r: (not r["ok"], -r["score"]))


# ---------------------------------------------------------------- screen ----
SCREEN_Q = {
    "rumour_as_fact": Noul(instructions=(
        "Does this sentence state as settled fact something that is really a rumour, "
        "unconfirmed media report, or disputed allegation about a real person?")),
    "defamatory": Noul(instructions=(
        "Does this sentence accuse a real, named person of a crime, cheating, abuse, or "
        "serious misconduct in a way that could be defamatory if not proven?")),
    "invented_quote": Noul(instructions=(
        "Does this sentence put words in a real person's mouth in a way that looks like a "
        "literal quotation, which may be invented or paraphrased as if verbatim?")),
    "sensitive_exploit": Noul(instructions=(
        "Does this sentence exploit a death, illness, a child, or a private family tragedy "
        "for shock value in a tasteless way?")),
    "overclaim": Noul(instructions=(
        "Does this sentence contain an absolute or superlative claim ('first ever', 'never', "
        "'only player', exact figure) that is risky unless verified?")),
}


def screen(script):
    sents = [s.strip() for s in re.split(r"(?<=[.!?])\s+", script) if s.strip()]

    def one(s):
        a = ask({"sentence": s, "full_script": script}, SCREEN_Q)
        return {"sentence": s, **{k: a[k].noul for k in SCREEN_Q}}

    rows = pmap(one, sents)
    for r in rows:
        r["worst"] = max(r[k] for k in SCREEN_Q)
    return rows


# -------------------------------------------------------------- comments ----
def triage_comments(comments):
    def one(c):
        a = ask({"comment": c}, {
            "kind": Choice(instructions="What is the main nature of this YouTube comment on a football short?",
                           criteria={"debate_take": None, "question": None, "praise": None,
                                     "request_topic": None, "hate_or_abuse": None,
                                     "spam_or_promo": None, "other": None}),
            "pin_worthy": Noul(instructions=(
                "Would pinning this comment spark more good-faith debate or engagement from "
                "other viewers (a bold but civil take, a funny line, or a sharp question)?")),
            "short_idea": Noul(instructions=(
                "Does this comment suggest a specific topic, player, moment or question that "
                "would make a good follow-up football short?")),
        })
        return {"comment": c, "kind": a["kind"].choice, "pin": a["pin_worthy"].noul,
                "idea": a["short_idea"].noul}

    return pmap(one, comments)


# ------------------------------------------------------------- batch gate ----
DUP_BLOCK, DUP_WARN, RISK_BLOCK, RISK_WARN = 0.80, 0.55, 0.80, 0.50
# Only these flags can abort a build; the rest (invented_quote, sensitive_exploit,
# overclaim) are advisory warnings, since dramatic hooks trip them constantly.
BLOCKING_FLAGS = ("defamatory", "rumour_as_fact")


def preflight_gate(subject, script, batch_file):
    """Pre-render gate for batch_generator. Returns (blocks, warnings) as lists of str.

    Hard-blocks a near-duplicate topic and a high-risk sentence; fails OPEN (warning
    only) on any API error so a Jev outage never stops a build.
    """
    blocks, warns = [], []
    try:
        top = dedup(subject, k=30, exclude_file=batch_file)[:1]
        if top:
            d = max(top[0]["same"], top[0]["angle"])
            msg = f"duplicate topic {d:.2f} of [{top[0]['file']}]: {top[0]['subject'][:70]}"
            if d >= DUP_BLOCK:
                blocks.append(msg)
            elif d >= DUP_WARN:
                warns.append("possible " + msg)
        for r in screen(script or subject):
            flags = [k for k in SCREEN_Q if r[k] >= RISK_WARN]
            if not flags:
                continue
            msg = f"{r['worst']:.2f} {flags}: {r['sentence'][:90]}"
            hard = any(r[k] >= RISK_BLOCK for k in BLOCKING_FLAGS)
            (blocks if hard else warns).append("claim risk " + msg)
    except Exception as e:
        warns.append(f"Jev gate skipped (API error, failing open): {e}")
    return blocks, warns


# ------------------------------------------------------------------- cli ----
def _lines(p):
    return [l.strip() for l in open(p) if l.strip()]


def main(argv):
    if len(argv) < 3:
        print(__doc__)
        return 1
    cmd, arg = argv[1], argv[2]
    if cmd == "dedup":
        for r in dedup(arg)[:8]:
            print(f"same={r['same']:.2f} angle={r['angle']:.2f} [{r['file']}] {r['subject'][:90]}")
    elif cmd == "topics":
        for r in rank_topics(_lines(arg)):
            print(f"{'OK ' if r['ok'] else 'NO '} {r['score']:.2f} dup={r['dup']:.2f}({r['dup_with']}) "
                  f"film={r['filmable']:.2f} | {r['topic'][:80]}")
    elif cmd == "screen":
        txt = open(arg).read() if os.path.isfile(arg) else arg
        for r in sorted(screen(txt), key=lambda r: -r["worst"]):
            flags = [k for k in SCREEN_Q if r[k] >= 0.5]
            print(f"{r['worst']:.2f} {flags or '-'} {r['sentence'][:100]}")
    elif cmd == "comments":
        for r in sorted(triage_comments(_lines(arg)), key=lambda r: -(r["pin"] + r["idea"])):
            print(f"{r['kind']:<14} pin={r['pin']:.2f} idea={r['idea']:.2f} | {r['comment'][:80]}")
    else:
        print(__doc__)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
