// A deliberately tiny History-API router: no dependency, no cookies, no storage.
// Cloudflare Pages serves index.html for unknown paths (no 404.html in the build),
// so every route below also works when it is opened directly or refreshed.
import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
  type AnchorHTMLAttributes,
  type MouseEvent,
  type ReactNode,
} from 'react';

interface NavigateOptions {
  replace?: boolean;
  keepScroll?: boolean;
}

interface RouterState {
  path: string;
  search: string;
  navigate: (to: string, options?: NavigateOptions) => void;
}

const RouterContext = createContext<RouterState | null>(null);

function normalise(pathname: string): string {
  const trimmed = pathname.replace(/\/+$/, '');
  return trimmed === '' ? '/' : trimmed;
}

function readLocation() {
  return { path: normalise(window.location.pathname), search: window.location.search };
}

export function RouterProvider({ children }: { children: ReactNode }) {
  const [location, setLocation] = useState(readLocation);

  useEffect(() => {
    const onPop = () => setLocation(readLocation());
    window.addEventListener('popstate', onPop);
    return () => window.removeEventListener('popstate', onPop);
  }, []);

  const navigate = useCallback((to: string, options: NavigateOptions = {}) => {
    const current = window.location.pathname + window.location.search;
    if (to !== current) {
      if (options.replace) window.history.replaceState(null, '', to);
      else window.history.pushState(null, '', to);
    }
    setLocation(readLocation());
    if (!options.keepScroll) window.scrollTo(0, 0);
  }, []);

  const value = useMemo(() => ({ ...location, navigate }), [location, navigate]);
  return <RouterContext.Provider value={value}>{children}</RouterContext.Provider>;
}

export function useRouter(): RouterState {
  const ctx = useContext(RouterContext);
  if (!ctx) throw new Error('useRouter must be used inside RouterProvider');
  return ctx;
}

type LinkProps = Omit<AnchorHTMLAttributes<HTMLAnchorElement>, 'href'> & { to: string };

export function Link({ to, onClick, children, ...rest }: LinkProps) {
  const { navigate } = useRouter();
  const handleClick = (event: MouseEvent<HTMLAnchorElement>) => {
    onClick?.(event);
    if (event.defaultPrevented || event.button !== 0 || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) {
      return;
    }
    event.preventDefault();
    navigate(to);
  };
  return (
    <a href={to} onClick={handleClick} {...rest}>
      {children}
    </a>
  );
}

/** true when `path` is `section` or inside it (used for aria-current in the nav). */
export function isActive(path: string, section: string): boolean {
  if (section === '/') return path === '/';
  return path === section || path.startsWith(`${section}/`);
}
