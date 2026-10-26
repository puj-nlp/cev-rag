/**
 * Writes public/sitemap.xml (with hreflang alternates for the localized routes) and public/robots.txt.
 * Runs before `npm run build`; the site URL comes from REACT_APP_SITE_URL.
 */
const fs = require('fs');
const path = require('path');

const SITE_URL = (process.env.REACT_APP_SITE_URL || 'https://localhost').replace(/\/$/, '');
const LANGUAGES = ['es', 'en'];
const PAGES = ['/', '/chat', '/about'];

const url = (lang, page) => `${SITE_URL}/${lang}${page === '/' ? '/' : page}`;

const entries = PAGES.flatMap((page) =>
  LANGUAGES.map((lang) => {
    const alternates = LANGUAGES.map(
      (alt) => `    <xhtml:link rel="alternate" hreflang="${alt}" href="${url(alt, page)}"/>`
    ).concat(`    <xhtml:link rel="alternate" hreflang="x-default" href="${SITE_URL}/"/>`);
    return ['  <url>', `    <loc>${url(lang, page)}</loc>`, ...alternates, '  </url>'].join('\n');
  })
);

const xml = [
  '<?xml version="1.0" encoding="UTF-8"?>',
  '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">',
  ...entries,
  '</urlset>',
  '',
].join('\n');

const robots = ['User-agent: *', 'Allow: /es/', 'Allow: /en/', 'Disallow: /api/', `Sitemap: ${SITE_URL}/sitemap.xml`, ''].join('\n');

const publicDir = path.join(__dirname, '..', 'public');
fs.writeFileSync(path.join(publicDir, 'sitemap.xml'), xml);
fs.writeFileSync(path.join(publicDir, 'robots.txt'), robots);
console.log(`sitemap.xml and robots.txt written for ${SITE_URL}`);
