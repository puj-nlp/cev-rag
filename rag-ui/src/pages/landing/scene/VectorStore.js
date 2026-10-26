import React, { useMemo, useRef } from 'react';
import { useFrame } from '@react-three/fiber';

import { COLORS, NODES, STAGES, STAGE_DURATION } from '../content';
import NodeLabel from './NodeLabel';
import useHoverCursor from './useHoverCursor';

const RADIUS = 1.5;
const HEIGHT = 2.8;
const TOP_K = 5;

/** Milvus collection: a cloud of vectors inside a cylinder; the top-k neighbours light up on retrieval. */
const VectorStore = ({ anim, active, label, onSelect, pointCount }) => {
  const cloud = useRef();
  const geometry = useRef();
  const hits = useRef([]);
  const { hovered, bind } = useHoverCursor();

  const { positions, nearest } = useMemo(() => {
    const array = new Float32Array(pointCount * 3);
    for (let i = 0; i < pointCount; i += 1) {
      const r = RADIUS * Math.sqrt(Math.random()) * 0.92;
      const angle = Math.random() * Math.PI * 2;
      array[i * 3] = Math.cos(angle) * r;
      array[i * 3 + 1] = (Math.random() - 0.5) * HEIGHT * 0.92;
      array[i * 3 + 2] = Math.sin(angle) * r;
    }
    // The "query vector" lands near this point; its closest neighbours are the retrieved fragments
    const target = [0.5, 0.4, 0.3];
    const distance = (i) =>
      (array[i * 3] - target[0]) ** 2 + (array[i * 3 + 1] - target[1]) ** 2 + (array[i * 3 + 2] - target[2]) ** 2;
    const order = Array.from({ length: pointCount }, (_, i) => i).sort((a, b) => distance(a) - distance(b));
    const closest = order.slice(0, TOP_K).map((i) => [array[i * 3], array[i * 3 + 1], array[i * 3 + 2]]);
    return { positions: array, nearest: closest };
  }, [pointCount]);

  useFrame(() => {
    const { time, stage, stageTime } = anim.current;
    const name = STAGES[stage];
    const storeIndex = STAGES.indexOf('store');

    // Before ingestion the collection is empty; during "store" it fills up
    let visible = pointCount;
    if (stage < storeIndex) visible = 0;
    else if (stage === storeIndex) visible = Math.floor((stageTime / STAGE_DURATION) * pointCount);
    if (geometry.current) geometry.current.setDrawRange(0, visible);

    if (cloud.current) cloud.current.rotation.y = time * 0.08;

    const retrieving = name === 'retrieve' || name === 'generate';
    hits.current.forEach((hit, i) => {
      if (!hit) return;
      hit.visible = retrieving;
      if (retrieving) hit.scale.setScalar(1 + Math.sin(time * 6 + i) * 0.3);
    });
  });

  return (
    <group position={NODES.vectorStore.position}>
      <group onClick={onSelect} {...bind}>
        <mesh>
          <cylinderGeometry args={[RADIUS, RADIUS, HEIGHT, 40, 1, true]} />
          <meshStandardMaterial
            color={COLORS.navy}
            emissive={COLORS.sky}
            emissiveIntensity={active || hovered ? 0.35 : 0.1}
            transparent
            opacity={0.28}
            depthWrite={false}
            side={2}
          />
        </mesh>
        <group ref={cloud}>
          <points>
            <bufferGeometry ref={geometry}>
              <bufferAttribute attach="attributes-position" count={pointCount} array={positions} itemSize={3} />
            </bufferGeometry>
            <pointsMaterial color={COLORS.sky} size={0.06} sizeAttenuation transparent opacity={0.85} depthWrite={false} />
          </points>
          {nearest.map((position, i) => (
            <mesh key={i} ref={(el) => (hits.current[i] = el)} position={position} visible={false}>
              <sphereGeometry args={[0.09, 12, 12]} />
              <meshBasicMaterial color={COLORS.gold} toneMapped={false} />
            </mesh>
          ))}
        </group>
      </group>
      <NodeLabel text={label} active={active} onSelect={onSelect} offset={[0, -2.1, 0]} />
    </group>
  );
};

export default VectorStore;
