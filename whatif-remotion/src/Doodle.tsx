import React from "react";
import {
  AbsoluteFill,
  Audio,
  staticFile,
  useCurrentFrame,
  interpolate,
} from "remotion";

// Lighter hand-drawn wobble — the old one was too aggressive and made lines jagged/glitchy
// instead of charming. Small displacement, low frequency = a gentle sketch wobble.
const SketchFilter: React.FC = () => (
  <svg width="0" height="0">
    <defs>
      <filter id="sketchy" x="-20%" y="-20%" width="140%" height="140%">
        <feTurbulence type="fractalNoise" baseFrequency="0.012" numOctaves="2" result="noise" seed="7" />
        <feDisplacementMap in="SourceGraphic" in2="noise" scale="2.2" />
      </filter>
    </defs>
  </svg>
);

const SKIN = "#f4c89a";
const SHIRT = "#4a90d9";
const HAIR = "#3a2a1a";
const INK = "#2a2a2a";

// Big, close-up, expressive character — filling the frame instead of a tiny stick figure
// floating in empty space. This is the actual visual language of the genre.
const Boy: React.FC<{ x: number; y: number; scale: number; talking: boolean; happy: boolean }> = ({
  x,
  y,
  scale,
  talking,
  happy,
}) => {
  const frame = useCurrentFrame();
  const bob = Math.sin(frame / 9) * 6;
  const mouthOpen = talking && Math.floor(frame / 5) % 2 === 0;
  const browLift = happy ? -6 : 0;

  return (
    <g transform={`translate(${x}, ${y + bob}) scale(${scale})`} style={{ filter: "url(#sketchy)" }}>
      {/* body / shirt */}
      <path d="M -70 60 Q 0 20 70 60 L 85 220 Q 0 250 -85 220 Z" fill={SHIRT} stroke={INK} strokeWidth={5} />
      {/* arms */}
      <path d={happy ? "M -70 75 Q -130 40 -145 -10" : "M -70 75 Q -110 110 -120 170"} stroke={SKIN} strokeWidth={22} strokeLinecap="round" fill="none" />
      <path d={happy ? "M 70 75 Q 130 40 145 -10" : "M 70 75 Q 110 110 120 170"} stroke={SKIN} strokeWidth={22} strokeLinecap="round" fill="none" />
      {/* legs */}
      <path d="M -35 230 L -45 320" stroke="#2b3a55" strokeWidth={24} strokeLinecap="round" />
      <path d="M 35 230 L 45 320" stroke="#2b3a55" strokeWidth={24} strokeLinecap="round" />
      {/* head */}
      <circle cx={0} cy={-60} r={100} fill={SKIN} stroke={INK} strokeWidth={5} />
      {/* hair */}
      <path d="M -98 -95 Q 0 -175 98 -95 Q 95 -130 0 -140 Q -95 -130 -98 -95 Z" fill={HAIR} stroke={INK} strokeWidth={4} />
      {/* ears */}
      <circle cx={-98} cy={-55} r={14} fill={SKIN} stroke={INK} strokeWidth={4} />
      <circle cx={98} cy={-55} r={14} fill={SKIN} stroke={INK} strokeWidth={4} />
      {/* eyebrows */}
      <path d={`M -48 ${-90 + browLift} Q -30 ${-100 + browLift} -12 ${-90 + browLift}`} stroke={INK} strokeWidth={5} fill="none" strokeLinecap="round" />
      <path d={`M 12 ${-90 + browLift} Q 30 ${-100 + browLift} 48 ${-90 + browLift}`} stroke={INK} strokeWidth={5} fill="none" strokeLinecap="round" />
      {/* big eyes */}
      <ellipse cx={-30} cy={-65} rx={16} ry={20} fill="white" stroke={INK} strokeWidth={4} />
      <ellipse cx={30} cy={-65} rx={16} ry={20} fill="white" stroke={INK} strokeWidth={4} />
      <circle cx={-27} cy={-62} r={8} fill={INK} />
      <circle cx={33} cy={-62} r={8} fill={INK} />
      {/* cheeks */}
      {happy && (
        <>
          <ellipse cx={-62} cy={-30} rx={14} ry={9} fill="#f29b9b" opacity={0.6} />
          <ellipse cx={62} cy={-30} rx={14} ry={9} fill="#f29b9b" opacity={0.6} />
        </>
      )}
      {/* mouth */}
      {mouthOpen ? (
        <ellipse cx={0} cy={-15} rx={22} ry={16} fill="#7a2e2e" stroke={INK} strokeWidth={4} />
      ) : (
        <path d={happy ? "M -28 -18 Q 0 10 28 -18" : "M -24 -16 Q 0 -4 24 -16"} stroke={INK} strokeWidth={5} fill="none" strokeLinecap="round" />
      )}
    </g>
  );
};

const FUR = "#d8a04a";
const FUR_DARK = "#b5812f";

const Dog: React.FC<{ x: number; y: number; scale: number; wag: boolean; shivering: boolean }> = ({
  x,
  y,
  scale,
  wag,
  shivering,
}) => {
  const frame = useCurrentFrame();
  const tailWag = wag ? Math.sin(frame / 2.2) * 40 : -5;
  const bob = Math.sin(frame / 11 + 2) * 4;
  const shiver = shivering ? Math.sin(frame * 1.6) * 3 : 0;

  return (
    <g transform={`translate(${x + shiver}, ${y + bob}) scale(${scale})`} style={{ filter: "url(#sketchy)" }}>
      {/* back legs */}
      <path d="M -50 60 L -58 110" stroke={FUR_DARK} strokeWidth={18} strokeLinecap="round" />
      <path d="M 40 60 L 48 110" stroke={FUR_DARK} strokeWidth={18} strokeLinecap="round" />
      {/* tail */}
      <path
        d={`M 85 10 Q 140 ${tailWag - 20} 150 ${tailWag - 70}`}
        stroke={FUR_DARK}
        strokeWidth={16}
        strokeLinecap="round"
        fill="none"
      />
      {/* body */}
      <ellipse cx={0} cy={30} rx={95} ry={55} fill={FUR} stroke={INK} strokeWidth={5} />
      {/* front legs */}
      <path d="M -60 70 L -65 115" stroke={FUR_DARK} strokeWidth={18} strokeLinecap="round" />
      <path d="M 10 75 L 8 115" stroke={FUR_DARK} strokeWidth={18} strokeLinecap="round" />
      {/* head */}
      <circle cx={-95} cy={-15} r={55} fill={FUR} stroke={INK} strokeWidth={5} />
      {/* ears, floppy */}
      <path d="M -135 -45 Q -165 -5 -140 30 Q -120 10 -118 -35 Z" fill={FUR_DARK} stroke={INK} strokeWidth={4} />
      <path d="M -70 -50 Q -50 -15 -70 20 Q -90 5 -85 -40 Z" fill={FUR_DARK} stroke={INK} strokeWidth={4} />
      {/* snout */}
      <ellipse cx={-130} cy={5} rx={28} ry={20} fill="#efd3a0" stroke={INK} strokeWidth={4} />
      <circle cx={-150} cy={0} r={8} fill={INK} />
      {/* eyes, big and sad/happy */}
      <circle cx={-105} cy={-25} r={9} fill={INK} />
      <ellipse cx={-105} cy={-30} rx={3} ry={3} fill="white" />
      {/* mouth */}
      <path
        d={shivering ? "M -140 18 Q -130 10 -120 18" : "M -145 18 Q -130 32 -112 16"}
        stroke={INK}
        strokeWidth={4}
        fill="none"
        strokeLinecap="round"
      />
    </g>
  );
};

const RainScene: React.FC<{ opacity: number }> = ({ opacity }) => {
  const frame = useCurrentFrame();
  return (
    <g opacity={opacity} stroke="#7fa6d9" strokeWidth={3} strokeLinecap="round">
      {Array.from({ length: 22 }).map((_, i) => {
        const xBase = (i * 67 + 20) % 1080;
        const offset = ((frame * 18 + i * 53) % 900) - 150;
        return <line key={i} x1={xBase} y1={offset} x2={xBase - 22} y2={offset + 55} />;
      })}
    </g>
  );
};

const Bench: React.FC<{ opacity: number }> = ({ opacity }) => (
  <g transform="translate(790, 560)" opacity={opacity} style={{ filter: "url(#sketchy)" }} stroke={INK} strokeWidth={6} fill="#8a5a33">
    <rect x={-90} y={-10} width={180} height={22} rx={6} />
    <rect x={-90} y={-55} width={180} height={18} rx={6} />
    <rect x={-75} y={12} width={16} height={55} fill="#6b4323" />
    <rect x={60} y={12} width={16} height={55} fill="#6b4323" />
  </g>
);

const Heart: React.FC<{ frame0: number; x: number; y: number }> = ({ frame0, x, y }) => {
  const frame = useCurrentFrame();
  const t = frame - frame0;
  if (t < 0) return null;
  const pop = interpolate(t, [0, 10, 100], [0, 1.4, 1.1], { extrapolateRight: "clamp" });
  const opacity = interpolate(t, [0, 8], [0, 1], { extrapolateRight: "clamp" });
  const rise = interpolate(t, [0, 100], [0, -60], { extrapolateRight: "clamp" });
  return (
    <g transform={`translate(${x}, ${y + rise}) scale(${pop})`} opacity={opacity} style={{ filter: "url(#sketchy)" }}>
      <path d="M0 14 C -28 -20, -68 2, 0 48 C 68 2, 28 -20, 0 14 Z" fill="#e8485a" stroke={INK} strokeWidth={4} />
    </g>
  );
};

const Sky: React.FC<{ stormy: number }> = ({ stormy }) => {
  const top = `rgb(${255 - stormy * 100}, ${248 - stormy * 70}, ${225 - stormy * 50})`;
  const bottom = `rgb(${255 - stormy * 140}, ${236 - stormy * 100}, ${190 - stormy * 70})`;
  return (
    <>
      <defs>
        <linearGradient id="sky" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stopColor={top} />
          <stop offset="100%" stopColor={bottom} />
        </linearGradient>
      </defs>
      <rect x={0} y={0} width={1080} height={1920} fill="url(#sky)" />
    </>
  );
};

export const DoodleStory: React.FC = () => {
  const frame = useCurrentFrame();
  const scene1 = frame < 100; // boy walking, notices something, rain
  const scene2 = frame >= 95 && frame < 210; // kneels, finds the shivering puppy
  const scene3 = frame >= 205; // happy ending, heart

  const stormy = interpolate(frame, [0, 90, 205, 240], [1, 1, 0, 0], { extrapolateRight: "clamp" });

  return (
    <AbsoluteFill style={{ backgroundColor: "#fdf1dc" }}>
      <SketchFilter />
      <svg viewBox="0 0 1080 1920" width="100%" height="100%">
        <Sky stormy={stormy} />
        {/* ground */}
        <path d="M 0 900 Q 540 860 1080 900 L 1080 1920 L 0 1920 Z" fill="#c9e3a8" style={{ filter: "url(#sketchy)" }} />
        <line x1={0} y1={900} x2={1080} y2={900} stroke={INK} strokeWidth={6} style={{ filter: "url(#sketchy)" }} />

        {scene1 && (
          <>
            <RainScene opacity={1} />
            <Bench opacity={1} />
            <Boy x={420} y={680} scale={1.35} talking happy={false} />
          </>
        )}

        {scene2 && (
          <>
            <RainScene opacity={interpolate(frame, [95, 150, 205], [0.9, 0.5, 0], { extrapolateRight: "clamp" })} />
            <Bench opacity={0.9} />
            <Boy x={330} y={720} scale={1.15} talking happy={false} />
            <Dog x={620} y={830} scale={1.1} wag={false} shivering />
          </>
        )}

        {scene3 && (
          <>
            <Boy x={400} y={760} scale={1.3} talking={false} happy />
            <Dog x={660} y={830} scale={1.3} wag shivering={false} />
            <Heart frame0={225} x={530} y={560} />
          </>
        )}
      </svg>
      <Audio src={staticFile("doodle_voice.wav")} volume={1} />
    </AbsoluteFill>
  );
};
