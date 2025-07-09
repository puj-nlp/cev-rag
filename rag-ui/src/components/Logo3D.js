import React, { useRef, useEffect } from 'react';
import * as THREE from 'three';

const Logo3D = () => {
  const mountRef = useRef(null);
  const rendererRef = useRef(null);
  const animationRef = useRef(null);

  useEffect(() => {
    // Escena y cámara
    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(75, 1, 0.1, 1000);
    const renderer = new THREE.WebGLRenderer({ alpha: true, antialias: true });
    renderer.setSize(60, 60);
    renderer.setClearColor(0x000000, 0);
    mountRef.current.appendChild(renderer.domElement);

    // Marco exterior (delgado)
    const frameGroup = new THREE.Group();
    const frameColor = 0xecd9c6;
    const frameThickness = 0.12;
    const frameLength = 2.0;
    // Lados
    const left = new THREE.Mesh(
      new THREE.BoxGeometry(frameThickness, frameLength, 0.12),
      new THREE.MeshLambertMaterial({ color: frameColor })
    );
    left.position.x = -frameLength / 2 + frameThickness / 2;
    frameGroup.add(left);
    const right = left.clone();
    right.position.x = frameLength / 2 - frameThickness / 2;
    frameGroup.add(right);
    // Arriba
    const top = new THREE.Mesh(
      new THREE.BoxGeometry(frameLength, frameThickness, 0.12),
      new THREE.MeshLambertMaterial({ color: frameColor })
    );
    top.position.y = frameLength / 2 - frameThickness / 2;
    frameGroup.add(top);
    // Abajo
    const bottom = top.clone();
    bottom.position.y = -frameLength / 2 + frameThickness / 2;
    frameGroup.add(bottom);
    scene.add(frameGroup);

    // Fondo azul cielo
    const bgGeometry = new THREE.PlaneGeometry(1.76, 1.76);
    const bgMaterial = new THREE.MeshLambertMaterial({ color: 0x87ceeb });
    const bg = new THREE.Mesh(bgGeometry, bgMaterial);
    bg.position.z = -0.01;
    scene.add(bg);

    // Colina 1 (verde claro)
    const hill1Geometry = new THREE.SphereGeometry(0.7, 32, 32, 0, Math.PI);
    const hill1Material = new THREE.MeshLambertMaterial({ color: 0x7ec850 });
    const hill1 = new THREE.Mesh(hill1Geometry, hill1Material);
    hill1.position.set(-0.4, -0.6, 0.01);
    hill1.scale.set(1.2, 0.6, 1);
    scene.add(hill1);

    // Colina 2 (verde oscuro)
    const hill2Geometry = new THREE.SphereGeometry(0.6, 32, 32, 0, Math.PI);
    const hill2Material = new THREE.MeshLambertMaterial({ color: 0x4e944f });
    const hill2 = new THREE.Mesh(hill2Geometry, hill2Material);
    hill2.position.set(0.5, -0.7, 0.02);
    hill2.scale.set(1.1, 0.5, 1);
    scene.add(hill2);

    // Sol
    const sunGeometry = new THREE.SphereGeometry(0.25, 32, 32);
    const sunMaterial = new THREE.MeshLambertMaterial({ color: 0xffd700 });
    const sun = new THREE.Mesh(sunGeometry, sunMaterial);
    sun.position.set(0.5, 0.5, 0.03);
    scene.add(sun);

    // Rayos del sol (opcional, simple)
    for (let i = 0; i < 8; i++) {
      const rayGeometry = new THREE.CylinderGeometry(0.01, 0.01, 0.18, 8);
      const rayMaterial = new THREE.MeshLambertMaterial({ color: 0xffd700 });
      const ray = new THREE.Mesh(rayGeometry, rayMaterial);
      ray.position.set(0.5 + 0.32 * Math.cos(i * Math.PI / 4), 0.5 + 0.32 * Math.sin(i * Math.PI / 4), 0.03);
      ray.rotation.z = i * Math.PI / 4;
      scene.add(ray);
    }

    // Nube 1
    const cloud1 = new THREE.Group();
    const cloud1a = new THREE.Mesh(new THREE.SphereGeometry(0.13, 16, 16), new THREE.MeshLambertMaterial({ color: 0xffffff }));
    cloud1a.position.set(-0.5, 0.4, 0.03);
    cloud1.add(cloud1a);
    const cloud1b = new THREE.Mesh(new THREE.SphereGeometry(0.09, 16, 16), new THREE.MeshLambertMaterial({ color: 0xffffff }));
    cloud1b.position.set(-0.38, 0.42, 0.03);
    cloud1.add(cloud1b);
    const cloud1c = new THREE.Mesh(new THREE.SphereGeometry(0.08, 16, 16), new THREE.MeshLambertMaterial({ color: 0xffffff }));
    cloud1c.position.set(-0.57, 0.48, 0.03);
    cloud1.add(cloud1c);
    scene.add(cloud1);

    // Nube 2
    const cloud2 = new THREE.Group();
    const cloud2a = new THREE.Mesh(new THREE.SphereGeometry(0.09, 16, 16), new THREE.MeshLambertMaterial({ color: 0xffffff }));
    cloud2a.position.set(0.1, 0.2, 0.03);
    cloud2.add(cloud2a);
    const cloud2b = new THREE.Mesh(new THREE.SphereGeometry(0.07, 16, 16), new THREE.MeshLambertMaterial({ color: 0xffffff }));
    cloud2b.position.set(0.18, 0.22, 0.03);
    cloud2.add(cloud2b);
    scene.add(cloud2);

    // Hojas de ventana abiertas (shutters)
    const shutterColor = 0xe0b97a;
    const shutterWidth = 0.18;
    const shutterHeight = 1.5;
    const shutterDepth = 0.06;
    // Izquierda
    const leftShutter = new THREE.Mesh(
      new THREE.BoxGeometry(shutterWidth, shutterHeight, shutterDepth),
      new THREE.MeshLambertMaterial({ color: shutterColor })
    );
    leftShutter.position.set(-frameLength / 2 - shutterWidth / 2 + frameThickness / 2, 0, 0.06);
    leftShutter.rotation.y = Math.PI / 2.5;
    scene.add(leftShutter);
    // Derecha
    const rightShutter = leftShutter.clone();
    rightShutter.position.set(frameLength / 2 + shutterWidth / 2 - frameThickness / 2, 0, 0.06);
    rightShutter.rotation.y = -Math.PI / 2.5;
    scene.add(rightShutter);

    // Iluminación
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.9);
    scene.add(ambientLight);
    const directionalLight = new THREE.DirectionalLight(0xffffff, 0.7);
    directionalLight.position.set(5, 5, 5);
    scene.add(directionalLight);

    // Cámara
    camera.position.z = 3;

    // Animación (opcional: sol gira lentamente)
    const animate = () => {
      animationRef.current = requestAnimationFrame(animate);
      sun.rotation.z += 0.01;
      renderer.render(scene, camera);
    };
    animate();

    rendererRef.current = renderer;

    // Cleanup
    return () => {
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current);
      }
      if (mountRef.current && renderer.domElement) {
        mountRef.current.removeChild(renderer.domElement);
      }
      renderer.dispose();
    };
  }, []);

  return (
    <div 
      ref={mountRef} 
      style={{ 
        width: '60px', 
        height: '60px',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center'
      }} 
    />
  );
};

export default Logo3D;
