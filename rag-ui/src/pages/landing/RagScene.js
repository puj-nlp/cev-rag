import React, { useState } from 'react';
import { TOUCH } from 'three';
import { Canvas, useFrame } from '@react-three/fiber';
import { AdaptiveDpr, OrbitControls, PerformanceMonitor } from '@react-three/drei';

import { COLORS, NODES, STAGES, STAGE_DURATION, nodeForStage } from './content';
import DocumentsCluster from './scene/DocumentsCluster';
import EmbeddingModule from './scene/EmbeddingModule';
import VectorStore from './scene/VectorStore';
import QueryNode from './scene/QueryNode';
import LLMNode from './scene/LLMNode';
import Flow from './scene/Flow';
import ResponsiveCamera from './scene/ResponsiveCamera';
import { DEFAULT_CAMERA, maxDistanceFor } from './scene/cameraFit';
import useViewport from '../../hooks/useViewport';

const QUALITY = {
  high: { dpr: [1, 2], points: 1600, particles: 14, antialias: true, lite: false },
  low: { dpr: [0.75, 1.25], points: 600, particles: 7, antialias: false, lite: false },
  // Phones: lower density and simplified geometry (fewer segments, fewer document pages)
  mobile: { dpr: [0.75, 1], points: 300, particles: 4, antialias: false, lite: true },
};

// PerformanceMonitor only steps down; "mobile" is already the lightest preset
const lower = (quality) => (quality === 'high' ? 'low' : quality);

/** Advances the animation clock while playing and moves through the pipeline stages. */
const Director = ({ anim, playing, onStageChange, onQueryDone }) => {
  useFrame((_, delta) => {
    if (!playing) return;
    const state = anim.current;
    const step = Math.min(delta, 0.1); // avoid jumps after a stalled frame
    state.time += step;
    state.stageTime += step;
    if (state.stageTime < STAGE_DURATION) return;

    if (state.mode === 'query' && STAGES[state.stage] === 'generate') {
      state.stageTime = STAGE_DURATION;
      onQueryDone();
      return;
    }
    state.stage = (state.stage + 1) % STAGES.length;
    state.stageTime = 0;
    onStageChange(state.stage);
  });
  return null;
};

/**
 * Interactive 3D view of the cev-rag pipeline.
 * Resolution and particle counts adapt to the device through PerformanceMonitor.
 */
const RagScene = ({
  anim,
  stage,
  playing,
  visible,
  initialQuality,
  labels,
  selectedNode,
  controlsRef,
  onSelectNode,
  onStageChange,
  onQueryDone,
  onContextLost,
  ariaLabel,
}) => {
  const [quality, setQuality] = useState(initialQuality);
  const [dpr, setDpr] = useState(QUALITY[initialQuality].dpr[1]);
  const [fitDistance, setFitDistance] = useState(14);
  const { isMobile, isTouch } = useViewport();
  const settings = QUALITY[quality];
  const focus = selectedNode || nodeForStage(STAGES[stage]);
  const flowCount = settings.particles;

  const props = (id) => ({
    anim,
    active: focus === id,
    label: labels[id],
    lite: settings.lite,
    compact: isMobile,
    onSelect: () => onSelectNode(id),
  });

  return (
    <Canvas
      role="img"
      aria-label={ariaLabel}
      dpr={dpr}
      // Render continuously only while the animation plays on screen; otherwise only on interaction
      frameloop={playing && visible ? 'always' : 'demand'}
      camera={{ position: DEFAULT_CAMERA, fov: 45 }}
      gl={{ antialias: settings.antialias, powerPreference: 'high-performance' }}
      onCreated={({ gl }) => {
        gl.domElement.addEventListener('webglcontextlost', (event) => {
          event.preventDefault();
          onContextLost();
        });
      }}
      onPointerMissed={() => onSelectNode(null)}
    >
      <PerformanceMonitor
        flipflops={3}
        onDecline={() => {
          setDpr((value) => Math.max(settings.dpr[0], value - 0.25));
          setQuality(lower);
        }}
        onIncline={() => setDpr((value) => Math.min(QUALITY[quality].dpr[1], value + 0.25))}
        onFallback={() => {
          const next = lower(quality);
          setQuality(next);
          setDpr(QUALITY[next].dpr[0]);
        }}
      />
      <AdaptiveDpr pixelated />
      <ResponsiveCamera onFit={setFitDistance} />

      <color attach="background" args={[COLORS.background]} />
      <fog attach="fog" args={[COLORS.background, 18, 34]} />
      <ambientLight intensity={0.5} />
      <directionalLight position={[5, 8, 6]} intensity={1.1} />
      <pointLight position={[-6, 4, 4]} intensity={20} color={COLORS.sky} />

      <Director anim={anim} playing={playing} onStageChange={onStageChange} onQueryDone={onQueryDone} />

      <DocumentsCluster {...props('documents')} />
      <EmbeddingModule {...props('embedding')} />
      <VectorStore {...props('vectorStore')} pointCount={settings.points} />
      <QueryNode {...props('query')} />
      <LLMNode {...props('llm')} />

      {/* Ingestion: documents -> chunks -> embeddings -> Milvus */}
      <Flow anim={anim} from={NODES.documents.position} to={NODES.embedding.position} stages={['chunk']} color={COLORS.sky} count={flowCount} lite={settings.lite} />
      <Flow anim={anim} from={NODES.embedding.position} to={NODES.vectorStore.position} stages={['embed', 'store']} color={COLORS.gold} count={flowCount} lite={settings.lite} />
      {/* Query: question -> embedding -> similarity search -> LLM */}
      <Flow anim={anim} from={NODES.query.position} to={NODES.embedding.position} stages={['query']} color={COLORS.white} count={Math.ceil(flowCount / 3)} lift={0.2} size={0.14} lite={settings.lite} />
      <Flow anim={anim} from={NODES.embedding.position} to={NODES.vectorStore.position} stages={['retrieve']} color={COLORS.white} count={Math.ceil(flowCount / 3)} lift={-1} size={0.14} lite={settings.lite} />
      <Flow anim={anim} from={NODES.vectorStore.position} to={NODES.llm.position} stages={['retrieve', 'generate']} color={COLORS.gold} count={flowCount} lite={settings.lite} />

      <OrbitControls
        ref={controlsRef}
        makeDefault
        enablePan={false}
        enableDamping
        // Touch: one finger swipes to rotate, two fingers pinch to zoom
        touches={{ ONE: TOUCH.ROTATE, TWO: TOUCH.DOLLY_ROTATE }}
        rotateSpeed={isTouch ? 0.6 : 1}
        zoomSpeed={isTouch ? 0.8 : 1}
        minDistance={7}
        maxDistance={maxDistanceFor(fitDistance)}
        minPolarAngle={Math.PI * 0.15}
        maxPolarAngle={Math.PI * 0.7}
      />
    </Canvas>
  );
};

export default RagScene;
