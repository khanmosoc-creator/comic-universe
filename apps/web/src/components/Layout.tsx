import { useEffect, useRef, useState, type ReactNode } from 'react';
import { Link, isActive, useRouter } from '../lib/router';

const NAV = [
  { to: '/', label: 'Home' },
  { to: '/read/issue-1', label: 'Read #1', section: '/read' },
  { to: '/heroes', label: 'Heroes' },
  { to: '/villains', label: 'Villains' },
  { to: '/universe', label: 'Universe' },
  { to: '/art-vault', label: 'Art Vault' },
  { to: '/about', label: 'About' },
];

export function Layout({ children }: { children: ReactNode }) {
  const { path } = useRouter();
  const [menuOpen, setMenuOpen] = useState(false);
  const mainRef = useRef<HTMLElement>(null);
  const firstRender = useRef(true);

  // Move keyboard / screen-reader focus to the new page after client-side navigation.
  useEffect(() => {
    setMenuOpen(false);
    if (firstRender.current) {
      firstRender.current = false;
      return;
    }
    mainRef.current?.focus({ preventScroll: true });
  }, [path]);

  return (
    <div className="site">
      <a className="skip-link" href="#main">
        Skip to the comic
      </a>
      <header className="site-header">
        <div className="wrap header-row">
          <Link to="/" className="brand" aria-label="Super Zayd's Maze Guardians — home">
            <img src="/art/brand/badge.svg" width="44" height="44" alt="" />
            <span className="brand-text">
              <span className="brand-top">Super Zayd's</span>
              <span className="brand-bottom">Maze Guardians</span>
            </span>
          </Link>
          <button
            type="button"
            className="menu-toggle"
            aria-expanded={menuOpen}
            aria-controls="site-nav"
            onClick={() => setMenuOpen((open) => !open)}
          >
            <span className="menu-icon" aria-hidden="true" />
            Menu
          </button>
          <nav id="site-nav" className={menuOpen ? 'site-nav open' : 'site-nav'} aria-label="Main">
            <ul>
              {NAV.map((item) => {
                const active = isActive(path, item.section ?? item.to);
                return (
                  <li key={item.to}>
                    <Link to={item.to} aria-current={active ? 'page' : undefined}>
                      {item.label}
                    </Link>
                  </li>
                );
              })}
            </ul>
          </nav>
        </div>
      </header>
      <main id="main" ref={mainRef} tabIndex={-1}>
        {children}
      </main>
      <footer className="site-footer">
        <div className="wrap footer-grid">
          <div>
            <p className="footer-brand">Super Zayd's Maze Guardians</p>
            <p>An original comic for kids and families. No ads, no accounts, no tracking — just comics.</p>
          </div>
          <nav aria-label="Footer">
            <ul className="footer-links">
              <li><Link to="/read/issue-1">Read Issue #1</Link></li>
              <li><Link to="/heroes">Heroes</Link></li>
              <li><Link to="/villains">Villains</Link></li>
              <li><Link to="/art-vault">Art Vault</Link></li>
              <li><Link to="/about">About &amp; credits</Link></li>
              <li><Link to="/privacy">Privacy</Link></li>
            </ul>
          </nav>
        </div>
        <p className="wrap copyright">
          © 2026 Super Zayd's Maze Guardians. All characters, stories and artwork are original. All rights reserved.
        </p>
      </footer>
    </div>
  );
}
