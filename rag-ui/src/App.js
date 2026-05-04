import React from 'react';
import { Routes, Route } from 'react-router-dom';
import { Box } from '@mui/material';

import Header from './components/Header';
import Footer from './components/Footer';
import UnifiedChatInterface from './pages/UnifiedChatInterface';
import About from './pages/About';

function App() {
  return (
    <Box sx={{ height: '100dvh', overflow: 'hidden', display: 'flex', flexDirection: 'column' }}>
      <Header />
      <Box component="main" sx={{ flex: 1, overflow: 'auto', pt: '64px', pb: { xs: 0, md: '56px' } }}>
        <Routes>
          <Route path="/" element={<UnifiedChatInterface />} />
          <Route path="/chats/:chatId" element={<UnifiedChatInterface />} />
          <Route path="/about" element={<About />} />
        </Routes>
      </Box>
      <Footer />
    </Box>
  );
}

export default App;
