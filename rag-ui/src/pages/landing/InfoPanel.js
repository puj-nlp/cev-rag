import React from 'react';
import { Box, Chip, Drawer, IconButton, Link, Typography, useMediaQuery } from '@mui/material';
import { Close as CloseIcon, Code as CodeIcon } from '@mui/icons-material';
import { useTranslation } from 'react-i18next';

import { NODES, repoFileUrl } from './content';

/** Explanatory panel for the clicked component, with links to the code that implements it. */
const InfoPanel = ({ nodeId, onClose }) => {
  const { t } = useTranslation();
  const isMobile = useMediaQuery('(max-width:900px)');
  const node = nodeId ? NODES[nodeId] : null;

  return (
    <Drawer
      anchor={isMobile ? 'bottom' : 'right'}
      open={Boolean(node)}
      onClose={onClose}
      PaperProps={{ sx: { width: isMobile ? '100%' : 400, maxHeight: isMobile ? '70vh' : '100%', p: 3 } }}
    >
      {node && (
        <Box role="region" aria-labelledby="info-panel-title">
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', gap: 2 }}>
            <Typography id="info-panel-title" variant="h5" component="h2" sx={{ color: '#1e3a8a' }}>
              {t(`landing.nodes.${nodeId}.title`)}
            </Typography>
            <IconButton onClick={onClose} aria-label={t('landing.panel.close')}>
              <CloseIcon />
            </IconButton>
          </Box>
          <Typography variant="body1" sx={{ mt: 2, lineHeight: 1.7 }}>
            {t(`landing.nodes.${nodeId}.body`)}
          </Typography>
          <Typography variant="overline" component="p" sx={{ mt: 3, color: 'text.secondary' }}>
            {t('landing.panel.tech')}
          </Typography>
          <Chip label={t(`landing.nodes.${nodeId}.tech`)} sx={{ bgcolor: '#fef3c7', fontFamily: '"Inter", sans-serif' }} />
          <Typography variant="overline" component="p" sx={{ mt: 3, color: 'text.secondary' }}>
            {t('landing.panel.inRepo')}
          </Typography>
          <Box component="ul" sx={{ pl: 0, m: 0, listStyle: 'none' }}>
            {node.files.map((file) => (
              <Box component="li" key={file} sx={{ mb: 1, display: 'flex', alignItems: 'center', gap: 1 }}>
                <CodeIcon fontSize="small" sx={{ color: '#917d26' }} />
                <Link
                  href={repoFileUrl(file)}
                  target="_blank"
                  rel="noopener noreferrer"
                  sx={{ fontFamily: 'monospace !important', fontSize: 13, wordBreak: 'break-all' }}
                >
                  {file}
                </Link>
              </Box>
            ))}
          </Box>
        </Box>
      )}
    </Drawer>
  );
};

export default InfoPanel;
