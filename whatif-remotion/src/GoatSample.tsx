import React from "react";
import { AbsoluteFill, Audio, Easing, Img, Sequence, interpolate, random, spring, staticFile, useCurrentFrame } from "remotion";
import { ThreeCanvas } from "@remotion/three";
import timeline from "./goat_timeline.json";

const FPS = 30;
const COND = "'Avenir Next Condensed', 'Avenir Next', sans-serif";
const SANS = "'Avenir Next', 'Helvetica Neue', sans-serif";
const MESSI = "#6cb8ff";
const RONALDO = "#ff3b4e";
const GOLD = "#ffcc33";
const clamp = { extrapolateLeft: "clamp", extrapolateRight: "clamp" } as const;
const out = Easing.out(Easing.cubic);

type Beat = { id: string; start: number; end: number; text: string };
const B: Record<string, { s: number; e: number }> = Object.fromEntries(
  (timeline as Beat[]).map((b) => [b.id, { s: Math.round(b.start * FPS), e: Math.round(b.end * FPS) }])
);
export const GOAT_DURATION = B.f3.e + 4 * FPS;

const sp = (f: number, at: number, damping = 14) => spring({ frame: f - at, fps: FPS, config: { damping, mass: 0.8 } });

type Stat =
  | { type: "num"; m: number; r: number; mAt: number; rAt: number; label: string; rPrefix?: string }
  | { type: "icons"; icon: "ball" | "cup"; m: number; r: number; mAt: number; rAt: number; label: string; rBadge?: string }
  | { type: "country" };

type Round = { n: number; title: string; m: string; r: string; winner: "M" | "R"; winAt: number; start: number; end: number; stat: Stat };

const ROUNDS: Round[] = [
  { n: 1, title: "GOALS", m: "m_goals", r: "r_goals", winner: "R", winAt: B.r1d.s, start: 0, end: 0,
    stat: { type: "num", m: 880, r: 950, mAt: B.r1c.s, rAt: B.r1b.s, label: "CAREER GOALS" } },
  { n: 2, title: "ASSISTS", m: "m_assists", r: "r_assists", winner: "M", winAt: B.r2d.s, start: 0, end: 0,
    stat: { type: "num", m: 350, r: 250, mAt: B.r2b.s, rAt: B.r2c.s, label: "CAREER ASSISTS", rPrefix: "~" } },
  { n: 3, title: "BALLON D'OR", m: "m_bdo", r: "r_bdo", winner: "M", winAt: B.r3c.s, start: 0, end: 0,
    stat: { type: "icons", icon: "ball", m: 8, r: 5, mAt: B.r3b.s, rAt: Math.round((B.r3b.s + B.r3b.e) / 2), label: "BALLON D'OR WINS" } },
  { n: 4, title: "CHAMPIONS LEAGUE", m: "m_ucl", r: "r_ucl", winner: "R", winAt: B.r4d.s, start: 0, end: 0,
    stat: { type: "icons", icon: "cup", m: 4, r: 5, mAt: B.r4c.s, rAt: B.r4b.s, label: "UCL TITLES", rBadge: "140 UCL GOALS · RECORD" } },
  { n: 5, title: "COUNTRY", m: "m_country", r: "r_country", winner: "M", winAt: B.r5c.s + 12, start: 0, end: 0, stat: { type: "country" } },
].map((r, i, arr) => ({
  ...r,
  start: B[`r${r.n}a`].s - 10,
  end: i < arr.length - 1 ? B[`r${r.n + 1}a`].s - 10 : B.f1.s - 6,
})) as Round[];

const IMPACTS = [B.h5.s, B.h8.s, ...ROUNDS.map((r) => B[`r${r.n}a`].s), ...ROUNDS.map((r) => r.winAt), B.f2.s];

const scoreAt = (f: number) => ({
  m: ROUNDS.filter((r) => r.winner === "M" && f >= r.winAt).length,
  r: ROUNDS.filter((r) => r.winner === "R" && f >= r.winAt).length,
});

/* ---------------- background ---------------- */

const Background: React.FC<{ glowM: number; glowR: number }> = ({ glowM, glowR }) => {
  const f = useCurrentFrame();
  return (
    <AbsoluteFill style={{ background: "radial-gradient(ellipse at 50% 120%, #141a2e 0%, #05070d 60%)", overflow: "hidden" }}>
      <AbsoluteFill style={{ background: `radial-gradient(ellipse at 18% 70%, ${MESSI}55 0%, transparent 55%)`, opacity: glowM }} />
      <AbsoluteFill style={{ background: `radial-gradient(ellipse at 82% 70%, ${RONALDO}55 0%, transparent 55%)`, opacity: glowR }} />
      {Array.from({ length: 7 }).map((_, i) => (
        <div
          key={i}
          style={{
            position: "absolute",
            top: -400,
            left: ((i * 330 + f * (4 + i)) % 2600) - 400,
            width: 3 + (i % 3) * 2,
            height: 2000,
            background: "linear-gradient(180deg, transparent, rgba(255,255,255,0.06), transparent)",
            transform: "rotate(24deg)",
          }}
        />
      ))}
      <AbsoluteFill
        style={{
          backgroundImage: "linear-gradient(rgba(255,255,255,0.03) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,0.03) 1px, transparent 1px)",
          backgroundSize: "80px 80px",
          backgroundPosition: `0 ${f * 0.6}px`,
        }}
      />
    </AbsoluteFill>
  );
};

/* ---------------- players ---------------- */

const Player: React.FC<{ src: string; side: "L" | "R"; from: number; to: number; dim?: number; win?: number; boxW?: number; boxH?: number }> = ({
  src, side, from, to, dim = 0, win = 0, boxW = 820, boxH = 930,
}) => {
  const f = useCurrentFrame();
  if (f < from - 2 || f > to + 12) return null;
  const inP = sp(f, from, 16);
  const outP = interpolate(f, [to, to + 10], [0, 1], { ...clamp, easing: Easing.in(Easing.cubic) });
  const dir = side === "L" ? -1 : 1;
  const x = dir * ((1 - inP) * 900 + outP * 900);
  const blur = Math.abs(1 - inP) * 14 + outP * 14;
  const color = side === "L" ? MESSI : RONALDO;
  const zoom = 1 + (f - from) * 0.0005;
  const cx = side === "L" ? 470 : 1450;
  return (
    <div
      style={{
        position: "absolute",
        left: cx - boxW / 2,
        bottom: 0,
        width: boxW,
        height: boxH,
        transform: `translateX(${x}px) scale(${zoom * (1 + win * 0.04)})`,
        transformOrigin: "50% 100%",
        filter: `blur(${blur}px) grayscale(${dim * 0.9}) brightness(${1 - dim * 0.5 + win * 0.08}) drop-shadow(0 0 ${30 + win * 40}px ${color}${win ? "cc" : "88"})`,
        opacity: 1 - outP * 0.3,
      }}
    >
      <Img src={staticFile(`goat/${src}.png`)} style={{ width: "100%", height: "100%", objectFit: "contain", objectPosition: "50% 100%" }} />
    </div>
  );
};

/* ---------------- typography ---------------- */

const Slam: React.FC<{ text: string; from: number; to: number; size?: number; color?: string; y?: number; stroke?: boolean }> = ({
  text, from, to, size = 150, color = "white", y = 790, stroke = false,
}) => {
  const f = useCurrentFrame();
  if (f < from || f > to + 8) return null;
  const p = sp(f, from, 12);
  const o = interpolate(f, [to, to + 8], [1, 0], clamp);
  return (
    <div style={{ position: "absolute", left: 0, right: 0, top: y, display: "flex", justifyContent: "center", opacity: o }}>
      <div
        style={{
          fontFamily: COND,
          fontWeight: 800,
          fontStyle: "italic",
          fontSize: size,
          lineHeight: 1,
          letterSpacing: -2,
          color: stroke ? "transparent" : color,
          WebkitTextStroke: stroke ? `3px ${color}` : undefined,
          transform: `scale(${interpolate(p, [0, 1], [1.8, 1])})`,
          filter: `blur(${(1 - p) * 10}px)`,
          textShadow: stroke ? undefined : "0 10px 40px rgba(0,0,0,0.8)",
          whiteSpace: "nowrap",
        }}
      >
        {text}
      </div>
    </div>
  );
};

const Counter: React.FC<{ value: number; from: number; dur?: number; size: number; color: string; prefix?: string; suffix?: string }> = ({
  value, from, dur = 26, size, color, prefix = "", suffix = "+",
}) => {
  const f = useCurrentFrame();
  const p = interpolate(f, [from, from + dur], [0, 1], { ...clamp, easing: out });
  const pop = sp(f, from + dur, 8);
  return (
    <span style={{ fontFamily: COND, fontWeight: 800, fontStyle: "italic", fontSize: size, color, fontVariantNumeric: "tabular-nums", display: "inline-block", transform: `scale(${1 + (f >= from + dur ? 0.12 * (1 - pop) : 0)})`, textShadow: `0 0 30px ${color}88` }}>
      {prefix}
      {Math.round(p * value).toLocaleString("en-US")}
      {p >= 1 ? suffix : ""}
    </span>
  );
};

/* ---------------- 3D split planet ---------------- */

const SplitPlanet: React.FC<{ from: number; to: number }> = ({ from, to }) => {
  const f = useCurrentFrame();
  if (f < from || f > to + 10) return null;
  const t = f - from;
  const split = interpolate(t, [18, 55], [0, 1.4], { ...clamp, easing: Easing.inOut(Easing.cubic) });
  const appear = sp(f, from, 15);
  const o = interpolate(f, [to, to + 10], [1, 0], clamp);
  const spin = t * 0.03;
  return (
    <AbsoluteFill style={{ opacity: o }}>
      <ThreeCanvas width={1920} height={1080} camera={{ fov: 35, position: [0, 0, 9] }}>
        <ambientLight intensity={0.4} />
        <pointLight position={[0, 4, 6]} intensity={80} />
        <group scale={appear} rotation={[0.25, 0, 0]}>
          {[
            { color: MESSI, x: -split, phi: -Math.PI / 2 },
            { color: RONALDO, x: split, phi: Math.PI / 2 },
          ].map((h, i) => (
            <group key={i} position={[h.x, 0, 0]} rotation={[spin, 0, 0]}>
              <mesh rotation={[0, h.phi, 0]}>
                <sphereGeometry args={[1.8, 48, 32, 0, Math.PI]} />
                <meshStandardMaterial color="#0b1020" emissive={h.color} emissiveIntensity={0.35} transparent opacity={0.85} side={2} />
              </mesh>
              <mesh rotation={[0, h.phi, 0]} scale={1.01}>
                <sphereGeometry args={[1.8, 24, 16, 0, Math.PI]} />
                <meshBasicMaterial color={h.color} wireframe transparent opacity={0.9} />
              </mesh>
            </group>
          ))}
        </group>
      </ThreeCanvas>
      <AbsoluteFill style={{ background: `radial-gradient(circle at 50% 50%, rgba(255,255,255,${0.35 * Math.max(0, 1 - Math.abs(t - 30) / 12)}) 0%, transparent 25%)` }} />
    </AbsoluteFill>
  );
};

const DigitRain: React.FC<{ from: number; to: number }> = ({ from, to }) => {
  const f = useCurrentFrame();
  if (f < from || f > to) return null;
  const o = interpolate(f, [from, from + 10, to - 10, to], [0, 0.3, 0.3, 0], clamp);
  return (
    <AbsoluteFill style={{ opacity: o, overflow: "hidden" }}>
      {Array.from({ length: 34 }).map((_, i) => {
        const speed = 6 + random(`dr${i}`) * 10;
        const y = ((random(`dy${i}`) * 1400 + (f - from) * speed) % 1500) - 400;
        const digits = Array.from({ length: 14 }, (_, k) => Math.floor(random(`dg${i}${k}${Math.floor(f / 6)}`) * 10)).join("\n");
        return (
          <pre key={i} style={{ position: "absolute", left: i * 57, top: y, margin: 0, fontFamily: "Menlo, monospace", fontSize: 26, lineHeight: "30px", color: GOLD }}>
            {digits}
          </pre>
        );
      })}
    </AbsoluteFill>
  );
};

/* ---------------- round elements ---------------- */

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
      <div
        style={{
          position: "absolute",
          left: -300,
          top: 300,
          width: 2520,
          height: 480,
          transform: `translateX(${(sweepIn + sweepOut) * 2600}px) skewX(-14deg)`,
          background: `linear-gradient(90deg, ${MESSI} 0%, #1b2440 30%, #1b2440 70%, ${RONALDO} 100%)`,
          boxShadow: "0 0 80px rgba(0,0,0,0.8)",
        }}
      />
      <AbsoluteFill style={{ justifyContent: "center", alignItems: "center", transform: `translateX(${sweepOut * 2600}px)` }}>
        <div style={{ fontFamily: SANS, fontWeight: 700, fontSize: 34, letterSpacing: 18, color: GOLD, opacity: title, marginBottom: -10 }}>HEAD TO HEAD</div>
        <div style={{ fontFamily: COND, fontWeight: 800, fontStyle: "italic", fontSize: 220, lineHeight: 1, color: "white", transform: `scale(${interpolate(title, [0, 1], [2, 1])})`, opacity: title, textShadow: "0 12px 50px rgba(0,0,0,0.6)" }}>
          ROUND {r.n}
        </div>
        <div style={{ fontFamily: COND, fontWeight: 800, fontStyle: "italic", fontSize: 84, color: GOLD, transform: `translateY(${(1 - sub) * 40}px)`, opacity: sub, letterSpacing: 4 }}>
          {r.title}
        </div>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};

const RoundTag: React.FC<{ r: Round }> = ({ r }) => {
  const f = useCurrentFrame();
  const from = B[`r${r.n}a`].e + 10;
  if (f < from || f > r.end) return null;
  const p = sp(f, from, 16);
  return (
    <div style={{ position: "absolute", left: 60, top: 54, display: "flex", alignItems: "center", gap: 14, transform: `translateX(${(1 - p) * -300}px)`, opacity: p }}>
      <div style={{ background: GOLD, color: "#111", fontFamily: COND, fontWeight: 800, fontStyle: "italic", fontSize: 30, padding: "4px 14px" }}>ROUND {r.n}</div>
      <div style={{ color: "white", fontFamily: COND, fontWeight: 800, fontStyle: "italic", fontSize: 30, letterSpacing: 2 }}>{r.title}</div>
    </div>
  );
};

const BallIcon: React.FC = () => (
  <div style={{ width: 70, height: 70, borderRadius: "50%", background: "radial-gradient(circle at 35% 30%, #fff6c8 0%, #ffd34d 30%, #c98a12 70%, #6b4300 100%)", boxShadow: "0 0 24px rgba(255,200,60,0.7), inset -6px -8px 14px rgba(0,0,0,0.35)" }} />
);
const CupIcon: React.FC = () => (
  <svg width={72} height={90} viewBox="0 0 72 90">
    <defs>
      <linearGradient id="silver" x1="0" y1="0" x2="1" y2="1">
        <stop offset="0%" stopColor="#ffffff" />
        <stop offset="50%" stopColor="#b9c3d0" />
        <stop offset="100%" stopColor="#6f7a88" />
      </linearGradient>
    </defs>
    <path d="M18 8 h36 v22 a18 18 0 0 1 -36 0 z" fill="url(#silver)" />
    <path d="M18 12 C2 12 2 40 20 40" stroke="url(#silver)" strokeWidth="7" fill="none" />
    <path d="M54 12 C70 12 70 40 52 40" stroke="url(#silver)" strokeWidth="7" fill="none" />
    <rect x="32" y="46" width="8" height="20" fill="url(#silver)" />
    <rect x="20" y="66" width="32" height="10" rx="2" fill="url(#silver)" />
    <rect x="16" y="76" width="40" height="8" rx="2" fill="#6f7a88" />
  </svg>
);

const StatSide: React.FC<{ r: Round; side: "M" | "R" }> = ({ r, side }) => {
  const f = useCurrentFrame();
  const st = r.stat;
  const color = side === "M" ? MESSI : RONALDO;
  const name = side === "M" ? "MESSI" : "RONALDO";
  const align = side === "M" ? "flex-end" : "flex-start";
  const left = side === "M" ? 380 : 1010;
  const box: React.CSSProperties = {
    position: "absolute", left, width: 530, top: 540, padding: "20px 26px", display: "flex", flexDirection: "column", alignItems: align, textAlign: side === "M" ? "right" : "left",
    background: side === "M" ? "linear-gradient(270deg, rgba(5,7,13,0.78) 0%, rgba(5,7,13,0.5) 70%, transparent 100%)" : "linear-gradient(90deg, rgba(5,7,13,0.78) 0%, rgba(5,7,13,0.5) 70%, transparent 100%)",
  };
  if (st.type === "num") {
    const at = side === "M" ? st.mAt : st.rAt;
    if (f < at) return null;
    const v = side === "M" ? st.m : st.r;
    const max = Math.max(st.m, st.r);
    const bar = interpolate(f, [at, at + 26], [0, v / max], { ...clamp, easing: out });
    const appear = sp(f, at, 14);
    return (
      <div style={{ ...box, opacity: appear }}>
        <div style={{ fontFamily: SANS, fontWeight: 700, fontSize: 26, letterSpacing: 6, color: "rgba(255,255,255,0.75)" }}>{name}</div>
        <Counter value={v} from={at} size={190} color="white" prefix={side === "R" ? st.rPrefix ?? "" : ""} suffix={side === "R" && st.rPrefix ? "" : "+"} />
        <div style={{ width: 460, height: 16, background: "rgba(255,255,255,0.1)", borderRadius: 8, overflow: "hidden", display: "flex", justifyContent: align }}>
          <div style={{ width: `${bar * 100}%`, height: "100%", background: `linear-gradient(90deg, ${color}, white)`, boxShadow: `0 0 20px ${color}` }} />
        </div>
        <div style={{ fontFamily: SANS, fontWeight: 600, fontSize: 22, letterSpacing: 5, color, marginTop: 12 }}>{st.label}</div>
      </div>
    );
  }
  if (st.type === "icons") {
    const at = side === "M" ? st.mAt : st.rAt;
    if (f < at) return null;
    const count = side === "M" ? st.m : st.r;
    const Icon = st.icon === "ball" ? BallIcon : CupIcon;
    const perRow = st.icon === "ball" ? 4 : 5;
    return (
      <div style={box}>
        <div style={{ fontFamily: SANS, fontWeight: 700, fontSize: 26, letterSpacing: 6, color: "rgba(255,255,255,0.75)", opacity: sp(f, at) }}>{name}</div>
        <div style={{ fontFamily: COND, fontWeight: 800, fontStyle: "italic", fontSize: 170, lineHeight: 1, color: "white", opacity: sp(f, at), textShadow: `0 0 30px ${color}88` }}>{count}</div>
        <div style={{ display: "flex", flexWrap: "wrap", gap: 12, width: perRow * 84, justifyContent: align, marginTop: 6 }}>
          {Array.from({ length: count }).map((_, i) => {
            const p = sp(f, at + 4 + i * 3, 9);
            return (
              <div key={i} style={{ transform: `scale(${p}) translateY(${(1 - p) * -40}px)`, opacity: Math.min(1, p * 2) }}>
                <Icon />
              </div>
            );
          })}
        </div>
        {side === "R" && st.rBadge && f > at + 30 && (
          <div style={{ marginTop: 18, background: RONALDO, color: "white", fontFamily: COND, fontWeight: 800, fontStyle: "italic", fontSize: 30, padding: "6px 16px", transform: `scale(${sp(f, at + 30, 10)})` }}>{st.rBadge}</div>
        )}
      </div>
    );
  }
  // country round
  if (side === "R") {
    const at = B.r5b.s;
    if (f < at) return null;
    return (
      <div style={{ ...box, opacity: sp(f, at) }}>
        <div style={{ fontFamily: SANS, fontWeight: 700, fontSize: 26, letterSpacing: 6, color: "rgba(255,255,255,0.75)" }}>RONALDO</div>
        <Counter value={140} from={at} size={190} color="white" />
        <div style={{ fontFamily: SANS, fontWeight: 600, fontSize: 22, letterSpacing: 5, color: RONALDO }}>INTERNATIONAL GOALS</div>
        <div style={{ marginTop: 16, background: RONALDO, color: "white", fontFamily: COND, fontWeight: 800, fontStyle: "italic", fontSize: 30, padding: "6px 16px", transform: `scale(${sp(f, at + 34, 10)})` }}>ALL-TIME RECORD</div>
      </div>
    );
  }
  const at = B.r5c.s + 12;
  if (f < at) return null;
  return (
    <div style={{ ...box, opacity: sp(f, at) }}>
      <div style={{ fontFamily: SANS, fontWeight: 700, fontSize: 26, letterSpacing: 6, color: "rgba(255,255,255,0.75)" }}>MESSI</div>
      <div style={{ fontFamily: COND, fontWeight: 800, fontStyle: "italic", fontSize: 120, lineHeight: 1, color: GOLD, textShadow: `0 0 40px ${GOLD}aa`, transform: `scale(${interpolate(sp(f, at, 10), [0, 1], [1.6, 1])})` }}>WORLD</div>
      <div style={{ fontFamily: COND, fontWeight: 800, fontStyle: "italic", fontSize: 120, lineHeight: 1, color: GOLD, textShadow: `0 0 40px ${GOLD}aa` }}>CHAMPION</div>
      <div style={{ fontFamily: SANS, fontWeight: 600, fontSize: 24, letterSpacing: 8, color: "white", marginTop: 8 }}>QATAR 2022</div>
    </div>
  );
};

const WinnerStamp: React.FC<{ r: Round }> = ({ r }) => {
  const f = useCurrentFrame();
  if (f < r.winAt || f > r.end) return null;
  const p = sp(f, r.winAt, 9);
  const isM = r.winner === "M";
  return (
    <div
      style={{
        position: "absolute",
        left: isM ? 360 : 960,
        top: 430,
        width: 600,
        display: "flex",
        justifyContent: "center",
        transform: `scale(${interpolate(p, [0, 1], [2.4, 1])}) rotate(${isM ? -8 : 8}deg)`,
        opacity: Math.min(1, p * 1.5),
      }}
    >
      <div style={{ border: `6px solid ${GOLD}`, padding: "6px 28px", fontFamily: COND, fontWeight: 800, fontStyle: "italic", fontSize: 76, color: GOLD, letterSpacing: 4, background: "rgba(0,0,0,0.45)", boxShadow: `0 0 40px ${GOLD}88` }}>
        WINNER
      </div>
    </div>
  );
};

const Confetti: React.FC<{ at: number; x: number }> = ({ at, x }) => {
  const f = useCurrentFrame();
  const t = f - at;
  if (t < 0 || t > 70) return null;
  return (
    <AbsoluteFill>
      {Array.from({ length: 70 }).map((_, i) => {
        const ang = -Math.PI / 2 + (random(`ca${at}${i}`) - 0.5) * 2.2;
        const v = 14 + random(`cv${at}${i}`) * 18;
        const px = x + Math.cos(ang) * v * t;
        const py = 620 + Math.sin(ang) * v * t + 0.55 * t * t;
        const c = [GOLD, "#ffffff", "#ffe08a", MESSI][i % 4];
        return <div key={i} style={{ position: "absolute", left: px, top: py, width: 12, height: 20, background: c, transform: `rotate(${t * 14 + i * 40}deg)`, opacity: 1 - t / 70 }} />;
      })}
    </AbsoluteFill>
  );
};

/* ---------------- scoreboard ---------------- */

const Scoreboard: React.FC = () => {
  const f = useCurrentFrame();
  const show = ROUNDS[0].start + 20;
  if (f < show) return null;
  const { m, r } = scoreAt(f);
  const finalP = interpolate(f, [B.f1.s - 4, B.f1.s + 14], [0, 1], { ...clamp, easing: Easing.inOut(Easing.cubic) });
  const gone = interpolate(f, [B.f2.s, B.f2.s + 6], [1, 0], clamp);
  const appear = sp(f, show, 16);
  const scale = interpolate(finalP, [0, 1], [1, 2.3]);
  const top = interpolate(finalP, [0, 1], [40, 150]);
  const lastChange = Math.max(...ROUNDS.filter((x) => f >= x.winAt).map((x) => x.winAt), -100);
  const pop = f - lastChange < 20 ? 1 + 0.25 * Math.exp(-(f - lastChange) / 5) : 1;
  const cell = (name: string, val: number, color: string, leftSide: boolean) => (
    <div style={{ display: "flex", alignItems: "center", flexDirection: leftSide ? "row" : "row-reverse" }}>
      <div style={{ background: color, color: "#0b0f1a", fontFamily: COND, fontWeight: 800, fontStyle: "italic", fontSize: 30, padding: "8px 20px", letterSpacing: 2 }}>{name}</div>
      <div style={{ background: "#0b0f1a", color: "white", fontFamily: COND, fontWeight: 800, fontSize: 44, width: 74, textAlign: "center", transform: `scale(${pop})`, border: `2px solid ${color}` }}>{val}</div>
    </div>
  );
  return (
    <div style={{ position: "absolute", left: 0, right: 0, top, display: "flex", justifyContent: "center", opacity: appear * gone }}>
      <div style={{ display: "flex", alignItems: "center", gap: 10, transform: `scale(${scale * (0.8 + appear * 0.2)})`, transformOrigin: "50% 0%", boxShadow: "0 10px 40px rgba(0,0,0,0.6)" }}>
        {cell("MESSI", m, MESSI, true)}
        <div style={{ color: GOLD, fontFamily: COND, fontWeight: 800, fontSize: 36 }}>:</div>
        {cell("RONALDO", r, RONALDO, false)}
      </div>
    </div>
  );
};

/* ---------------- finale ---------------- */

const Glitch: React.FC = () => {
  const f = useCurrentFrame();
  const s = B.f2.s;
  if (f < s || f > s + 26) return null;
  const k = f - s;
  return (
    <AbsoluteFill style={{ pointerEvents: "none" }}>
      <AbsoluteFill style={{ background: k % 4 < 2 ? "rgba(255,30,60,0.22)" : "rgba(40,200,255,0.12)", mixBlendMode: "screen" }} />
      {Array.from({ length: 8 }).map((_, i) => (
        <div key={i} style={{ position: "absolute", left: 0, right: 0, top: random(`gy${i}${k}`) * 1080, height: 4 + random(`gh${i}${k}`) * 30, background: "rgba(255,255,255,0.18)", transform: `translateX(${(random(`gx${i}${k}`) - 0.5) * 200}px)` }} />
      ))}
      <AbsoluteFill style={{ backgroundImage: "repeating-linear-gradient(0deg, rgba(0,0,0,0.25) 0 2px, transparent 2px 5px)" }} />
    </AbsoluteFill>
  );
};

const EndCard: React.FC = () => {
  const f = useCurrentFrame();
  const from = B.f3.e + 8;
  if (f < from) return null;
  const p = sp(f, from, 12);
  const btn = sp(f, from + 18, 10);
  const pulse = 1 + 0.04 * Math.sin((f - from) / 4);
  return (
    <AbsoluteFill style={{ justifyContent: "center", alignItems: "center", background: "rgba(5,7,13,0.85)" }}>
      <div style={{ fontFamily: COND, fontWeight: 800, fontStyle: "italic", fontSize: 130, color: "white", opacity: p, transform: `scale(${interpolate(p, [0, 1], [1.4, 1])})`, letterSpacing: 2 }}>
        TO BE <span style={{ color: GOLD }}>CONTINUED…</span>
      </div>
      <div style={{ marginTop: 40, display: "flex", alignItems: "center", gap: 20, transform: `scale(${btn * pulse})` }}>
        <div style={{ background: "#ff0033", color: "white", fontFamily: SANS, fontWeight: 800, fontSize: 40, padding: "16px 44px", borderRadius: 14, boxShadow: "0 0 40px rgba(255,0,51,0.6)" }}>SUBSCRIBE</div>
        <div style={{ fontFamily: SANS, fontWeight: 600, fontSize: 30, color: "rgba(255,255,255,0.8)" }}>for the full verdict</div>
      </div>
    </AbsoluteFill>
  );
};

/* ---------------- composition ---------------- */

export const GoatSample: React.FC = () => {
  const f = useCurrentFrame();
  const shake = IMPACTS.reduce((a, at) => a + (f >= at ? 14 * Math.exp(-(f - at) / 4) : 0), 0);
  const sx = Math.sin(f * 3.3) * shake;
  const sy = Math.cos(f * 2.9) * shake;
  const hookEnd = ROUNDS[0].start + 4;
  const hookDim = interpolate(f, [B.h4.s, B.h4.s + 8, B.h5.s, B.h5.s + 6], [0, 0.75, 0.75, 0], clamp);
  const flash = Math.max(
    interpolate(f, [B.h8.s, B.h8.s + 3, B.h8.s + 14], [0, 0.9, 0], clamp),
    interpolate(f, [B.h5.s, B.h5.s + 2, B.h5.s + 10], [0, 0.5, 0], clamp)
  );
  const round = ROUNDS.find((r) => f >= r.start && f < r.end + 12);
  const glowM = round ? (round.winner === "M" && f >= round.winAt ? 1.6 : 1) : 1;
  const glowR = round ? (round.winner === "R" && f >= round.winAt ? 1.6 : 1) : 1;
  const finalDim = interpolate(f, [B.f1.s - 4, B.f1.s + 10], [0, 0.6], clamp);
  const h6mid = Math.round((B.h6.s + B.h6.e) / 2) + 4;
  const h7mid = Math.round((B.h7.s + B.h7.e) / 2);

  return (
    <AbsoluteFill style={{ backgroundColor: "#05070d" }}>
      <AbsoluteFill style={{ transform: `translate(${sx}px, ${sy}px)` }}>
        <Background glowM={glowM} glowR={glowR} />
        <DigitRain from={B.h6.s} to={B.h7.e + 6} />

        {/* hook */}
        <Player src="m_hook" side="L" from={B.h1.s} to={hookEnd} dim={hookDim} boxW={760} boxH={980} />
        <Player src="r_hook" side="R" from={B.h2.s} to={hookEnd} dim={hookDim} boxW={760} boxH={900} />
        <SplitPlanet from={B.h4.s} to={B.h5.s} />

        {/* rounds */}
        {ROUNDS.map((r) => {
          const enter = B[`r${r.n}a`].e + 6;
          const dimM = r.winner === "R" && f >= r.winAt ? 1 : 0;
          const dimR = r.winner === "M" && f >= r.winAt ? 1 : 0;
          return (
            <React.Fragment key={r.n}>
              <Player src={r.m} side="L" from={enter} to={r.end} dim={dimM} win={1 - dimM && f >= r.winAt ? 1 : 0} />
              <Player src={r.r} side="R" from={enter} to={r.end} dim={dimR} win={1 - dimR && f >= r.winAt ? 1 : 0} />
            </React.Fragment>
          );
        })}
        <AbsoluteFill style={{ background: "linear-gradient(180deg, rgba(5,7,13,0.6) 0%, transparent 22%, transparent 55%, rgba(5,7,13,0.75) 100%)" }} />
        {ROUNDS.map((r) => (
          <React.Fragment key={`s${r.n}`}>
            {f >= r.start && f < r.end + 10 && (
              <AbsoluteFill style={{ opacity: interpolate(f, [r.end, r.end + 10], [1, 0], clamp) }}>
                <StatSide r={r} side="M" />
                <StatSide r={r} side="R" />
                <WinnerStamp r={r} />
                <RoundTag r={r} />
              </AbsoluteFill>
            )}
          </React.Fragment>
        ))}
        <div style={{ position: "absolute", left: 958, top: 140, width: 4, height: 940, background: `linear-gradient(180deg, transparent, ${GOLD}, transparent)`, opacity: f > ROUNDS[0].start && f < B.f1.s ? 0.5 : 0 }} />
        <Confetti at={B.r5c.s + 12} x={640} />

        {/* hook typography */}
        <Slam text="TWO PLAYERS" from={B.h1.s} to={B.h2.s - 1} />
        <Slam text="20 YEARS" from={B.h2.s} to={B.h3.s - 1} color={GOLD} />
        {f >= B.h3.s && f < B.h4.s + 2 && (
          <div style={{ position: "absolute", left: 0, right: 0, top: 700, textAlign: "center" }}>
            <Counter value={1800} from={B.h3.s} dur={40} size={210} color={GOLD} />
            <div style={{ fontFamily: SANS, fontWeight: 700, fontSize: 34, letterSpacing: 14, color: "white", marginTop: -10 }}>GOALS BETWEEN THEM</div>
          </div>
        )}
        <Slam text="ONE QUESTION" from={B.h4.s + 4} to={B.h5.s - 1} size={110} y={860} />
        <Slam text="WHO IS THE" from={B.h5.s} to={B.h6.s - 1} size={90} y={600} />
        <Slam text="G.O.A.T.?" from={B.h5.s + 8} to={B.h6.s - 1} size={300} color={GOLD} y={690} />
        <Slam text="WE SETTLE IT" from={B.h6.s} to={h6mid} size={150} />
        <Slam text="WITH NUMBERS" from={h6mid} to={B.h7.s - 1} size={150} color={GOLD} />
        <Slam text="NO OPINIONS." from={B.h7.s} to={h7mid} size={150} stroke />
        <Slam text="JUST STATS." from={h7mid} to={B.h8.s - 1} size={170} color={GOLD} />
        <Slam text="LET'S GO!" from={B.h8.s} to={ROUNDS[0].start} size={260} />

        {ROUNDS.map((r) => (
          <RoundBanner key={`b${r.n}`} r={r} />
        ))}

        {/* finale */}
        <AbsoluteFill style={{ background: "#05070d", opacity: finalDim }} />
        <Player src="m_hook" side="L" from={B.f1.s} to={B.f2.s} win={1} boxW={700} boxH={860} />
        <Player src="r_hook" side="R" from={B.f1.s} to={B.f2.s} dim={0.6} boxW={700} boxH={800} />
        <Scoreboard />
        <Slam text="TO MESSI" from={B.f1.e - 30} to={B.f2.s - 1} size={130} color={MESSI} y={890} />
        <Slam text="BUT WAIT…" from={B.f2.s} to={B.f3.s - 1} size={240} color={RONALDO} y={400} />
        <Slam text="THE NEXT NUMBERS" from={B.f3.s} to={B.f3.e + 6} size={120} y={380} />
        <Slam text="CHANGE EVERYTHING" from={B.f3.s + 34} to={B.f3.e + 6} size={150} color={GOLD} y={520} />
        <EndCard />
      </AbsoluteFill>

      <AbsoluteFill style={{ backgroundColor: "white", opacity: flash }} />
      <Glitch />
      <AbsoluteFill style={{ background: "radial-gradient(ellipse at center, transparent 55%, rgba(0,0,0,0.6) 100%)" }} />

      <Audio src={staticFile("goat/voice.wav")} volume={1} />
      <Audio src={staticFile("goat/music.wav")} volume={(fr) => interpolate(fr, [0, B.h8.e, B.h8.e + 6], [0.4, 0.4, 0.3], clamp)} />
      {[B.h1.s, B.h2.s, ...ROUNDS.map((r) => r.start), ...ROUNDS.map((r) => B[`r${r.n}a`].e + 6), B.f1.s].map((at, i) => (
        <Sequence key={`w${i}`} from={at}>
          <Audio src={staticFile("sfx_whoosh.wav")} volume={0.5} />
        </Sequence>
      ))}
      {IMPACTS.map((at, i) => (
        <Sequence key={`i${i}`} from={at}>
          <Audio src={staticFile("sfx_impact.wav")} volume={0.55} />
        </Sequence>
      ))}
      <Sequence from={B.r5c.s + 12}>
        <Audio src={staticFile("sfx_sparkle.wav")} volume={0.5} />
      </Sequence>
      <Sequence from={B.f2.s}>
        <Audio src={staticFile("sfx_crash.wav")} volume={0.35} />
      </Sequence>
    </AbsoluteFill>
  );
};
