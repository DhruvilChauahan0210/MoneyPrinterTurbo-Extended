import React from "react";
import {
  AbsoluteFill,
  Audio,
  Img,
  OffthreadVideo,
  Sequence,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
  interpolate,
  spring,
  Easing,
} from "remotion";

// R2 prototype: 'PICK ONE' duel. Two portraits, a visible countdown in frame 1, four stat rows that animate in as
// butterfly bars with counting numbers, then a hard-number reveal and a question. All text comes from props.

export type DuelSide = {
  name: string; // shown on the photo, e.g. "DEMBÉLÉ"
  sub: string; // small line under the name, e.g. "PSG"
  photo: string; // file in public/
  color: string; // bar + accent colour
  posX?: number; // object-position x % (face focus)
  posY?: number; // object-position y %
  zoom?: number; // extra zoom on the face
  clips?: string[]; // moving clips in public/, cycled every clipSeconds; preferred over the photo
};

export type DuelRow = {
  label: string;
  a: number;
  b: number;
  fmt?: "num" | "comma";
  win?: "a" | "b"; // who takes the point; omit for a neutral row
};

export type DuelProps = {
  headline: string; // "PICK ONE"
  countdownSeconds: number; // 5
  left: DuelSide;
  right: DuelSide;
  rows: DuelRow[]; // 4 rows
  rowStarts: number[]; // seconds each row starts (synced to the voice)
  revealAt: number; // seconds the reveal starts
  reveal: { number: number; fmt?: "num" | "comma"; label: string; detail: string; question: string };
  source: string;
  audioFile: string; // one pre-mixed wav (voice + ducked music + sfx)
  durationInSeconds?: number;
};

const FONT_BIG = "Impact, 'Arial Narrow Bold', 'Arial Black', Arial, sans-serif";
const FONT = "'Arial Black', Arial, Helvetica, sans-serif";

const fmtNum = (n: number, f?: "num" | "comma") => {
  const r = Math.round(n);
  if (f === "comma") return String(r).replace(/\B(?=(\d{3})+(?!\d))/g, ",");
  return String(r);
};

const PHOTO_W = 510;
const PHOTO_H = 560;
const PHOTO_Y = 380;
const ROWS_Y = 985;
const ROWS_TOTAL = 688;

const CLIP_SECONDS = 4.5;

const Photo: React.FC<{ side: DuelSide; x: number; t: number; dim: number; flash: number; dir: number }> = ({ side, x, t, dim, flash, dir }) => {
  const { fps, durationInFrames } = useVideoConfig();
  const z = (side.zoom ?? 1) * (1.02 + 0.06 * Math.min(1, t / 18) + 0.05 * flash);
  const drift = dir * 10 * Math.sin(t * 0.6);
  const pos = `${side.posX ?? 50}% ${side.posY ?? 25}%`;
  return (
    <div
      style={{
        position: "absolute",
        left: x,
        top: PHOTO_Y,
        width: PHOTO_W,
        height: PHOTO_H,
        overflow: "hidden",
        borderRadius: 26,
        border: `${6 + 4 * flash}px solid ${flash > 0.05 ? "#fff" : side.color}`,
        boxShadow: `0 0 ${40 + 80 * flash}px ${side.color}${flash > 0.05 ? "ee" : "66"}`,
        transform: `translateY(${-14 * flash}px)`,
        background: "#000",
      }}
    >
      {side.clips && side.clips.length ? (
        Array.from({ length: Math.ceil(durationInFrames / (CLIP_SECONDS * fps)) }).map((_, k) => {
          const from = Math.round(k * CLIP_SECONDS * fps);
          return (
            <Sequence key={k} from={from} durationInFrames={Math.round(CLIP_SECONDS * fps)} layout="none">
              <OffthreadVideo
                src={staticFile(side.clips![k % side.clips!.length])}
                muted
                style={{
                  position: "absolute",
                  inset: 0,
                  width: "100%",
                  height: "100%",
                  objectFit: "cover",
                  objectPosition: "50% 30%",
                  transform: `scale(${1.05 + 0.05 * flash})`,
                  filter: `brightness(${1 - dim})`,
                }}
              />
            </Sequence>
          );
        })
      ) : (
        <Img
          src={staticFile(side.photo)}
          style={{
            width: "100%",
            height: "100%",
            objectFit: "cover",
            objectPosition: pos,
            transform: `scale(${z}) translateX(${drift}px)`,
            transformOrigin: pos,
            filter: `brightness(${1 - dim})`,
          }}
        />
      )}
      <div
        style={{
          position: "absolute",
          left: 0,
          right: 0,
          bottom: 0,
          height: 190,
          background: "linear-gradient(to top, rgba(0,0,0,0.92), rgba(0,0,0,0))",
        }}
      />
      <div style={{ position: "absolute", left: 0, right: 0, bottom: 14, textAlign: "center" }}>
        <div
          style={{
            fontFamily: FONT_BIG,
            fontSize: 74,
            lineHeight: 1,
            color: "white",
            letterSpacing: 1,
            textShadow: "0 3px 12px rgba(0,0,0,0.8)",
          }}
        >
          {side.name}
        </div>
        <div style={{ fontFamily: FONT, fontSize: 28, color: side.color, marginTop: 4, letterSpacing: 3 }}>
          {side.sub}
        </div>
      </div>
    </div>
  );
};

export const Duel: React.FC<DuelProps> = (p) => {
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();
  const t = frame / fps;

  // Countdown: number 5 -> 0 and a draining bar. Both are fully visible on frame 0 (thumbnail).
  const remaining = Math.max(0, p.countdownSeconds - t);
  const shown = remaining > 0 ? Math.ceil(remaining) : 0;
  const barFrac = remaining / p.countdownSeconds;
  const barColor = barFrac > 0.5 ? "#35e07a" : barFrac > 0.25 ? "#ffd12b" : "#ff3b3b";
  const tickPulse = remaining > 0 ? 1 + 0.12 * Math.max(0, 1 - ((t % 1) / 0.18)) : 1;
  const locked = remaining <= 0;

  const ROW_H = ROWS_TOTAL / Math.max(1, p.rows.length);
  const compact = p.rows.length > 4;
  // A row "lands" 1.0 s after it starts; the winner takes a point and their photo flashes.
  const landed = p.rows.map((r, i) => ({ r, at: (p.rowStarts[i] ?? 999) + 1.0 }));
  const scoreA = landed.filter((x) => x.r.win === "a" && t >= x.at).length;
  const scoreB = landed.filter((x) => x.r.win === "b" && t >= x.at).length;
  const flashFor = (w: "a" | "b") =>
    landed.filter((x) => x.r.win === w && t >= x.at).reduce((m, x) => Math.max(m, Math.exp(-(t - x.at) / 0.35)), 0);
  const flashA = flashFor("a");
  const flashB = flashFor("b");
  const lastScore = landed.filter((x) => x.r.win && t >= x.at).reduce((m, x) => Math.max(m, x.at), -99);
  const scorePop = 1 + 0.35 * Math.exp(-(t - lastScore) / 0.25);
  const revealT = t - p.revealAt;
  const revealOn = revealT >= 0;
  const revealSpring = spring({ frame: frame - Math.round(p.revealAt * fps), fps, config: { damping: 13, mass: 0.7 } });
  const rowsFade = revealOn ? interpolate(revealT, [0, 0.25], [1, 0.0], { extrapolateRight: "clamp" }) : 1;

  return (
    <AbsoluteFill style={{ background: "radial-gradient(ellipse at 50% 30%, #1c2340 0%, #0a0d1a 70%)" }}>
      {/* HEADER: PICK ONE + timer number + draining bar. Visible and fully formed on frame 0. */}
      <div style={{ position: "absolute", top: 96, left: 0, right: 0, textAlign: "center" }}>
        <div style={{ display: "flex", justifyContent: "center", alignItems: "baseline", gap: 26 }}>
          <span style={{ fontFamily: FONT_BIG, fontSize: 150, color: "#fff", letterSpacing: 2, lineHeight: 1 }}>
            {p.headline}
          </span>
          {locked ? null : (
            <span
              style={{
                fontFamily: FONT_BIG,
                fontSize: 190,
                color: barColor,
                lineHeight: 1,
                transform: `scale(${tickPulse})`,
                display: "inline-block",
                minWidth: 120,
                textAlign: "left",
              }}
            >
              {shown}
            </span>
          )}
        </div>
        {locked ? (
          <div style={{ display: "flex", justifyContent: "center", alignItems: "center", gap: 24, marginTop: 14 }}>
            <span style={{ fontFamily: FONT_BIG, fontSize: 64, color: p.left.color, letterSpacing: 1 }}>{p.left.name}</span>
            <span style={{ fontFamily: FONT_BIG, fontSize: 104, color: "#fff", display: "inline-block", transform: `scale(${scorePop})`, minWidth: 220, textAlign: "center", background: "rgba(255,255,255,0.10)", borderRadius: 18, padding: "0 18px" }}>
              {scoreA} - {scoreB}
            </span>
            <span style={{ fontFamily: FONT_BIG, fontSize: 64, color: p.right.color, letterSpacing: 1 }}>{p.right.name}</span>
          </div>
        ) : null}
        <div
          style={{
            display: locked ? "none" : "block",
            margin: "22px auto 0",
            width: 920,
            height: 34,
            borderRadius: 17,
            background: "rgba(255,255,255,0.14)",
            overflow: "hidden",
          }}
        >
          <div style={{ width: `${barFrac * 100}%`, height: "100%", background: barColor, borderRadius: 17 }} />
        </div>
      </div>

      {/* PHOTOS */}
      <Photo side={p.left} x={18} t={t} dim={revealOn ? 0.25 : 0} flash={flashA} dir={1} />
      <Photo side={p.right} x={1080 - 18 - PHOTO_W} t={t} dim={revealOn ? 0.25 : 0} flash={flashB} dir={-1} />
      <div
        style={{
          position: "absolute",
          left: 540 - 46,
          top: PHOTO_Y + PHOTO_H / 2 - 46,
          width: 92,
          height: 92,
          borderRadius: 46,
          background: "#fff",
          color: "#0a0d1a",
          fontFamily: FONT_BIG,
          fontSize: 52,
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          boxShadow: "0 0 30px rgba(0,0,0,0.6)",
          transform: `scale(${1 + 0.08 * Math.sin(t * 5)}) rotate(${4 * Math.sin(t * 2.3)}deg)`,
        }}
      >
        VS
      </div>

      {/* STAT ROWS (butterfly bars) */}
      <div style={{ position: "absolute", left: 0, top: ROWS_Y, width: 1080, height: ROWS_TOTAL, opacity: rowsFade }}>
        {p.rows.map((r, i) => {
          const start = p.rowStarts[i] ?? 999;
          const local = t - start;
          const prog = interpolate(local, [0, 1.0], [0, 1], {
            easing: Easing.out(Easing.cubic),
            extrapolateLeft: "clamp",
            extrapolateRight: "clamp",
          });
          const on = local >= 0;
          const max = Math.max(r.a, r.b);
          const maxLen = 400;
          const la = (r.a / max) * maxLen * prog;
          const lb = (r.b / max) * maxLen * prog;
          const slide = on ? interpolate(local, [0, 0.35], [24, 0], { extrapolateRight: "clamp", easing: Easing.out(Easing.quad) }) : 24;
          const won = r.win && local >= 1.0;
          const glow = won ? 0.5 + 0.5 * Math.abs(Math.sin((local - 1.0) * 4)) : 0;
          const BAR_H = compact ? 58 : 72;
          return (
            <div key={i} style={{ position: "absolute", left: 0, top: i * ROW_H, width: 1080, height: ROW_H }}>
              <div
                style={{
                  textAlign: "center",
                  fontFamily: FONT,
                  fontSize: compact ? 30 : 36,
                  letterSpacing: compact ? 3 : 4,
                  color: on ? "#fff" : "rgba(255,255,255,0.35)",
                  textTransform: "uppercase",
                  marginTop: compact ? 2 : 8,
                  transform: `translateY(${slide}px)`,
                }}
              >
                {r.label}
              </div>
              <div style={{ position: "relative", height: BAR_H + 12, marginTop: compact ? 8 : 24 }}>
                {/* ghost tracks */}
                <div style={{ position: "absolute", right: 546, top: 6, width: maxLen, height: BAR_H, borderRadius: 14, background: "rgba(255,255,255,0.07)" }} />
                <div style={{ position: "absolute", left: 546, top: 6, width: maxLen, height: BAR_H, borderRadius: 14, background: "rgba(255,255,255,0.07)" }} />
                {on ? (
                  <>
                    <div
                      style={{
                        position: "absolute",
                        right: 546,
                        top: 6,
                        width: la,
                        height: BAR_H,
                        borderRadius: 14,
                        background: p.left.color,
                        boxShadow: won && r.win === "a" ? `0 0 ${18 + 30 * glow}px ${p.left.color}` : "none",
                        outline: won && r.win === "a" ? "3px solid #fff" : "none",
                        display: "flex",
                        alignItems: "center",
                        justifyContent: "flex-start",
                        paddingLeft: 18,
                        overflow: "hidden",
                      }}
                    >
                      <span style={{ fontFamily: FONT_BIG, fontSize: compact ? 52 : 62, color: "#fff", textShadow: "0 2px 6px rgba(0,0,0,0.5)", whiteSpace: "nowrap" }}>
                        {fmtNum(r.a * prog, r.fmt)}
                      </span>
                    </div>
                    <div
                      style={{
                        position: "absolute",
                        left: 546,
                        top: 6,
                        width: lb,
                        height: BAR_H,
                        borderRadius: 14,
                        background: p.right.color,
                        boxShadow: won && r.win === "b" ? `0 0 ${18 + 30 * glow}px ${p.right.color}` : "none",
                        outline: won && r.win === "b" ? "3px solid #fff" : "none",
                        display: "flex",
                        alignItems: "center",
                        justifyContent: "flex-end",
                        paddingRight: 18,
                        overflow: "hidden",
                      }}
                    >
                      <span style={{ fontFamily: FONT_BIG, fontSize: compact ? 52 : 62, color: "#fff", textShadow: "0 2px 6px rgba(0,0,0,0.5)", whiteSpace: "nowrap" }}>
                        {fmtNum(r.b * prog, r.fmt)}
                      </span>
                    </div>
                  </>
                ) : null}
              </div>
            </div>
          );
        })}
      </div>

      {/* REVEAL: hard number + question */}
      {revealOn ? (
        <div
          style={{
            position: "absolute",
            left: 30,
            right: 30,
            top: ROWS_Y - 10,
            height: ROWS_TOTAL + 10,
            borderRadius: 30,
            background: "rgba(8,10,22,0.93)",
            border: "4px solid #ffd12b",
            transform: `scale(${interpolate(revealSpring, [0, 1], [0.8, 1])})`,
            opacity: interpolate(revealT, [0, 0.15], [0, 1], { extrapolateRight: "clamp" }),
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
            justifyContent: "center",
            gap: 4,
          }}
        >
          <div style={{ fontFamily: FONT_BIG, fontSize: 330, lineHeight: 1, color: "#ffd12b" }}>
            {fmtNum(p.reveal.number * interpolate(revealT, [0, 0.8], [0, 1], { extrapolateRight: "clamp", easing: Easing.out(Easing.cubic) }), p.reveal.fmt)}
          </div>
          <div style={{ fontFamily: FONT, fontSize: 44, color: "#fff", letterSpacing: 3, textAlign: "center" }}>{p.reveal.label}</div>
          <div style={{ fontFamily: FONT, fontSize: 30, color: "rgba(255,255,255,0.7)", marginTop: 6 }}>{p.reveal.detail}</div>
          <div
            style={{
              fontFamily: FONT_BIG,
              fontSize: 82,
              color: "#fff",
              marginTop: 26,
              textAlign: "center",
              transform: `scale(${1 + 0.04 * Math.sin(revealT * 6)})`,
              opacity: interpolate(revealT, [1.0, 1.3], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" }),
            }}
          >
            {p.reveal.question}
          </div>
        </div>
      ) : null}

      {/* source line */}
      <div style={{ position: "absolute", left: 0, right: 0, top: 1664, textAlign: "center", fontFamily: "Arial, sans-serif", fontSize: 24, color: "rgba(255,255,255,0.45)" }}>
        {p.source}
      </div>

      <Audio src={staticFile(p.audioFile)} volume={1} />
    </AbsoluteFill>
  );
};
