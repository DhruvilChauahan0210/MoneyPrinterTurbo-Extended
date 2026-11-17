import React from "react";
import { AbsoluteFill, Easing, Img, interpolate, random, spring, staticFile, useCurrentFrame } from "remotion";
import { ThreeCanvas } from "@remotion/three";

export const FPS = 30;
export const COND = "'Avenir Next Condensed', 'Avenir Next', sans-serif";
export const SANS = "'Avenir Next', 'Helvetica Neue', sans-serif";
export const MESSI = "#6cb8ff";
export const RONALDO = "#ff3b4e";
export const GOLD = "#ffcc33";
export const clamp = { extrapolateLeft: "clamp", extrapolateRight: "clamp" } as const;
export const out = Easing.out(Easing.cubic);
export const sp = (f: number, at: number, damping = 14) => spring({ frame: f - at, fps: FPS, config: { damping, mass: 0.8 } });
export const mid = (b: { s: number; e: number }, k = 0.5) => Math.round(b.s + (b.e - b.s) * k);

export const Background: React.FC<{ glowM: number; glowR: number; tint?: string }> = ({ glowM, glowR, tint }) => {
  const f = useCurrentFrame();
  return (
    <AbsoluteFill style={{ background: "radial-gradient(ellipse at 50% 120%, #141a2e 0%, #05070d 60%)", overflow: "hidden" }}>
      <AbsoluteFill style={{ background: `radial-gradient(ellipse at 18% 70%, ${MESSI}55 0%, transparent 55%)`, opacity: glowM }} />
      <AbsoluteFill style={{ background: `radial-gradient(ellipse at 82% 70%, ${RONALDO}55 0%, transparent 55%)`, opacity: glowR }} />
      {tint && <AbsoluteFill style={{ background: tint }} />}
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

export const Player: React.FC<{ src: string; side: "L" | "R"; from: number; to: number; dim?: number; win?: number; boxW?: number; boxH?: number }> = ({
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
  const zoom = 1 + (f - from) * 0.0004;
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

export const PhotoBg: React.FC<{ src: string; from: number; to: number; dark?: number; gray?: number }> = ({ src, from, to, dark = 0.55, gray = 0 }) => {
  const f = useCurrentFrame();
  if (f < from || f > to + 10) return null;
  const o = interpolate(f, [from, from + 10, to, to + 10], [0, 1, 1, 0], clamp);
  return (
    <AbsoluteFill style={{ opacity: o }}>
      <Img
        src={staticFile(`goat/${src}`)}
        style={{ width: "100%", height: "100%", objectFit: "cover", transform: `scale(${1.05 + (f - from) * 0.0006})`, filter: `grayscale(${gray}) brightness(${1 - dark * 0.6})` }}
      />
      <AbsoluteFill style={{ background: `linear-gradient(180deg, rgba(5,7,13,${dark}) 0%, rgba(5,7,13,${dark * 0.4}) 45%, rgba(5,7,13,${dark + 0.2}) 100%)` }} />
    </AbsoluteFill>
  );
};

export const Slam: React.FC<{ text: string; from: number; to: number; size?: number; color?: string; y?: number; stroke?: boolean }> = ({
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

export const Counter: React.FC<{ value: number; from: number; dur?: number; size: number; color: string; prefix?: string; suffix?: string; decimals?: number }> = ({
  value, from, dur = 26, size, color, prefix = "", suffix = "+", decimals = 0,
}) => {
  const f = useCurrentFrame();
  const p = interpolate(f, [from, from + dur], [0, 1], { ...clamp, easing: out });
  const pop = sp(f, from + dur, 8);
  const v = p * value;
  return (
    <span
      style={{
        fontFamily: COND,
        fontWeight: 800,
        fontStyle: "italic",
        fontSize: size,
        lineHeight: 1,
        color,
        fontVariantNumeric: "tabular-nums",
        display: "inline-block",
        transform: `scale(${1 + (f >= from + dur ? 0.12 * (1 - pop) : 0)})`,
        textShadow: `0 0 30px ${color}88`,
      }}
    >
      {prefix}
      {decimals ? v.toFixed(decimals) : Math.round(v).toLocaleString("en-US")}
      {p >= 1 ? suffix : ""}
    </span>
  );
};

export const Chip: React.FC<{ at: number; text: string; color?: string; textColor?: string; size?: number }> = ({ at, text, color = GOLD, textColor = "#111", size = 30 }) => {
  const f = useCurrentFrame();
  if (f < at) return null;
  const p = sp(f, at, 11);
  return (
    <div style={{ display: "inline-block", background: color, color: textColor, fontFamily: COND, fontWeight: 800, fontStyle: "italic", fontSize: size, padding: "6px 16px", transform: `scale(${interpolate(p, [0, 1], [1.6, 1])})`, opacity: Math.min(1, p * 1.5), boxShadow: `0 0 26px ${color}66`, whiteSpace: "nowrap" }}>
      {text}
    </div>
  );
};

export const SplitPlanet: React.FC<{ from: number; to: number }> = ({ from, to }) => {
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
    </AbsoluteFill>
  );
};

export const DigitRain: React.FC<{ from: number; to: number }> = ({ from, to }) => {
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

export const BallIcon: React.FC<{ size?: number }> = ({ size = 70 }) => (
  <div style={{ width: size, height: size, borderRadius: "50%", background: "radial-gradient(circle at 35% 30%, #fff6c8 0%, #ffd34d 30%, #c98a12 70%, #6b4300 100%)", boxShadow: "0 0 24px rgba(255,200,60,0.7), inset -6px -8px 14px rgba(0,0,0,0.35)" }} />
);

export const CupIcon: React.FC = () => (
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

export const Confetti: React.FC<{ at: number; x: number; colors?: string[] }> = ({ at, x, colors = [GOLD, "#ffffff", "#ffe08a", MESSI] }) => {
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
        return <div key={i} style={{ position: "absolute", left: px, top: py, width: 12, height: 20, background: colors[i % colors.length], transform: `rotate(${t * 14 + i * 40}deg)`, opacity: 1 - t / 70 }} />;
      })}
    </AbsoluteFill>
  );
};

export const Panel: React.FC<{ side: "M" | "R"; top?: number; children: React.ReactNode; opacity?: number }> = ({ side, top = 300, children, opacity = 1 }) => (
  <div
    style={{
      position: "absolute",
      left: side === "M" ? 380 : 1010,
      width: 530,
      top,
      padding: "20px 26px",
      display: "flex",
      flexDirection: "column",
      gap: 14,
      alignItems: side === "M" ? "flex-end" : "flex-start",
      textAlign: side === "M" ? "right" : "left",
      opacity,
      background:
        side === "M"
          ? "linear-gradient(270deg, rgba(5,7,13,0.8) 0%, rgba(5,7,13,0.5) 70%, transparent 100%)"
          : "linear-gradient(90deg, rgba(5,7,13,0.8) 0%, rgba(5,7,13,0.5) 70%, transparent 100%)",
    }}
  >
    {children}
  </div>
);

export const Label: React.FC<{ text: string; color?: string; size?: number }> = ({ text, color = "rgba(255,255,255,0.75)", size = 26 }) => (
  <div style={{ fontFamily: SANS, fontWeight: 700, fontSize: size, letterSpacing: 6, color }}>{text}</div>
);

export const WinnerStamp: React.FC<{ at: number; to: number; side: "M" | "R"; text?: string; top?: number }> = ({ at, to, side, text = "WINNER", top = 430 }) => {
  const f = useCurrentFrame();
  if (f < at || f > to) return null;
  const p = sp(f, at, 9);
  return (
    <div style={{ position: "absolute", left: side === "M" ? 360 : 960, top, width: 600, display: "flex", justifyContent: "center", transform: `scale(${interpolate(p, [0, 1], [2.4, 1])}) rotate(${side === "M" ? -8 : 8}deg)`, opacity: Math.min(1, p * 1.5) }}>
      <div style={{ border: `6px solid ${GOLD}`, padding: "6px 28px", fontFamily: COND, fontWeight: 800, fontStyle: "italic", fontSize: 76, color: GOLD, letterSpacing: 4, background: "rgba(0,0,0,0.45)", boxShadow: `0 0 40px ${GOLD}88`, whiteSpace: "nowrap" }}>
        {text}
      </div>
    </div>
  );
};
