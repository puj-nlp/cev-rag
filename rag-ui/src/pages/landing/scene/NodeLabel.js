import React from 'react';
import { Html } from '@react-three/drei';

/** DOM label anchored to a 3D node; also a keyboard-accessible button that opens its panel. */
const NodeLabel = ({ text, offset = [0, -1.6, 0], active, compact = false, onSelect }) => (
  <Html position={offset} center zIndexRange={[10, 0]}>
    <button
      type="button"
      onClick={onSelect}
      style={{
        whiteSpace: 'nowrap',
        padding: compact ? '0.2rem 0.5rem' : '0.25rem 0.625rem',
        borderRadius: 999,
        border: `1px solid ${active ? '#fcd116' : 'rgba(248, 250, 252, 0.35)'}`,
        background: active ? 'rgba(252, 209, 22, 0.18)' : 'rgba(11, 20, 55, 0.75)',
        color: '#f8fafc',
        font: `600 ${compact ? '0.6875rem' : '0.8125rem'} "Inter", sans-serif`,
        cursor: 'pointer',
        transition: 'all 0.3s ease',
      }}
    >
      {text}
    </button>
  </Html>
);

export default NodeLabel;
