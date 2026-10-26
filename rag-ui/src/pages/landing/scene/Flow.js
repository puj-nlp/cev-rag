import React, { useMemo, useRef } from 'react';
import { useFrame } from '@react-three/fiber';
import { QuadraticBezierLine } from '@react-three/drei';
import { Object3D, QuadraticBezierCurve3, Vector3 } from 'three';

import { STAGES } from '../content';

/** Curved connection between two components; particles travel along it during its stages. */
const Flow = ({ anim, from, to, stages, color, count, lift = 1.2, speed = 0.45, size = 0.11 }) => {
  const particles = useRef();
  const dummy = useMemo(() => new Object3D(), []);

  const { curve, mid } = useMemo(() => {
    const start = new Vector3(...from);
    const end = new Vector3(...to);
    const middle = start.clone().lerp(end, 0.5).add(new Vector3(0, lift, 0));
    return { curve: new QuadraticBezierCurve3(start, middle, end), mid: middle.toArray() };
  }, [from, to, lift]);

  useFrame(() => {
    const mesh = particles.current;
    if (!mesh) return;
    const { stage, stageTime } = anim.current;
    const running = stages.includes(STAGES[stage]);
    mesh.visible = running;
    if (!running) return;

    for (let i = 0; i < count; i += 1) {
      const t = (stageTime * speed + i / count) % 1;
      curve.getPoint(t, dummy.position);
      dummy.scale.setScalar(size * (0.35 + Math.sin(t * Math.PI)));
      dummy.updateMatrix();
      mesh.setMatrixAt(i, dummy.matrix);
    }
    mesh.instanceMatrix.needsUpdate = true;
  });

  return (
    <group>
      <QuadraticBezierLine start={from} end={to} mid={mid} color={color} lineWidth={1} transparent opacity={0.25} />
      <instancedMesh ref={particles} args={[null, null, count]} visible={false}>
        <sphereGeometry args={[1, 10, 10]} />
        <meshBasicMaterial color={color} toneMapped={false} />
      </instancedMesh>
    </group>
  );
};

export default Flow;
