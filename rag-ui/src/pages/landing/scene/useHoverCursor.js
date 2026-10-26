import { useEffect, useState } from 'react';

/** Pointer cursor while hovering an interactive mesh. */
const useHoverCursor = () => {
  const [hovered, setHovered] = useState(false);

  useEffect(() => {
    document.body.style.cursor = hovered ? 'pointer' : 'auto';
    return () => {
      document.body.style.cursor = 'auto';
    };
  }, [hovered]);

  return {
    hovered,
    bind: {
      onPointerOver: (event) => {
        event.stopPropagation();
        setHovered(true);
      },
      onPointerOut: () => setHovered(false),
    },
  };
};

export default useHoverCursor;
