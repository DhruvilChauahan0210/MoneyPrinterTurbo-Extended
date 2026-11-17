import { registerRoot, Composition, Still } from "remotion";
import React from "react";
import { RonaldoRetire, RonaldoThumb, RETIRE_DURATION } from "./RonaldoRetire";
import { WhatIf } from "./WhatIf";
import { SceneTemplate } from "./SceneTemplate";
import { Showcase } from "./Showcase";
import { Premium } from "./Premium";
import { Ganpati } from "./Ganpati";
import { GanpatiAnim } from "./GanpatiAnim";
import { GoatSample, GOAT_DURATION } from "./GoatSample";
import { GoatFull, GOAT_FULL_DURATION } from "./GoatFull";
import { Duel } from "./Duel";
import { WhoIsIt } from "./WhoIsIt";
import { NewsCut } from "./NewsCut";

const FPS = 30;

const Root: React.FC = () => {
  return React.createElement(
    React.Fragment,
    null,
    React.createElement(Composition, {
      id: "Duel",
      component: Duel,
      durationInFrames: 20 * FPS,
      fps: FPS,
      width: 1080,
      height: 1920,
      defaultProps: {
        headline: "PICK ONE", countdownSeconds: 5,
        left: { name: "LEFT", sub: "", photo: "wi_haaland_2022.jpg", color: "#2f7bff", posX: 50, posY: 25, zoom: 1 },
        right: { name: "RIGHT", sub: "", photo: "wi_messi_2021.jpg", color: "#ff3b5c", posX: 50, posY: 25, zoom: 1 },
        rows: [{ label: "ROW", a: 3, b: 5 }, { label: "ROW", a: 3, b: 5 }, { label: "ROW", a: 3, b: 5 }, { label: "ROW", a: 3, b: 5 }],
        rowStarts: [5, 8, 11, 14], revealAt: 17,
        reveal: { number: 100, label: "LABEL", detail: "", question: "WHO?" },
        source: "", audioFile: "voice.wav", durationInSeconds: 20,
      },
      calculateMetadata: async ({ props }: { props: any }) => {
        return { durationInFrames: Math.round((props.durationInSeconds ?? 20) * FPS) };
      },
    }),
    React.createElement(Composition, {
      id: "WhoIsIt",
      component: WhoIsIt,
      durationInFrames: 16 * FPS,
      fps: FPS,
      width: 1080,
      height: 1920,
      defaultProps: {
        headline: "WHO IS IT?", photo: "wi_haaland_2022.jpg", posX: 50, posY: 25, zoom: 1.1,
        clues: ["CLUE ONE", "CLUE TWO", "CLUE THREE"], clueStarts: [0, 4, 8], revealAt: 12,
        name: "NAME", fact: "FACT", source: "", audioFile: "voice.wav", durationInSeconds: 16,
      },
      calculateMetadata: async ({ props }: { props: any }) => {
        return { durationInFrames: Math.round((props.durationInSeconds ?? 16) * FPS) };
      },
    }),
    React.createElement(Composition, {
      id: "NewsCut",
      component: NewsCut,
      durationInFrames: 30 * FPS,
      fps: FPS,
      width: 1080,
      height: 1920,
      defaultProps: {
        shots: [], caps: [{ t: 0, text: "NEWSCUT" }], cards: [], cover: {}, coverFrames: 0,
        watermark: "CD PHANTOM", audioFile: "voice.wav", voiceEnd: 30, durationInSeconds: 30,
      },
      calculateMetadata: async ({ props }: { props: any }) => {
        return { durationInFrames: Math.round((props.durationInSeconds ?? 30) * FPS) };
      },
    }),
    React.createElement(Composition, {
      id: "RonaldoRetire",
      component: RonaldoRetire,
      durationInFrames: RETIRE_DURATION,
      fps: FPS,
      width: 1920,
      height: 1080,
    }),
    React.createElement(Still, {
      id: "RonaldoThumb",
      component: RonaldoThumb,
      width: 1280,
      height: 720,
    }),
    React.createElement(Composition, {
      id: "GoatFull",
      component: GoatFull,
      durationInFrames: GOAT_FULL_DURATION,
      fps: FPS,
      width: 1920,
      height: 1080,
    }),
    React.createElement(Composition, {
      id: "GoatSample",
      component: GoatSample,
      durationInFrames: GOAT_DURATION,
      fps: FPS,
      width: 1920,
      height: 1080,
    }),
    React.createElement(Composition, {
      id: "GanpatiAnim",
      component: GanpatiAnim,
      durationInFrames: 450,
      fps: FPS,
      width: 1080,
      height: 1920,
    }),
    React.createElement(Composition, {
      id: "Ganpati",
      component: Ganpati,
      durationInFrames: 450,
      fps: FPS,
      width: 1080,
      height: 1920,
    }),
    React.createElement(Composition, {
      id: "Premium",
      component: Premium,
      durationInFrames: 300,
      fps: FPS,
      width: 1920,
      height: 1080,
    }),
    React.createElement(Composition, {
      id: "Showcase",
      component: Showcase,
      durationInFrames: 300,
      fps: FPS,
      width: 1080,
      height: 1920,
    }),
    React.createElement(Composition, {
      id: "SceneTemplate",
      component: SceneTemplate,
      durationInFrames: 6 * FPS,
      fps: FPS,
      width: 1080,
      height: 1920,
      defaultProps: {
        background: "",
        line1: "FILL IN LINE 1",
        line2: "",
        voiceFile: "voice.wav",
        musicFile: "music.mp3",
        musicVolume: 0.1,
        durationInSeconds: 6,
      },
      calculateMetadata: async ({ props }: { props: any }) => {
        const seconds = props.durationInSeconds ?? 6;
        return { durationInFrames: Math.round(seconds * FPS) };
      },
    }),
    React.createElement(
    Composition,
    {
      id: "WhatIf",
      component: WhatIf,
      // Default length; override per-render with --props='{"durationInSeconds":7.5}'
      durationInFrames: 6 * FPS,
      fps: FPS,
      width: 1080,
      height: 1920,
      defaultProps: {
        imageFile: "ronaldo_2018_ballondor.png",
        voiceFile: "voice.wav",
        musicFile: "music.mp3",
        line1: "WHAT IF RONALDO WON",
        line2: "THE 2018 BALLON D'OR?",
        musicVolume: 0.12,
        durationInSeconds: 6,
      },
      calculateMetadata: async ({ props }: { props: any }) => {
        const seconds = props.durationInSeconds ?? 6;
        return { durationInFrames: Math.round(seconds * FPS) };
      },
    })
  );
};

registerRoot(Root);
