import React from 'react';
import { Alert } from '@mui/material';
import { maintenanceMode, maintenanceMessage } from '../config';

const MaintenanceBanner = () => {
  if (maintenanceMode !== 'banner') return null;

  return (
    <Alert
      severity="warning"
      sx={{ borderRadius: 0, justifyContent: 'center', position: 'sticky', top: 0, zIndex: 10 }}
    >
      {maintenanceMessage}
    </Alert>
  );
};

export default MaintenanceBanner;
