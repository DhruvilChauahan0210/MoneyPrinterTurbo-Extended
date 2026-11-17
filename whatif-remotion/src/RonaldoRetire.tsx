import React from "react";
import { AbsoluteFill, Audio, Img, Sequence, interpolate, random, staticFile, useCurrentFrame } from "remotion";
import { COND, SANS, GOLD, RONALDO, FPS, clamp, out, sp, Counter } from "./goatKit";
import timeline from "./ronaldo_timeline.json";
import manifest from "../public/ronaldo_retire/manifest.json";

type Ov = any;
type Scene = {
  i: number; start: number; end: number; voice_at: number; vd: number;
  text: string; shot: string; ov: Ov[]; kb?: string | null; ch?: number; title?: string;
};

const SCENES = (timeline as any).scenes as Scene[];
export const RETIRE_DURATION = Math.round((timeline as any).total * FPS);
const fr = (s: number) => Math.round(s * FPS);
const WHITE = "#ffffff";
const colorOf = (c?: string) => (c === "red" ? RONALDO : c === "gold" ? GOLD : WHITE);
const CHAPTERS = SCENES.filter((s) => s.ch).map((s) => ({ n: s.ch as number, at: s.start, title: s.title as string }));

// ---------------------------------------------------------------- photo
const Photo: React.FC<{ shot: string; kb: string; len: number; dim?: number }> = ({ shot, kb, len, dim = 0.18 }) => {
  const f = useCurrentFrame();
  const meta = (manifest as any)[shot] || { w: 1920, h: 1080 };
  const ar = meta.w / meta.h;
  const t = f / Math.max(1, len);
  let scale = 1.05, tx = 0, ty = 0;
  if (kb === "in") scale = 1.04 + t * 0.14;
  else if (kb === "out") scale = 1.18 - t * 0.14;
  else if (kb === "left") { scale = 1.14; tx = (0.5 - t) * 70; }
  else if (kb === "right") { scale = 1.14; tx = (t - 0.5) * 70; }
  else if (kb === "up") { scale = 1.14; ty = (0.5 - t) * 50; }
  const punch = interpolate(f, [0, 9], [1.07, 1], { ...clamp, easing: out });
  const src = staticFile(`ronaldo_retire/${shot}.jpg`);
  const contain = ar < 1.34;
  const fade = interpolate(f, [0, 6], [0, 1], clamp);
  return (
    <AbsoluteFill style={{ opacity: fade, overflow: "hidden", background: "#05070d" }}>
      {contain && (
        <Img src={src} style={{ position: "absolute", inset: -60, width: "calc(100% + 120px)", height: "calc(100% + 120px)", objectFit: "cover", filter: "blur(46px) brightness(0.42) saturate(1.2)" }} />
      )}
      <AbsoluteFill style={{ transform: `translate(${tx}px, ${ty}px) scale(${scale * punch})` }}>
        <Img
          src={src}
          style={{
            width: "100%", height: "100%", objectFit: contain ? "contain" : "cover",
            filter: "contrast(1.1) saturate(1.12) brightness(0.92)",
            boxShadow: contain ? "0 0 120px rgba(0,0,0,0.6)" : undefined,
          }}
        />
      </AbsoluteFill>
      <AbsoluteFill style={{ background: `linear-gradient(180deg, rgba(5,7,13,0.55) 0%, rgba(5,7,13,${dim}) 26%, rgba(5,7,13,${dim}) 52%, rgba(5,7,13,0.78) 100%)` }} />
      <AbsoluteFill style={{ background: "radial-gradient(ellipse at 50% 45%, transparent 55%, rgba(0,0,0,0.5) 100%)" }} />
    </AbsoluteFill>
  );
};

// ---------------------------------------------------------------- caption
const Caption: React.FC<{ text: string; hide?: boolean }> = ({ text, hide }) => {
  const f = useCurrentFrame();
  if (hide) return null;
  const p = sp(f, 3, 18);
  const parts = text.split(/(\d[\d,.\-–'’]*\d|\d)/g);
  return (
    <div style={{ position: "absolute", left: 0, right: 0, bottom: 78, display: "flex", justifyContent: "center", padding: "0 150px", opacity: Math.min(1, p * 1.4), transform: `translateY(${(1 - p) * 26}px)` }}>
      <div
        style={{
          fontFamily: COND, fontWeight: 800, fontSize: 60, lineHeight: 1.1, textAlign: "center", color: WHITE, maxWidth: 1600, letterSpacing: 0.5,
          textShadow: "0 4px 0 rgba(0,0,0,0.55), 0 0 26px rgba(0,0,0,0.9), 0 0 3px #000",
          WebkitTextStroke: "1.5px rgba(0,0,0,0.6)",
        }}
      >
        {parts.map((pt, k) => (/\d/.test(pt) ? <span key={k} style={{ color: GOLD }}>{pt}</span> : <React.Fragment key={k}>{pt}</React.Fragment>))}
      </div>
    </div>
  );
};

// ---------------------------------------------------------------- overlays
const DateTag: React.FC<{ o: Ov; len: number }> = ({ o, len }) => {
  const f = useCurrentFrame();
  const at = fr(o.at ?? 0.2);
  if (f < at) return null;
  const p = sp(f, at, 14);
  const outp = interpolate(f, [len - 8, len], [1, 0], clamp);
  return (
    <div style={{ position: "absolute", left: 70, top: 70, transform: `translateX(${(1 - p) * -520}px)`, opacity: outp }}>
      <div style={{ display: "inline-flex", alignItems: "center", background: GOLD, color: "#0b0b0b", fontFamily: COND, fontWeight: 800, fontStyle: "italic", fontSize: 50, padding: "6px 26px 6px 22px", boxShadow: "0 10px 40px rgba(0,0,0,0.55)" }}>
        <div style={{ width: 10, height: 44, background: "#0b0b0b", marginRight: 18 }} />
        {o.t}
      </div>
    </div>
  );
};

const ChipOv: React.FC<{ o: Ov; len: number }> = ({ o, len }) => {
  const f = useCurrentFrame();
  const at = fr(o.at ?? 0.4);
  if (f < at) return null;
  const p = sp(f, at, 12);
  const bg = o.c === "red" ? RONALDO : o.c === "white" ? "#f3f3f3" : GOLD;
  const fg = o.c === "red" ? "#fff" : "#0b0b0b";
  const outp = interpolate(f, [len - 8, len], [1, 0], clamp);
  const pos: React.CSSProperties = o.pos === "bl" ? { left: 70, top: 640 } : { left: 70, top: 160 };
  return (
    <div style={{ position: "absolute", ...pos, opacity: outp * Math.min(1, p * 1.5), transform: `scale(${0.7 + p * 0.3})`, transformOrigin: "0 50%" }}>
      <div style={{ background: bg, color: fg, fontFamily: COND, fontWeight: 800, fontStyle: "italic", fontSize: 40, padding: "6px 22px", letterSpacing: 1.5, boxShadow: `0 0 34px ${bg}77`, whiteSpace: "nowrap" }}>{o.t}</div>
    </div>
  );
};

const SlamOv: React.FC<{ o: Ov; len: number }> = ({ o, len }) => {
  const f = useCurrentFrame();
  const at = fr(o.at ?? 0.2);
  if (f < at) return null;
  const p = sp(f, at, 11);
  const outp = interpolate(f, [len - 8, len], [1, 0], clamp);
  const c = colorOf(o.c);
  const shake = f - at < 8 ? Math.sin((f - at) * 3) * 6 * (1 - (f - at) / 8) : 0;
  return (
    <div style={{ position: "absolute", left: 0, right: 0, top: `${(o.y ?? 0.5) * 100}%`, transform: `translateY(-50%) translateX(${shake}px)`, display: "flex", justifyContent: "center", opacity: outp }}>
      <div
        style={{
          fontFamily: COND, fontWeight: 800, fontStyle: "italic", fontSize: o.size ?? 170, lineHeight: 1, letterSpacing: -2, color: c, whiteSpace: "nowrap",
          transform: `scale(${interpolate(p, [0, 1], [2.1, 1])})`, filter: `blur(${(1 - p) * 12}px)`,
          textShadow: `0 10px 0 rgba(0,0,0,0.5), 0 0 60px ${c}66, 0 0 5px #000`, WebkitTextStroke: "2px rgba(0,0,0,0.55)",
        }}
      >
        {o.t}
      </div>
    </div>
  );
};

const StatOv: React.FC<{ o: Ov; len: number }> = ({ o, len }) => {
  const f = useCurrentFrame();
  const at = fr(o.at ?? 0.2);
  if (f < at) return null;
  const p = sp(f, at, 14);
  const outp = interpolate(f, [len - 8, len], [1, 0], clamp);
  const c = colorOf(o.c);
  return (
    <div style={{ position: "absolute", left: 0, right: 0, top: 150, display: "flex", flexDirection: "column", alignItems: "center", gap: 4, opacity: outp * Math.min(1, p * 1.6), transform: `scale(${0.85 + p * 0.15})` }}>
      <Counter value={o.v} from={at} dur={Math.min(30, Math.max(14, len - at - 14))} size={330} color={c} suffix={o.suf ?? ""} decimals={o.dec ?? 0} />
      <div style={{ fontFamily: COND, fontWeight: 800, fontStyle: "italic", fontSize: 76, color: WHITE, letterSpacing: 6, textShadow: "0 6px 0 rgba(0,0,0,0.5), 0 0 24px #000" }}>{o.l}</div>
      {o.sub ? (
        <div style={{ marginTop: 8, background: c, color: c === WHITE ? "#0b0b0b" : "#0b0b0b", fontFamily: COND, fontWeight: 800, fontStyle: "italic", fontSize: 40, padding: "4px 22px", letterSpacing: 2 }}>{o.sub}</div>
      ) : null}
    </div>
  );
};

const StatsOv: React.FC<{ o: Ov; len: number }> = ({ o, len }) => {
  const f = useCurrentFrame();
  const at = fr(o.at ?? 0.2);
  if (f < at) return null;
  const outp = interpolate(f, [len - 8, len], [1, 0], clamp);
  const n = o.items.length;
  return (
    <div style={{ position: "absolute", left: 0, right: 0, top: 170, display: "flex", justifyContent: "center", gap: 90, opacity: outp }}>
      {o.items.map((it: any, k: number) => {
        const a = at + k * 9;
        const p = sp(f, a, 13);
        return (
          <div key={k} style={{ display: "flex", flexDirection: "column", alignItems: "center", opacity: Math.min(1, p * 1.6), transform: `translateY(${(1 - p) * 40}px) scale(${0.85 + p * 0.15})` }}>
            {it.raw ? (
              <div style={{ fontFamily: COND, fontWeight: 800, fontStyle: "italic", fontSize: n > 2 ? 230 : 280, lineHeight: 1, color: GOLD, textShadow: `0 0 30px ${GOLD}88, 0 8px 0 rgba(0,0,0,0.5)` }}>{it.v}</div>
            ) : (
              <Counter value={it.v} from={a} dur={24} size={n > 2 ? 230 : 280} color={GOLD} suffix="" />
            )}
            <div style={{ fontFamily: COND, fontWeight: 800, fontStyle: "italic", fontSize: 54, color: WHITE, letterSpacing: 5, textShadow: "0 5px 0 rgba(0,0,0,0.5), 0 0 20px #000" }}>{it.l}</div>
          </div>
        );
      })}
    </div>
  );
};

const QuoteOv: React.FC<{ o: Ov; len: number }> = ({ o, len }) => {
  const f = useCurrentFrame();
  const at = fr(o.at ?? 0.2);
  if (f < at) return null;
  const p = sp(f, at, 15);
  const outp = interpolate(f, [len - 8, len], [1, 0], clamp);
  return (
    <div style={{ position: "absolute", left: 130, right: 130, top: 210, opacity: outp * Math.min(1, p * 1.5), transform: `translateY(${(1 - p) * 30}px)` }}>
      <div style={{ background: "linear-gradient(90deg, rgba(5,7,13,0.86) 0%, rgba(5,7,13,0.6) 100%)", borderLeft: `10px solid ${GOLD}`, padding: "30px 44px" }}>
        <div style={{ fontFamily: COND, fontWeight: 800, fontSize: 130, lineHeight: 0.6, color: GOLD, height: 60 }}>“</div>
        <div style={{ fontFamily: SANS, fontWeight: 700, fontStyle: "italic", fontSize: 58, lineHeight: 1.18, color: WHITE, textShadow: "0 4px 18px #000" }}>{o.t}</div>
        <div style={{ marginTop: 18, fontFamily: COND, fontWeight: 800, fontStyle: "italic", fontSize: 36, color: GOLD, letterSpacing: 4 }}>— {o.who}</div>
      </div>
    </div>
  );
};

const FlashOv: React.FC = () => {
  const f = useCurrentFrame();
  const o = interpolate(f, [0, 2, 9], [0, 0.85, 0], clamp);
  return <AbsoluteFill style={{ background: "#fff", opacity: o }} />;
};

const ConfettiOv: React.FC<{ o: Ov }> = ({ o }) => {
  const f = useCurrentFrame();
  const t = f - fr(o.at ?? 0.3);
  if (t < 0 || t > 80) return null;
  return (
    <AbsoluteFill>
      {Array.from({ length: 90 }).map((_, i) => {
        const ang = -Math.PI / 2 + (random(`cf${i}`) - 0.5) * 2.6;
        const v = 15 + random(`cv${i}`) * 22;
        const px = 960 + Math.cos(ang) * v * t;
        const py = 700 + Math.sin(ang) * v * t + 0.6 * t * t;
        const col = [GOLD, "#ffffff", "#ff3b4e", "#0b7a3b"][i % 4];
        return <div key={i} style={{ position: "absolute", left: px, top: py, width: 14, height: 24, background: col, transform: `rotate(${t * 14 + i * 40}deg)`, opacity: 1 - t / 80 }} />;
      })}
    </AbsoluteFill>
  );
};

// ---------------------------------------------------------------- chapter card
const ChapterCard: React.FC<{ s: Scene; len: number }> = ({ s, len }) => {
  const f = useCurrentFrame();
  const p = sp(f, 4, 13);
  const line = interpolate(f, [2, 22], [0, 1], { ...clamp, easing: out });
  const outp = interpolate(f, [len - 8, len], [1, 0], clamp);
  return (
    <AbsoluteFill style={{ opacity: outp }}>
      <AbsoluteFill style={{ background: "linear-gradient(90deg, rgba(5,7,13,0.94) 0%, rgba(5,7,13,0.72) 60%, rgba(5,7,13,0.5) 100%)" }} />
      <div style={{ position: "absolute", left: 120, top: 250 }}>
        <div style={{ fontFamily: COND, fontWeight: 800, fontStyle: "italic", fontSize: 44, color: GOLD, letterSpacing: 14, opacity: Math.min(1, p * 2) }}>CHAPTER</div>
        <div style={{ fontFamily: COND, fontWeight: 800, fontStyle: "italic", fontSize: 420, lineHeight: 0.85, color: "transparent", WebkitTextStroke: `5px ${GOLD}`, transform: `translateX(${(1 - p) * -300}px)`, opacity: Math.min(1, p * 1.6) }}>
          {String(s.ch).padStart(2, "0")}
        </div>
      </div>
      <div style={{ position: "absolute", left: 120, right: 100, top: 690 }}>
        <div style={{ height: 10, width: `${line * 760}px`, background: GOLD, marginBottom: 22 }} />
        <div style={{ fontFamily: COND, fontWeight: 800, fontStyle: "italic", fontSize: 150, lineHeight: 1, color: WHITE, textShadow: "0 10px 0 rgba(0,0,0,0.5), 0 0 40px rgba(0,0,0,0.8)", transform: `translateX(${(1 - p) * 220}px)`, opacity: Math.min(1, p * 1.6), whiteSpace: "nowrap" }}>
          {s.title}
        </div>
      </div>
    </AbsoluteFill>
  );
};

// ---------------------------------------------------------------- scene
const SceneView: React.FC<{ s: Scene; len: number }> = ({ s, len }) => {
  const isCh = !!s.ch;
  return (
    <AbsoluteFill>
      <Photo shot={s.shot} kb={s.kb || "in"} len={len} dim={isCh ? 0.5 : 0.16} />
      {isCh ? <ChapterCard s={s} len={len} /> : null}
      {!isCh && s.ov.map((o, k) => {
        if (o.k === "date") return <DateTag key={k} o={o} len={len} />;
        if (o.k === "chip") return <ChipOv key={k} o={o} len={len} />;
        if (o.k === "slam") return <SlamOv key={k} o={o} len={len} />;
        if (o.k === "stat") return <StatOv key={k} o={o} len={len} />;
        if (o.k === "stats") return <StatsOv key={k} o={o} len={len} />;
        if (o.k === "quote") return <QuoteOv key={k} o={o} len={len} />;
        if (o.k === "flash") return <FlashOv key={k} />;
        if (o.k === "confetti") return <ConfettiOv key={k} o={o} />;
        return null;
      })}
      {!isCh && <Caption text={s.text} hide={s.ov.some((o) => o.k === "quote")} />}
    </AbsoluteFill>
  );
};

// ---------------------------------------------------------------- HUD
const Hud: React.FC = () => {
  const f = useCurrentFrame();
  const p = Math.min(1, f / RETIRE_DURATION);
  return (
    <>
      <div style={{ position: "absolute", left: 0, bottom: 0, width: "100%", height: 10, background: "rgba(255,255,255,0.14)" }}>
        <div style={{ width: `${p * 100}%`, height: "100%", background: `linear-gradient(90deg, ${RONALDO}, ${GOLD})` }} />
        {CHAPTERS.map((c) => (
          <div key={c.n} style={{ position: "absolute", left: `${(fr(c.at) / RETIRE_DURATION) * 100}%`, top: -6, width: 4, height: 22, background: "#fff", opacity: 0.85 }} />
        ))}
      </div>
      <div style={{ position: "absolute", right: 60, top: 54, fontFamily: COND, fontWeight: 800, fontStyle: "italic", fontSize: 34, letterSpacing: 5, color: "rgba(255,255,255,0.8)", textShadow: "0 3px 12px #000" }}>
        CD <span style={{ color: GOLD }}>PHANTOM</span>
      </div>
    </>
  );
};

export const RonaldoRetire: React.FC = () => {
  return (
    <AbsoluteFill style={{ background: "#05070d" }}>
      <Audio src={staticFile("ronaldo_retire/mix.mp3")} />
      {SCENES.map((s, k) => {
        const from = fr(s.start);
        const nextFrom = k < SCENES.length - 1 ? fr(SCENES[k + 1].start) : RETIRE_DURATION;
        const len = Math.max(8, nextFrom - from);
        // let each scene run 8 frames under the next one so cuts cross-fade instead of flashing black
        const run = k < SCENES.length - 1 ? len + 8 : len;
        return (
          <Sequence key={s.i} from={from} durationInFrames={run}>
            <SceneView s={s} len={len} />
          </Sequence>
        );
      })}
      <Hud />
    </AbsoluteFill>
  );
};

// ---------------------------------------------------------------- thumbnail (1280x720 still)
export const RonaldoThumb: React.FC = () => {
  const shot = "ronaldo_closeup_c";
  const meta = (manifest as any)[shot] || { w: 1920, h: 1080 };
  return (
    <AbsoluteFill style={{ background: "#05070d" }}>
      <Img src={staticFile(`ronaldo_retire/${shot}.jpg`)} style={{ position: "absolute", right: 0, top: 0, height: "100%", width: "70%", objectFit: "cover", objectPosition: "42% 30%", filter: "contrast(1.18) saturate(1.2)" }} />
      <AbsoluteFill style={{ background: "linear-gradient(90deg, #05070d 28%, rgba(5,7,13,0.55) 55%, transparent 80%)" }} />
      <div style={{ position: "absolute", left: 40, top: 40, background: RONALDO, color: "#fff", fontFamily: COND, fontWeight: 800, fontStyle: "italic", fontSize: 54, padding: "4px 20px", letterSpacing: 4 }}>BREAKING</div>
      <div style={{ position: "absolute", left: 40, top: 150, fontFamily: COND, fontWeight: 800, fontStyle: "italic", fontSize: 190, lineHeight: 0.92, color: "#fff", textShadow: "0 10px 0 rgba(0,0,0,0.6)" }}>
        HE QUIT<br /><span style={{ color: GOLD }}>PORTUGAL</span>
      </div>
      <div style={{ position: "absolute", left: 40, bottom: 44, display: "flex", gap: 24 }}>
        <div style={{ background: GOLD, color: "#0b0b0b", fontFamily: COND, fontWeight: 800, fontStyle: "italic", fontSize: 58, padding: "2px 18px" }}>234 CAPS</div>
        <div style={{ background: "#fff", color: "#0b0b0b", fontFamily: COND, fontWeight: 800, fontStyle: "italic", fontSize: 58, padding: "2px 18px" }}>146 GOALS</div>
      </div>
    </AbsoluteFill>
  );
};
