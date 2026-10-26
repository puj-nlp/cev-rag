import React, { useMemo } from 'react';
import { Box, Typography } from '@mui/material';
import { useTranslation } from 'react-i18next';

import { COLORS, STAGES } from './content';

// 2D layout of the same pipeline drawn by the 3D scene
const BOXES = {
  documents: { x: 20, y: 160, w: 150 },
  embedding: { x: 235, y: 160, w: 150 },
  vectorStore: { x: 450, y: 160, w: 190 },
  llm: { x: 705, y: 160, w: 150 },
  query: { x: 235, y: 20, w: 150 },
};
const BOX_HEIGHT = 64;
const center = (id) => ({ x: BOXES[id].x + BOXES[id].w / 2, y: BOXES[id].y + BOX_HEIGHT / 2 });

const LINKS = [
  { from: 'documents', to: 'embedding', color: COLORS.sky },
  { from: 'embedding', to: 'vectorStore', color: COLORS.gold },
  { from: 'vectorStore', to: 'llm', color: COLORS.gold },
  { from: 'query', to: 'embedding', color: COLORS.white },
];

const edgePath = ({ from, to }) => {
  const a = center(from);
  const b = center(to);
  if (from === 'query') return `M ${a.x} ${a.y + BOX_HEIGHT / 2} L ${b.x} ${b.y - BOX_HEIGHT / 2}`;
  return `M ${BOXES[from].x + BOXES[from].w} ${a.y} L ${BOXES[to].x} ${b.y}`;
};

/**
 * Lightweight version of the landing infographic for devices without WebGL,
 * weak hardware or reduced-motion preferences: inline SVG, translatable and accessible.
 */
const FallbackInfographic = ({ onSelectNode, showNote = true }) => {
  const { t } = useTranslation();
  const animate = useMemo(
    () => !(typeof window.matchMedia === 'function' && window.matchMedia('(prefers-reduced-motion: reduce)').matches),
    []
  );

  const activate = (id) => (event) => {
    if (event.type === 'click' || event.key === 'Enter' || event.key === ' ') {
      event.preventDefault();
      onSelectNode(id);
    }
  };

  return (
    <Box sx={{ bgcolor: COLORS.background, p: { xs: 2, md: 3 } }}>
      <Typography variant="h6" component="h2" sx={{ color: COLORS.white, mb: 1 }}>
        {t('landing.fallback.title')}
      </Typography>
      <Box
        component="svg"
        viewBox="0 0 875 250"
        role="group"
        aria-label={t('landing.canvasLabel')}
        sx={{ width: '100%', height: 'auto', display: 'block' }}
      >
        <defs>
          <marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
            <path d="M 0 0 L 10 5 L 0 10 z" fill="rgba(248,250,252,0.6)" />
          </marker>
        </defs>

        {LINKS.map((link) => {
          const d = edgePath(link);
          return (
            <g key={`${link.from}-${link.to}`}>
              <path d={d} stroke="rgba(248,250,252,0.35)" strokeWidth="2" fill="none" markerEnd="url(#arrow)" />
              {animate &&
                [0, 0.33, 0.66].map((offset) => (
                  <circle key={offset} r="5" fill={link.color}>
                    <animateMotion dur="2.4s" begin={`${offset * 2.4}s`} repeatCount="indefinite" path={d} />
                  </circle>
                ))}
            </g>
          );
        })}

        {Object.entries(BOXES).map(([id, box]) => (
          <g
            key={id}
            role="button"
            tabIndex={0}
            aria-label={t(`landing.nodes.${id}.title`)}
            onClick={activate(id)}
            onKeyDown={activate(id)}
            style={{ cursor: 'pointer' }}
          >
            <rect
              x={box.x}
              y={box.y}
              width={box.w}
              height={BOX_HEIGHT}
              rx="12"
              fill="#111a45"
              stroke={id === 'embedding' || id === 'llm' ? COLORS.gold : COLORS.sky}
              strokeWidth="2"
            />
            <text
              x={box.x + box.w / 2}
              y={box.y + BOX_HEIGHT / 2 + 5}
              textAnchor="middle"
              fill={COLORS.white}
              style={{ font: '600 15px "Inter", sans-serif' }}
            >
              {t(`landing.short.${id}`)}
            </text>
          </g>
        ))}
      </Box>

      <Box component="ol" sx={{ color: 'rgba(248,250,252,0.85)', pl: 2.5, mt: 2, mb: 0, columns: { md: 2 }, columnGap: 4 }}>
        {STAGES.map((stage) => (
          <Typography component="li" variant="body2" key={stage} sx={{ mb: 1, breakInside: 'avoid', fontFamily: '"Inter", sans-serif' }}>
            <strong>{t(`landing.stages.${stage}`).replace(/^\d+\.\s*/, '')}:</strong> {t(`landing.stageHints.${stage}`)}
          </Typography>
        ))}
      </Box>
      {showNote && (
        <Typography variant="caption" component="p" sx={{ color: 'rgba(248,250,252,0.6)', mt: 1 }}>
          {t('landing.fallback.note')}
        </Typography>
      )}
    </Box>
  );
};

export default FallbackInfographic;
