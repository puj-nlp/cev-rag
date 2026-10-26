import React, { useRef } from 'react';
import { useFrame } from '@react-three/fiber';

import { COLORS, NODES } from '../content';
import NodeLabel from './NodeLabel';
import useHoverCursor from './useHoverCursor';

/** Language model that writes the cited answer from the retrieved fragments. */
const LLMNode = ({ anim, active, label, onSelect }) => {
  const core = useRef();
  const ringA = useRef();
  const ringB = useRef();
  const { hovered, bind } = useHoverCursor();

  useFrame(() => {
    const { time } = anim.current;
    const pulse = active ? 1 + Math.sin(time * 5) * 0.08 : 1;
    if (core.current) core.current.scale.setScalar(pulse);
    if (ringA.current) ringA.current.rotation.set(time * 0.7, time * 0.4, 0);
    if (ringB.current) ringB.current.rotation.set(-time * 0.5, 0, time * 0.6);
  });

  return (
    <group position={NODES.llm.position}>
      <group onClick={onSelect} {...bind} scale={hovered ? 1.08 : 1}>
        <mesh ref={core}>
          <sphereGeometry args={[0.85, 32, 32]} />
          <meshStandardMaterial
            color={COLORS.navy}
            emissive={COLORS.gold}
            emissiveIntensity={active ? 0.6 : 0.15}
            metalness={0.4}
            roughness={0.3}
          />
        </mesh>
        <mesh ref={ringA}>
          <torusGeometry args={[1.25, 0.03, 8, 64]} />
          <meshBasicMaterial color={COLORS.gold} transparent opacity={0.7} />
        </mesh>
        <mesh ref={ringB}>
          <torusGeometry args={[1.45, 0.02, 8, 64]} />
          <meshBasicMaterial color={COLORS.sky} transparent opacity={0.5} />
        </mesh>
      </group>
      <NodeLabel text={label} active={active} onSelect={onSelect} offset={[0, -1.9, 0]} />
    </group>
  );
};

export default LLMNode;
