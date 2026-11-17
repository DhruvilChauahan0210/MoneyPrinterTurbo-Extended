import React, { useEffect, useMemo } from "react";
import {
  AbsoluteFill,
  Audio,
  Easing,
  Sequence,
  interpolate,
  random,
  spring,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { ThreeCanvas } from "@remotion/three";
import { useThree } from "@react-three/fiber";
import * as THREE from "three";
import { RoomEnvironment } from "three/examples/jsm/environments/RoomEnvironment.js";

const SANS = "'Avenir Next', 'Helvetica Neue', sans-serif";
const MONO = "Menlo, monospace";
const VIOLET = "#8b5cf6";
const CYAN = "#22d3ee";
const PINK = "#ec4899";
const clamp = { extrapolateLeft: "clamp", extrapolateRight: "clamp" } as const;
const easeInOut = Easing.bezier(0.7, 0, 0.3, 1);
const easeOut = Easing.bezier(0.16, 1, 0.3, 1);

/* ---------- 3D ---------- */

const Environment: React.FC = () => {
  const { gl, scene } = useThree();
  // Must be set synchronously: an effect runs after Remotion has already captured the first frame.
  const env = useMemo(() => {
    const pmrem = new THREE.PMREMGenerator(gl);
    const texture = pmrem.fromScene(new RoomEnvironment(), 0.04).texture;
    pmrem.dispose();
    return texture;
  }, [gl]);
  scene.environment = env;
  scene.environmentIntensity = 0.55;
  gl.toneMapping = THREE.ACESFilmicToneMapping;
  gl.toneMappingExposure = 1.15;
  useEffect(() => () => env.dispose(), [env]);
  return null;
};

const CameraRig: React.FC<{ z: number; y?: number }> = ({ z, y = 0 }) => {
  const { camera } = useThree();
  camera.position.set(0, y, z);
  camera.lookAt(0, 0, 0);
  return null;
};

const Particles: React.FC<{ drift: number }> = ({ drift }) => {
  const positions = useMemo(() => {
    const arr = new Float32Array(900 * 3);
    for (let i = 0; i < 900; i++) {
      arr[i * 3] = (random(`x${i}`) - 0.5) * 22;
      arr[i * 3 + 1] = (random(`y${i}`) - 0.5) * 14;
      arr[i * 3 + 2] = (random(`z${i}`) - 0.5) * 16;
    }
    return arr;
  }, []);
  return (
    <points position={[0, 0, drift]}>
      <bufferGeometry>
        <bufferAttribute attach="attributes-position" args={[positions, 3]} />
      </bufferGeometry>
      <pointsMaterial size={0.035} color="#c4b5fd" transparent opacity={0.75} sizeAttenuation />
    </points>
  );
};

const Hero3D: React.FC<{ cameraZ: number; spin: number; scale: number; drift: number }> = ({
  cameraZ,
  spin,
  scale,
  drift,
}) => {
  const { width, height } = useVideoConfig();
  return (
    <ThreeCanvas width={width} height={height} camera={{ fov: 35, position: [0, 0, cameraZ] }}>
      <Environment />
      <CameraRig z={cameraZ} />
      <pointLight position={[5, 3, 4]} intensity={60} color={VIOLET} />
      <pointLight position={[-5, -2, 3]} intensity={50} color={CYAN} />
      <pointLight position={[0, 5, -4]} intensity={40} color={PINK} />
      <mesh rotation={[spin * 0.6, spin, spin * 0.3]} scale={scale} position={[0, 0.55, 0]}>
        <torusKnotGeometry args={[1.15, 0.36, 320, 56, 2, 3]} />
        <meshPhysicalMaterial
          color="#ffffff"
          metalness={1}
          roughness={0.08}
          clearcoat={1}
          clearcoatRoughness={0.05}
          iridescence={1}
          iridescenceIOR={1.7}
          iridescenceThicknessRange={[250, 1300]}
        />
      </mesh>
      <Particles drift={drift} />
    </ThreeCanvas>
  );
};

/* ---------- shared visual layers ---------- */

const AmbientGlow: React.FC = () => {
  const frame = useCurrentFrame();
  const blob = (color: string, x: number, y: number, size: number, phase: number) => (
    <div
      style={{
        position: "absolute",
        left: x + Math.sin(frame / 40 + phase) * 160,
        top: y + Math.cos(frame / 50 + phase) * 120,
        width: size,
        height: size,
        borderRadius: "50%",
        background: `radial-gradient(circle, ${color} 0%, transparent 65%)`,
        opacity: 0.45,
      }}
    />
  );
  return (
    <AbsoluteFill style={{ backgroundColor: "#04040a", overflow: "hidden" }}>
      {blob(VIOLET, -200, -300, 1300, 0)}
      {blob(CYAN, 1100, 400, 1200, 2)}
      {blob(PINK, 500, 700, 1000, 4)}
    </AbsoluteFill>
  );
};

const Grain: React.FC = () => {
  const frame = useCurrentFrame();
  return (
    <AbsoluteFill style={{ mixBlendMode: "overlay", opacity: 0.22, pointerEvents: "none" }}>
      <svg width="100%" height="100%">
        <filter id="grain">
          <feTurbulence type="fractalNoise" baseFrequency="0.9" numOctaves="2" seed={frame % 12} />
          <feColorMatrix type="saturate" values="0" />
        </filter>
        <rect width="100%" height="100%" filter="url(#grain)" />
      </svg>
    </AbsoluteFill>
  );
};

const Vignette: React.FC = () => (
  <AbsoluteFill
    style={{ background: "radial-gradient(ellipse at center, transparent 50%, rgba(0,0,0,0.75) 100%)" }}
  />
);

const Label: React.FC<{ text: string; delay?: number }> = ({ text, delay = 0 }) => {
  const frame = useCurrentFrame();
  const o = interpolate(frame, [delay, delay + 15], [0, 1], clamp);
  const x = interpolate(frame, [delay, delay + 20], [-20, 0], { ...clamp, easing: easeOut });
  return (
    <div
      style={{
        position: "absolute",
        top: 80,
        left: 100,
        fontFamily: MONO,
        fontSize: 20,
        letterSpacing: 6,
        color: "rgba(255,255,255,0.7)",
        opacity: o,
        transform: `translateX(${x}px)`,
        display: "flex",
        alignItems: "center",
        gap: 18,
      }}
    >
      <span style={{ width: 40, height: 1, background: "rgba(255,255,255,0.6)" }} />
      {text}
    </div>
  );
};

const SplitReveal: React.FC<{ text: string; start: number; size: number; stagger?: number }> = ({
  text,
  start,
  size,
  stagger = 2,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  return (
    <div style={{ display: "flex", overflow: "hidden", padding: "0.1em 0" }}>
      {text.split("").map((ch, i) => {
        const p = spring({ frame: frame - start - i * stagger, fps, config: { damping: 200 }, durationInFrames: 22 });
        return (
          <span
            key={i}
            style={{
              display: "inline-block",
              fontFamily: SANS,
              fontWeight: 800,
              fontSize: size,
              color: "white",
              letterSpacing: -2,
              whiteSpace: "pre",
              transform: `translateY(${(1 - p) * 110}%)`,
              opacity: p,
              filter: `blur(${(1 - p) * 10}px)`,
            }}
          >
            {ch}
          </span>
        );
      })}
    </div>
  );
};

/* ---------- Scene 1: 3D hero ---------- */

const SceneHero: React.FC = () => {
  const frame = useCurrentFrame();
  const cameraZ = interpolate(frame, [0, 90], [14, 9.8], { ...clamp, easing: easeOut });
  const spin = frame * 0.025;
  const objScale = spring({ frame, fps: 30, config: { damping: 18, mass: 1.2 } });
  const exit = interpolate(frame, [76, 92], [0, 1], { ...clamp, easing: Easing.in(Easing.cubic) });

  return (
    <AbsoluteFill
      style={{ transform: `scale(${1 + exit * 0.35})`, filter: `blur(${exit * 24}px)`, opacity: 1 - exit }}
    >
      <Hero3D cameraZ={cameraZ} spin={spin} scale={objScale} drift={frame * 0.04} />
      <Label text="CAPABILITY REEL — 01 / 3D" delay={8} />
      <AbsoluteFill style={{ justifyContent: "flex-end", alignItems: "center", paddingBottom: 110 }}>
        <SplitReveal text="MOTION, ENGINEERED." start={12} size={96} stagger={1.2} />
        <div
          style={{
            fontFamily: MONO,
            fontSize: 20,
            letterSpacing: 8,
            color: "rgba(255,255,255,0.55)",
            marginTop: 10,
            opacity: interpolate(frame, [34, 48], [0, 1], clamp),
          }}
        >
          REAL-TIME WEBGL · PHYSICAL MATERIALS · RENDERED IN CODE
        </div>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};

/* ---------- Scene 2: kinetic type over perspective grid ---------- */

const PerspectiveGrid: React.FC = () => {
  const frame = useCurrentFrame();
  const line = "rgba(139,92,246,0.45)";
  return (
    <AbsoluteFill style={{ perspective: 700, overflow: "hidden" }}>
      <div
        style={{
          position: "absolute",
          left: "-100%",
          width: "300%",
          height: "140%",
          top: "45%",
          transform: "rotateX(76deg)",
          transformOrigin: "top center",
          backgroundImage: `repeating-linear-gradient(0deg, ${line} 0 2px, transparent 2px 90px), repeating-linear-gradient(90deg, ${line} 0 2px, transparent 2px 90px)`,
          backgroundPosition: `0 ${frame * 9}px`,
          maskImage: "linear-gradient(to bottom, transparent 0%, black 30%, black 100%)",
          WebkitMaskImage: "linear-gradient(to bottom, transparent 0%, black 30%, black 100%)",
        }}
      />
      <div
        style={{
          position: "absolute",
          top: "43%",
          left: 0,
          right: 0,
          height: 6,
          background: `linear-gradient(90deg, transparent, ${CYAN}, ${VIOLET}, transparent)`,
          filter: "blur(6px)",
          opacity: 0.9,
        }}
      />
    </AbsoluteFill>
  );
};

const WORDS = ["DESIGN.", "ANIMATE.", "RENDER."];

const WordCycler: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  return (
    <div style={{ position: "relative", height: 260, width: 1100, overflow: "hidden" }}>
      {WORDS.map((w, i) => {
        const t = frame - (16 + i * 24);
        const isLast = i === WORDS.length - 1;
        const enter = spring({ frame: t, fps, config: { damping: 200 }, durationInFrames: 14 });
        const leave = isLast ? 0 : interpolate(t, [20, 30], [0, 1], { ...clamp, easing: easeInOut });
        if (t < 0 || leave >= 1) return null;
        return (
          <div
            key={w}
            style={{
              position: "absolute",
              top: 0,
              left: 0,
              fontFamily: SANS,
              fontWeight: 800,
              fontSize: 220,
              lineHeight: "260px",
              letterSpacing: -8,
              backgroundImage: `linear-gradient(90deg, #ffffff 0%, #ddd6fe 45%, ${CYAN} 100%)`,
              WebkitBackgroundClip: "text",
              backgroundClip: "text",
              color: "transparent",
              transform: `translateY(${(1 - enter) * 100 - leave * 100}%)`,
              filter: `blur(${(1 - enter) * 8 + leave * 8}px)`,
            }}
          >
            {w}
          </div>
        );
      })}
    </div>
  );
};

const FrameCounter: React.FC = () => {
  const frame = useCurrentFrame();
  const p = interpolate(frame, [18, 80], [0, 1], { ...clamp, easing: easeOut });
  const r = 120;
  const c = 2 * Math.PI * r;
  return (
    <div style={{ position: "relative", width: 300, height: 300 }}>
      <svg width={300} height={300} style={{ position: "absolute", transform: "rotate(-90deg)" }}>
        <defs>
          <linearGradient id="ring" x1="0" y1="0" x2="1" y2="1">
            <stop offset="0%" stopColor={CYAN} />
            <stop offset="100%" stopColor={PINK} />
          </linearGradient>
        </defs>
        <circle cx={150} cy={150} r={r} stroke="rgba(255,255,255,0.1)" strokeWidth={3} fill="none" />
        <circle
          cx={150}
          cy={150}
          r={r}
          stroke="url(#ring)"
          strokeWidth={5}
          strokeLinecap="round"
          fill="none"
          strokeDasharray={c}
          strokeDashoffset={c * (1 - p)}
        />
      </svg>
      <div
        style={{
          position: "absolute",
          inset: 0,
          display: "flex",
          flexDirection: "column",
          justifyContent: "center",
          alignItems: "center",
        }}
      >
        <div style={{ fontFamily: SANS, fontWeight: 700, fontSize: 84, color: "white", fontVariantNumeric: "tabular-nums" }}>
          {Math.round(p * 300)}
        </div>
        <div style={{ fontFamily: MONO, fontSize: 15, letterSpacing: 4, color: "rgba(255,255,255,0.6)" }}>
          FRAMES IN CODE
        </div>
      </div>
    </div>
  );
};

const SceneKinetic: React.FC = () => {
  const frame = useCurrentFrame();
  const reveal = interpolate(frame, [0, 20], [0, 80], { ...clamp, easing: easeInOut });
  const exit = interpolate(frame, [82, 94], [0, 1], { ...clamp, easing: Easing.in(Easing.cubic) });
  return (
    <AbsoluteFill
      style={{
        clipPath: `circle(${reveal}% at 50% 50%)`,
        transform: `scale(${1 + exit * 0.2}) translateX(${-exit * 200}px)`,
        filter: `blur(${exit * 18}px)`,
        opacity: 1 - exit,
        backgroundColor: "#05050c",
      }}
    >
      <AmbientGlow />
      <PerspectiveGrid />
      <Label text="02 / KINETIC TYPOGRAPHY" delay={14} />
      <AbsoluteFill style={{ flexDirection: "row", alignItems: "center", justifyContent: "space-between", padding: "0 140px 140px" }}>
        <WordCycler />
        <FrameCounter />
      </AbsoluteFill>
    </AbsoluteFill>
  );
};

/* ---------- Scene 3: glass cards in 3D space ---------- */

const MiniCube: React.FC = () => {
  const frame = useCurrentFrame();
  const face = (t: string) => (
    <div
      style={{
        position: "absolute",
        width: 90,
        height: 90,
        border: `2px solid ${CYAN}`,
        background: "rgba(34,211,238,0.08)",
        transform: t,
      }}
    />
  );
  return (
    <div style={{ width: 90, height: 90, perspective: 600 }}>
      <div
        style={{
          width: 90,
          height: 90,
          position: "relative",
          transformStyle: "preserve-3d",
          transform: `rotateX(${frame * 3}deg) rotateY(${frame * 4}deg)`,
        }}
      >
        {face("translateZ(45px)")}
        {face("rotateY(180deg) translateZ(45px)")}
        {face("rotateY(90deg) translateZ(45px)")}
        {face("rotateY(-90deg) translateZ(45px)")}
        {face("rotateX(90deg) translateZ(45px)")}
        {face("rotateX(-90deg) translateZ(45px)")}
      </div>
    </div>
  );
};

const MiniType: React.FC = () => {
  const frame = useCurrentFrame();
  const weights = [200, 400, 500, 600, 700, 800, 700, 600, 500, 400];
  const w = weights[Math.floor(frame / 3) % weights.length];
  return (
    <div style={{ fontFamily: SANS, fontSize: 96, fontWeight: w, color: "white", lineHeight: "90px" }}>
      Aa
    </div>
  );
};

const MiniBars: React.FC = () => {
  const frame = useCurrentFrame();
  return (
    <div style={{ display: "flex", alignItems: "flex-end", gap: 8, height: 90 }}>
      {Array.from({ length: 9 }).map((_, i) => (
        <div
          key={i}
          style={{
            width: 12,
            borderRadius: 6,
            height: 20 + Math.abs(Math.sin(frame / 4 + i * 0.9)) * 70,
            background: `linear-gradient(to top, ${VIOLET}, ${PINK})`,
          }}
        />
      ))}
    </div>
  );
};

const MiniChart: React.FC = () => {
  const frame = useCurrentFrame();
  const p = interpolate(frame, [10, 50], [0, 1], { ...clamp, easing: easeOut });
  const d = "M0 80 C 30 70, 50 30, 80 45 S 130 10, 160 25 S 200 5, 220 0";
  return (
    <svg width={220} height={90} viewBox="-5 -5 230 95">
      <path d={d} stroke={CYAN} strokeWidth={4} fill="none" strokeLinecap="round" pathLength={1} strokeDasharray={1} strokeDashoffset={1 - p} />
    </svg>
  );
};

const CARDS = [
  { n: "01", title: "3D / WebGL", sub: "Three.js scenes", Visual: MiniCube },
  { n: "02", title: "Kinetic Type", sub: "Frame-exact text", Visual: MiniType },
  { n: "03", title: "Audio Sync", sub: "Multi-track mix", Visual: MiniBars },
  { n: "04", title: "Data-Driven", sub: "JSON → video", Visual: MiniChart },
];

const GlassCard: React.FC<{ i: number; x: number }> = ({ i, x }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const p = spring({ frame: frame - 4 - i * 5, fps, config: { damping: 16, mass: 0.9 } });
  const sweep = interpolate(frame, [20 + i * 4, 50 + i * 4], [-150, 500], clamp);
  const { n, title, sub, Visual } = CARDS[i];
  return (
    <div
      style={{
        position: "absolute",
        left: -190,
        top: -250,
        width: 380,
        height: 500,
        transform: `translateX(${x}px) translateZ(${interpolate(p, [0, 1], [-1400, 0])}px) rotateY(${(1 - p) * 40}deg)`,
        opacity: p,
        borderRadius: 30,
        overflow: "hidden",
        background: "linear-gradient(150deg, rgba(255,255,255,0.16) 0%, rgba(255,255,255,0.04) 60%, rgba(255,255,255,0.02) 100%)",
        border: "1px solid rgba(255,255,255,0.22)",
        boxShadow: "0 50px 100px rgba(0,0,0,0.55), inset 0 1px 0 rgba(255,255,255,0.35)",
        padding: 40,
        display: "flex",
        flexDirection: "column",
        justifyContent: "space-between",
      }}
    >
      <div style={{ fontFamily: MONO, fontSize: 18, letterSpacing: 4, color: "rgba(255,255,255,0.55)" }}>{n}</div>
      <div style={{ height: 120, display: "flex", alignItems: "center" }}>
        <Visual />
      </div>
      <div>
        <div style={{ fontFamily: SANS, fontWeight: 700, fontSize: 42, color: "white", letterSpacing: -1 }}>{title}</div>
        <div style={{ fontFamily: MONO, fontSize: 17, color: "rgba(255,255,255,0.55)", marginTop: 8 }}>{sub}</div>
      </div>
      <div
        style={{
          position: "absolute",
          top: -100,
          left: sweep,
          width: 120,
          height: 800,
          transform: "rotate(20deg)",
          background: "linear-gradient(90deg, transparent, rgba(255,255,255,0.18), transparent)",
        }}
      />
    </div>
  );
};

const SceneCards: React.FC = () => {
  const frame = useCurrentFrame();
  const rotY = interpolate(frame, [0, 85], [-18, 12], { easing: Easing.inOut(Easing.sin), ...clamp });
  const enter = interpolate(frame, [0, 10], [0, 1], clamp);
  const exit = interpolate(frame, [72, 85], [0, 1], { ...clamp, easing: Easing.in(Easing.cubic) });
  return (
    <AbsoluteFill style={{ opacity: enter * (1 - exit), filter: `blur(${exit * 20}px)` }}>
      <AmbientGlow />
      <Label text="03 / COMPOSITING IN 3D SPACE" delay={6} />
      <AbsoluteFill style={{ perspective: 1800, justifyContent: "center", alignItems: "center" }}>
        <div
          style={{
            position: "relative",
            transformStyle: "preserve-3d",
            transform: `translateZ(${exit * 900}px) rotateX(6deg) rotateY(${rotY}deg)`,
          }}
        >
          {[-630, -210, 210, 630].map((x, i) => (
            <GlassCard key={i} i={i} x={x} />
          ))}
        </div>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};

/* ---------- Scene 4: title lockup ---------- */

const SceneLockup: React.FC = () => {
  const frame = useCurrentFrame();
  const p = interpolate(frame, [0, 28], [0, 1], { ...clamp, easing: easeOut });
  const line = interpolate(frame, [14, 36], [0, 640], { ...clamp, easing: easeOut });
  const shimmer = interpolate(frame, [20, 52], [130, -30], clamp);
  const sub = interpolate(frame, [26, 40], [0, 1], clamp);
  const fadeOut = interpolate(frame, [48, 60], [0, 1], clamp);
  return (
    <AbsoluteFill style={{ opacity: interpolate(frame, [0, 6], [0, 1], clamp) }}>
      <AmbientGlow />
      <AbsoluteFill style={{ opacity: 0.55 }}>
        <Hero3D cameraZ={11 - p * 1.5} spin={frame * 0.02 + 2} scale={0.8} drift={frame * 0.03} />
      </AbsoluteFill>
      <AbsoluteFill style={{ background: "radial-gradient(ellipse at center, rgba(4,4,10,0.55) 0%, transparent 70%)" }} />
      <AbsoluteFill style={{ justifyContent: "center", alignItems: "center", flexDirection: "column" }}>
        <div
          style={{
            fontFamily: SANS,
            fontWeight: 800,
            fontSize: 130,
            letterSpacing: interpolate(p, [0, 1], [70, -3]),
            opacity: p,
            filter: `blur(${(1 - p) * 16}px)`,
            backgroundImage:
              "linear-gradient(110deg, #ffffff 0%, #ffffff 40%, #c4b5fd 47%, #67e8f9 50%, #ffffff 56%, #ffffff 100%)",
            backgroundSize: "300% 100%",
            backgroundPosition: `${shimmer}% 0`,
            WebkitBackgroundClip: "text",
            backgroundClip: "text",
            color: "transparent",
          }}
        >
          MADE WITH CODE.
        </div>
        <div
          style={{
            width: line,
            height: 2,
            marginTop: 20,
            background: `linear-gradient(90deg, transparent, ${CYAN}, ${VIOLET}, ${PINK}, transparent)`,
          }}
        />
        <div style={{ fontFamily: MONO, fontSize: 20, letterSpacing: 10, color: "rgba(255,255,255,0.7)", marginTop: 28, opacity: sub }}>
          REACT · THREE.JS · REMOTION
        </div>
      </AbsoluteFill>
      <AbsoluteFill style={{ backgroundColor: "black", opacity: fadeOut }} />
    </AbsoluteFill>
  );
};

/* ---------- Composition ---------- */

const Flash: React.FC<{ at: number }> = ({ at }) => {
  const frame = useCurrentFrame();
  const o = interpolate(frame, [at - 3, at, at + 9], [0, 0.85, 0], clamp);
  return (
    <AbsoluteFill
      style={{ background: "radial-gradient(circle at 50% 50%, rgba(255,255,255,1) 0%, rgba(196,181,253,0.6) 35%, transparent 75%)", opacity: o, mixBlendMode: "screen" }}
    />
  );
};

export const Premium: React.FC = () => {
  return (
    <AbsoluteFill style={{ backgroundColor: "#04040a" }}>
      <AmbientGlow />
      <Sequence from={0} durationInFrames={95}>
        <SceneHero />
      </Sequence>
      <Sequence from={80} durationInFrames={95}>
        <SceneKinetic />
      </Sequence>
      <Sequence from={168} durationInFrames={86}>
        <SceneCards />
      </Sequence>
      <Sequence from={240} durationInFrames={60}>
        <SceneLockup />
      </Sequence>

      <Flash at={84} />
      <Flash at={244} />
      <Vignette />
      <Grain />

      <Audio
        src={staticFile("music4.mp3")}
        volume={(f) => interpolate(f, [0, 20, 270, 300], [0, 1, 1, 0], clamp)}
      />
      <Sequence from={36}>
        <Audio src={staticFile("sfx_riser.wav")} volume={0.55} />
      </Sequence>
      <Sequence from={82}>
        <Audio src={staticFile("sfx_impact.wav")} volume={0.9} />
      </Sequence>
      <Sequence from={160}>
        <Audio src={staticFile("sfx_whoosh.wav")} volume={0.7} />
      </Sequence>
      <Sequence from={232}>
        <Audio src={staticFile("sfx_whoosh.wav")} volume={0.6} />
      </Sequence>
      <Sequence from={243}>
        <Audio src={staticFile("sfx_impact.wav")} volume={0.8} />
      </Sequence>
    </AbsoluteFill>
  );
};
