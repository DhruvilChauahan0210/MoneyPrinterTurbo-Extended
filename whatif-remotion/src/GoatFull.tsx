import React from "react";
import { AbsoluteFill, Audio, Easing, Sequence, interpolate, random, staticFile, useCurrentFrame } from "remotion";
import timeline from "./goat_full_timeline.json";
import {
  FPS, COND, SANS, MESSI, RONALDO, GOLD, clamp, out, sp, mid,
  Background, Player, PhotoBg, Slam, Counter, Chip, SplitPlanet, DigitRain, BallIcon, CupIcon, Confetti, Panel, Label, WinnerStamp,
} from "./goatKit";

type Beat = { id: string; start: number; end: number; text: string };
const B: Record<string, { s: number; e: number }> = Object.fromEntries(
  (timeline as Beat[]).map((b) => [b.id, { s: Math.round(b.start * FPS), e: Math.round(b.end * FPS) }])
);
export const GOAT_FULL_DURATION = B.v7.e + 10 * FPS;

const inWin = (f: number, a: number, b: number) => f >= a && f < b;

/* ================= chapter card ================= */

const ChapterCard: React.FC<{ id: string; num: number; title: string }> = ({ id, num, title }) => {
  const f = useCurrentFrame();
  const s = B[id].s - 6;
  const e = B[id].e + 14;
  if (f < s || f > e + 12) return null;
  const inP = interpolate(f, [s, s + 10], [0, 1], { ...clamp, easing: out });
  const outP = interpolate(f, [e, e + 12], [0, 1], { ...clamp, easing: Easing.in(Easing.cubic) });
  const t = sp(f, s + 6, 12);
  const line = interpolate(f, [s + 8, s + 26], [0, 900], { ...clamp, easing: out });
  return (
    <AbsoluteFill style={{ opacity: 1 - outP }}>
      <AbsoluteFill style={{ background: "rgba(5,7,13,0.92)", clipPath: `inset(0 ${(1 - inP) * 100}% 0 0)` }} />
      <AbsoluteFill style={{ justifyContent: "center", alignItems: "center", transform: `scale(${1 + outP * 0.15})` }}>
        <div style={{ fontFamily: SANS, fontWeight: 700, fontSize: 36, letterSpacing: 22, color: GOLD, opacity: t }}>CHAPTER {num}</div>
        <div style={{ fontFamily: COND, fontWeight: 800, fontStyle: "italic", fontSize: 170, color: "white", lineHeight: 1.05, opacity: t, transform: `translateY(${(1 - t) * 50}px)`, textShadow: "0 12px 50px rgba(0,0,0,0.7)", whiteSpace: "nowrap" }}>
          {title}
        </div>
        <div style={{ width: line, height: 4, marginTop: 18, background: `linear-gradient(90deg, transparent, ${MESSI}, ${GOLD}, ${RONALDO}, transparent)` }} />
      </AbsoluteFill>
    </AbsoluteFill>
  );
};

/* ================= hook ================= */

const HookStat: React.FC<{ id: string; value: number; label: string; color: string; suffix?: string }> = ({ id, value, label, color, suffix = "" }) => {
  const f = useCurrentFrame();
  const b = B[id];
  if (f < b.s || f > b.e + 6) return null;
  const o = interpolate(f, [b.e, b.e + 6], [1, 0], clamp);
  return (
    <div style={{ position: "absolute", left: 0, right: 0, top: 650, textAlign: "center", opacity: o }}>
      <Counter value={value} from={b.s} dur={Math.min(36, b.e - b.s)} size={230} color={color} suffix={suffix} />
      <div style={{ fontFamily: SANS, fontWeight: 700, fontSize: 34, letterSpacing: 14, color: "white", marginTop: -6 }}>{label}</div>
    </div>
  );
};

const Hook: React.FC = () => {
  const f = useCurrentFrame();
  const end = B.c1t.s;
  const dim = interpolate(f, [B.h4.s, B.h4.s + 8, B.h5.s, B.h5.s + 6], [0, 0.75, 0.75, 0], clamp);
  const h6m = mid(B.h6, 0.45);
  const h7a = mid(B.h7, 0.22);
  const h7b = mid(B.h7, 0.42);
  return (
    <>
      <DigitRain from={B.h6.s} to={B.h7.e + 6} />
      <Player src="r_hook" side="R" from={B.h1.s} to={end} dim={dim} boxW={760} boxH={900} />
      <Player src="m_hook" side="L" from={B.h2.s} to={end} dim={dim} boxW={760} boxH={980} />
      <SplitPlanet from={B.h4.s} to={B.h5.s} />
      <HookStat id="h1" value={982} label="RONALDO · CAREER GOALS" color={RONALDO} />
      <HookStat id="h2" value={936} label="MESSI · CAREER GOALS" color={MESSI} />
      <HookStat id="h3" value={1900} label="GOALS BETWEEN THEM" color={GOLD} suffix="+" />
      <Slam text="ONE QUESTION" from={B.h4.s + 4} to={B.h5.s - 1} size={110} y={860} />
      <Slam text="WHO IS THE" from={B.h5.s} to={B.h6.s - 1} size={90} y={600} />
      <Slam text="G.O.A.T.?" from={B.h5.s + 8} to={B.h6.s - 1} size={300} color={GOLD} y={690} />
      <Slam text="WE SETTLE IT" from={B.h6.s} to={h6m} size={150} />
      <Slam text="WITH THE LATEST NUMBERS" from={h6m} to={B.h7.s - 1} size={120} color={GOLD} y={810} />
      <Slam text="NO OPINIONS." from={B.h7.s} to={h7a} size={150} stroke />
      <Slam text="JUST STATS." from={h7a} to={h7b} size={170} color={GOLD} />
      <Slam text="YOU'LL KNOW THE ANSWER" from={h7b} to={B.h8.s - 1} size={120} y={810} />
      <Slam text="LET'S GO!" from={B.h8.s} to={end - 4} size={260} />
    </>
  );
};

/* ================= chapter 1: origins ================= */

type Item = { at: number; year: string; text: string };
const Pin: React.FC<{ color: string }> = ({ color }) => (
  <div style={{ width: 22, height: 22, borderRadius: "50% 50% 50% 0", background: color, transform: "rotate(-45deg)", boxShadow: `0 0 16px ${color}` }} />
);

const OriginPanel: React.FC<{ side: "M" | "R"; place: string; placeAt: number; items: Item[]; to: number }> = ({ side, place, placeAt, items, to }) => {
  const f = useCurrentFrame();
  if (f < placeAt || f > to + 8) return null;
  const color = side === "M" ? MESSI : RONALDO;
  const o = interpolate(f, [to, to + 8], [1, 0], clamp);
  const p = sp(f, placeAt, 14);
  return (
    <Panel side={side} top={250} opacity={o}>
      <div style={{ display: "flex", alignItems: "center", gap: 14, flexDirection: side === "M" ? "row-reverse" : "row", opacity: p }}>
        <Pin color={color} />
        <div style={{ fontFamily: COND, fontWeight: 800, fontStyle: "italic", fontSize: 50, color: "white", whiteSpace: "nowrap" }}>{place}</div>
      </div>
      {items.map((it, i) => {
        if (f < it.at) return null;
        const q = sp(f, it.at, 13);
        return (
          <div key={i} style={{ display: "flex", alignItems: "center", gap: 16, flexDirection: side === "M" ? "row-reverse" : "row", transform: `translateX(${(1 - q) * (side === "M" ? 60 : -60)}px)`, opacity: q }}>
            <div style={{ background: color, color: "#0b0f1a", fontFamily: COND, fontWeight: 800, fontStyle: "italic", fontSize: 34, padding: "4px 14px", minWidth: 110, textAlign: "center" }}>{it.year}</div>
            <div style={{ fontFamily: SANS, fontWeight: 700, fontSize: 26, letterSpacing: 2, color: "white", whiteSpace: "nowrap" }}>{it.text}</div>
          </div>
        );
      })}
    </Panel>
  );
};

const Origins: React.FC = () => {
  const end = B.c2t.s;
  const panelsEnd = B.c1g.s;
  return (
    <>
      <Player src="m_young" side="L" from={B.c1a.s} to={end} boxW={760} boxH={920} />
      <Player src="r_young" side="R" from={B.c1d.s} to={end} boxW={780} boxH={960} />
      <OriginPanel side="M" place="ROSARIO, ARGENTINA" placeAt={B.c1a.s} to={panelsEnd} items={[
        { at: mid(B.c1a, 0.5), year: "AGE 10", text: "GROWTH HORMONE DEFICIENCY" },
        { at: mid(B.c1b, 0.55), year: "2000", text: "BARCELONA STEP IN" },
        { at: B.c1c.s, year: "AGE 13", text: "MOVES TO SPAIN" },
        { at: mid(B.c1c, 0.55), year: "2004", text: "DEBUT AT 17" },
      ]} />
      <OriginPanel side="R" place="MADEIRA, PORTUGAL" placeAt={B.c1d.s} to={panelsEnd} items={[
        { at: mid(B.c1d, 0.5), year: "AGE 12", text: "LEAVES HOME FOR LISBON" },
        { at: B.c1e.s, year: "2002", text: "SPORTING CP DEBUT" },
        { at: mid(B.c1e, 0.5), year: "2003", text: "MANCHESTER UNITED" },
        { at: B.c1f.s, year: "#7", text: "FERGUSON'S NUMBER SEVEN" },
      ]} />
      <Slam text="TWO KIDS." from={B.c1g.s} to={mid(B.c1g, 0.42)} size={140} y={330} />
      <Slam text="ONE RIVALRY." from={mid(B.c1g, 0.42)} to={end - 2} size={180} color={GOLD} y={330} />
    </>
  );
};

/* ================= chapter 2: head to head ================= */

type Stat =
  | { type: "num"; m: number; r: number; mAt: number; rAt: number; label: string; mSuffix: string; rSuffix: string; rPrefix?: string }
  | { type: "icons"; icon: "ball" | "cup"; m: number; r: number; mAt: number; rAt: number; mBadge?: string; rBadge?: string }
  | { type: "country" };
type Round = { n: number; title: string; m: string; r: string; winner: "M" | "R"; winAt: number; start: number; end: number; stat: Stat };

const ROUNDS: Round[] = [
  { n: 1, title: "GOALS", m: "m_goals", r: "r_goals", winner: "R", winAt: B.r1d.s,
    stat: { type: "num", m: 936, r: 982, mAt: B.r1c.s, rAt: B.r1b.s, label: "CAREER GOALS", mSuffix: "", rSuffix: "" } },
  { n: 2, title: "ASSISTS", m: "m_assists", r: "r_assists", winner: "M", winAt: B.r2d.s,
    stat: { type: "num", m: 400, r: 300, mAt: B.r2b.s, rAt: B.r2c.s, label: "CAREER ASSISTS", mSuffix: "+", rSuffix: "", rPrefix: "~" } },
  { n: 3, title: "BALLON D'OR", m: "m_bdo", r: "r_bdo", winner: "M", winAt: B.r3c.s,
    stat: { type: "icons", icon: "ball", m: 8, r: 5, mAt: B.r3b.s, rAt: mid(B.r3b, 0.55) } },
  { n: 4, title: "CHAMPIONS LEAGUE", m: "m_ucl", r: "r_ucl", winner: "R", winAt: B.r4d.s,
    stat: { type: "icons", icon: "cup", m: 4, r: 5, mAt: B.r4c.s, rAt: B.r4b.s, mBadge: "129 UCL GOALS", rBadge: "140 UCL GOALS · RECORD" } },
  { n: 5, title: "COUNTRY", m: "m_country", r: "r_country", winner: "M", winAt: B.r5d.s, stat: { type: "country" } },
].map((r, i, arr) => ({
  ...r,
  start: B[`r${r.n}a`].s - 10,
  end: i < arr.length - 1 ? B[`r${r.n + 1}a`].s - 10 : B.f1.s - 6,
})) as Round[];

const RoundBanner: React.FC<{ r: Round }> = ({ r }) => {
  const f = useCurrentFrame();
  const a = B[`r${r.n}a`];
  const s = r.start;
  const e = a.e + 4;
  if (f < s || f > e + 14) return null;
  const sweepIn = interpolate(f, [s, s + 9], [-1, 0], { ...clamp, easing: out });
  const sweepOut = interpolate(f, [e, e + 12], [0, 1], { ...clamp, easing: Easing.in(Easing.cubic) });
  const title = sp(f, s + 6, 11);
  const sub = sp(f, s + 14, 12);
  return (
    <AbsoluteFill style={{ overflow: "hidden" }}>
      <div style={{ position: "absolute", left: -300, top: 300, width: 2520, height: 480, transform: `translateX(${(sweepIn + sweepOut) * 2600}px) skewX(-14deg)`, background: `linear-gradient(90deg, ${MESSI} 0%, #1b2440 30%, #1b2440 70%, ${RONALDO} 100%)`, boxShadow: "0 0 80px rgba(0,0,0,0.8)" }} />
      <AbsoluteFill style={{ justifyContent: "center", alignItems: "center", transform: `translateX(${sweepOut * 2600}px)` }}>
        <div style={{ fontFamily: SANS, fontWeight: 700, fontSize: 34, letterSpacing: 18, color: GOLD, opacity: title, marginBottom: -10 }}>HEAD TO HEAD</div>
        <div style={{ fontFamily: COND, fontWeight: 800, fontStyle: "italic", fontSize: 220, lineHeight: 1, color: "white", transform: `scale(${interpolate(title, [0, 1], [2, 1])})`, opacity: title, textShadow: "0 12px 50px rgba(0,0,0,0.6)" }}>ROUND {r.n}</div>
        <div style={{ fontFamily: COND, fontWeight: 800, fontStyle: "italic", fontSize: 84, color: GOLD, transform: `translateY(${(1 - sub) * 40}px)`, opacity: sub, letterSpacing: 4 }}>{r.title}</div>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};

const RoundTag: React.FC<{ n: number | string; title: string; from: number; to: number }> = ({ n, title, from, to }) => {
  const f = useCurrentFrame();
  if (f < from || f > to) return null;
  const p = sp(f, from, 16);
  return (
    <div style={{ position: "absolute", left: 60, top: 54, display: "flex", alignItems: "center", gap: 14, transform: `translateX(${(1 - p) * -300}px)`, opacity: p }}>
      <div style={{ background: GOLD, color: "#111", fontFamily: COND, fontWeight: 800, fontStyle: "italic", fontSize: 30, padding: "4px 14px" }}>{n}</div>
      <div style={{ color: "white", fontFamily: COND, fontWeight: 800, fontStyle: "italic", fontSize: 30, letterSpacing: 2 }}>{title}</div>
    </div>
  );
};

const StatSide: React.FC<{ r: Round; side: "M" | "R" }> = ({ r, side }) => {
  const f = useCurrentFrame();
  const st = r.stat;
  const color = side === "M" ? MESSI : RONALDO;
  const name = side === "M" ? "MESSI" : "RONALDO";
  if (st.type === "num") {
    const at = side === "M" ? st.mAt : st.rAt;
    if (f < at) return null;
    const v = side === "M" ? st.m : st.r;
    const bar = interpolate(f, [at, at + 26], [0, v / Math.max(st.m, st.r)], { ...clamp, easing: out });
    return (
      <Panel side={side} top={540} opacity={sp(f, at, 14)}>
        <Label text={name} />
        <Counter value={v} from={at} size={190} color="white" prefix={side === "R" ? st.rPrefix ?? "" : ""} suffix={side === "M" ? st.mSuffix : st.rSuffix} />
        <div style={{ width: 460, height: 16, background: "rgba(255,255,255,0.1)", borderRadius: 8, overflow: "hidden", display: "flex", justifyContent: side === "M" ? "flex-end" : "flex-start" }}>
          <div style={{ width: `${bar * 100}%`, height: "100%", background: `linear-gradient(90deg, ${color}, white)`, boxShadow: `0 0 20px ${color}` }} />
        </div>
        <Label text={st.label} color={color} size={22} />
      </Panel>
    );
  }
  if (st.type === "icons") {
    const at = side === "M" ? st.mAt : st.rAt;
    if (f < at) return null;
    const count = side === "M" ? st.m : st.r;
    const Icon = st.icon === "ball" ? BallIcon : CupIcon;
    const perRow = st.icon === "ball" ? 4 : 5;
    const badge = side === "M" ? st.mBadge : st.rBadge;
    return (
      <Panel side={side} top={520}>
        <div style={{ opacity: sp(f, at) }}><Label text={name} /></div>
        <div style={{ fontFamily: COND, fontWeight: 800, fontStyle: "italic", fontSize: 170, lineHeight: 1, color: "white", opacity: sp(f, at), textShadow: `0 0 30px ${color}88` }}>{count}</div>
        <div style={{ display: "flex", flexWrap: "wrap", gap: 12, width: perRow * 84, justifyContent: side === "M" ? "flex-end" : "flex-start" }}>
          {Array.from({ length: count }).map((_, i) => {
            const p = sp(f, at + 4 + i * 3, 9);
            return (
              <div key={i} style={{ transform: `scale(${p}) translateY(${(1 - p) * -40}px)`, opacity: Math.min(1, p * 2) }}>
                <Icon />
              </div>
            );
          })}
        </div>
        {badge && <Chip at={at + 26} text={badge} color={color} textColor="white" />}
      </Panel>
    );
  }
  if (side === "R") {
    const at = B.r5b.s;
    if (f < at) return null;
    return (
      <Panel side="R" top={520} opacity={sp(f, at)}>
        <Label text="RONALDO" />
        <Counter value={146} from={mid(B.r5b, 0.6)} size={190} color="white" suffix="" />
        <Label text="INTERNATIONAL GOALS" color={RONALDO} size={22} />
        <Chip at={mid(B.r5b, 0.8)} text="ALL-TIME RECORD" color={RONALDO} textColor="white" />
      </Panel>
    );
  }
  const at = B.r5c.s;
  if (f < at) return null;
  const wc = mid(B.r5c, 0.6);
  return (
    <Panel side="M" top={500} opacity={sp(f, at)}>
      <Label text="MESSI" />
      <div style={{ display: "flex", alignItems: "baseline", gap: 14 }}>
        <Counter value={125} from={at} dur={20} size={110} color="white" suffix="" />
        <Label text="INT'L GOALS" color={MESSI} size={20} />
      </div>
      {f >= wc && (
        <>
          <div style={{ fontFamily: COND, fontWeight: 800, fontStyle: "italic", fontSize: 110, lineHeight: 1, color: GOLD, textShadow: `0 0 40px ${GOLD}aa`, transform: `scale(${interpolate(sp(f, wc, 10), [0, 1], [1.6, 1])})` }}>WORLD CHAMPION</div>
          <Label text="QATAR 2022" color="white" size={24} />
        </>
      )}
    </Panel>
  );
};

const Scoreboard: React.FC = () => {
  const f = useCurrentFrame();
  const show = ROUNDS[0].start + 20;
  if (f < show || f > B.f2.s + 8) return null;
  const m = ROUNDS.filter((r) => r.winner === "M" && f >= r.winAt).length;
  const r = ROUNDS.filter((x) => x.winner === "R" && f >= x.winAt).length;
  const finalP = interpolate(f, [B.f1.s - 4, B.f1.s + 14], [0, 1], { ...clamp, easing: Easing.inOut(Easing.cubic) });
  const gone = interpolate(f, [B.f2.s, B.f2.s + 6], [1, 0], clamp);
  const appear = sp(f, show, 16);
  const lastChange = Math.max(...ROUNDS.filter((x) => f >= x.winAt).map((x) => x.winAt), -100);
  const pop = f - lastChange < 20 ? 1 + 0.25 * Math.exp(-(f - lastChange) / 5) : 1;
  const cell = (name: string, val: number, color: string, leftSide: boolean) => (
    <div style={{ display: "flex", alignItems: "center", flexDirection: leftSide ? "row" : "row-reverse" }}>
      <div style={{ background: color, color: "#0b0f1a", fontFamily: COND, fontWeight: 800, fontStyle: "italic", fontSize: 30, padding: "8px 20px", letterSpacing: 2 }}>{name}</div>
      <div style={{ background: "#0b0f1a", color: "white", fontFamily: COND, fontWeight: 800, fontSize: 44, width: 74, textAlign: "center", transform: `scale(${pop})`, border: `2px solid ${color}` }}>{val}</div>
    </div>
  );
  return (
    <div style={{ position: "absolute", left: 0, right: 0, top: interpolate(finalP, [0, 1], [40, 150]), display: "flex", justifyContent: "center", opacity: appear * gone }}>
      <div style={{ display: "flex", alignItems: "center", gap: 10, transform: `scale(${interpolate(finalP, [0, 1], [1, 2.3]) * (0.8 + appear * 0.2)})`, transformOrigin: "50% 0%", boxShadow: "0 10px 40px rgba(0,0,0,0.6)" }}>
        {cell("MESSI", m, MESSI, true)}
        <div style={{ color: GOLD, fontFamily: COND, fontWeight: 800, fontSize: 36 }}>:</div>
        {cell("RONALDO", r, RONALDO, false)}
      </div>
    </div>
  );
};

const Glitch: React.FC<{ at: number }> = ({ at }) => {
  const f = useCurrentFrame();
  if (f < at || f > at + 26) return null;
  const k = f - at;
  return (
    <AbsoluteFill>
      <AbsoluteFill style={{ background: k % 4 < 2 ? "rgba(255,30,60,0.22)" : "rgba(40,200,255,0.12)", mixBlendMode: "screen" }} />
      {Array.from({ length: 8 }).map((_, i) => (
        <div key={i} style={{ position: "absolute", left: 0, right: 0, top: random(`gy${i}${k}`) * 1080, height: 4 + random(`gh${i}${k}`) * 30, background: "rgba(255,255,255,0.18)", transform: `translateX(${(random(`gx${i}${k}`) - 0.5) * 200}px)` }} />
      ))}
      <AbsoluteFill style={{ backgroundImage: "repeating-linear-gradient(0deg, rgba(0,0,0,0.25) 0 2px, transparent 2px 5px)" }} />
    </AbsoluteFill>
  );
};

const HeadToHead: React.FC = () => {
  const f = useCurrentFrame();
  const finalDim = interpolate(f, [B.f1.s - 4, B.f1.s + 10, B.f3.e + 10, B.f3.e + 20], [0, 0.6, 0.6, 0], clamp);
  return (
    <>
      {ROUNDS.map((r) => {
        const enter = B[`r${r.n}a`].e + 6;
        const dimM = r.winner === "R" && f >= r.winAt ? 1 : 0;
        const dimR = r.winner === "M" && f >= r.winAt ? 1 : 0;
        return (
          <React.Fragment key={r.n}>
            <Player src={r.m} side="L" from={enter} to={r.end} dim={dimM} win={!dimM && f >= r.winAt ? 1 : 0} />
            <Player src={r.r} side="R" from={enter} to={r.end} dim={dimR} win={!dimR && f >= r.winAt ? 1 : 0} />
          </React.Fragment>
        );
      })}
      <AbsoluteFill style={{ background: "linear-gradient(180deg, rgba(5,7,13,0.6) 0%, transparent 22%, transparent 55%, rgba(5,7,13,0.6) 100%)", opacity: inWin(f, ROUNDS[0].start, B.f1.s) ? 1 : 0 }} />
      {ROUNDS.map((r) =>
        inWin(f, r.start, r.end + 10) ? (
          <AbsoluteFill key={`s${r.n}`} style={{ opacity: interpolate(f, [r.end, r.end + 10], [1, 0], clamp) }}>
            <StatSide r={r} side="M" />
            <StatSide r={r} side="R" />
            <WinnerStamp at={r.winAt} to={r.end} side={r.winner} top={r.stat.type === "country" ? 380 : 400} />
            <RoundTag n={`ROUND ${r.n}`} title={r.title} from={B[`r${r.n}a`].e + 10} to={r.end} />
          </AbsoluteFill>
        ) : null
      )}
      <div style={{ position: "absolute", left: 958, top: 140, width: 4, height: 940, background: `linear-gradient(180deg, transparent, ${GOLD}, transparent)`, opacity: inWin(f, ROUNDS[0].start, B.f1.s) ? 0.5 : 0 }} />
      <Confetti at={B.r5d.s} x={640} />
      {ROUNDS.map((r) => <RoundBanner key={`b${r.n}`} r={r} />)}
      <AbsoluteFill style={{ background: "#05070d", opacity: finalDim }} />
      <Player src="m_hook" side="L" from={B.f1.s} to={B.f2.s} win={1} boxW={700} boxH={860} />
      <Player src="r_hook" side="R" from={B.f1.s} to={B.f2.s} dim={0.6} boxW={700} boxH={800} />
      <Scoreboard />
      <Slam text="TO MESSI" from={B.f1.e - 30} to={B.f2.s - 1} size={130} color={MESSI} y={890} />
      <Slam text="BUT WAIT…" from={B.f2.s} to={B.f3.s - 1} size={240} color={RONALDO} y={400} />
      <Slam text="THE NEXT NUMBERS" from={B.f3.s} to={B.f3.e + 10} size={120} y={380} />
      <Slam text="CHANGE EVERYTHING" from={mid(B.f3, 0.5)} to={B.f3.e + 10} size={150} color={GOLD} y={520} />
    </>
  );
};

/* ================= chapter 3: hidden numbers ================= */

const DuelRow: React.FC<{ name: string; color: string; value: number; at: number; max: number; decimals?: number; prefix?: string; suffix?: string }> = ({ name, color, value, at, max, decimals = 0, prefix = "", suffix = "" }) => {
  const f = useCurrentFrame();
  if (f < at) return <div style={{ height: 150 }} />;
  const p = sp(f, at, 14);
  const bar = interpolate(f, [at, at + 30], [0, value / max], { ...clamp, easing: out });
  return (
    <div style={{ display: "flex", alignItems: "center", gap: 26, height: 150, opacity: p, transform: `translateX(${(1 - p) * -80}px)` }}>
      <div style={{ width: 230, fontFamily: COND, fontWeight: 800, fontStyle: "italic", fontSize: 50, color, textAlign: "right" }}>{name}</div>
      <div style={{ width: 280, textAlign: "right" }}>
        <Counter value={value} from={at} size={120} color="white" decimals={decimals} prefix={prefix} suffix={suffix} />
      </div>
      <div style={{ width: 420, height: 26, background: "rgba(255,255,255,0.08)", borderRadius: 13, overflow: "hidden" }}>
        <div style={{ width: `${bar * 100}%`, height: "100%", background: `linear-gradient(90deg, ${color}, white)`, boxShadow: `0 0 24px ${color}` }} />
      </div>
    </div>
  );
};

const DuelCard: React.FC<{ from: number; to: number; title: string; children: React.ReactNode }> = ({ from, to, title, children }) => {
  const f = useCurrentFrame();
  if (f < from || f > to + 10) return null;
  const p = sp(f, from, 15);
  const o = interpolate(f, [to, to + 10], [1, 0], clamp);
  return (
    <div style={{ position: "absolute", left: 360, top: 200, width: 1200, padding: "34px 50px", background: "linear-gradient(160deg, rgba(20,26,46,0.92), rgba(8,10,20,0.92))", border: "1px solid rgba(255,255,255,0.14)", borderRadius: 24, boxShadow: "0 40px 100px rgba(0,0,0,0.7)", opacity: p * o, transform: `translateY(${(1 - p) * 80}px) scale(${0.94 + p * 0.06})` }}>
      <div style={{ fontFamily: COND, fontWeight: 800, fontStyle: "italic", fontSize: 64, color: GOLD, letterSpacing: 3, marginBottom: 10 }}>{title}</div>
      {children}
    </div>
  );
};

const HiddenNumbers: React.FC = () => {
  const f = useCurrentFrame();
  const s = B.c4t.e + 8;
  const end = B.c3t.s;
  const goal = 982;
  const roadP = interpolate(f, [B.c4i.s, B.c4i.s + 60], [0, goal / 1000], { ...clamp, easing: out });
  const leagues = ["PORTUGAL", "ENGLAND", "SPAIN", "ITALY", "SAUDI ARABIA"];
  return (
    <>
      <Player src="m_hook" side="L" from={s} to={end} dim={0.55} boxW={620} boxH={820} />
      <Player src="r_hook" side="R" from={s} to={end} dim={0.55} boxW={620} boxH={780} />
      <AbsoluteFill style={{ background: "rgba(5,7,13,0.35)", opacity: inWin(f, s, end) ? 1 : 0 }} />
      <RoundTag n="CH 3" title="THE HIDDEN NUMBERS" from={s} to={end} />
      <DuelCard from={B.c4a.s - 4} to={B.c4d.s - 6} title="GAMES PLAYED">
        <DuelRow name="RONALDO" color={RONALDO} value={1340} at={mid(B.c4a, 0.45)} max={1340} />
        <DuelRow name="MESSI" color={MESSI} value={1182} at={mid(B.c4b, 0.2)} max={1340} />
        <div style={{ display: "flex", gap: 14, flexWrap: "wrap", marginTop: 8 }}>
          <Chip at={mid(B.c4c, 0.4)} text="+158 GAMES FOR RONALDO" color={RONALDO} textColor="white" />
          {leagues.map((l, i) => <Chip key={l} at={mid(B.c4c2, 0.3 + i * 0.13)} text={l} color="rgba(255,255,255,0.9)" size={26} />)}
        </div>
      </DuelCard>
      <DuelCard from={B.c4d.s - 4} to={B.c4g.s - 6} title="GOALS PER GAME">
        <DuelRow name="MESSI" color={MESSI} value={0.79} at={mid(B.c4d, 0.55)} max={0.79} decimals={2} />
        <DuelRow name="RONALDO" color={RONALDO} value={0.73} at={mid(B.c4e, 0.3)} max={0.79} decimals={2} />
        <div style={{ marginTop: 8 }}><Chip at={mid(B.c4f, 0.6)} text="EFFICIENCY → MESSI" color={MESSI} /></div>
      </DuelCard>
      <DuelCard from={B.c4g.s - 4} to={B.c4i.s - 6} title="TROPHIES">
        <DuelRow name="MESSI" color={MESSI} value={48} at={mid(B.c4g, 0.2)} max={48} prefix="~" />
        <DuelRow name="RONALDO" color={RONALDO} value={37} at={mid(B.c4g, 0.65)} max={48} prefix="~" />
        <div style={{ marginTop: 8 }}><Chip at={mid(B.c4h, 0.5)} text="MOST DECORATED IN HISTORY" color={GOLD} /></div>
      </DuelCard>
      <DuelCard from={B.c4i.s - 4} to={end - 8} title="RONALDO · ROAD TO 1,000">
        <div style={{ display: "flex", alignItems: "baseline", gap: 20, marginTop: 10 }}>
          <Counter value={982} from={B.c4i.s} dur={60} size={200} color="white" suffix="" />
          <div style={{ fontFamily: COND, fontWeight: 800, fontStyle: "italic", fontSize: 70, color: "rgba(255,255,255,0.4)" }}>/ 1,000</div>
        </div>
        <div style={{ position: "relative", height: 44, background: "rgba(255,255,255,0.08)", borderRadius: 22, overflow: "hidden", marginTop: 14 }}>
          <div style={{ width: `${roadP * 100}%`, height: "100%", background: `linear-gradient(90deg, #7a1020, ${RONALDO}, #ffd0d6)`, boxShadow: `0 0 30px ${RONALDO}` }} />
          {[250, 500, 750].map((m) => <div key={m} style={{ position: "absolute", top: 0, bottom: 0, left: `${m / 10}%`, width: 2, background: "rgba(255,255,255,0.25)" }} />)}
        </div>
        {f >= mid(B.c4j, 0.5) && (
          <div style={{ marginTop: 22, fontFamily: COND, fontWeight: 800, fontStyle: "italic", fontSize: 90, color: RONALDO, textShadow: `0 0 40px ${RONALDO}`, transform: `scale(${(1 + 0.04 * Math.sin(f / 4)) * interpolate(sp(f, mid(B.c4j, 0.5), 9), [0, 1], [1.8, 1])})`, transformOrigin: "0% 50%" }}>
            ONLY 18 TO GO
          </div>
        )}
      </DuelCard>
    </>
  );
};

/* ================= chapter 4: spain years ================= */

const BALLON_YEARS: [number, "M" | "R"][] = [[2008, "R"], [2009, "M"], [2010, "M"], [2011, "M"], [2012, "M"], [2013, "R"], [2014, "R"], [2015, "M"], [2016, "R"], [2017, "R"]];

const BallonRow: React.FC<{ from: number; to: number }> = ({ from, to }) => {
  const f = useCurrentFrame();
  if (f < from || f > to + 10) return null;
  const o = interpolate(f, [from, from + 8, to, to + 10], [0, 1, 1, 0], clamp);
  const per = Math.max(6, Math.floor((to - from - 40) / 10));
  return (
    <AbsoluteFill style={{ opacity: o }}>
      <AbsoluteFill style={{ background: "rgba(5,7,13,0.78)" }} />
      <div style={{ position: "absolute", top: 230, left: 0, right: 0, textAlign: "center", fontFamily: COND, fontWeight: 800, fontStyle: "italic", fontSize: 80, color: "white" }}>
        10 BALLON D'ORS · <span style={{ color: GOLD }}>10 YEARS IN A ROW</span>
      </div>
      <div style={{ position: "absolute", top: 420, left: 110, right: 110, display: "flex", justifyContent: "space-between" }}>
        {BALLON_YEARS.map(([y, w], i) => {
          const at = from + 10 + i * per;
          const p = sp(f, at, 10);
          const c = w === "M" ? MESSI : RONALDO;
          return (
            <div key={y} style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: 14, opacity: Math.min(1, p * 2), transform: `translateY(${(1 - p) * -60}px) scale(${p})` }}>
              <div style={{ borderRadius: "50%", padding: 6, border: `5px solid ${c}`, boxShadow: `0 0 26px ${c}` }}><BallIcon size={110} /></div>
              <div style={{ fontFamily: COND, fontWeight: 800, fontStyle: "italic", fontSize: 40, color: "white" }}>{y}</div>
              <div style={{ background: c, color: "#0b0f1a", fontFamily: COND, fontWeight: 800, fontStyle: "italic", fontSize: 30, padding: "2px 12px" }}>{w === "M" ? "MESSI" : "RONALDO"}</div>
            </div>
          );
        })}
      </div>
      <div style={{ position: "absolute", top: 780, left: 0, right: 0, display: "flex", justifyContent: "center", gap: 30 }}>
        <Chip at={from + 10 + 10 * per} text="MESSI 5  ·  RONALDO 5" color={GOLD} size={44} />
      </div>
    </AbsoluteFill>
  );
};

const SpainYears: React.FC = () => {
  const f = useCurrentFrame();
  const s = B.c3t.e + 8;
  const end = B.c5t.s;
  const panelsEnd = B.s6.s;
  const clasico = B.s6.s;
  const barca = "linear-gradient(90deg, rgba(165,0,68,0.28) 0%, rgba(0,77,152,0.22) 30%, transparent 50%, rgba(255,255,255,0.08) 70%, rgba(254,190,16,0.14) 100%)";
  return (
    <>
      <AbsoluteFill style={{ background: barca, opacity: inWin(f, s, end) ? 1 : 0 }} />
      <Player src="m_spain" side="L" from={B.s1.s} to={end} dim={f >= B.s7.s ? 0 : 0} win={f >= B.s7.s ? 1 : 0} boxW={720} boxH={960} />
      <Player src="r_spain" side="R" from={B.s1.s} to={end} dim={f >= B.s7.s ? 0.8 : 0} boxW={900} boxH={940} />
      <RoundTag n="CH 4" title="THE SPAIN YEARS · 2009–2018" from={s} to={end} />
      <Slam text="LA LIGA BECAME A WAR" from={mid(B.s1, 0.6)} to={B.s1b.s - 2} size={120} color={GOLD} y={150} />
      <BallonRow from={B.s1b.s} to={B.s2.s - 4} />
      {inWin(f, B.s2.s, panelsEnd + 10) && (
        <AbsoluteFill style={{ opacity: interpolate(f, [panelsEnd, panelsEnd + 10], [1, 0], clamp) }}>
          <Panel side="R" top={260} opacity={sp(f, B.s2.s)}>
            <Label text="RONALDO · REAL MADRID" color={RONALDO} />
            <div style={{ display: "flex", alignItems: "baseline", gap: 14 }}>
              <Counter value={450} from={mid(B.s2, 0.25)} size={150} color="white" suffix="" />
              <Label text="GOALS" size={24} />
            </div>
            {f >= mid(B.s2, 0.6) && (
              <div style={{ display: "flex", alignItems: "baseline", gap: 14 }}>
                <Counter value={438} from={mid(B.s2, 0.6)} size={110} color="rgba(255,255,255,0.75)" suffix="" />
                <Label text="GAMES" size={24} />
              </div>
            )}
            <Chip at={B.s3.s} text="MORE GOALS THAN GAMES" color={RONALDO} textColor="white" />
            <Chip at={mid(B.s3, 0.5)} text="MADRID'S ALL-TIME TOP SCORER" color="white" />
          </Panel>
          {f >= B.s4.s && (
            <Panel side="M" top={260} opacity={sp(f, B.s4.s)}>
              <Label text="MESSI · BARCELONA" color={MESSI} />
              <div style={{ display: "flex", alignItems: "baseline", gap: 14, flexDirection: "row-reverse" }}>
                <Counter value={672} from={mid(B.s4, 0.2)} size={150} color="white" suffix="" />
                <Label text="GOALS" size={24} />
              </div>
              <Chip at={mid(B.s4, 0.6)} text="BARÇA'S ALL-TIME TOP SCORER" color="white" />
              {f >= B.s5.s && (
                <div style={{ display: "flex", alignItems: "baseline", gap: 14, flexDirection: "row-reverse" }}>
                  <Counter value={474} from={mid(B.s5, 0.35)} size={110} color={GOLD} suffix="" />
                  <Label text="LA LIGA GOALS" size={22} />
                </div>
              )}
              <Chip at={mid(B.s5, 0.7)} text="LEAGUE RECORD" color={MESSI} />
            </Panel>
          )}
        </AbsoluteFill>
      )}
      <DuelCard from={clasico} to={end - 8} title="EL CLÁSICO · GOALS">
        <DuelRow name="MESSI" color={MESSI} value={26} at={mid(B.s6, 0.62)} max={26} />
        <DuelRow name="RONALDO" color={RONALDO} value={18} at={mid(B.s6, 0.85)} max={26} />
      </DuelCard>
      <WinnerStamp at={B.s7.s + 6} to={end} side="M" text="SPAIN → MESSI" top={640} />
    </>
  );
};

/* ================= chapter 5: records ================= */

const RecordCard: React.FC<{ at: number; num: string; text: string; color: string; side: "M" | "R" }> = ({ at, num, text, color, side }) => {
  const f = useCurrentFrame();
  if (f < at) return null;
  const p = sp(f, at, 13);
  return (
    <div style={{ display: "flex", alignItems: "center", gap: 20, flexDirection: side === "M" ? "row-reverse" : "row", opacity: p, transform: `translateX(${(1 - p) * (side === "M" ? 120 : -120)}px)`, background: "rgba(10,14,26,0.85)", borderLeft: side === "R" ? `6px solid ${color}` : undefined, borderRight: side === "M" ? `6px solid ${color}` : undefined, padding: "12px 22px", width: 500, justifyContent: "flex-start" }}>
      <div style={{ fontFamily: COND, fontWeight: 800, fontStyle: "italic", fontSize: 88, lineHeight: 1, color, minWidth: 120, textAlign: "center", textShadow: `0 0 26px ${color}88` }}>{num}</div>
      <div style={{ fontFamily: SANS, fontWeight: 700, fontSize: 26, letterSpacing: 2, color: "white", lineHeight: 1.25, whiteSpace: "pre-line", textAlign: side === "M" ? "right" : "left" }}>{text}</div>
    </div>
  );
};

const Records: React.FC = () => {
  const f = useCurrentFrame();
  const s = B.c5t.e + 8;
  const end = B.c6t.s;
  if (f < B.c5a.s - 2 || f > end + 12) return null;
  return (
    <AbsoluteFill style={{ opacity: interpolate(f, [end, end + 10], [1, 0], clamp) }}>
      <Player src="r_records" side="R" from={B.c5a.s} to={end} boxW={700} boxH={980} />
      <Player src="m_records" side="L" from={B.c5c.s} to={end} boxW={820} boxH={900} />
      <RoundTag n="CH 5" title="RECORDS ONLY ONE MAN HOLDS" from={s} to={end} />
      <div style={{ position: "absolute", left: 1010, top: 250, display: "flex", flexDirection: "column", gap: 22 }}>
        <RecordCard at={mid(B.c5a, 0.1)} num="146" text={"MOST INTERNATIONAL\nGOALS EVER"} color={RONALDO} side="R" />
        <RecordCard at={mid(B.c5a, 0.55)} num="140" text={"MOST CHAMPIONS\nLEAGUE GOALS"} color={RONALDO} side="R" />
        <RecordCard at={mid(B.c5b, 0.2)} num="5" text={"WORLD CUPS\nSCORED AT"} color={RONALDO} side="R" />
      </div>
      <div style={{ position: "absolute", left: 410, top: 250, display: "flex", flexDirection: "column", gap: 22 }}>
        <RecordCard at={mid(B.c5c, 0.15)} num="8" text={"BALLON D'OR\nWINS"} color={MESSI} side="M" />
        <RecordCard at={mid(B.c5d, 0.2)} num="2×" text={"WORLD CUP\nGOLDEN BALL"} color={MESSI} side="M" />
        <RecordCard at={mid(B.c5e, 0.15)} num="91" text={"GOALS IN ONE\nYEAR (2012)"} color={MESSI} side="M" />
      </div>
    </AbsoluteFill>
  );
};

/* ================= chapter 6: last dance ================= */

const Scorebug: React.FC<{ at: number; to: number }> = ({ at, to }) => {
  const f = useCurrentFrame();
  if (f < at || f > to + 8) return null;
  const p = sp(f, at, 13);
  const o = interpolate(f, [to, to + 8], [1, 0], clamp);
  const team = (name: string, bg: string, fg: string) => (
    <div style={{ background: bg, color: fg, fontFamily: COND, fontWeight: 800, fontStyle: "italic", fontSize: 64, padding: "10px 34px", minWidth: 330, textAlign: "center" }}>{name}</div>
  );
  return (
    <div style={{ position: "absolute", left: 0, right: 0, top: 700, display: "flex", flexDirection: "column", alignItems: "center", opacity: p * o, transform: `translateY(${(1 - p) * 60}px)` }}>
      <div style={{ fontFamily: SANS, fontWeight: 700, fontSize: 30, letterSpacing: 12, color: GOLD, marginBottom: 12 }}>WORLD CUP 2026 · FINAL</div>
      <div style={{ display: "flex", alignItems: "stretch", boxShadow: "0 20px 60px rgba(0,0,0,0.7)" }}>
        {team("SPAIN", "#c60b1e", "#ffc400")}
        <div style={{ background: "#0b0f1a", color: "white", fontFamily: COND, fontWeight: 800, fontSize: 80, padding: "4px 30px" }}>1 – 0</div>
        {team("ARGENTINA", "#75aadb", "white")}
      </div>
      <div style={{ fontFamily: SANS, fontWeight: 700, fontSize: 26, letterSpacing: 8, color: "white", marginTop: 12 }}>AFTER EXTRA TIME</div>
    </div>
  );
};

const LastDance: React.FC = () => {
  const f = useCurrentFrame();
  const s = B.c6t.e + 8;
  const end = B.v1.s;
  return (
    <>
      <Player src="m_now" side="L" from={B.c6a.s} to={B.c6c.s} boxW={900} boxH={860} />
      <Player src="m_now" side="L" from={B.c6e.s} to={end} boxW={900} boxH={860} />
      <Player src="r_now" side="R" from={B.c6d.s} to={end} boxW={720} boxH={1000} />
      <RoundTag n="CH 6" title="THE LAST DANCE" from={s} to={end} />
      {inWin(f, B.c6a.s, B.c6c.s + 8) && (
        <AbsoluteFill style={{ opacity: interpolate(f, [B.c6c.s - 2, B.c6c.s + 8], [1, 0], clamp) }}>
          <Panel side="R" top={280} opacity={sp(f, B.c6a.s)}>
            <Label text="MESSI · ARGENTINA" color={MESSI} />
            <div style={{ fontFamily: COND, fontWeight: 800, fontStyle: "italic", fontSize: 110, lineHeight: 1, color: "white" }}>WORLD CUP 2026</div>
            <Chip at={mid(B.c6a, 0.45)} text="AGE 39" color={MESSI} />
            {f >= B.c6b.s && (
              <div style={{ display: "flex", gap: 40 }}>
                <div><Counter value={8} from={B.c6b.s} dur={14} size={150} color={GOLD} suffix="" /><Label text="GOALS" size={22} /></div>
                <div><Counter value={4} from={mid(B.c6b, 0.5)} dur={12} size={150} color={GOLD} suffix="" /><Label text="ASSISTS" size={22} /></div>
              </div>
            )}
          </Panel>
        </AbsoluteFill>
      )}
      <PhotoBg src="bg_final_loss.jpg" from={B.c6c.s} to={B.c6m.s - 4} dark={0.6} gray={0.5} />
      <Scorebug at={mid(B.c6c, 0.35)} to={B.c6m.s - 4} />
      <PhotoBg src="bg_miami.jpg" from={B.c6m.s} to={B.c6d.s - 4} dark={0.5} />
      {inWin(f, B.c6m.s, B.c6d.s) && (
        <div style={{ position: "absolute", left: 0, right: 0, top: 760, display: "flex", flexDirection: "column", alignItems: "center", gap: 12 }}>
          <Chip at={mid(B.c6m, 0.3)} text="INTER MIAMI · MLS CUP CHAMPIONS 2025" color="#f7b5cd" size={52} />
          <Chip at={mid(B.c6m, 0.6)} text="THE CLUB'S FIRST EVER" color="white" size={34} />
        </div>
      )}
      {inWin(f, B.c6d.s, B.c6e.s + 8) && (
        <AbsoluteFill style={{ opacity: interpolate(f, [B.c6e.s - 2, B.c6e.s + 8], [1, 0], clamp) }}>
          <Panel side="M" top={280} opacity={sp(f, B.c6d.s)}>
            <Label text="RONALDO · AL NASSR" color={RONALDO} />
            <div style={{ display: "flex", alignItems: "baseline", gap: 14, flexDirection: "row-reverse" }}>
              <Counter value={41} from={mid(B.c6d, 0.15)} dur={20} size={190} color="white" suffix="" />
              <Label text="YEARS OLD" size={24} />
            </div>
            <Chip at={mid(B.c6d, 0.6)} text="STILL SCORING EVERY WEEK" color={RONALDO} textColor="white" />
            <Chip at={mid(B.c6g, 0.2)} text="2× SAUDI PRO LEAGUE GOLDEN BOOT" color={GOLD} />
            <Chip at={mid(B.c6g, 0.6)} text="982 GOALS · 18 TO 1,000" color="white" />
          </Panel>
        </AbsoluteFill>
      )}
      <Slam text="STILL REFUSING TO STOP" from={mid(B.c6e, 0.3)} to={end - 4} size={130} color={GOLD} y={140} />
    </>
  );
};

/* ================= verdict ================= */

const Check: React.FC<{ at: number; text: string; color: string; side: "M" | "R" }> = ({ at, text, color, side }) => {
  const f = useCurrentFrame();
  if (f < at) return null;
  const p = sp(f, at, 12);
  return (
    <div style={{ display: "flex", alignItems: "center", gap: 16, flexDirection: side === "M" ? "row-reverse" : "row", opacity: p, transform: `translateX(${(1 - p) * (side === "M" ? 60 : -60)}px)` }}>
      <div style={{ width: 46, height: 46, borderRadius: 10, background: color, display: "flex", justifyContent: "center", alignItems: "center", color: "#0b0f1a", fontFamily: SANS, fontWeight: 900, fontSize: 32, transform: `scale(${interpolate(p, [0, 1], [1.8, 1])})` }}>✓</div>
      <div style={{ fontFamily: COND, fontWeight: 800, fontStyle: "italic", fontSize: 46, color: "white", whiteSpace: "nowrap" }}>{text}</div>
    </div>
  );
};

const CommentPrompt: React.FC<{ from: number; to: number }> = ({ from, to }) => {
  const f = useCurrentFrame();
  if (f < from || f > to + 8) return null;
  const p = sp(f, from, 13);
  const o = interpolate(f, [to, to + 8], [1, 0], clamp);
  const pulse = (k: number) => 1 + 0.05 * Math.sin((f - from) / 5 + k);
  return (
    <div style={{ position: "absolute", left: 460, top: 300, width: 1000, opacity: p * o, transform: `translateY(${(1 - p) * 60}px)` }}>
      <div style={{ background: "rgba(18,22,36,0.95)", borderRadius: 24, padding: "30px 38px", border: "1px solid rgba(255,255,255,0.15)", boxShadow: "0 30px 80px rgba(0,0,0,0.7)" }}>
        <div style={{ display: "flex", alignItems: "center", gap: 18 }}>
          <div style={{ width: 64, height: 64, borderRadius: "50%", background: `linear-gradient(135deg, ${MESSI}, ${RONALDO})` }} />
          <div style={{ fontFamily: SANS, fontWeight: 600, fontSize: 34, color: "rgba(255,255,255,0.6)" }}>Add a comment…</div>
        </div>
        <div style={{ fontFamily: COND, fontWeight: 800, fontStyle: "italic", fontSize: 76, color: "white", marginTop: 20 }}>WHO'S YOUR G.O.A.T.?</div>
        <div style={{ display: "flex", gap: 30, marginTop: 24 }}>
          <div style={{ flex: 1, textAlign: "center", background: MESSI, color: "#0b0f1a", fontFamily: COND, fontWeight: 800, fontStyle: "italic", fontSize: 64, padding: "14px 0", borderRadius: 16, transform: `scale(${pulse(0)})` }}>MESSI</div>
          <div style={{ flex: 1, textAlign: "center", background: RONALDO, color: "white", fontFamily: COND, fontWeight: 800, fontStyle: "italic", fontSize: 64, padding: "14px 0", borderRadius: 16, transform: `scale(${pulse(Math.PI)})` }}>RONALDO</div>
        </div>
      </div>
    </div>
  );
};

const EndCard: React.FC<{ from: number }> = ({ from }) => {
  const f = useCurrentFrame();
  if (f < from) return null;
  const p = sp(f, from, 12);
  const btn = sp(f, from + 18, 10);
  const pulse = 1 + 0.04 * Math.sin((f - from) / 4);
  return (
    <AbsoluteFill style={{ justifyContent: "center", alignItems: "center", background: `rgba(5,7,13,${0.88 * Math.min(1, p * 1.5)})` }}>
      <div style={{ fontFamily: SANS, fontWeight: 700, fontSize: 36, letterSpacing: 18, color: GOLD, opacity: p }}>THE DEBATE NEVER ENDS</div>
      <div style={{ fontFamily: COND, fontWeight: 800, fontStyle: "italic", fontSize: 150, color: "white", opacity: p, transform: `scale(${interpolate(p, [0, 1], [1.4, 1])})` }}>
        <span style={{ color: MESSI }}>MESSI</span> <span style={{ color: GOLD }}>vs</span> <span style={{ color: RONALDO }}>RONALDO</span>
      </div>
      <div style={{ marginTop: 34, display: "flex", alignItems: "center", gap: 22, transform: `scale(${btn * pulse})` }}>
        <div style={{ background: "#ff0033", color: "white", fontFamily: SANS, fontWeight: 800, fontSize: 44, padding: "18px 50px", borderRadius: 14, boxShadow: "0 0 40px rgba(255,0,51,0.6)" }}>SUBSCRIBE</div>
        <div style={{ fontFamily: SANS, fontWeight: 600, fontSize: 32, color: "rgba(255,255,255,0.8)" }}>for the next battle</div>
      </div>
    </AbsoluteFill>
  );
};

const Verdict: React.FC = () => {
  const f = useCurrentFrame();
  const s = B.v1.s;
  const listsEnd = B.v5.s;
  const mWin = f >= B.v4.s;
  return (
    <>
      <Player src="m_hook" side="L" from={s} to={B.v7.s + 30} win={mWin ? 1 : 0} boxW={720} boxH={900} />
      <Player src="r_hook" side="R" from={s} to={B.v7.s + 30} dim={mWin && f < B.v5.s ? 0.5 : 0} boxW={720} boxH={860} />
      <AbsoluteFill style={{ background: "rgba(5,7,13,0.3)", opacity: f >= s ? 1 : 0 }} />
      <RoundTag n="VERDICT" title="WHO WINS?" from={B.v1b.s} to={B.v7.s} />
      <Slam text="SO… WHO WINS?" from={s} to={B.v1b.s - 1} size={200} color={GOLD} y={420} />
      <Slam text="LET'S ADD IT ALL UP" from={B.v1b.s} to={B.v2.s - 1} size={130} y={440} />
      {inWin(f, B.v2.s, listsEnd + 10) && (
        <AbsoluteFill style={{ opacity: interpolate(f, [listsEnd, listsEnd + 10], [1, 0], clamp) }}>
          <Panel side="R" top={230}>
            <Label text="RONALDO HAS" color={RONALDO} />
            {["MORE GOALS", "MORE UCL GOALS", "MORE INT'L GOALS", "MORE GAMES"].map((t, i) => (
              <Check key={t} at={mid(B.v2, 0.08 + i * 0.22)} text={t} color={RONALDO} side="R" />
            ))}
          </Panel>
          {f >= B.v3.s && (
            <Panel side="M" top={230}>
              <Label text="MESSI HAS" color={MESSI} />
              {["MORE ASSISTS", "MORE BALLON D'ORS", "MORE TROPHIES", "A WORLD CUP", "BETTER GOALS / GAME"].map((t, i) => (
                <Check key={t} at={mid(B.v3, 0.05 + i * 0.19)} text={t} color={MESSI} side="M" />
              ))}
            </Panel>
          )}
        </AbsoluteFill>
      )}
      {inWin(f, B.v4.s, B.v5.s + 8) && (
        <div style={{ position: "absolute", left: 0, right: 0, top: 820, display: "flex", justifyContent: "center", opacity: interpolate(f, [B.v5.s, B.v5.s + 8], [1, 0], clamp) }}>
          <div style={{ background: GOLD, color: "#0b0f1a", fontFamily: COND, fontWeight: 800, fontStyle: "italic", fontSize: 96, padding: "8px 46px", transform: `scale(${interpolate(sp(f, B.v4.s, 10), [0, 1], [2, 1])})`, boxShadow: `0 0 60px ${GOLD}aa` }}>
            BY THE NUMBERS: MESSI
          </div>
        </div>
      )}
      <Confetti at={B.v4.s + 4} x={960} colors={[GOLD, "#ffffff", MESSI]} />
      <Slam text="NUMBERS DON'T DECIDE" from={B.v5.s} to={B.v6.s - 1} size={130} y={330} />
      <Slam text="WHO YOU LOVE." from={mid(B.v5, 0.55)} to={B.v6.s - 1} size={170} color={GOLD} y={480} />
      <CommentPrompt from={B.v6.s} to={B.v7.s - 2} />
      <EndCard from={B.v7.s} />
    </>
  );
};

/* ================= composition ================= */

const CHAPTERS: [string, number, string][] = [
  ["c1t", 1, "THE BEGINNING"],
  ["c2t", 2, "HEAD TO HEAD"],
  ["c4t", 3, "THE HIDDEN NUMBERS"],
  ["c3t", 4, "THE SPAIN YEARS"],
  ["c5t", 5, "RECORDS ONLY ONE MAN HOLDS"],
  ["c6t", 6, "THE LAST DANCE"],
];

export const GoatFull: React.FC = () => {
  const f = useCurrentFrame();
  const impacts = [B.h5.s, B.h8.s, ...CHAPTERS.map(([id]) => B[id].s), ...ROUNDS.map((r) => B[`r${r.n}a`].s), ...ROUNDS.map((r) => r.winAt), B.f2.s, B.s7.s + 6, B.v4.s];
  const shake = impacts.reduce((a, at) => a + (f >= at ? 14 * Math.exp(-(f - at) / 4) : 0), 0);
  const flash = Math.max(
    interpolate(f, [B.h8.s, B.h8.s + 3, B.h8.s + 14], [0, 0.9, 0], clamp),
    interpolate(f, [B.h5.s, B.h5.s + 2, B.h5.s + 10], [0, 0.5, 0], clamp),
    interpolate(f, [B.v4.s, B.v4.s + 2, B.v4.s + 12], [0, 0.6, 0], clamp)
  );
  const round = ROUNDS.find((r) => f >= r.start && f < r.end + 12);
  const glowM = round ? (round.winner === "M" && f >= round.winAt ? 1.6 : 1) : 1;
  const glowR = round ? (round.winner === "R" && f >= round.winAt ? 1.6 : 1) : 1;
  const whooshes = [B.h1.s, B.h2.s, ...CHAPTERS.map(([id]) => B[id].s - 6), ...ROUNDS.map((r) => r.start), ...ROUNDS.map((r) => B[`r${r.n}a`].e + 6), B.f1.s, B.c1a.s, B.c1d.s, B.s1.s, B.c5a.s, B.c5c.s, B.c6a.s, B.c6d.s, B.v1.s];

  return (
    <AbsoluteFill style={{ backgroundColor: "#05070d" }}>
      <AbsoluteFill style={{ transform: `translate(${Math.sin(f * 3.3) * shake}px, ${Math.cos(f * 2.9) * shake}px)` }}>
        <Background glowM={glowM} glowR={glowR} />
        <Hook />
        <Origins />
        <HeadToHead />
        <HiddenNumbers />
        <SpainYears />
        <Records />
        <LastDance />
        <Verdict />
        {CHAPTERS.map(([id, n, t]) => <ChapterCard key={id} id={id} num={n} title={t} />)}
      </AbsoluteFill>
      <AbsoluteFill style={{ backgroundColor: "white", opacity: flash }} />
      <Glitch at={B.f2.s} />
      <AbsoluteFill style={{ background: "radial-gradient(ellipse at center, transparent 55%, rgba(0,0,0,0.6) 100%)" }} />

      <Audio src={staticFile("goat/voice_full.wav")} volume={1} />
      <Audio src={staticFile("goat/music_full.wav")} volume={(fr) => interpolate(fr, [0, B.h8.e, B.h8.e + 6, B.v7.e, B.v7.e + 30], [0.4, 0.4, 0.28, 0.28, 0.45], clamp)} />
      {whooshes.map((at, i) => (
        <Sequence key={`w${i}`} from={Math.max(0, at)}>
          <Audio src={staticFile("sfx_whoosh.wav")} volume={0.45} />
        </Sequence>
      ))}
      {impacts.map((at, i) => (
        <Sequence key={`i${i}`} from={at}>
          <Audio src={staticFile("sfx_impact.wav")} volume={0.5} />
        </Sequence>
      ))}
      {[B.r5d.s, B.v4.s + 4].map((at, i) => (
        <Sequence key={`sp${i}`} from={at}>
          <Audio src={staticFile("sfx_sparkle.wav")} volume={0.45} />
        </Sequence>
      ))}
      <Sequence from={B.f2.s}>
        <Audio src={staticFile("sfx_crash.wav")} volume={0.35} />
      </Sequence>
    </AbsoluteFill>
  );
};
