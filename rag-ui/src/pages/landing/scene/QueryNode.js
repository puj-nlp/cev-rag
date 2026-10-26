import React, { useRef } from 'react';
import { useFrame } from '@react-three/fiber';

import { COLORS, NODES } from '../content';
import NodeLabel from './NodeLabel';
import useHoverCursor from './useHoverCursor';

/** The user's prompt entering the system. */
const QueryNode = ({ anim, active, label, onSelect }) => {
  const mesh = useRef();
  const { hovered, bind } = useHoverCursor();

  useFrame(() => {
    const { time } = anim.current;
    if (!mesh.current) return;
    mesh.current.rotation.y = time * 0.9;
    mesh.current.position.y = Math.sin(time * 1.5) * 0.12;
  });

  return (
    <group position={NODES.query.position}>
      <mesh ref={mesh} onClick={onSelect} {...bind} scale={hovered ? 1.15 : 1}>
        <octahedronGeometry args={[0.45, 0]} />
        <meshStandardMaterial
          color={COLORS.white}
          emissive={COLORS.white}
          emissiveIntensity={active ? 0.8 : 0.2}
          flatShading
        />
      </mesh>
      <NodeLabel text={label} active={active} onSelect={onSelect} offset={[0, 0.9, 0]} />
    </group>
  );
};

export default QueryNode;
