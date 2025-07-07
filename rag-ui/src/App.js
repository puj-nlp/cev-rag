import React from 'react';
import { Routes, Route } from 'react-router-dom';
import { Box } from '@mui/material';

import Header from './components/Header';
import UnifiedChatInterface from './pages/UnifiedChatInterface';
import About from './pages/About';

function App() {
  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
      <Header />
      <Box component="main" sx={{ flexGrow: 1 }}>
        <Routes>
          <Route path="/" element={<UnifiedChatInterface />} />
          <Route path="/chats/:chatId" element={<UnifiedChatInterface />} />
          <Route path="/about" element={<About />} />
        </Routes>
      </Box>
    </Box>
  );
}

export default App;
