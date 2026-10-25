// Runtime config (window.__APP_CONFIG__, see public/config.js) takes precedence
// over build-time REACT_APP_* variables.
const runtime = window.__APP_CONFIG__ || {};

export const maintenanceMode = (
  runtime.MAINTENANCE_MODE || process.env.REACT_APP_MAINTENANCE_MODE || 'off'
).toLowerCase();

export const maintenanceMessage =
  runtime.MAINTENANCE_MESSAGE ||
  process.env.REACT_APP_MAINTENANCE_MESSAGE ||
  'Estamos realizando tareas de mantenimiento. Algunas funciones podrían no estar disponibles.';
