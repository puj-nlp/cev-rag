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
      'Cinzel',
      'serif',
      'Georgia',
      'Times New Roman'
    ].join(','),
    h1: {
      fontFamily: 'Cinzel, serif',
      fontWeight: 700,
    },
    h2: {
      fontFamily: 'Cinzel, serif',
      fontWeight: 600,
    },
    h3: {
      fontFamily: 'Cinzel, serif',
      fontWeight: 600,
    },
    h4: {
      fontFamily: 'Cinzel, serif',
      fontWeight: 600,
    },
    h5: {
      fontFamily: 'Cinzel, serif',
      fontWeight: 500,
    },
    h6: {
      fontFamily: 'Cinzel, serif',
      fontWeight: 500,
    },
    body1: {
      fontFamily: 'Cinzel, serif',
      fontWeight: 400,
    },
    body2: {
      fontFamily: 'Cinzel, serif',
      fontWeight: 400,
    },
    button: {
      fontFamily: 'Cinzel, serif',
      fontWeight: 500,
    },
    caption: {
      fontFamily: 'Cinzel, serif',
      fontWeight: 400,
    },
    overline: {
      fontFamily: 'Cinzel, serif',
      fontWeight: 400,
    }
  },
  components: {
    MuiCssBaseline: {
      styleOverrides: {
        '@global': {
          '*': {
            fontFamily: 'Cinzel, serif !important',
          },
          body: {
            fontFamily: 'Cinzel, serif !important',
          },
        },
      },
    },
    MuiTypography: {
      styleOverrides: {
        root: {
          fontFamily: 'Cinzel, serif',
        },
      },
    },
    MuiButton: {
      styleOverrides: {
        root: {
          textTransform: 'none',
          borderRadius: 8,
          fontFamily: 'Cinzel, serif',
          fontWeight: 500,
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
            fontFamily: 'Cinzel, serif',
          },
          '& .MuiFormLabel-root': {
            fontFamily: 'Cinzel, serif',
          },
        },
      },
    },
    MuiMenuItem: {
      styleOverrides: {
        root: {
          fontFamily: 'Cinzel, serif',
        },
      },
    },
    MuiTab: {
      styleOverrides: {
        root: {
          fontFamily: 'Cinzel, serif',
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
