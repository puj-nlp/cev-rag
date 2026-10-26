import React, { Suspense, lazy, useCallback, useEffect, useMemo, useRef, useState } from 'react';
import { Box, Button, CircularProgress, Container, Grid, Paper, Typography } from '@mui/material';
import { Link as RouterLink } from 'react-router-dom';
import { Helmet } from 'react-helmet-async';
import { useTranslation } from 'react-i18next';

import useLocalizedPath from '../../i18n/useLocalizedPath';
import { NODE_IDS, QUERY_STAGE_INDEX, STAGES } from './content';
import useDeviceTier from './useDeviceTier';
import ControlsBar from './ControlsBar';
import InfoPanel from './InfoPanel';
import QuerySimulator from './QuerySimulator';
import FallbackInfographic from './FallbackInfographic';
import SceneErrorBoundary from './SceneErrorBoundary';

const RagScene = lazy(() => import('./RagScene'));

/** Pauses rendering while the canvas is off screen or the tab is hidden. */
const useOnScreen = (ref) => {
  const [onScreen, setOnScreen] = useState(true);
  const [tabVisible, setTabVisible] = useState(() => document.visibilityState !== 'hidden');

  useEffect(() => {
    const onVisibility = () => setTabVisible(document.visibilityState !== 'hidden');
    document.addEventListener('visibilitychange', onVisibility);
    return () => document.removeEventListener('visibilitychange', onVisibility);
  }, []);

  useEffect(() => {
    if (!ref.current || typeof IntersectionObserver === 'undefined') return undefined;
    const observer = new IntersectionObserver(([entry]) => setOnScreen(entry.isIntersecting), { threshold: 0.05 });
    observer.observe(ref.current);
    return () => observer.disconnect();
  }, [ref]);

  return onScreen && tabVisible;
};

const SceneLoading = ({ label }) => (
  <Box sx={{ height: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 2, color: '#f8fafc' }}>
    <CircularProgress size={28} sx={{ color: '#fcd116' }} />
    <Typography variant="body2">{label}</Typography>
  </Box>
);

/**
 * Home page: interactive 3D infographic explaining how cev-rag works
 * (documents -> embeddings -> Milvus -> retrieval -> LLM answer).
 */
const LandingPage = () => {
  const { t } = useTranslation();
  const localizedPath = useLocalizedPath();
  const tier = useDeviceTier();
  const [mode, setMode] = useState(tier === 'fallback' ? 'fallback' : '3d');

  const anim = useRef({ time: 0, stage: 0, stageTime: 0, mode: 'tour' });
  const controlsRef = useRef();
  const sceneRef = useRef();
  const visible = useOnScreen(sceneRef);

  const [stage, setStage] = useState(0);
  const [playing, setPlaying] = useState(true);
  const [selectedNode, setSelectedNode] = useState(null);
  const [query, setQuery] = useState(null);

  const labels = useMemo(
    () => Object.fromEntries(NODE_IDS.map((id) => [id, t(`landing.short.${id}`)])),
    [t]
  );

  const goToStage = useCallback((index) => {
    const next = (index + STAGES.length) % STAGES.length;
    Object.assign(anim.current, { stage: next, stageTime: 0, mode: 'tour' });
    setQuery(null);
    setStage(next);
  }, []);

  const togglePlay = () => {
    if (!playing && query?.done) {
      // Resume the guided tour after a finished simulated query
      goToStage(0);
    }
    setPlaying((value) => !value);
  };

  const runQuery = (question) => {
    Object.assign(anim.current, { stage: QUERY_STAGE_INDEX, stageTime: 0, mode: 'query' });
    setStage(QUERY_STAGE_INDEX);
    setQuery({ question, done: false });
    setPlaying(true);
  };

  const onQueryDone = useCallback(() => {
    setPlaying(false);
    setQuery((current) => (current ? { ...current, done: true } : current));
  }, []);

  const fallback = <FallbackInfographic onSelectNode={setSelectedNode} showNote={tier === 'fallback'} />;
  const stageName = STAGES[stage];

  return (
    <Box sx={{ bgcolor: '#f1f5f9', pb: 6 }}>
      <Helmet>
        <title>{t('seo.landingTitle')}</title>
      </Helmet>

      <Container maxWidth="xl" sx={{ pt: { xs: 4, md: 6 }, pb: 3 }}>
        <Typography variant="overline" sx={{ color: '#917D26', fontFamily: '"Inter", sans-serif', fontWeight: 700 }}>
          {t('landing.eyebrow')}
        </Typography>
        <Typography variant="h3" component="h1" sx={{ color: '#1e3a8a', fontFamily: '"Cinzel", serif !important', fontSize: { xs: '1.9rem', md: '2.8rem' } }}>
          {t('landing.title')}
        </Typography>
        <Typography variant="body1" sx={{ maxWidth: 820, mt: 1.5, color: '#475569', fontFamily: '"Inter", sans-serif' }}>
          {t('landing.subtitle')}
        </Typography>
        <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 2, mt: 3 }}>
          <Button
            component={RouterLink}
            to={localizedPath('/chat')}
            variant="contained"
            size="large"
            sx={{ bgcolor: '#1e3a8a', '&:hover': { bgcolor: '#1e40af' } }}
          >
            {t('landing.cta')}
          </Button>
          {tier !== 'fallback' && (
            <Button variant="text" onClick={() => setMode(mode === '3d' ? 'fallback' : '3d')} sx={{ color: '#1e3a8a' }}>
              {mode === '3d' ? t('landing.fallbackButton') : t('landing.interactiveButton')}
            </Button>
          )}
        </Box>
      </Container>

      <Container maxWidth="xl">
        <Grid container spacing={3}>
          <Grid item xs={12} lg={8}>
            <Paper elevation={3} sx={{ overflow: 'hidden', borderRadius: 3 }}>
              {mode === '3d' ? (
                <SceneErrorBoundary fallback={fallback} onError={() => setMode('fallback')}>
                  <Box ref={sceneRef} sx={{ height: { xs: 380, md: 540 }, bgcolor: '#0b1437', touchAction: 'none' }}>
                    <Suspense fallback={<SceneLoading label={t('landing.loading')} />}>
                      <RagScene
                        anim={anim}
                        stage={stage}
                        playing={playing}
                        visible={visible}
                        initialQuality={tier === 'high' ? 'high' : 'low'}
                        labels={labels}
                        selectedNode={selectedNode}
                        controlsRef={controlsRef}
                        onSelectNode={setSelectedNode}
                        onStageChange={setStage}
                        onQueryDone={onQueryDone}
                        onContextLost={() => setMode('fallback')}
                        ariaLabel={t('landing.canvasLabel')}
                      />
                    </Suspense>
                  </Box>
                  <ControlsBar
                    stage={stage}
                    playing={playing}
                    onTogglePlay={togglePlay}
                    onStep={(delta) => goToStage(stage + delta)}
                    onGoToStage={goToStage}
                    onResetCamera={() => controlsRef.current?.reset()}
                  />
                </SceneErrorBoundary>
              ) : (
                fallback
              )}
            </Paper>
          </Grid>

          <Grid item xs={12} lg={4}>
            <Paper sx={{ p: 3, borderRadius: 3, height: '100%' }}>
              {mode === '3d' && (
                <Box sx={{ mb: 3 }} aria-live="polite">
                  <Typography variant="caption" color="text.secondary" sx={{ fontFamily: '"Inter", sans-serif' }}>
                    {t('landing.stageLabel', { current: stage + 1, total: STAGES.length })}
                  </Typography>
                  <Typography variant="h6" component="h2" sx={{ color: '#1e3a8a' }}>
                    {t(`landing.stages.${stageName}`)}
                  </Typography>
                  <Typography variant="body2" sx={{ mt: 0.5, lineHeight: 1.7 }}>
                    {t(`landing.stageHints.${stageName}`)}
                  </Typography>
                </Box>
              )}
              <QuerySimulator stage={stage} query={query} onRun={runQuery} />
            </Paper>
          </Grid>
        </Grid>
      </Container>

      <InfoPanel nodeId={selectedNode} onClose={() => setSelectedNode(null)} />
    </Box>
  );
};

export default LandingPage;
