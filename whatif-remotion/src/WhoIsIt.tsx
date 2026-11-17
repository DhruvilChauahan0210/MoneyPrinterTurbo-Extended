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

// R2 prototype: 'WHO IS IT?' blur-to-clear guess. One portrait, three clues (counter 1/3..3/3), each clue unblurs the
// photo, countdown number to the reveal, then the name and one verified fact line. Frame 0 is already complete.

export type WhoIsItProps = {
  headline: string; // "WHO IS IT?"
  photo: string; // file in public/ (fallback when no clips)
  clips?: string[]; // moving clips in public/: one per stage (clue1, clue2, clue3, reveal); preferred over the photo
  posX?: number;
  posY?: number;
  zoom?: number;
  shiftY?: number; // push the photo down (px) so the face clears the header
  clues: string[]; // 3 short clue lines shown on screen
  clueStarts: number[]; // seconds each clue starts (synced to the voice); clueStarts[0] should be 0
  revealAt: number; // seconds
  name: string; // "ERLING HAALAND"
  fact: string; // one verified fact line
  source: string;
  audioFile: string;
  durationInSeconds?: number;
};

const FONT_BIG = "Impact, 'Arial Narrow Bold', 'Arial Black', Arial, sans-serif";
const FONT = "'Arial Black', Arial, Helvetica, sans-serif";

// blur (px) and brightness after each stage: before clue2 .. etc. Index 0 = clue 1 state.
const BLUR = [42, 24, 11];
const BRIGHT = [0.62, 0.8, 0.92];

export const WhoIsIt: React.FC<WhoIsItProps> = (p) => {
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();
  const t = frame / fps;

  // active clue index
  let ci = 0;
  p.clueStarts.forEach((s, i) => {
    if (t >= s) ci = i;
  });
  const revealOn = t >= p.revealAt;

  // blur target by stage, eased over 0.9 s after each clue start / the reveal
  const stages = [...p.clueStarts, p.revealAt];
  const blurPts = [...BLUR, 0];
  const brightPts = [...BRIGHT, 1];
  let blur = blurPts[0];
  let bright = brightPts[0];
  for (let i = 1; i < stages.length; i++) {
    const k = interpolate(t, [stages[i], stages[i] + 0.9], [0, 1], {
      extrapolateLeft: "clamp",
      extrapolateRight: "clamp",
      easing: Easing.out(Easing.cubic),
    });
    blur = blur + (blurPts[i] - blur) * k;
    bright = bright + (brightPts[i] - bright) * k;
  }

  const remaining = Math.max(0, p.revealAt - t);
  const shown = Math.ceil(remaining);
  const ringFrac = remaining / p.revealAt;
  const pulse = remaining > 0 ? 1 + 0.1 * Math.max(0, 1 - ((t % 1) / 0.18)) : 1;
  const ringColor = remaining > 6 ? "#35e07a" : remaining > 3 ? "#ffd12b" : "#ff3b3b";
  const R = 76;
  const C = 2 * Math.PI * R;

  const zoomBase = (p.zoom ?? 1.1) * (1 + 0.05 * Math.min(1, t / 16));
  const pos = `${p.posX ?? 50}% ${p.posY ?? 25}%`;

  const clueSpring = (i: number) =>
    i === 0 ? 1 : spring({ frame: frame - Math.round(p.clueStarts[i] * fps), fps, config: { damping: 13, mass: 0.6 } });
  const revealSpring = spring({ frame: frame - Math.round(p.revealAt * fps), fps, config: { damping: 12, mass: 0.7 } });
  const revealT = t - p.revealAt;

  return (
    <AbsoluteFill style={{ background: "#05070f" }}>
      {/* moving clips (one per stage) or the photo, full-bleed, blurred / dark until the reveal */}
      <AbsoluteFill style={{ overflow: "hidden" }}>
        {p.clips && p.clips.length ? (
          stages.map((st, i) => {
            const from = Math.round(st * fps);
            const end = i + 1 < stages.length ? Math.round(stages[i + 1] * fps) : durationInFrames;
            const src = p.clips![Math.min(i, p.clips!.length - 1)];
            return (
              <Sequence key={i} from={from} durationInFrames={Math.max(1, end - from)}>
                <AbsoluteFill>
                  <OffthreadVideo
                    src={staticFile(src)}
                    muted
                    style={{
                      width: "100%",
                      height: "100%",
                      objectFit: "cover",
                      transform: `translateY(${p.shiftY ?? 0}px) scale(${blur > 1 ? 1.12 : 1.02})`,
                      filter: `blur(${blur}px) brightness(${bright}) ${blur > 12 ? "grayscale(0.6)" : ""}`,
                    }}
                  />
                </AbsoluteFill>
              </Sequence>
            );
          })
        ) : (
        <Img
          src={staticFile(p.photo)}
          style={{
            width: "100%",
            height: "100%",
            objectFit: "cover",
            objectPosition: pos,
            transform: `translateY(${p.shiftY ?? 0}px) scale(${zoomBase * (blur > 1 ? 1.12 : 1)})`,
            transformOrigin: pos,
            filter: `blur(${blur}px) brightness(${bright}) ${blur > 12 ? "grayscale(0.6)" : ""}`,
          }}
        />
        )}
        <AbsoluteFill style={{ background: "linear-gradient(to bottom, rgba(0,0,0,0.65) 0%, rgba(0,0,0,0) 26%, rgba(0,0,0,0) 48%, rgba(0,0,0,0.88) 74%)" }} />
      </AbsoluteFill>

      {/* header: WHO IS IT? + timer ring */}
      <div style={{ position: "absolute", top: 100, left: 0, right: 0, display: "flex", justifyContent: "center", alignItems: "center", gap: 28 }}>
        <div style={{ fontFamily: FONT_BIG, fontSize: 160, lineHeight: 1, color: "#fff", textShadow: "0 6px 24px rgba(0,0,0,0.9)" }}>
          {revealOn ? "IT'S" : p.headline}
        </div>
        {!revealOn ? (
          <div style={{ position: "relative", width: 2 * R + 20, height: 2 * R + 20, transform: `scale(${pulse})` }}>
            <svg width={2 * R + 20} height={2 * R + 20} style={{ position: "absolute", left: 0, top: 0 }}>
              <circle cx={R + 10} cy={R + 10} r={R} fill="rgba(0,0,0,0.55)" stroke="rgba(255,255,255,0.2)" strokeWidth={14} />
              <circle
                cx={R + 10}
                cy={R + 10}
                r={R}
                fill="none"
                stroke={ringColor}
                strokeWidth={14}
                strokeLinecap="round"
                strokeDasharray={C}
                strokeDashoffset={C * (1 - ringFrac)}
                transform={`rotate(-90 ${R + 10} ${R + 10})`}
              />
            </svg>
            <div style={{ position: "absolute", inset: 0, display: "flex", alignItems: "center", justifyContent: "center", fontFamily: FONT_BIG, fontSize: 104, color: ringColor }}>
              {shown}
            </div>
          </div>
        ) : null}
      </div>

      {/* clue counter pill */}
      {!revealOn ? (
        <div style={{ position: "absolute", top: 800, left: 0, right: 0, display: "flex", justifyContent: "center" }}>
          <div style={{ fontFamily: FONT, fontSize: 56, color: "#0a0d1a", background: "#ffd12b", padding: "10px 40px", borderRadius: 40, letterSpacing: 3 }}>
            CLUE {ci + 1}/{p.clues.length}
          </div>
        </div>
      ) : null}

      {/* clue stack */}
      {!revealOn ? (
        <div style={{ position: "absolute", left: 40, right: 40, top: 1080, display: "flex", flexDirection: "column", gap: 18 }}>
          {p.clues.map((c, i) => {
            const on = i <= ci;
            const cur = i === ci;
            const sp = clueSpring(i);
            return (
              <div
                key={i}
                style={{
                  minHeight: 128,
                  borderRadius: 24,
                  padding: "14px 30px",
                  display: "flex",
                  alignItems: "center",
                  gap: 24,
                  background: cur ? "rgba(255,209,43,0.96)" : on ? "rgba(20,24,44,0.88)" : "rgba(20,24,44,0.55)",
                  border: cur ? "none" : "3px solid rgba(255,255,255,0.18)",
                  transform: cur ? `scale(${interpolate(sp, [0, 1], [0.92, 1])})` : "scale(1)",
                }}
              >
                <div style={{ fontFamily: FONT_BIG, fontSize: 80, color: cur ? "#0a0d1a" : on ? "#ffd12b" : "rgba(255,255,255,0.3)", minWidth: 60 }}>{i + 1}</div>
                <div style={{ fontFamily: FONT, fontSize: 44, lineHeight: 1.12, color: cur ? "#0a0d1a" : on ? "#fff" : "rgba(255,255,255,0.3)" }}>
                  {on ? c : "???"}
                </div>
              </div>
            );
          })}
        </div>
      ) : null}

      {/* reveal: name + fact */}
      {revealOn ? (
        <div style={{ position: "absolute", left: 30, right: 30, top: 1060, textAlign: "center" }}>
          <div
            style={{
              fontFamily: FONT_BIG,
              fontSize: 150,
              lineHeight: 1,
              color: "#ffd12b",
              transform: `scale(${interpolate(revealSpring, [0, 1], [0.6, 1])})`,
              textShadow: "0 6px 24px rgba(0,0,0,0.9)",
            }}
          >
            {p.name}
          </div>
          <div
            style={{
              marginTop: 34,
              fontFamily: FONT,
              fontSize: 48,
              lineHeight: 1.2,
              color: "#fff",
              background: "rgba(8,10,22,0.85)",
              borderRadius: 24,
              padding: "26px 34px",
              opacity: interpolate(revealT, [0.5, 0.8], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" }),
            }}
          >
            {p.fact}
          </div>
          <div style={{ marginTop: 28, fontFamily: FONT_BIG, fontSize: 70, color: "#fff", opacity: interpolate(revealT, [1.6, 1.9], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" }) }}>
            DID YOU GET IT?
          </div>
        </div>
      ) : null}

      <div style={{ position: "absolute", left: 0, right: 0, top: 1664, textAlign: "center", fontFamily: "Arial, sans-serif", fontSize: 24, color: "rgba(255,255,255,0.5)" }}>
        {p.source}
      </div>

      <Audio src={staticFile(p.audioFile)} volume={1} />
    </AbsoluteFill>
  );
};
