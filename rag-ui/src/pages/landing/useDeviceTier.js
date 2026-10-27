import { useMemo } from 'react';

const hasWebGL = () => {
  try {
    const canvas = document.createElement('canvas');
    return Boolean(
      window.WebGLRenderingContext &&
      (canvas.getContext('webgl2') || canvas.getContext('webgl') || canvas.getContext('experimental-webgl'))
    );
  } catch (e) {
    return false;
  }
};

const matches = (query) => typeof window.matchMedia === 'function' && window.matchMedia(query).matches;

const prefersReducedMotion = () => matches('(prefers-reduced-motion: reduce)');

// Phones: shortest screen side below the tablet breakpoint (640px), in either orientation
const isPhone = () => Math.min(window.screen?.width || window.innerWidth, window.screen?.height || window.innerHeight) < 640;

/**
 * Picks the rendering tier for the landing infographic:
 *  - "fallback": no WebGL, reduced motion, data saver or very weak device -> lightweight SVG
 *  - "mobile": phone -> simplified geometry, few points/particles, touch-first controls
 *  - "low": modest device or touch tablet -> 3D with fewer particles, no antialiasing, capped resolution
 *  - "high": full 3D scene
 */
export const getDeviceTier = () => {
  if (typeof window === 'undefined') return 'fallback';
  if (!hasWebGL() || prefersReducedMotion()) return 'fallback';

  const cores = navigator.hardwareConcurrency || 4;
  const memory = navigator.deviceMemory || 4; // GB, Chromium only
  const saveData = Boolean(navigator.connection && navigator.connection.saveData);

  if (saveData || cores <= 2 || memory <= 2) return 'fallback';
  if (isPhone()) return 'mobile';
  if (cores <= 4 || memory <= 4 || window.devicePixelRatio > 2.5 || matches('(pointer: coarse)')) return 'low';
  return 'high';
};

const useDeviceTier = () => useMemo(getDeviceTier, []);

export default useDeviceTier;
