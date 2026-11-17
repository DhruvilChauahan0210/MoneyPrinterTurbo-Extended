import React from "react";
import { AbsoluteFill, Audio, staticFile, useCurrentFrame, interpolate } from "remotion";

/**
 * Fast-start template for a new short.
 * Fill in the four PROPS below, add a <Composition> for it in index.ts, render.
 * Covers the common case (photo/background + stripe text + voice + music) in one file
 * so a new short doesn't need a new bespoke component.
 */
export type SceneProps = {
  background: string; // staticFile name: image or solid color via CSS if left empty
  line1: string;
  line2?: string;
  voiceFile: string;
  musicFile?: string;
  musicVolume?: number;
  durationInSeconds?: number;
};

const STRIPE_HEIGHT = 360;

export const SceneTemplate: React.FC<SceneProps> = ({
  background,
  line1,
  line2,
  voiceFile,
  musicFile,
  musicVolume = 0.1,
  durationInSeconds = 6,
}) => {
  const frame = useCurrentFrame();
  const fps = 30;
  const totalFrames = Math.round(durationInSeconds * fps);
  const zoom = interpolate(frame, [0, totalFrames], [1, 1.12]);
  const flash = interpolate(frame, [0, 10], [1, 0], { extrapolateRight: "clamp" });

  return (
    <AbsoluteFill style={{ backgroundColor: "black" }}>
      {background ? (
        <AbsoluteFill
          style={{
            backgroundImage: `url(${staticFile(background)})`,
            backgroundSize: "cover",
            backgroundPosition: "center",
            transform: `scale(${zoom})`,
          }}
        />
      ) : null}

      <AbsoluteFill
        style={{
          top: 0,
          height: STRIPE_HEIGHT,
          backgroundColor: "black",
          display: "flex",
          flexDirection: "column",
          justifyContent: "center",
          alignItems: "center",
          padding: "0 60px",
        }}
      >
        <div style={{ color: "white", fontSize: 64, fontWeight: 800, textAlign: "center" }}>{line1}</div>
        {line2 ? (
          <div style={{ color: "#f5c518", fontSize: 56, fontWeight: 800, textAlign: "center", marginTop: 12 }}>
            {line2}
          </div>
        ) : null}
      </AbsoluteFill>

      <AbsoluteFill style={{ backgroundColor: "white", opacity: flash }} />

      <Audio src={staticFile(voiceFile)} volume={1} />
      {musicFile ? <Audio src={staticFile(musicFile)} volume={musicVolume} /> : null}
    </AbsoluteFill>
  );
};
