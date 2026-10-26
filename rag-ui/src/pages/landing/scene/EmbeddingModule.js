import React, { useRef } from 'react';
import { useFrame } from '@react-three/fiber';

import { COLORS, NODES } from '../content';
import NodeLabel from './NodeLabel';
import useHoverCursor from './useHoverCursor';

/** Transformer block: text fragments go in, high-dimensional vectors come out. */
const EmbeddingModule = ({ anim, active, label, onSelect }) => {
  const shell = useRef();
  const core = useRef();
  const { hovered, bind } = useHoverCursor();

  useFrame(() => {
    const { time } = anim.current;
    const speed = active ? 2.4 : 0.35;
    if (shell.current) {
      shell.current.rotation.y = time * speed * 0.6;
      shell.current.rotation.x = time * speed * 0.25;
    }
    if (core.current) {
      core.current.rotation.y = -time * speed;
      core.current.scale.setScalar(active ? 1 + Math.sin(time * 8) * 0.08 : 1);
    }
  });

  return (
    <group position={NODES.embedding.position}>
      <group onClick={onSelect} {...bind} scale={hovered ? 1.08 : 1}>
        <mesh ref={shell}>
          <icosahedronGeometry args={[1.1, 1]} />
          <meshBasicMaterial color={COLORS.gold} wireframe transparent opacity={active || hovered ? 0.9 : 0.45} />
        </mesh>
        <mesh ref={core}>
          <boxGeometry args={[0.7, 0.7, 0.7]} />
          <meshStandardMaterial
            color={COLORS.ochre}
            emissive={COLORS.gold}
            emissiveIntensity={active ? 0.9 : 0.25}
            metalness={0.3}
            roughness={0.35}
          />
        </mesh>
      </group>
      <NodeLabel text={label} active={active} onSelect={onSelect} />
    </group>
  );
};

export default EmbeddingModule;
