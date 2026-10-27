import React, { Suspense, lazy } from 'react';
import { Routes, Route, Navigate, useParams } from 'react-router-dom';
import { Box, CircularProgress } from '@mui/material';

import Header from './components/Header';
import Footer from './components/Footer';
import LocaleLayout from './components/LocaleLayout';
import UnifiedChatInterface from './pages/UnifiedChatInterface';
import About from './pages/About';
import HomePage from './pages/HomePage';
import { detectLanguage } from './i18n/detectLanguage';

// The 3D landing (three.js) is code-split so the chat bundle does not download it
const LandingPage = lazy(() => import('./pages/landing/LandingPage'));

const LegacyChatRedirect = () => {
  const { lang, chatId } = useParams();
  return <Navigate to={`/${lang}/chat/${chatId}`} replace />;
};

const PageFallback = () => (
  <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '60vh' }}>
    <CircularProgress />
  </Box>
);

function App() {
  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
      <Header />
      <Box component="main" sx={{ flexGrow: 1 }}>
        <Suspense fallback={<PageFallback />}>
          <Routes>
            {/* nginx redirects "/" by language in production; this covers local development */}
            <Route path="/" element={<Navigate to={`/${detectLanguage()}/`} replace />} />
            <Route path="/:lang" element={<LocaleLayout />}>
              <Route index element={<HomePage />} />
              <Route path="como-funciona" element={<LandingPage />} />
              <Route path="chat" element={<UnifiedChatInterface />} />
              <Route path="chat/:chatId" element={<UnifiedChatInterface />} />
              <Route path="chats/:chatId" element={<LegacyChatRedirect />} />
              <Route path="about" element={<About />} />
              <Route path="*" element={<Navigate to="." replace />} />
            </Route>
          </Routes>
        </Suspense>
      </Box>
      <Footer />
    </Box>
  );
}

export default App;
