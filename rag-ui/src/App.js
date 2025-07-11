import React from 'react';
import { Routes, Route } from 'react-router-dom';
import { Box } from '@mui/material';

import Header from './components/Header';
import Footer from './components/Footer';
import UnifiedChatInterface from './pages/UnifiedChatInterface';
import About from './pages/About';

function App() {
  return (
    <Box sx={{ minHeight: '100vh', position: 'relative' }}>
      <Header />
      <Box component="main" sx={{ pt: '64px', pb: '56px' }}>
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
