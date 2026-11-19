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

// NewsCut: fast news-drama Short. A hard cut every ~1.2 s on moving clips, the script burned in as 1-3 word captions
// in the centre (white / yellow), small graphics for the numbers, a source card, a split-screen cover as the last frames.
// Props come from gen_newscut.py; all times are seconds.

export type NewsCutShot = {
  from: number;
  dur: number;
  src?: string; // clip in public/
  gfx?: "post" | "crash" | "price"; // graphic drawn over the (dimmed) clip
  marks?: number[]; // seconds from the shot start where the graphic's second step lands
  tag?: string;
  lines?: string[];
  label?: string;
  note?: string;
  a?: string;
  b?: string;
};

export type NewsCutProps = {
  shots: NewsCutShot[];
  caps: { t: number; text: string }[];
  cards?: { from: number; to: number; label?: string; title: string; lines?: string[] }[];
  cover?: { top?: string; bottom?: string; text?: string };
  coverFrames?: number;
  watermark?: string;
  hook?: string; // headline on the opening frames (frame 0 is the feed thumbnail)
  hookDur?: number; // seconds the hook stays up
  audioFile: string;
  voiceEnd?: number;
  durationInSeconds?: number;
};

const FONT_BIG = "Impact, 'Arial Narrow Bold', 'Arial Black', Arial, sans-serif";
const FONT = "'Arial Black', Arial, Helvetica, sans-serif";
const FONT_CAP = "'Avenir Next', 'Arial Black', Arial, sans-serif";
const YELLOW = "#ffe400";
const RED = "#ff2d2d";
const GOLD = "#f5c542";
const CLAMP = { extrapolateLeft: "clamp", extrapolateRight: "clamp" } as const;

// round black outline made of text shadows (text-stroke gives spikes on M / N / W at this width)
const outline = (r: number, extra = ""): string => {
  const out: string[] = [];
  for (const [rad, n] of [[r, 36], [r * 0.55, 20]] as const) {
    for (let i = 0; i < n; i++) {
      const a = (i / n) * Math.PI * 2;
      out.push(`${(Math.cos(a) * rad).toFixed(1)}px ${(Math.sin(a) * rad).toFixed(1)}px 0 #000`);
    }
  }
  if (extra) out.push(extra);
  return out.join(", ");
};

// "€120 → €17": the arrow is drawn, Impact has no arrow glyph
const WithArrow: React.FC<{ text: string; size: number; color: string; outlined?: boolean }> = ({ text, size, color, outlined }) => {
  const parts = text.split("→");
  const d = "M4 25 H46 M30 7 L50 25 L30 43";
  return (
    <>
      {parts.map((part, i) => (
        <React.Fragment key={i}>
          {i > 0 ? (
            <svg width={size * 0.6} height={size * 0.5} viewBox="0 0 56 50" style={{ display: "inline-block", margin: `0 ${size * 0.1}px`, verticalAlign: "middle", overflow: "visible" }}>
              {outlined ? <path d={d} stroke="#000" strokeWidth={22} fill="none" strokeLinecap="round" strokeLinejoin="round" /> : null}
              <path d={d} stroke={color} strokeWidth={9} fill="none" strokeLinecap="round" strokeLinejoin="round" />
            </svg>
          ) : null}
          <span>{part.trim()}</span>
        </React.Fragment>
      ))}
    </>
  );
};

const Tag: React.FC<{ text: string; top: number }> = ({ text, top }) => (
  <div style={{ position: "absolute", top, left: 0, right: 0, display: "flex", justifyContent: "center" }}>
    <div style={{ fontFamily: FONT, fontSize: 36, letterSpacing: 3, color: "#fff", background: RED, padding: "10px 28px", borderRadius: 12, boxShadow: "0 8px 24px rgba(0,0,0,0.5)" }}>
      {text}
    </div>
  </div>
);

// a generic social post (no platform, no account): the claim, stamped as unverified
const PostCard: React.FC<{ s: NewsCutShot }> = ({ s }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const sp = spring({ frame, fps, config: { damping: 14, mass: 0.5 } });
  const stamp = spring({ frame: frame - 7, fps, config: { damping: 10, mass: 0.5 } });
  const lines = s.lines ?? [];
  return (
    <div style={{ position: "absolute", left: 90, width: 900, top: 280, transform: `rotate(-2.5deg) scale(${interpolate(sp, [0, 1], [0.86, 1])})`, opacity: interpolate(frame, [0, 3], [0.5, 1], CLAMP) }}>
      <div style={{ background: "#fff", borderRadius: 36, padding: "34px 40px 32px", boxShadow: "0 30px 80px rgba(0,0,0,0.65)" }}>
        <div style={{ display: "flex", alignItems: "center", gap: 24 }}>
          <div style={{ width: 92, height: 92, borderRadius: 46, background: "#c9ced6" }} />
          <div style={{ flex: 1 }}>
            <div style={{ width: 270, height: 26, borderRadius: 13, background: "#c9ced6" }} />
            <div style={{ width: 170, height: 20, borderRadius: 10, background: "#dfe3e8", marginTop: 14 }} />
          </div>
          {s.tag ? <div style={{ fontFamily: FONT, fontSize: 30, letterSpacing: 2, color: "#fff", background: "#14171a", padding: "8px 20px", borderRadius: 10 }}>{s.tag}</div> : null}
        </div>
        <div style={{ marginTop: 26, fontFamily: "Arial, Helvetica, sans-serif", fontSize: 46, lineHeight: 1.2, color: "#14171a" }}>{lines[0]}</div>
        <div style={{ marginTop: 6, fontFamily: FONT_BIG, fontSize: 150, lineHeight: 1.05, color: "#14171a", whiteSpace: "nowrap" }}>
          <WithArrow text={lines[1] ?? ""} size={150} color="#14171a" />
        </div>
        <div style={{ display: "flex", gap: 46, marginTop: 20 }}>
          {[96, 96, 96].map((w, i) => (
            <div key={i} style={{ width: w, height: 22, borderRadius: 11, background: "#dfe3e8" }} />
          ))}
        </div>
      </div>
      {s.note && frame >= 7 ? (
        <div style={{ position: "absolute", right: -6, bottom: -40, fontFamily: FONT_BIG, fontSize: 60, letterSpacing: 2, color: RED, background: "#fff", border: `8px solid ${RED}`, borderRadius: 14, padding: "4px 22px", transform: `rotate(-7deg) scale(${interpolate(stamp, [0, 1], [1.7, 1])})`, boxShadow: "0 12px 30px rgba(0,0,0,0.5)" }}>
          {s.note}
        </div>
      ) : null}
    </div>
  );
};

const CRASH_PTS: [number, number][] = [[0, 70], [80, 48], [150, 86], [230, 58], [310, 104], [380, 82], [450, 170], [520, 140], [600, 280], [680, 320], [760, 410], [860, 440]];

const crashY = (x: number): number => {
  for (let i = 1; i < CRASH_PTS.length; i++) {
    const [x0, y0] = CRASH_PTS[i - 1];
    const [x1, y1] = CRASH_PTS[i];
    if (x <= x1) return y0 + ((y1 - y0) * (x - x0)) / (x1 - x0);
  }
  return CRASH_PTS[CRASH_PTS.length - 1][1];
};

// a falling red line (the claim), then the claimed number with a question mark
const CrashGfx: React.FC<{ s: NewsCutShot }> = ({ s }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const draw = interpolate(frame, [0, Math.round(0.85 * fps)], [0.04, 1], { ...CLAMP, easing: Easing.inOut(Easing.quad) });
  const m = Math.round((s.marks?.[0] ?? 0.6) * fps);
  const sp = spring({ frame: frame - m, fps, config: { damping: 10, mass: 0.6 } });
  const line = "M" + CRASH_PTS.map((q) => q.join(" ")).join(" L");
  const tipX = 860 * draw;
  return (
    <>
      {s.tag ? <Tag text={s.tag} top={270} /> : null}
      <svg width={940} height={500} viewBox="-40 0 940 500" style={{ position: "absolute", left: 70, top: 350, overflow: "visible" }}>
        <defs>
          <linearGradient id="ncfall" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0" stopColor={RED} stopOpacity={0.55} />
            <stop offset="1" stopColor={RED} stopOpacity={0} />
          </linearGradient>
          <clipPath id="ncclip">
            <rect x={-40} y={-40} width={tipX + 40} height={600} />
          </clipPath>
        </defs>
        {[40, 160, 280, 400].map((y) => (
          <line key={y} x1={0} x2={860} y1={y} y2={y} stroke="rgba(255,255,255,0.16)" strokeWidth={3} />
        ))}
        <g clipPath="url(#ncclip)">
          <path d={`${line} L860 480 L0 480 Z`} fill="url(#ncfall)" />
          <path d={line} stroke="#000" strokeWidth={30} fill="none" strokeLinecap="round" strokeLinejoin="round" />
          <path d={line} stroke={RED} strokeWidth={16} fill="none" strokeLinecap="round" strokeLinejoin="round" />
        </g>
        <circle cx={tipX} cy={crashY(tipX)} r={20} fill="#fff" stroke={RED} strokeWidth={10} />
      </svg>
      {s.label && frame >= m ? (
        <div style={{ position: "absolute", top: 1085, left: 0, right: 0, textAlign: "center", fontFamily: FONT_BIG, fontSize: 250, lineHeight: 1, color: RED, textShadow: outline(13, "0 18px 30px rgba(0,0,0,0.7)"), transform: `scale(${interpolate(sp, [0, 1], [0.5, 1])})` }}>
          {s.label}
        </div>
      ) : null}
    </>
  );
};

// the two prices of the claim: the first struck out, the second dropping in
const PriceGfx: React.FC<{ s: NewsCutShot }> = ({ s }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const m = Math.round((s.marks?.[0] ?? 1) * fps);
  const inA = spring({ frame, fps, config: { damping: 12, mass: 0.5 } });
  const strike = interpolate(frame, [m - 4, m + 3], [0, 1], CLAMP);
  const inB = spring({ frame: frame - m, fps, config: { damping: 10, mass: 0.6 } });
  return (
    <>
      {s.tag ? <Tag text={s.tag} top={270} /> : null}
      <div style={{ position: "absolute", top: 350, left: 0, right: 0, display: "flex", justifyContent: "center" }}>
        <div style={{ position: "relative", fontFamily: FONT_BIG, fontSize: 300, lineHeight: 1, color: "#fff", opacity: 1 - 0.25 * strike, textShadow: outline(13, "0 18px 30px rgba(0,0,0,0.7)"), transform: `scale(${interpolate(inA, [0, 1], [0.8, 1])})` }}>
          {s.a}
          <div style={{ position: "absolute", left: "-6%", top: "52%", height: 26, width: `${112 * strike}%`, background: RED, borderRadius: 13, transform: "rotate(-9deg)", transformOrigin: "left center", boxShadow: "0 0 0 7px #000" }} />
        </div>
      </div>
      {frame >= m ? (
        <div style={{ position: "absolute", top: 1085, left: 0, right: 0, display: "flex", justifyContent: "center", alignItems: "center", gap: 26, transform: `scale(${interpolate(inB, [0, 1], [0.5, 1])})` }}>
          <svg width={150} height={176} viewBox="-6 -6 162 182">
            <path d="M75 165 L8 70 H48 V5 H102 V70 H142 Z" fill={RED} stroke="#000" strokeWidth={12} strokeLinejoin="round" />
          </svg>
          <div style={{ fontFamily: FONT_BIG, fontSize: 330, lineHeight: 1, color: RED, textShadow: outline(14, "0 18px 30px rgba(0,0,0,0.7)") }}>{s.b}</div>
        </div>
      ) : null}
    </>
  );
};

const Shot: React.FC<{ s: NewsCutShot; frames: number }> = ({ s, frames }) => {
  const frame = useCurrentFrame();
  const zoom = 1.03 + 0.05 * (frames > 1 ? frame / (frames - 1) : 0);
  return (
    <AbsoluteFill style={{ overflow: "hidden", background: "#000" }}>
      {s.src ? (
        <OffthreadVideo
          src={staticFile(s.src)}
          muted
          style={{ width: "100%", height: "100%", objectFit: "cover", transform: `scale(${zoom})`, filter: s.gfx ? "brightness(0.36) saturate(0.8) blur(6px)" : undefined }}
        />
      ) : null}
      {s.gfx === "post" ? <PostCard s={s} /> : null}
      {s.gfx === "crash" ? <CrashGfx s={s} /> : null}
      {s.gfx === "price" ? <PriceGfx s={s} /> : null}
    </AbsoluteFill>
  );
};

const Caption: React.FC<{ caps: { t: number; text: string }[] }> = ({ caps }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  if (!caps.length) return null;
  let i = 0;
  caps.forEach((c, k) => {
    if (frame >= Math.round(c.t * fps)) i = k;
  });
  const sp = i === 0 ? 1 : spring({ frame: frame - Math.round(caps[i].t * fps), fps, config: { damping: 12, mass: 0.4, stiffness: 220 } });
  return (
    <div style={{ position: "absolute", left: 70, right: 70, top: "49%", transform: `translateY(-50%) scale(${interpolate(sp, [0, 1], [0.8, 1])})`, textAlign: "center" }}>
      <div style={{ fontFamily: FONT_CAP, fontWeight: 900, fontSize: 104, lineHeight: 1.04, letterSpacing: -1, textTransform: "uppercase", color: i % 2 === 0 ? "#fff" : YELLOW, textShadow: outline(10, "0 12px 0 #000, 0 16px 28px rgba(0,0,0,0.75)") }}>
        {caps[i].text}
      </div>
    </div>
  );
};

const SourceCard: React.FC<{ c: { from: number; to: number; label?: string; title: string; lines?: string[] } }> = ({ c }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const t = frame / fps;
  if (t < c.from || t >= c.to) return null;
  const a = interpolate(t, [c.from, c.from + 0.25], [0, 1], { ...CLAMP, easing: Easing.out(Easing.cubic) });
  const b = interpolate(t, [c.to - 0.2, c.to], [1, 0], CLAMP);
  const lines = c.lines ?? [];
  return (
    <div style={{ position: "absolute", left: 50, width: 860, top: 1270, transform: `translateY(${(1 - a) * 60}px)`, opacity: Math.min(a, b), background: "rgba(8,10,20,0.92)", borderRadius: 22, borderLeft: `12px solid ${GOLD}`, padding: "20px 30px 22px", boxSizing: "border-box", boxShadow: "0 16px 40px rgba(0,0,0,0.55)" }}>
      <div style={{ fontFamily: FONT, fontSize: 28, letterSpacing: 5, color: GOLD }}>{c.label ?? "SOURCE"}</div>
      <div style={{ fontFamily: FONT, fontSize: 52, lineHeight: 1.15, color: "#fff", marginTop: 4 }}>{c.title}</div>
      {lines[0] ? <div style={{ fontFamily: "Arial, Helvetica, sans-serif", fontSize: 32, color: "rgba(255,255,255,0.72)", marginTop: 6 }}>{lines[0]}</div> : null}
      {lines[1] ? <div style={{ fontFamily: "Arial, Helvetica, sans-serif", fontWeight: 700, fontSize: 40, color: "#fff", marginTop: 8 }}>{lines[1]}</div> : null}
    </div>
  );
};

const Cover: React.FC<{ cover: { top?: string; bottom?: string; text?: string } }> = ({ cover }) => (
  <AbsoluteFill style={{ background: "#000" }}>
    {cover.top ? <Img src={staticFile(cover.top)} style={{ position: "absolute", top: 0, left: 0, width: 1080, height: 960, objectFit: "cover", objectPosition: "50% 30%" }} /> : null}
    {cover.bottom ? <Img src={staticFile(cover.bottom)} style={{ position: "absolute", top: 960, left: 0, width: 1080, height: 960, objectFit: "cover" }} /> : null}
    <div style={{ position: "absolute", top: 954, left: 0, right: 0, height: 12, background: "#fff" }} />
    {cover.text ? (
      <div style={{ position: "absolute", top: 960, left: 0, right: 0, transform: "translateY(-50%)", textAlign: "center", fontFamily: FONT_BIG, fontSize: 190, lineHeight: 1, color: YELLOW, whiteSpace: "nowrap", textShadow: outline(13, "0 18px 30px rgba(0,0,0,0.7)") }}>
        <WithArrow text={cover.text} size={190} color={YELLOW} outlined />
      </div>
    ) : null}
  </AbsoluteFill>
);

export const NewsCut: React.FC<NewsCutProps> = (p) => {
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();
  const hasCover = !!(p.cover && (p.cover.top || p.cover.bottom));
  const bodyEnd = durationInFrames - (hasCover ? p.coverFrames ?? 0 : 0);
  const starts = p.shots.map((s) => Math.round(s.from * fps));
  return (
    <AbsoluteFill style={{ background: "#000" }}>
      {p.shots.map((s, i) => {
        const end = i + 1 < p.shots.length ? starts[i + 1] : bodyEnd;
        const frames = Math.max(1, end - starts[i]);
        return (
          <Sequence key={i} from={starts[i]} durationInFrames={frames}>
            <Shot s={s} frames={frames} />
          </Sequence>
        );
      })}
      <AbsoluteFill style={{ background: "linear-gradient(to bottom, rgba(0,0,0,0.42) 0%, rgba(0,0,0,0) 16%)" }} />
      {p.watermark ? (
        <div style={{ position: "absolute", top: 168, right: 46, fontFamily: FONT_BIG, fontSize: 40, letterSpacing: 2, color: GOLD, textShadow: outline(3, "0 4px 10px rgba(0,0,0,0.8)") }}>{p.watermark}</div>
      ) : null}
      {(p.cards ?? []).map((c, i) => (
        <SourceCard key={i} c={c} />
      ))}
      <Caption caps={p.caps} />
      {p.hook && frame < Math.round((p.hookDur ?? 0.7) * fps) ? (
        <div style={{ position: "absolute", left: 50, right: 50, top: 250, textAlign: "center", fontFamily: FONT_BIG, fontSize: 132, lineHeight: 1.02, color: YELLOW, textTransform: "uppercase", textShadow: outline(12, "0 16px 30px rgba(0,0,0,0.75)") }}>
          {p.hook}
        </div>
      ) : null}
      {hasCover && frame >= bodyEnd ? <Cover cover={p.cover!} /> : null}
      <Audio src={staticFile(p.audioFile)} volume={1} />
    </AbsoluteFill>
  );
};
