import React, { useRef } from "react";
import { AbsoluteFill, Audio, staticFile, useCurrentFrame, interpolate, spring, useVideoConfig } from "remotion";
import { ThreeCanvas } from "@remotion/three";
import * as THREE from "three";

const GOLD = "#f5c518";
const INK = "#0a0a0a";

const TrophyMesh: React.FC = () => {
  const frame = useCurrentFrame();
  const group = useRef<THREE.Group>(null);
  const rotation = frame * 0.035;
  const bob = Math.sin(frame / 20) * 0.15;
  const introScale = spring({ frame, fps: 30, config: { damping: 12 }, durationInFrames: 30 });

  return (
    <group ref={group} rotation={[0.3, rotation, 0]} position={[0, bob, 0]} scale={introScale}>
      {/* core gem */}
      <mesh>
        <icosahedronGeometry args={[1.15, 0]} />
        <meshStandardMaterial color={GOLD} metalness={0.85} roughness={0.15} emissive={GOLD} emissiveIntensity={0.25} />
      </mesh>
      {/* orbiting ring */}
      <mesh rotation={[Math.PI / 2.4, 0, 0]}>
        <torusGeometry args={[1.8, 0.05, 16, 100]} />
        <meshStandardMaterial color="#ffffff" metalness={0.9} roughness={0.2} emissive={GOLD} emissiveIntensity={0.4} />
      </mesh>
      <mesh rotation={[Math.PI / 1.6, 0.6, 0]}>
        <torusGeometry args={[2.1, 0.035, 16, 100]} />
        <meshStandardMaterial color={GOLD} metalness={0.9} roughness={0.2} emissive={GOLD} emissiveIntensity={0.3} />
      </mesh>
    </group>
  );
};

const Scene3D: React.FC = () => {
  const { width, height } = useVideoConfig();
  return (
    <ThreeCanvas width={width} height={height} style={{ position: "absolute", top: 0, left: 0 }}>
      <ambientLight intensity={0.5} />
      <pointLight position={[4, 4, 4]} intensity={2.2} color={GOLD} />
      <pointLight position={[-4, -2, 3]} intensity={1.2} color="#ffffff" />
      <TrophyMesh />
    </ThreeCanvas>
  );
};

const STRIPE_HEIGHT = 380;

export const Showcase: React.FC = () => {
  const frame = useCurrentFrame();
  const fps = 30;
  const totalFrames = 300; // 10s

  // Scene timing
  const introEnd = 55; // 3D hero intro
  const bodyStart = 45;
  const outroStart = 250;

  const flash = interpolate(frame, [0, 12], [1, 0], { extrapolateRight: "clamp" });
  const introOpacity = interpolate(frame, [0, 10, introEnd - 15, introEnd], [0, 1, 1, 0], { extrapolateRight: "clamp" });
  const introScale = interpolate(frame, [0, introEnd], [0.85, 1.15], { extrapolateRight: "clamp" });

  // Hard cut at outroStart (no crossfade — fading a layer's own opaque background
  // makes it translucent too, letting the layer behind bleed through). A quick
  // white flash masks the cut instead.
  const bodyOpacity = interpolate(frame, [bodyStart, bodyStart + 20, outroStart - 6, outroStart], [0, 1, 1, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const photoZoom = interpolate(frame, [bodyStart, totalFrames], [1, 1.18], { extrapolateRight: "clamp" });

  const titleIn = spring({ frame: frame - bodyStart - 5, fps, config: { damping: 14 } });
  const subtitleIn = spring({ frame: frame - bodyStart - 14, fps, config: { damping: 14 } });

  const cutFlash = interpolate(frame, [outroStart - 6, outroStart + 2, outroStart + 10], [0, 1, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const showOutro = frame >= outroStart;
  const outroContentIn = spring({ frame: frame - outroStart - 6, fps, config: { damping: 12 } });

  const vignette =
    "radial-gradient(ellipse at center, rgba(0,0,0,0) 45%, rgba(0,0,0,0.65) 100%)";

  return (
    <AbsoluteFill style={{ backgroundColor: INK }}>
      {/* SCENE 1 — 3D hero intro, proves Three.js integration */}
      <AbsoluteFill style={{ opacity: introOpacity, transform: `scale(${introScale})` }}>
        <Scene3D />
        <AbsoluteFill
          style={{
            justifyContent: "flex-end",
            alignItems: "center",
            paddingBottom: 260,
          }}
        >
          <div
            style={{
              color: GOLD,
              fontSize: 46,
              fontWeight: 900,
              letterSpacing: 4,
              textTransform: "uppercase",
              textShadow: "0 0 30px rgba(245,197,24,0.6)",
            }}
          >
            Legends Never Fade
          </div>
        </AbsoluteFill>
      </AbsoluteFill>

      {/* SCENE 2 — real photo + Ken Burns + animated headline stripe */}
      <AbsoluteFill style={{ opacity: bodyOpacity }}>
        <AbsoluteFill
          style={{
            backgroundImage: `url(${staticFile("ronaldo_2018_ballondor.png")})`,
            backgroundSize: "cover",
            backgroundPosition: "center 20%",
            transform: `scale(${photoZoom})`,
          }}
        />
        <AbsoluteFill style={{ background: vignette }} />

        <AbsoluteFill
          style={{
            top: 0,
            height: STRIPE_HEIGHT,
            backgroundColor: INK,
            display: "flex",
            flexDirection: "column",
            justifyContent: "center",
            alignItems: "center",
            padding: "0 70px",
            borderBottom: `3px solid ${GOLD}`,
          }}
        >
          <div
            style={{
              color: "white",
              fontSize: 62,
              fontWeight: 900,
              textAlign: "center",
              transform: `scale(${titleIn})`,
              opacity: titleIn,
            }}
          >
            WHAT MAKES A LEGEND?
          </div>
          <div
            style={{
              color: GOLD,
              fontSize: 50,
              fontWeight: 800,
              textAlign: "center",
              marginTop: 14,
              transform: `scale(${subtitleIn})`,
              opacity: subtitleIn,
            }}
          >
            ONE MOMENT CHANGES EVERYTHING.
          </div>
        </AbsoluteFill>
      </AbsoluteFill>

      {/* SCENE 3 — outro / CTA card (hard-cut in, always fully opaque once shown) */}
      {showOutro ? (
        <AbsoluteFill
          style={{
            backgroundColor: INK,
            justifyContent: "center",
            alignItems: "center",
          }}
        >
          <div
            style={{
              transform: `scale(${outroContentIn})`,
              opacity: outroContentIn,
              textAlign: "center",
            }}
          >
            <div style={{ color: GOLD, fontSize: 70, fontWeight: 900, letterSpacing: 2 }}>FOLLOW FOR MORE</div>
            <div style={{ color: "white", fontSize: 38, fontWeight: 600, marginTop: 14, opacity: 0.85 }}>
              legends · moments · history
            </div>
          </div>
        </AbsoluteFill>
      ) : null}

      {/* reveal flash + hard-cut mask flash */}
      <AbsoluteFill style={{ backgroundColor: "white", opacity: Math.max(flash, cutFlash) }} />

      {/* Audio stack — voice + music, proves layered multi-track audio */}
      <Audio src={staticFile("showcase_voice.wav")} volume={1} />
      <Audio src={staticFile("music2.mp3")} volume={0.14} />
      <Audio src={staticFile("boom.mp3")} volume={0.5} startFrom={0} endAt={25} />
    </AbsoluteFill>
  );
};
