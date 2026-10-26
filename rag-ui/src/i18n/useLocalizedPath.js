import { useCallback } from 'react';
import { useTranslation } from 'react-i18next';

/** Returns a function that prefixes an app path with the active language: "/chat" -> "/es/chat". */
const useLocalizedPath = () => {
  const { i18n } = useTranslation();
  return useCallback(
    (path = '/') => `/${i18n.language}${path === '/' ? '/' : path}`,
    [i18n.language]
  );
};

export default useLocalizedPath;
