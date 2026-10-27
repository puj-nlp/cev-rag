import useMediaQuery from '@mui/material/useMediaQuery';
import { useTheme } from '@mui/material/styles';

/**
 * Current device class from the theme breakpoints:
 * mobile (< sm = 640px), tablet (sm-md = 640-1023px), desktop (>= md = 1024px).
 * `isTouch` reports a coarse primary pointer (finger) regardless of screen size.
 */
const useViewport = () => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'), { noSsr: true });
  const isDesktop = useMediaQuery(theme.breakpoints.up('md'), { noSsr: true });
  const isPortrait = useMediaQuery('(orientation: portrait)', { noSsr: true });
  const isTouch = useMediaQuery('(pointer: coarse)', { noSsr: true });

  return {
    isMobile,
    isTablet: !isMobile && !isDesktop,
    isDesktop,
    isPortrait,
    isTouch,
  };
};

export default useViewport;
