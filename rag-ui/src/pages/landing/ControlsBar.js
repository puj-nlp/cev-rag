import React from 'react';
import { Box, IconButton, Tooltip, ToggleButton, ToggleButtonGroup } from '@mui/material';
import {
  PlayArrow as PlayIcon,
  Pause as PauseIcon,
  SkipPrevious as PrevIcon,
  SkipNext as NextIcon,
  CenterFocusStrong as ResetIcon,
} from '@mui/icons-material';
import { useTranslation } from 'react-i18next';

import { STAGES } from './content';

/** Playback controls plus a keyboard-accessible list of stages that mirrors the 3D scene. */
const ControlsBar = ({ stage, playing, onTogglePlay, onStep, onGoToStage, onResetCamera }) => {
  const { t } = useTranslation();

  const iconButton = (label, onClick, icon) => (
    <Tooltip title={label}>
      <IconButton onClick={onClick} aria-label={label} sx={{ color: '#f8fafc' }}>
        {icon}
      </IconButton>
    </Tooltip>
  );

  return (
    <Box
      sx={{
        display: 'flex',
        flexWrap: 'wrap',
        alignItems: 'center',
        gap: 1,
        px: 1.5,
        py: 1,
        bgcolor: '#111a45',
        borderTop: '1px solid rgba(248, 250, 252, 0.12)',
      }}
    >
      <Box sx={{ display: 'flex' }}>
        {iconButton(t('landing.controls.prev'), () => onStep(-1), <PrevIcon />)}
        {iconButton(playing ? t('landing.controls.pause') : t('landing.controls.play'), onTogglePlay, playing ? <PauseIcon /> : <PlayIcon />)}
        {iconButton(t('landing.controls.next'), () => onStep(1), <NextIcon />)}
        {iconButton(t('landing.controls.resetCamera'), onResetCamera, <ResetIcon />)}
      </Box>
      <ToggleButtonGroup
        exclusive
        size="small"
        value={stage}
        onChange={(_e, value) => value !== null && onGoToStage(value)}
        aria-label={t('landing.controls.stages')}
        sx={{
          flexWrap: 'wrap',
          '& .MuiToggleButton-root': {
            color: 'rgba(248, 250, 252, 0.75)',
            borderColor: 'rgba(248, 250, 252, 0.2)',
            fontFamily: '"Inter", sans-serif',
            fontSize: 12,
            py: 0.4,
          },
          '& .Mui-selected': { color: '#0b1437 !important', bgcolor: '#fcd116 !important' },
        }}
      >
        {STAGES.map((name, index) => (
          <ToggleButton key={name} value={index}>
            {t(`landing.stages.${name}`)}
          </ToggleButton>
        ))}
      </ToggleButtonGroup>
    </Box>
  );
};

export default ControlsBar;
