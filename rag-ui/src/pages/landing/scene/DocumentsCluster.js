import React, { useMemo, useRef } from 'react';
import { useFrame } from '@react-three/fiber';

import { NODES, STAGES } from '../content';
import NodeLabel from './NodeLabel';
import useHoverCursor from './useHoverCursor';

// Reports, testimonies and supporting documents
const PAGE_COLORS = ['#60a5fa', '#fcd116', '#cbd5e1'];
const PAGES_PER_STACK = 6;
const PAGES_PER_STACK_LITE = 3;
const STACK_HEIGHT = 0.96;

/** Stacks of pages representing the Truth Commission archive; they fan out while being chunked. */
const DocumentsCluster = ({ anim, active, label, onSelect, lite, compact }) => {
  const pagesPerStack = lite ? PAGES_PER_STACK_LITE : PAGES_PER_STACK;
  const group = useRef();
  const pages = useRef([]);
  const { hovered, bind } = useHoverCursor();

  const layout = useMemo(
    () =>
      PAGE_COLORS.flatMap((color, stack) =>
        Array.from({ length: pagesPerStack }, (_, level) => ({
          color,
          x: (stack - 1) * 1.05,
          y: level * (STACK_HEIGHT / pagesPerStack) - 0.5,
          tilt: (Math.sin(stack * 7 + level * 3) * 0.12),
        }))
      ),
    [pagesPerStack]
  );

  useFrame(() => {
    const { time, stage, stageTime } = anim.current;
    const chunking = STAGES[stage] === 'chunk';
    const spread = chunking ? Math.sin(Math.min(stageTime / 1.2, 1) * Math.PI * 0.5) * 0.22 : 0;
    if (group.current) {
      group.current.position.y = NODES.documents.position[1] + Math.sin(time * 0.8) * 0.08;
    }
    pages.current.forEach((page, i) => {
      if (!page) return;
      const { y, tilt } = layout[i];
      const level = i % pagesPerStack;
      page.position.y = y + level * spread;
      page.rotation.z = tilt + (chunking ? Math.sin(time * 4 + i) * 0.05 : 0);
    });
  });

  return (
    <group ref={group} position={NODES.documents.position}>
      <group onClick={onSelect} {...bind} scale={hovered ? 1.06 : 1}>
        {layout.map((page, i) => (
          <mesh key={i} ref={(el) => (pages.current[i] = el)} position={[page.x, page.y, 0]}>
            <boxGeometry args={[0.8, 0.06, 1.05]} />
            <meshStandardMaterial
              color={page.color}
              emissive={page.color}
              emissiveIntensity={active || hovered ? 0.55 : 0.15}
              roughness={0.6}
            />
          </mesh>
        ))}
      </group>
      <NodeLabel text={label} active={active} compact={compact} onSelect={onSelect} />
    </group>
  );
};

export default DocumentsCluster;
