// World-space extent of the pipeline (nodes in content.js: x from -8.5 to 8, plus room for the DOM labels)
export const SCENE_BOUNDS = { width: 17.5, height: 6.6 };
// Initial camera position; its length (~14.4) is the framing used on wide screens
export const DEFAULT_CAMERA = [0, 3.2, 14];
export const DEFAULT_DISTANCE = Math.hypot(...DEFAULT_CAMERA);

/**
 * Distance at which a perspective camera sees the whole scene for the given viewport aspect.
 * Narrow (portrait) viewports are limited by the horizontal field of view, so the camera backs off.
 */
export const fitCameraDistance = (aspect, fov, bounds = SCENE_BOUNDS, margin = 1.08, minDistance = DEFAULT_DISTANCE) => {
  const tanHalf = Math.tan((fov * Math.PI) / 360);
  const fitHeight = bounds.height / 2 / tanHalf;
  const fitWidth = bounds.width / 2 / (tanHalf * Math.max(aspect, 0.1));
  return Math.max(minDistance, Math.max(fitHeight, fitWidth) * margin);
};

/** Zoom-out limit for OrbitControls: never below the original 24, always beyond the fitted framing. */
export const maxDistanceFor = (fitDistance) => Math.max(24, fitDistance * 1.5);
