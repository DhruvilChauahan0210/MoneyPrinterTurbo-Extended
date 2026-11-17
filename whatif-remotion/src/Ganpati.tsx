import React from "react";
import {
  AbsoluteFill,
  Audio,
  Easing,
  Img,
  interpolate,
  random,
  spring,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import timeline from "./ganpati_timeline.json";

const FPS = 30;
const SERIF = "Baskerville, 'Palatino', serif";
const SANS = "'Avenir Next', 'Helvetica Neue', sans-serif";
const GOLD_GRAD = "linear-gradient(180deg, #fff3c4 0%, #f7c95a 45%, #c8862a 100%)";
const clamp = { extrapolateLeft: "clamp", extrapolateRight: "clamp" } as const;

type Shot = { src: string; from: number; to: number; pos: [number, number]; zoom: [number, number]; pan: [number, number] };

// Cuts land just before each voice line starts.
const SHOTS: Shot[] = [
  { src: "g1_rat.jpg", from: 0, to: 131, pos: [0, 30], zoom: [1.14, 1.04], pan: [22, -16] },
  { src: "g2_noose.jpg", from: 131, to: 225, pos: [40, 50], zoom: [1.0, 1.12], pan: [0, 0] },
  { src: "g3_bow.jpg", from: 225, to: 289, pos: [55, 60], zoom: [1.0, 1.16], pan: [0, -10] },
  { src: "g4_ride.jpg", from: 289, to: 384, pos: [50, 45], zoom: [1.14, 1.02], pan: [0, 20] },
  { src: "g5_idol.jpg", from: 384, to: 450, pos: [55, 50], zoom: [1.0, 1.1], pan: [0, 0] },
];
const XFADE = 10;
const DHOL_HITS = [12.9, 13.5, 13.65, 14.1, 14.55, 14.7].map((s) => Math.round(s * FPS));

const shotOpacity = (frame: number, s: Shot, i: number) => {
  const fadeIn = i === 0 ? interpolate(frame, [0, 18], [0, 1], clamp) : interpolate(frame, [s.from - XFADE, s.from], [0, 1], clamp);
  return frame < s.from - XFADE || frame > s.to ? 0 : fadeIn;
};

const shotTransform = (frame: number, s: Shot) => {
  const p = interpolate(frame, [s.from - XFADE, s.to], [0, 1], { ...clamp, easing: Easing.inOut(Easing.sin) });
  return {
    scale: interpolate(p, [0, 1], s.zoom),
    x: interpolate(p, [0, 1], [s.pan[0], s.pan[1]]),
  };
};

/* ---------- background ---------- */

const BlurBackdrop: React.FC = () => {
  const frame = useCurrentFrame();
  return (
    <AbsoluteFill style={{ backgroundColor: "#140904" }}>
      {SHOTS.map((s, i) => (
        <AbsoluteFill key={s.src} style={{ opacity: shotOpacity(frame, s, i) }}>
          <Img
            src={staticFile(s.src)}
            style={{
              width: "100%",
              height: "100%",
              objectFit: "cover",
              transform: `scale(${1.35 + frame * 0.0006})`,
              filter: "blur(55px) brightness(0.42) saturate(1.4)",
            }}
          />
        </AbsoluteFill>
      ))}
      <AbsoluteFill style={{ background: "radial-gradient(ellipse at 50% 38%, rgba(255,170,60,0.28) 0%, transparent 60%)" }} />
    </AbsoluteFill>
  );
};

export const GodRays: React.FC = () => {
  const frame = useCurrentFrame();
  const boost = interpolate(frame, [380, 400], [0.22, 0.5], clamp);
  return (
    <AbsoluteFill style={{ opacity: boost, mixBlendMode: "screen" }}>
      <div
        style={{
          position: "absolute",
          left: -660,
          top: -540,
          width: 2400,
          height: 2400,
          background:
            "repeating-conic-gradient(from 0deg at 50% 50%, rgba(255,200,110,0.55) 0deg 4deg, transparent 4deg 15deg)",
          transform: `rotate(${frame * 0.12}deg)`,
          maskImage: "radial-gradient(circle at 50% 50%, black 0%, transparent 55%)",
          WebkitMaskImage: "radial-gradient(circle at 50% 50%, black 0%, transparent 55%)",
        }}
      />
    </AbsoluteFill>
  );
};

export const GoldDust: React.FC = () => {
  const frame = useCurrentFrame();
  return (
    <AbsoluteFill style={{ mixBlendMode: "screen" }}>
      {Array.from({ length: 70 }).map((_, i) => {
        const speed = 0.8 + random(`s${i}`) * 2.2;
        const size = 3 + random(`z${i}`) * 9;
        const x = random(`x${i}`) * 1080 + Math.sin(frame / 25 + i) * 18;
        const y = ((random(`y${i}`) * 2100 - frame * speed) % 2100 + 2100) % 2100 - 90;
        const tw = 0.35 + 0.65 * Math.abs(Math.sin(frame / (8 + (i % 7)) + i));
        return (
          <div
            key={i}
            style={{
              position: "absolute",
              left: x,
              top: y,
              width: size,
              height: size,
              borderRadius: "50%",
              background: "radial-gradient(circle, rgba(255,240,190,1) 0%, rgba(255,190,80,0.6) 40%, transparent 70%)",
              opacity: tw,
              boxShadow: `0 0 ${size * 2}px rgba(255,190,80,0.8)`,
            }}
          />
        );
      })}
    </AbsoluteFill>
  );
};

export const Petals: React.FC = () => {
  const frame = useCurrentFrame();
  const start = 384;
  if (frame < start) return null;
  const t = frame - start;
  return (
    <AbsoluteFill>
      {Array.from({ length: 46 }).map((_, i) => {
        const delay = random(`pd${i}`) * 30;
        const lt = t - delay;
        if (lt < 0) return null;
        const fall = 7 + random(`pf${i}`) * 9;
        const x = random(`px${i}`) * 1080 + Math.sin(lt / 12 + i) * 40;
        const y = -60 + lt * fall;
        const rot = lt * (4 + random(`pr${i}`) * 8) * (i % 2 ? 1 : -1);
        const color = i % 3 === 0 ? "#ffcf3a" : i % 3 === 1 ? "#ff9a1f" : "#f2701a";
        const s = 0.7 + random(`ps${i}`) * 0.8;
        return (
          <div
            key={i}
            style={{
              position: "absolute",
              left: x,
              top: y,
              width: 26 * s,
              height: 38 * s,
              borderRadius: "50% 50% 50% 50% / 60% 60% 40% 40%",
              background: `radial-gradient(ellipse at 50% 30%, ${color} 0%, ${color} 55%, rgba(150,50,0,0.9) 100%)`,
              transform: `rotate(${rot}deg) rotateX(${rot * 1.5}deg)`,
              boxShadow: "0 4px 10px rgba(0,0,0,0.35)",
            }}
          />
        );
      })}
    </AbsoluteFill>
  );
};

/* ---------- foreground ---------- */

export const Header: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const a = spring({ frame: frame - 6, fps, config: { damping: 200 }, durationInFrames: 24 });
  const b = spring({ frame: frame - 14, fps, config: { damping: 14 } });
  const line = interpolate(frame, [18, 42], [0, 300], { ...clamp, easing: Easing.out(Easing.cubic) });
  return (
    <div style={{ position: "absolute", top: 120, left: 0, right: 0, display: "flex", flexDirection: "column", alignItems: "center" }}>
      <div style={{ fontFamily: SANS, fontWeight: 600, fontSize: 26, letterSpacing: 14, color: "rgba(255,226,170,0.85)", opacity: a, transform: `translateY(${(1 - a) * 20}px)` }}>
        THE LEGEND OF
      </div>
      <div
        style={{
          fontFamily: SERIF,
          fontWeight: 700,
          fontSize: 92,
          letterSpacing: 2,
          marginTop: 6,
          backgroundImage: GOLD_GRAD,
          WebkitBackgroundClip: "text",
          backgroundClip: "text",
          color: "transparent",
          filter: "drop-shadow(0 6px 18px rgba(0,0,0,0.6))",
          transform: `scale(${0.85 + b * 0.15})`,
          opacity: b,
        }}
      >
        Bappa &amp; Mooshak
      </div>
      <div style={{ display: "flex", alignItems: "center", gap: 14, marginTop: 10 }}>
        <div style={{ width: line, height: 2, background: "linear-gradient(90deg, transparent, #f7c95a)" }} />
        <div style={{ width: 12, height: 12, background: "#f7c95a", transform: "rotate(45deg)", opacity: line / 300 }} />
        <div style={{ width: line, height: 2, background: "linear-gradient(90deg, #f7c95a, transparent)" }} />
      </div>
    </div>
  );
};

const CARD_W = 920;
const CARD_H = 1060;

const Card: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const intro = spring({ frame: frame - 4, fps, config: { damping: 16, mass: 1.1 } });
  const pulse = DHOL_HITS.reduce((acc, h) => acc + (frame >= h ? 0.03 * Math.exp(-(frame - h) / 4) : 0), 0);
  const flash = SHOTS.slice(1).reduce((acc, s) => Math.max(acc, interpolate(frame, [s.from - 6, s.from - 2, s.from + 6], [0, 0.55, 0], clamp)), 0);
  return (
    <div
      style={{
        position: "absolute",
        top: 410,
        left: (1080 - CARD_W) / 2,
        width: CARD_W,
        height: CARD_H,
        transform: `translateY(${(1 - intro) * 120}px) scale(${(0.92 + intro * 0.08) * (1 + pulse)})`,
        opacity: intro,
        borderRadius: 34,
        padding: 4,
        background: "linear-gradient(160deg, #fff1bf 0%, #e0a43c 35%, #7a4612 65%, #f3c766 100%)",
        boxShadow: "0 0 90px rgba(255,170,60,0.45), 0 40px 80px rgba(0,0,0,0.6)",
      }}
    >
      <div style={{ position: "relative", width: "100%", height: "100%", borderRadius: 30, overflow: "hidden", background: "#1a0d05" }}>
        {SHOTS.map((s, i) => {
          const { scale, x } = shotTransform(frame, s);
          return (
            <Img
              key={s.src}
              src={staticFile(s.src)}
              style={{
                position: "absolute",
                inset: 0,
                width: "100%",
                height: "100%",
                objectFit: "cover",
                objectPosition: `${s.pos[0]}% ${s.pos[1]}%`,
                transform: `scale(${scale}) translateX(${x}px)`,
                opacity: shotOpacity(frame, s, i),
              }}
            />
          );
        })}
        <AbsoluteFill style={{ background: "radial-gradient(ellipse at center, transparent 55%, rgba(20,8,0,0.55) 100%)" }} />
        <AbsoluteFill style={{ background: "linear-gradient(115deg, transparent 30%, rgba(255,235,180,0.9) 50%, transparent 70%)", opacity: flash, mixBlendMode: "screen" }} />
      </div>
    </div>
  );
};

type Line = { start: number; end: number; text: string };
const LINES = timeline as Line[];

export const Captions: React.FC = () => {
  const frame = useCurrentFrame();
  const t = frame / FPS;
  const idx = LINES.findIndex((l, i) => t >= l.start - 0.15 && t < (LINES[i + 1]?.start ?? 99) - 0.15);
  if (idx < 0 || idx === LINES.length - 1) return null;
  const line = LINES[idx];
  const words = line.text.split(" ");
  const weights = words.map((w) => w.replace(/[,।!.]/g, "").length + 2);
  const total = weights.reduce((a, b) => a + b, 0);
  let acc = 0;
  const starts = weights.map((w) => {
    const s = line.start + (acc / total) * (line.end - line.start);
    acc += w;
    return s;
  });
  const lineIn = interpolate(t, [line.start - 0.15, line.start + 0.1], [0, 1], clamp);
  return (
    <div
      style={{
        position: "absolute",
        top: 1530,
        left: 70,
        right: 70,
        display: "flex",
        flexWrap: "wrap",
        justifyContent: "center",
        gap: "4px 16px",
        opacity: lineIn,
        transform: `translateY(${(1 - lineIn) * 24}px)`,
      }}
    >
      {words.map((w, i) => {
        const spoken = t >= starts[i];
        const current = spoken && (i === words.length - 1 || t < starts[i + 1]);
        const pop = spoken ? interpolate(t, [starts[i], starts[i] + 0.12], [0.85, 1], clamp) : 0.85;
        return (
          <span
            key={i}
            style={{
              fontFamily: "'Kohinoor Devanagari', 'Avenir Next', sans-serif",
              fontWeight: 700,
              fontSize: 64,
              lineHeight: "78px",
              color: current ? "#ffd56b" : spoken ? "#ffffff" : "rgba(255,255,255,0.4)",
              textShadow: current ? "0 0 24px rgba(255,190,70,0.85), 0 4px 12px rgba(0,0,0,0.8)" : spoken ? "0 4px 12px rgba(0,0,0,0.8)" : "none",
              transform: `scale(${pop})`,
              display: "inline-block",
            }}
          >
            {w}
          </span>
        );
      })}
    </div>
  );
};

export const Finale: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const start = Math.round(LINES[LINES.length - 1].start * FPS) - 4;
  if (frame < start) return null;
  const words = ["गणपति", "बप्पा", "मोरया"];
  const sub = interpolate(frame, [start + 30, start + 44], [0, 1], clamp);
  return (
    <div style={{ position: "absolute", top: 1500, left: 0, right: 0, display: "flex", flexDirection: "column", alignItems: "center" }}>
      <div style={{ display: "flex", gap: 26 }}>
        {words.map((w, i) => {
          const p = spring({ frame: frame - start - i * 8, fps, config: { damping: 9, mass: 0.8 } });
          return (
            <span
              key={w}
              style={{
                fontFamily: "'Kohinoor Devanagari', 'Devanagari Sangam MN', sans-serif",
                fontWeight: 700,
                fontSize: 104,
                lineHeight: "150px",
                backgroundImage: GOLD_GRAD,
                WebkitBackgroundClip: "text",
                backgroundClip: "text",
                color: "transparent",
                filter: "drop-shadow(0 0 22px rgba(255,170,50,0.75)) drop-shadow(0 6px 10px rgba(0,0,0,0.7))",
                transform: `scale(${p}) translateY(${(1 - p) * 40}px)`,
                opacity: Math.min(1, p * 1.5),
                display: "inline-block",
              }}
            >
              {w}
            </span>
          );
        })}
      </div>
      <div style={{ fontFamily: SANS, fontWeight: 600, fontSize: 28, letterSpacing: 16, color: "rgba(255,230,180,0.9)", marginTop: 6, opacity: sub }}>
        GANPATI BAPPA MORYA
      </div>
    </div>
  );
};

export const Grain: React.FC = () => {
  const frame = useCurrentFrame();
  return (
    <AbsoluteFill style={{ mixBlendMode: "overlay", opacity: 0.18 }}>
      <svg width="100%" height="100%">
        <filter id="g">
          <feTurbulence type="fractalNoise" baseFrequency="0.85" numOctaves="2" seed={frame % 10} />
          <feColorMatrix type="saturate" values="0" />
        </filter>
        <rect width="100%" height="100%" filter="url(#g)" />
      </svg>
    </AbsoluteFill>
  );
};

export const Ganpati: React.FC = () => {
  const frame = useCurrentFrame();
  const fromBlack = interpolate(frame, [0, 14], [1, 0], clamp);
  return (
    <AbsoluteFill style={{ backgroundColor: "black" }}>
      <BlurBackdrop />
      <GodRays />
      <GoldDust />
      <Card />
      <Header />
      <Captions />
      <Finale />
      <Petals />
      <AbsoluteFill style={{ background: "radial-gradient(ellipse at center, transparent 55%, rgba(0,0,0,0.6) 100%)" }} />
      <Grain />
      <AbsoluteFill style={{ backgroundColor: "black", opacity: fromBlack }} />

      <Audio src={staticFile("ganpati_voice_hi.wav")} volume={1} />
      <Audio src={staticFile("ganpati_music.wav")} volume={(f) => interpolate(f, [0, 380, 390], [0.4, 0.4, 0.7], clamp)} />
    </AbsoluteFill>
  );
};
