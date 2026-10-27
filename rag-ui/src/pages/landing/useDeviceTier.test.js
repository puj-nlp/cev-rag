import { getDeviceTier } from './useDeviceTier';

const setScreen = (width, height) => {
  Object.defineProperty(window, 'screen', { configurable: true, value: { width, height } });
};

const setMatchMedia = (matching = []) => {
  window.matchMedia = (query) => ({ matches: matching.includes(query), addListener() {}, removeListener() {} });
};

describe('getDeviceTier', () => {
  const originalScreen = window.screen;

  beforeEach(() => {
    // jsdom has no WebGL: stub a context so the 3D tiers can be selected
    HTMLCanvasElement.prototype.getContext = () => ({});
    window.WebGLRenderingContext = function WebGLRenderingContext() {};
    Object.defineProperty(navigator, 'hardwareConcurrency', { configurable: true, value: 8 });
    Object.defineProperty(navigator, 'deviceMemory', { configurable: true, value: 8 });
    Object.defineProperty(window, 'devicePixelRatio', { configurable: true, value: 1 });
    setMatchMedia();
  });

  afterAll(() => {
    Object.defineProperty(window, 'screen', { configurable: true, value: originalScreen });
  });

  it('uses the full scene on capable desktops', () => {
    setScreen(1920, 1080);
    expect(getDeviceTier()).toBe('high');
  });

  it('uses the lightweight mobile preset on phones in either orientation', () => {
    setScreen(390, 844);
    expect(getDeviceTier()).toBe('mobile');
    setScreen(844, 390);
    expect(getDeviceTier()).toBe('mobile');
  });

  it('caps touch tablets at the low preset', () => {
    setScreen(820, 1180);
    setMatchMedia(['(pointer: coarse)']);
    expect(getDeviceTier()).toBe('low');
  });

  it('falls back to the SVG infographic when motion is reduced', () => {
    setScreen(1920, 1080);
    setMatchMedia(['(prefers-reduced-motion: reduce)']);
    expect(getDeviceTier()).toBe('fallback');
  });
});
