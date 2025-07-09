import React from 'react';
import ReactDOM from 'react-dom/client';
import { BrowserRouter } from 'react-router-dom';
import CssBaseline from '@mui/material/CssBaseline';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import App from './App';
import './index.css';

// Create a custom theme for Window to Truth
const theme = createTheme({
  palette: {
    primary: {
      main: '#111827', // Color oscuro para la barra superior
    },
    secondary: {
      main: '#1976d2', // Azul para botones y elementos secundarios
    },
    background: {
      default: '#ffffff',
      paper: '#f9fafb',
    },
    text: {
      primary: '#111827',
      secondary: '#6b7280',
    }
  },
  typography: {
    fontFamily: [
      'PT Serif',
      'serif',
      'Georgia',
      'Times New Roman'
    ].join(','),
    h1: {
      fontFamily: 'PT Serif, serif',
      fontWeight: 700,
    },
    h2: {
      fontFamily: 'PT Serif, serif',
      fontWeight: 700,
    },
    h3: {
      fontFamily: 'PT Serif, serif',
      fontWeight: 700,
    },
    h4: {
      fontFamily: 'PT Serif, serif',
      fontWeight: 700,
    },
    h5: {
      fontFamily: 'PT Serif, serif',
      fontWeight: 700,
    },
    h6: {
      fontFamily: 'PT Serif, serif',
      fontWeight: 700,
    },
    body1: {
      fontFamily: 'PT Serif, serif',
      fontWeight: 400,
    },
    body2: {
      fontFamily: 'PT Serif, serif',
      fontWeight: 400,
    },
    button: {
      fontFamily: 'PT Serif, serif',
      fontWeight: 700,
    },
    caption: {
      fontFamily: 'PT Serif, serif',
      fontWeight: 400,
    },
    overline: {
      fontFamily: 'PT Serif, serif',
      fontWeight: 400,
    }
  },
  components: {
    MuiCssBaseline: {
      styleOverrides: {
        '@global': {
          '*': {
            fontFamily: 'PT Serif, serif !important',
          },
          body: {
            fontFamily: 'PT Serif, serif !important',
          },
          'h1, h2, h3, h4, h5, h6': {
            fontFamily: 'PT Serif, serif !important',
            fontWeight: 700,
          },
        },
      },
    },
    MuiTypography: {
      styleOverrides: {
        root: {
          fontFamily: 'PT Serif, serif',
        },
      },
    },
    MuiButton: {
      styleOverrides: {
        root: {
          textTransform: 'none',
          borderRadius: 8,
          fontFamily: 'PT Serif, serif',
          fontWeight: 700,
        },
      },
    },
    MuiCard: {
      styleOverrides: {
        root: {
          borderRadius: 8,
        },
      },
    },
    MuiTextField: {
      styleOverrides: {
        root: {
          '& .MuiInputBase-input': {
            fontFamily: 'PT Serif, serif',
          },
          '& .MuiFormLabel-root': {
            fontFamily: 'PT Serif, serif',
          },
        },
      },
    },
    MuiMenuItem: {
      styleOverrides: {
        root: {
          fontFamily: 'PT Serif, serif',
        },
      },
    },
    MuiTab: {
      styleOverrides: {
        root: {
          fontFamily: 'PT Serif, serif',
          textTransform: 'none',
        },
      },
    },
  },
});

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <BrowserRouter>
      <ThemeProvider theme={theme}>
        <CssBaseline />
        <App />
      </ThemeProvider>
    </BrowserRouter>
  </React.StrictMode>
);
