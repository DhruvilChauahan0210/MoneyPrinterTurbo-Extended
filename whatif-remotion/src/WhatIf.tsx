import React from "react";
import {
  AbsoluteFill,
  Img,
  Audio,
  staticFile,
  useVideoConfig,
  useCurrentFrame,
  interpolate,
  spring,
  Easing,
} from "remotion";

export type WhatIfProps = {
  imageFile: string;
  voiceFile: string;
  musicFile: string;
  line1: string;
  line2: string;
  musicVolume?: number;
  sfxFile?: string; // boom/stinger, plays once at the start
  ambienceFile?: string; // low, constant atmosphere bed
  ambienceVolume?: number;
  durationInSeconds?: number;
};

const STRIPE_HEIGHT = 360;

export const WhatIf: React.FC<WhatIfProps> = ({
  imageFile,
  voiceFile,
  musicFile,
  line1,
  line2,
  musicVolume = 0.1,
  sfxFile,
  ambienceFile,
  ambienceVolume = 0.06,
}) => {
  const { height, durationInFrames, fps } = useVideoConfig();
  const frame = useCurrentFrame();

  // Slow continuous Ken Burns zoom across the whole clip: 1.0 -> 1.12
  const zoom = interpolate(frame, [0, durationInFrames], [1, 1.12], {
    easing: Easing.out(Easing.quad),
    extrapolateRight: "clamp",
  });

  // Text: punchy scale+fade entrance, staggered between the two lines
  const line1Spring = spring({ frame, fps, config: { damping: 14, mass: 0.6 } });
  const line2Spring = spring({
    frame: frame - 6,
    fps,
    config: { damping: 14, mass: 0.6 },
  });
  const line1Scale = interpolate(line1Spring, [0, 1], [0.7, 1]);
  const line2Scale = interpolate(line2Spring, [0, 1], [0.7, 1]);
  const line1Opacity = interpolate(frame, [0, 8], [0, 1], { extrapolateRight: "clamp" });
  const line2Opacity = interpolate(frame, [6, 14], [0, 1], { extrapolateRight: "clamp" });

  // Quick white flash on frame 0-4 to sell the "reveal" punch alongside the boom sfx
  const flash = interpolate(frame, [0, 3, 10], [0.85, 0.85, 0], {
    extrapolateRight: "clamp",
    extrapolateLeft: "clamp",
  });

  // Subtle vignette pulse on the stripe for depth
  const stripeGlow = interpolate(
    Math.sin(frame / 10),
    [-1, 1],
    [0.0, 0.12]
  );

  return (
    <AbsoluteFill style={{ backgroundColor: "black" }}>
      {/* Photo fills everything below the stripe, with a slow zoom */}
      <AbsoluteFill
        style={{
          top: STRIPE_HEIGHT,
          height: height - STRIPE_HEIGHT,
          overflow: "hidden",
        }}
      >
        <Img
          src={staticFile(imageFile)}
          style={{
            width: "100%",
            height: "100%",
            objectFit: "cover",
            objectPosition: "center 25%",
            transform: `scale(${zoom})`,
            transformOrigin: "center 30%",
          }}
        />
        {/* soft bottom gradient so the photo doesn't cut flat */}
        <AbsoluteFill
          style={{
            background:
              "linear-gradient(to bottom, rgba(0,0,0,0) 80%, rgba(0,0,0,0.35) 100%)",
          }}
        />
      </AbsoluteFill>

      {/* Black stripe with the full question/headline, animated in */}
      <AbsoluteFill
        style={{
          height: STRIPE_HEIGHT,
          justifyContent: "center",
          alignItems: "center",
          flexDirection: "column",
          gap: 14,
          padding: "0 32px",
          background: `radial-gradient(ellipse at center, rgba(255,215,0,${stripeGlow}) 0%, rgba(0,0,0,0) 70%)`,
        }}
      >
        <div
          style={{
            fontFamily: "Arial, Helvetica, sans-serif",
            fontWeight: 900,
            fontSize: 72,
            color: "white",
            textAlign: "center",
            lineHeight: 1.08,
            letterSpacing: 1,
            opacity: line1Opacity,
            transform: `scale(${line1Scale})`,
            textShadow: "0 4px 18px rgba(0,0,0,0.6)",
          }}
        >
          {line1}
        </div>
        <div
          style={{
            fontFamily: "Arial, Helvetica, sans-serif",
            fontWeight: 900,
            fontSize: 72,
            color: "white",
            textAlign: "center",
            lineHeight: 1.08,
            letterSpacing: 1,
            opacity: line2Opacity,
            transform: `scale(${line2Scale})`,
            textShadow: "0 4px 18px rgba(0,0,0,0.6)",
          }}
        >
          {line2}
        </div>
      </AbsoluteFill>

      {/* Reveal flash */}
      <AbsoluteFill style={{ backgroundColor: "white", opacity: flash }} />

      {/* Audio stack: voice is the loudest and clearest; music + ambience sit well under it */}
      <Audio src={staticFile(voiceFile)} volume={1} />
      <Audio src={staticFile(musicFile)} volume={musicVolume} />
      {ambienceFile ? (
        <Audio src={staticFile(ambienceFile)} volume={ambienceVolume} />
      ) : null}
      {sfxFile ? <Audio src={staticFile(sfxFile)} volume={0.9} /> : null}
    </AbsoluteFill>
  );
};
