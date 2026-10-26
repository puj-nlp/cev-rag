import React, { useEffect, useState } from 'react';
import { Box, Button, Chip, TextField, Typography } from '@mui/material';
import { Link as RouterLink } from 'react-router-dom';
import { useTranslation } from 'react-i18next';

import useLocalizedPath from '../../i18n/useLocalizedPath';
import { STAGES } from './content';

const MAX_SIMULATED_QUESTION = 300;
const RETRIEVE_INDEX = STAGES.indexOf('retrieve');
const GENERATE_INDEX = STAGES.indexOf('generate');

/** Reveals text progressively, like a streamed LLM answer. */
const TypedText = ({ text }) => {
  const [length, setLength] = useState(0);

  useEffect(() => {
    setLength(0);
    const timer = setInterval(() => {
      setLength((value) => {
        if (value >= text.length) {
          clearInterval(timer);
          return value;
        }
        return value + 3;
      });
    }, 30);
    return () => clearInterval(timer);
  }, [text]);

  return <span aria-live="polite">{text.slice(0, length)}</span>;
};

/**
 * Simulated query: runs entirely in the browser (no API call, no LLM cost) and drives
 * the 3D scene through the query -> retrieval -> generation stages.
 */
const QuerySimulator = ({ stage, query, onRun }) => {
  const { t } = useTranslation();
  const localizedPath = useLocalizedPath();
  const [draft, setDraft] = useState('');
  const samples = t('landing.simulator.samples', { returnObjects: true });
  const fragments = t('landing.simulator.fragments', { returnObjects: true });

  const running = Boolean(query);
  const showFragments = running && (query.done || stage >= RETRIEVE_INDEX);
  const showAnswer = running && (query.done || stage >= GENERATE_INDEX);

  const submit = (event) => {
    event.preventDefault();
    const question = draft.trim();
    if (question) onRun(question);
  };

  return (
    <Box sx={{ fontFamily: '"Inter", sans-serif' }}>
      <Typography variant="h6" component="h2" sx={{ color: '#1e3a8a' }}>
        {t('landing.simulator.title')}
      </Typography>
      <Typography variant="body2" color="text.secondary" sx={{ mb: 1.5 }}>
        {t('landing.simulator.hint')}
      </Typography>

      <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1, mb: 1.5 }}>
        {samples.map((sample) => (
          <Chip
            key={sample}
            label={sample}
            onClick={() => {
              setDraft(sample);
              onRun(sample);
            }}
            variant="outlined"
            sx={{ maxWidth: '100%' }}
          />
        ))}
      </Box>

      <Box component="form" onSubmit={submit} sx={{ display: 'flex', gap: 1 }}>
        <TextField
          size="small"
          fullWidth
          value={draft}
          onChange={(e) => setDraft(e.target.value)}
          placeholder={t('landing.simulator.placeholder')}
          inputProps={{ maxLength: MAX_SIMULATED_QUESTION, 'aria-label': t('landing.simulator.placeholder') }}
        />
        <Button type="submit" variant="contained" sx={{ bgcolor: '#917D26', '&:hover': { bgcolor: '#7A6A20' } }}>
          {t('landing.simulator.run')}
        </Button>
      </Box>

      {running && (
        <Box sx={{ mt: 2, p: 2, borderRadius: 2, bgcolor: '#f8fafc', border: '1px solid #e2e8f0' }}>
          <Typography variant="caption" color="text.secondary">{t('landing.question')}</Typography>
          <Typography variant="body1" sx={{ fontWeight: 700, mb: 1 }}>{query.question}</Typography>

          {showFragments && (
            <>
              <Typography variant="caption" color="text.secondary">{t('landing.simulator.retrieved')}</Typography>
              <Box component="ol" sx={{ mt: 0.5, mb: 1, pl: 2.5 }}>
                {fragments.map((fragment) => (
                  <Typography component="li" variant="body2" key={fragment}>{fragment}</Typography>
                ))}
              </Box>
            </>
          )}

          {showAnswer && (
            <>
              <Typography variant="caption" color="text.secondary">{t('landing.simulator.answer')}</Typography>
              <Typography variant="body2" sx={{ mt: 0.5, lineHeight: 1.6 }}>
                <TypedText text={t('landing.simulator.simulatedAnswer')} />
              </Typography>
              <Button
                component={RouterLink}
                to={`${localizedPath('/chat')}?q=${encodeURIComponent(query.question)}`}
                variant="outlined"
                size="small"
                sx={{ mt: 1.5 }}
              >
                {t('landing.simulator.askReal')}
              </Button>
            </>
          )}
        </Box>
      )}
    </Box>
  );
};

export default QuerySimulator;
