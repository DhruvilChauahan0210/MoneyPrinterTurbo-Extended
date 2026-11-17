import React from "react";
import { AbsoluteFill, Audio, Easing, Img, Sequence, interpolate, random, staticFile, useCurrentFrame } from "remotion";
import { Captions, Finale, GodRays, GoldDust, Grain, Header, Petals } from "./Ganpati";

const clamp = { extrapolateLeft: "clamp", extrapolateRight: "clamp" } as const;
const smooth = Easing.inOut(Easing.quad);

const GROUND = 1480;
const MOUSE_H = 640;
const MOUSE_W = Math.round((MOUSE_H * 1211) / 1598);
const GAN_H = 600;
const GAN_W = Math.round((GAN_H * 1177) / 1563);

// Story beats (frames @30fps), aligned to the voice timeline.
const CATCH = 186;
const THROW = 166;
const FORGIVE = 296;
const JUMP_START = 308;
const JUMP_LAND = 332;
const FINALE = 388;
const DHOL_HITS = [12.9, 13.5, 13.65, 14.1, 14.55, 14.7].map((s) => Math.round(s * 30));

/* ---------- motion functions (pure, so every layer agrees) ---------- */

const mouseX = (f: number) =>
  interpolate(f, [10, 100, 131, 160, 232, 252, 336, 384], [1250, 640, 640, 800, 800, 720, 720, 540], { ...clamp, easing: smooth });

const hopAmp = (f: number) => {
  if (f < CATCH) return f < 100 ? 1 : 0.6;
  if (f < 336) return 0;
  if (f < FINALE) return 0.45;
  return 0.2;
};
const hopPhase = (f: number) => Math.abs(Math.sin(f * 0.32));
const mouseHop = (f: number) => -hopPhase(f) * 85 * hopAmp(f);

const ganX = (f: number) => {
  if (f >= JUMP_LAND) return mouseX(f);
  if (f >= JUMP_START) return interpolate(f, [JUMP_START, JUMP_LAND], [240, mouseX(JUMP_LAND)], { ...clamp, easing: smooth });
  return interpolate(f, [131, 154], [-320, 240], { ...clamp, easing: Easing.out(Easing.cubic) });
};
const ganScale = (f: number) => interpolate(f, [JUMP_START, JUMP_LAND], [1, 0.7], { ...clamp, easing: smooth });
const RIDE_BASE = -MOUSE_H * 0.83;
const ganY = (f: number) => {
  if (f < 154) return -Math.abs(Math.sin(f * 0.45)) * 70 * interpolate(f, [131, 154], [1, 0], clamp);
  if (f < JUMP_START) return 0;
  if (f < JUMP_LAND) {
    const p = (f - JUMP_START) / (JUMP_LAND - JUMP_START);
    return RIDE_BASE * smooth(p) - 360 * 4 * p * (1 - p);
  }
  return RIDE_BASE + mouseHop(f) * 0.9;
};

const potHit = (potX: number) => {
  for (let f = 10; f < 131; f++) if (mouseX(f) - MOUSE_W * 0.32 <= potX + 30) return f;
  return 9999;
};
const POTS = [
  { x: 1000, s: 1.0 },
  { x: 840, s: 0.8 },
  { x: 470, s: 1.15 },
].map((p) => ({ ...p, hit: potHit(p.x) }));

const shakeAt = (f: number, at: number, amp: number, decay = 5) =>
  f >= at ? amp * Math.exp(-(f - at) / decay) : 0;
const cameraShake = (f: number) => {
  const a =
    POTS.reduce((acc, p) => acc + shakeAt(f, p.hit, 18), 0) +
    shakeAt(f, CATCH, 12) +
    shakeAt(f, 154, 6) +
    shakeAt(f, JUMP_LAND, 10) +
    DHOL_HITS.reduce((acc, h) => acc + shakeAt(f, h, 5, 3), 0);
  return { x: Math.sin(f * 3.1) * a, y: Math.cos(f * 2.7) * a };
};

/* ---------- props ---------- */

const Matka: React.FC<{ size: number }> = ({ size }) => (
  <svg width={size} height={size * 1.1} viewBox="0 0 100 110">
    <defs>
      <radialGradient id="clay" cx="38%" cy="38%" r="70%">
        <stop offset="0%" stopColor="#e3874a" />
        <stop offset="55%" stopColor="#b2531f" />
        <stop offset="100%" stopColor="#5e2509" />
      </radialGradient>
    </defs>
    <ellipse cx="50" cy="68" rx="44" ry="40" fill="url(#clay)" />
    <rect x="33" y="14" width="34" height="18" rx="4" fill="#a0461a" />
    <ellipse cx="50" cy="14" rx="22" ry="7" fill="#c86a33" stroke="#5e2509" strokeWidth="2" />
    <path d="M10 62 Q50 74 90 62" stroke="#f5deb3" strokeWidth="3" fill="none" opacity="0.85" />
    <path d="M14 74 Q50 86 86 74" stroke="#f5deb3" strokeWidth="2" fill="none" opacity="0.6" strokeDasharray="4 5" />
  </svg>
);

const Pot: React.FC<{ x: number; s: number; hit: number }> = ({ x, s, hit }) => {
  const f = useCurrentFrame();
  const size = 150 * s;
  const t = Math.max(0, f - hit);
  const flying = f >= hit;
  const px = flying ? x - 17 * t : x;
  const py = flying ? -32 * t + 1.7 * t * t : 0;
  const rot = flying ? -15 * t : 0;
  const op = flying ? interpolate(t, [16, 26], [1, 0], clamp) : 1;
  if (op <= 0) return null;
  return (
    <div style={{ position: "absolute", left: px - size / 2, top: GROUND - size * 1.1 + py + 8, transform: `rotate(${rot}deg)`, opacity: op }}>
      <Matka size={size} />
    </div>
  );
};

const Dust: React.FC<{ x: number; y: number; at: number; color?: string }> = ({ x, y, at, color = "rgba(214,190,150," }) => {
  const f = useCurrentFrame();
  const t = f - at;
  if (t < 0 || t > 30) return null;
  return (
    <>
      {Array.from({ length: 9 }).map((_, i) => {
        const ang = (i / 9) * Math.PI - Math.PI + (random(`da${at}${i}`) - 0.5) * 0.6;
        const dist = t * (5 + random(`dd${at}${i}`) * 6);
        const r = 30 + t * 3.5;
        return (
          <div
            key={i}
            style={{
              position: "absolute",
              left: x + Math.cos(ang) * dist - r / 2,
              top: y + Math.sin(ang) * dist * 0.6 - r / 2,
              width: r,
              height: r,
              borderRadius: "50%",
              background: `radial-gradient(circle, ${color}0.75) 0%, ${color}0) 70%)`,
              opacity: 1 - t / 30,
            }}
          />
        );
      })}
    </>
  );
};

const Sparkles: React.FC<{ x: number; y: number; at: number; n?: number; spread?: number }> = ({ x, y, at, n = 26, spread = 14 }) => {
  const f = useCurrentFrame();
  const t = f - at;
  if (t < 0 || t > 32) return null;
  return (
    <>
      {Array.from({ length: n }).map((_, i) => {
        const ang = random(`sa${at}${i}`) * Math.PI * 2;
        const v = spread * (0.4 + random(`sv${at}${i}`));
        const s = 8 + random(`ss${at}${i}`) * 14;
        const px = x + Math.cos(ang) * v * t;
        const py = y + Math.sin(ang) * v * t + 0.25 * t * t;
        return (
          <div
            key={i}
            style={{
              position: "absolute",
              left: px - s / 2,
              top: py - s / 2,
              width: s,
              height: s,
              background: "radial-gradient(circle, #fffbe6 0%, #ffd34d 40%, rgba(255,170,40,0) 70%)",
              clipPath: "polygon(50% 0%, 60% 40%, 100% 50%, 60% 60%, 50% 100%, 40% 60%, 0% 50%, 40% 40%)",
              opacity: 1 - t / 32,
              transform: `rotate(${t * 12}deg)`,
            }}
          />
        );
      })}
    </>
  );
};

const Shadow: React.FC<{ x: number; w: number; lift: number }> = ({ x, w, lift }) => {
  const k = Math.max(0.35, 1 - lift / 400);
  return (
    <div
      style={{
        position: "absolute",
        left: x - (w * k) / 2,
        top: GROUND - 22,
        width: w * k,
        height: 44 * k,
        borderRadius: "50%",
        background: "radial-gradient(ellipse, rgba(30,15,0,0.55) 0%, rgba(30,15,0,0) 70%)",
      }}
    />
  );
};

/* ---------- characters ---------- */

const Mouse: React.FC = () => {
  const f = useCurrentFrame();
  const x = mouseX(f);
  const amp = hopAmp(f);
  const lift = mouseHop(f);
  const landing = (1 - hopPhase(f)) ** 6 * amp;
  const caughtShake = f >= CATCH && f < CATCH + 22 ? Math.sin(f * 2.3) * 12 * (1 - (f - CATCH) / 22) : 0;
  const bow = interpolate(f, [234, 248, 260, 272, 286, 300], [0, 24, 8, 26, 10, 0], { ...clamp, easing: smooth });
  const landSquash = f >= JUMP_LAND ? 0.12 * Math.exp(-(f - JUMP_LAND) / 5) : 0;
  const sy = 1 - 0.09 * landing - landSquash;
  const sx = 1 + 0.07 * landing + landSquash * 0.6;
  const tilt = Math.sin(f * 0.16) * 6 * amp + bow;
  const pulse = DHOL_HITS.reduce((a, h) => a + (f >= h ? 0.035 * Math.exp(-(f - h) / 4) : 0), 0);
  return (
    <>
      <Shadow x={x} w={MOUSE_W * 0.8} lift={-lift} />
      <Img
        src={staticFile("char_mouse.png")}
        style={{
          position: "absolute",
          left: x - MOUSE_W / 2 + caughtShake,
          top: GROUND - MOUSE_H + lift + 6,
          width: MOUSE_W,
          height: MOUSE_H,
          transformOrigin: "50% 100%",
          transform: `rotate(${tilt}deg) scale(${sx * (1 + pulse)}, ${sy * (1 + pulse)})`,
          filter: "drop-shadow(0 18px 24px rgba(0,0,0,0.35))",
        }}
      />
    </>
  );
};

const Ganesha: React.FC = () => {
  const f = useCurrentFrame();
  if (f < 128) return null;
  const x = ganX(f);
  const y = ganY(f);
  const s = ganScale(f);
  const throwRot = interpolate(f, [THROW - 8, THROW, THROW + 6, THROW + 20], [0, -13, 11, 0], { ...clamp, easing: smooth });
  const jumpRot = interpolate(f, [JUMP_START, JUMP_START + 12, JUMP_LAND], [0, -12, 0], clamp);
  const breathe = 1 + Math.sin(f / 9) * 0.012;
  const bless = f > 236 && f < FORGIVE + 8 ? 1 + 0.03 * Math.sin((f - 236) / 6) : 1;
  const pulse = DHOL_HITS.reduce((a, h) => a + (f >= h ? 0.04 * Math.exp(-(f - h) / 4) : 0), 0);
  const halo = interpolate(f, [236, 258], [0, 1], clamp);
  const w = GAN_W * s;
  const h = GAN_H * s;
  return (
    <>
      {f < JUMP_START + 4 && <Shadow x={x} w={GAN_W * 0.7} lift={-y} />}
      <div
        style={{
          position: "absolute",
          left: x - w * 0.9,
          top: GROUND + y - h * 1.25,
          width: w * 1.8,
          height: w * 1.8,
          borderRadius: "50%",
          background: "radial-gradient(circle, rgba(255,226,140,0.85) 0%, rgba(255,180,60,0.35) 35%, rgba(255,160,40,0) 68%)",
          opacity: halo * (0.85 + 0.15 * Math.sin(f / 7)),
          mixBlendMode: "screen",
        }}
      />
      <Img
        src={staticFile("char_ganesha.png")}
        style={{
          position: "absolute",
          left: x - w / 2,
          top: GROUND - h + y + 4,
          width: w,
          height: h,
          transformOrigin: "50% 100%",
          transform: `rotate(${throwRot + jumpRot}deg) scale(${breathe * bless * (1 + pulse)})`,
          filter: "drop-shadow(0 18px 24px rgba(0,0,0,0.35))",
        }}
      />
    </>
  );
};

const Noose: React.FC = () => {
  const f = useCurrentFrame();
  if (f < THROW + 4 || f > FORGIVE + 14) return null;
  const draw = interpolate(f, [THROW + 4, CATCH], [0, 1], { ...clamp, easing: Easing.out(Easing.quad) });
  const loopIn = interpolate(f, [CATCH - 3, CATCH + 8], [0, 1], clamp);
  const rx = interpolate(f, [CATCH - 3, CATCH + 14], [MOUSE_W * 0.75, MOUSE_W * 0.4], { ...clamp, easing: Easing.out(Easing.back(2)) });
  const ry = rx * 0.24;
  const fade = interpolate(f, [FORGIVE, FORGIVE + 12], [1, 0], clamp);
  const gx = ganX(f) - GAN_W / 2 + GAN_W * 0.86;
  const gy = GROUND - GAN_H + GAN_H * 0.56 + ganY(f);
  const mx = mouseX(f);
  const my = GROUND - MOUSE_H * 0.28;
  const ex = mx - rx;
  const cx = (gx + ex) / 2;
  const cy = Math.min(gy, my) - 280;
  const glow = "drop-shadow(0 0 10px rgba(255,200,60,0.95)) drop-shadow(0 0 22px rgba(255,160,30,0.6))";
  return (
    <svg width={1080} height={1920} style={{ position: "absolute", left: 0, top: 0, overflow: "visible", opacity: fade, filter: glow }}>
      <defs>
        <linearGradient id="rope" x1="0" y1="0" x2="1" y2="0">
          <stop offset="0%" stopColor="#fff2b0" />
          <stop offset="50%" stopColor="#ffc93a" />
          <stop offset="100%" stopColor="#e09a1a" />
        </linearGradient>
      </defs>
      <path d={`M ${gx} ${gy} Q ${cx} ${cy} ${ex} ${my}`} stroke="url(#rope)" strokeWidth={10} strokeLinecap="round" fill="none" pathLength={1} strokeDasharray={1} strokeDashoffset={1 - draw} />
      {loopIn > 0 && (
        <ellipse cx={mx} cy={my} rx={rx} ry={ry} stroke="url(#rope)" strokeWidth={11} fill="none" pathLength={1} strokeDasharray={1} strokeDashoffset={1 - loopIn} />
      )}
    </svg>
  );
};

/* ---------- world + camera ---------- */

const World: React.FC = () => {
  const f = useCurrentFrame();
  const keys = [0, 125, 148, 178, 200, 228, 250, 300, 336, 384, 420];
  const z = interpolate(f, keys, [1.24, 1.24, 1.0, 1.0, 1.1, 1.1, 1.05, 1.0, 1.0, 1.0, 1.12], { ...clamp, easing: smooth });
  const cx = interpolate(f, keys, [700, 640, 540, 540, 720, 720, 520, 540, 600, 540, 540], { ...clamp, easing: smooth });
  const cy = interpolate(f, keys, [1130, 1130, 960, 960, 1080, 1080, 1060, 960, 980, 1000, 1040], { ...clamp, easing: smooth });
  const shake = cameraShake(f);
  const travel = interpolate(f, [336, 450], [0, -260], clamp);
  return (
    <AbsoluteFill style={{ overflow: "hidden" }}>
      <div
        style={{
          position: "absolute",
          left: 0,
          top: 0,
          width: 1080,
          height: 1920,
          transformOrigin: "0 0",
          transform: `translate(${540 + shake.x}px, ${960 + shake.y}px) scale(${z}) translate(${-cx}px, ${-cy}px)`,
        }}
      >
        <Img
          src={staticFile("bg_ashram.jpg")}
          style={{
            position: "absolute",
            left: -1300 + travel - (cx - 540) * 0.25,
            top: -430,
            height: 2320,
            width: Math.round((2320 * 1280) / 720),
            objectFit: "cover",
            filter: "blur(2.5px) saturate(1.15) brightness(0.92)",
          }}
        />
        <div style={{ position: "absolute", left: -600, top: GROUND - 40, width: 2400, height: 900, background: "linear-gradient(180deg, rgba(120,80,30,0) 0%, rgba(70,40,10,0.35) 100%)" }} />
        {POTS.map((p, i) => (
          <Pot key={i} {...p} />
        ))}
        {POTS.map((p, i) => (
          <Dust key={`d${i}`} x={p.x} y={GROUND - 40} at={p.hit} />
        ))}
        <Mouse />
        <Noose />
        <Ganesha />
        <Dust x={240} y={GROUND - 10} at={154} />
        <Sparkles x={mouseX(CATCH)} y={GROUND - MOUSE_H * 0.28} at={CATCH} />
        <Sparkles x={mouseX(FORGIVE)} y={GROUND - MOUSE_H * 0.28} at={FORGIVE} n={40} spread={18} />
        <Sparkles x={mouseX(JUMP_LAND)} y={GROUND - MOUSE_H * 0.8} at={JUMP_LAND} n={22} />
        <Sparkles x={mouseX(FINALE)} y={GROUND - MOUSE_H * 0.9} at={FINALE} n={44} spread={20} />
      </div>
    </AbsoluteFill>
  );
};

/* ---------- composition ---------- */

const thudFrames = Array.from({ length: 30 }, (_, k) => Math.round((k * Math.PI) / 0.32)).filter((fr) => fr >= 12 && fr < 128);

export const GanpatiAnim: React.FC = () => {
  const f = useCurrentFrame();
  const fromBlack = interpolate(f, [0, 12], [1, 0], clamp);
  const headerOut = interpolate(f, [372, 386], [1, 0], clamp);
  return (
    <AbsoluteFill style={{ backgroundColor: "black" }}>
      <World />
      <AbsoluteFill style={{ background: "radial-gradient(ellipse at 50% 30%, rgba(255,190,90,0.18) 0%, transparent 60%)", mixBlendMode: "screen" }} />
      <GodRays />
      <GoldDust />
      <AbsoluteFill style={{ background: "linear-gradient(180deg, rgba(0,0,0,0.55) 0%, rgba(0,0,0,0) 18%, rgba(0,0,0,0) 70%, rgba(0,0,0,0.8) 100%)" }} />
      <AbsoluteFill style={{ opacity: headerOut }}>
        <Header />
      </AbsoluteFill>
      <Captions />
      <Finale />
      <Petals />
      <AbsoluteFill style={{ background: "radial-gradient(ellipse at center, transparent 58%, rgba(0,0,0,0.55) 100%)" }} />
      <Grain />
      <AbsoluteFill style={{ backgroundColor: "black", opacity: fromBlack }} />

      <Audio src={staticFile("ganpati_voice_hi.wav")} volume={1} />
      <Audio src={staticFile("ganpati_music.wav")} volume={(fr) => interpolate(fr, [0, 380, 390], [0.32, 0.32, 0.62], clamp)} />
      {thudFrames.map((fr) => (
        <Sequence key={`t${fr}`} from={fr}>
          <Audio src={staticFile("sfx_thud.wav")} volume={0.35} />
        </Sequence>
      ))}
      {POTS.map((p, i) => (
        <Sequence key={`c${i}`} from={p.hit}>
          <Audio src={staticFile("sfx_crash.wav")} volume={0.5} />
        </Sequence>
      ))}
      <Sequence from={154}>
        <Audio src={staticFile("sfx_thud.wav")} volume={0.45} />
      </Sequence>
      <Sequence from={THROW}>
        <Audio src={staticFile("sfx_swish.wav")} volume={0.55} />
      </Sequence>
      {[CATCH, FORGIVE, JUMP_LAND, FINALE].map((fr) => (
        <Sequence key={`s${fr}`} from={fr}>
          <Audio src={staticFile("sfx_sparkle.wav")} volume={0.35} />
        </Sequence>
      ))}
      <Sequence from={JUMP_LAND}>
        <Audio src={staticFile("sfx_thud.wav")} volume={0.45} />
      </Sequence>
    </AbsoluteFill>
  );
};
