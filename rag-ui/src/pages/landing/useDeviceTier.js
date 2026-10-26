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

const prefersReducedMotion = () =>
  typeof window.matchMedia === 'function' && window.matchMedia('(prefers-reduced-motion: reduce)').matches;

/**
 * Picks the rendering tier for the landing infographic:
 *  - "fallback": no WebGL, reduced motion, data saver or very weak device -> lightweight SVG
 *  - "low": modest device -> 3D with fewer particles, no antialiasing, capped resolution
 *  - "high": full 3D scene
 */
export const getDeviceTier = () => {
  if (typeof window === 'undefined') return 'fallback';
  if (!hasWebGL() || prefersReducedMotion()) return 'fallback';

  const cores = navigator.hardwareConcurrency || 4;
  const memory = navigator.deviceMemory || 4; // GB, Chromium only
  const saveData = Boolean(navigator.connection && navigator.connection.saveData);

  if (saveData || cores <= 2 || memory <= 2) return 'fallback';
  if (cores <= 4 || memory <= 4 || window.devicePixelRatio > 2.5) return 'low';
  return 'high';
};

const useDeviceTier = () => useMemo(getDeviceTier, []);

export default useDeviceTier;
