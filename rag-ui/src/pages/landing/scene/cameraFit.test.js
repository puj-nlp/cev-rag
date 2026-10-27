import { DEFAULT_DISTANCE, SCENE_BOUNDS, fitCameraDistance } from './cameraFit';

const visibleWidth = (distance, aspect, fov) => 2 * distance * Math.tan((fov * Math.PI) / 360) * aspect;

describe('fitCameraDistance', () => {
  it('keeps the default framing on wide desktop viewports', () => {
    expect(fitCameraDistance(16 / 9, 45)).toBeCloseTo(DEFAULT_DISTANCE);
  });

  it('backs off on portrait phones so the whole pipeline stays visible', () => {
    const aspect = 375 / 400;
    const distance = fitCameraDistance(aspect, 45);
    expect(distance).toBeGreaterThan(DEFAULT_DISTANCE);
    expect(visibleWidth(distance, aspect, 45)).toBeGreaterThanOrEqual(SCENE_BOUNDS.width);
  });

  it('grows as the viewport narrows', () => {
    expect(fitCameraDistance(0.5, 45)).toBeGreaterThan(fitCameraDistance(0.9, 45));
  });

  it('guards against degenerate aspects', () => {
    expect(Number.isFinite(fitCameraDistance(0, 45))).toBe(true);
  });
});
