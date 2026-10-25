import React from 'react';
import { Box, Typography } from '@mui/material';
import { Build as BuildIcon } from '@mui/icons-material';
import { maintenanceMessage } from '../config';

const Maintenance = () => (
  <Box
    sx={{
      height: '100%',
      display: 'flex',
      flexDirection: 'column',
      justifyContent: 'center',
      alignItems: 'center',
      textAlign: 'center',
      px: { xs: 2.5, md: 5 },
      py: { xs: 2.5, md: 7.5 }
    }}
  >
    <BuildIcon sx={{ fontSize: 64, color: '#FCD116', mb: 3 }} />
    <Typography
      sx={{
        fontFamily: '"Cinzel", serif !important',
        fontWeight: 700,
        fontSize: { xs: '2rem', md: '2.5rem' },
        color: '#1e3a8a',
        lineHeight: 1.2,
        mb: 2.5
      }}
    >
      En mantenimiento
    </Typography>
    <Typography sx={{ color: '#475569', fontSize: { xs: '1rem', md: '1.1rem' }, lineHeight: 1.6, maxWidth: 500 }}>
      {maintenanceMessage}
    </Typography>
  </Box>
);

export default Maintenance;
