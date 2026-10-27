import { useEffect } from 'react';
import { useThree } from '@react-three/fiber';
import { Vector3 } from 'three';

import { DEFAULT_CAMERA, fitCameraDistance, maxDistanceFor } from './cameraFit';

const DEFAULT_DIRECTION = new Vector3(...DEFAULT_CAMERA).normalize();

/**
 * Refits the camera whenever the canvas is resized (rotation, window resize, layout change).
 * Keeps the user's orbit angle, rescales its distance, updates the OrbitControls reset pose
 * and moves the fog so distant framings stay readable.
 */
const ResponsiveCamera = ({ onFit }) => {
  const { camera, size, controls, scene, invalidate } = useThree();

  useEffect(() => {
    if (!size.width || !size.height) return;
    const distance = fitCameraDistance(size.width / size.height, camera.fov);
    const target = controls ? controls.target : new Vector3();

    const offset = camera.position.clone().sub(target);
    if (offset.lengthSq() === 0) offset.copy(DEFAULT_DIRECTION);
    camera.position.copy(target).add(offset.setLength(distance));
    camera.updateProjectionMatrix();

    if (controls) {
      // Raise the zoom limit before update(), otherwise the controls clamp the new distance
      controls.maxDistance = Math.max(controls.maxDistance, maxDistanceFor(distance));
      controls.position0.copy(DEFAULT_DIRECTION).multiplyScalar(distance);
      controls.update();
    }
    if (scene.fog) {
      scene.fog.near = distance + 4;
      scene.fog.far = distance + 20;
    }
    onFit?.(distance);
    invalidate();
  }, [size.width, size.height, camera, controls, scene, invalidate, onFit]);

  return null;
};

export default ResponsiveCamera;
