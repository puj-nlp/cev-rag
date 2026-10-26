import React from 'react';
import { Html } from '@react-three/drei';

/** DOM label anchored to a 3D node; also a keyboard-accessible button that opens its panel. */
const NodeLabel = ({ text, offset = [0, -1.6, 0], active, onSelect }) => (
  <Html position={offset} center zIndexRange={[10, 0]}>
    <button
      type="button"
      onClick={onSelect}
      style={{
        whiteSpace: 'nowrap',
        padding: '4px 10px',
        borderRadius: 999,
        border: `1px solid ${active ? '#fcd116' : 'rgba(248, 250, 252, 0.35)'}`,
        background: active ? 'rgba(252, 209, 22, 0.18)' : 'rgba(11, 20, 55, 0.75)',
        color: '#f8fafc',
        font: '600 13px "Inter", sans-serif',
        cursor: 'pointer',
        transition: 'all 0.3s ease',
      }}
    >
      {text}
    </button>
  </Html>
);

export default NodeLabel;
