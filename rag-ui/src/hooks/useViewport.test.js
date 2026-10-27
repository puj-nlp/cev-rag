import React from 'react';
import { render, screen } from '@testing-library/react';
import { ThemeProvider, createTheme } from '@mui/material/styles';

import useViewport from './useViewport';

const theme = createTheme({ breakpoints: { values: { xs: 0, sm: 640, md: 1024, lg: 1280, xl: 1536 } } });

// Minimal media query evaluator for min-width / max-width / orientation / pointer queries
const mockViewport = (width, height, { coarse = false } = {}) => {
  window.matchMedia = (query) => {
    const checks = query.split(' and ').map((part) => {
      const min = part.match(/min-width:\s*([\d.]+)px/);
      const max = part.match(/max-width:\s*([\d.]+)px/);
      if (min) return width >= Number(min[1]);
      if (max) return width <= Number(max[1]);
      if (part.includes('orientation: portrait')) return height >= width;
      if (part.includes('pointer: coarse')) return coarse;
      return false;
    });
    return {
      matches: checks.every(Boolean),
      media: query,
      addListener() {},
      removeListener() {},
      addEventListener() {},
      removeEventListener() {},
    };
  };
};

const Probe = () => {
  const viewport = useViewport();
  return <span data-testid="viewport">{JSON.stringify(viewport)}</span>;
};

const viewportFor = (width, height, options) => {
  mockViewport(width, height, options);
  render(
    <ThemeProvider theme={theme}>
      <Probe />
    </ThemeProvider>
  );
  return JSON.parse(screen.getByTestId('viewport').textContent);
};

describe('useViewport', () => {
  it('detects phones below 640px', () => {
    expect(viewportFor(375, 812, { coarse: true })).toEqual({
      isMobile: true, isTablet: false, isDesktop: false, isPortrait: true, isTouch: true,
    });
  });

  it('detects tablets between 640px and 1023px', () => {
    expect(viewportFor(768, 1024)).toMatchObject({ isMobile: false, isTablet: true, isDesktop: false });
  });

  it('detects desktops from 1024px', () => {
    expect(viewportFor(1280, 800)).toMatchObject({ isMobile: false, isTablet: false, isDesktop: true, isPortrait: false });
  });
});
