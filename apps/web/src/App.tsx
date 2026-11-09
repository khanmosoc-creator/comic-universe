import { Layout } from './components/Layout';
import { useRouter } from './lib/router';
import { About } from './pages/About';
import { ArtVault } from './pages/ArtVault';
import { CharacterDetail, CharacterIndex } from './pages/Characters';
import { Home } from './pages/Home';
import { NotFound } from './pages/NotFound';
import { Privacy } from './pages/Privacy';
import { ReadIndex, ReadIssue } from './pages/Read';
import { UniversePage } from './pages/Universe';

function route(path: string) {
  if (path === '/') return <Home />;
  if (path === '/heroes') return <CharacterIndex kind="heroes" />;
  if (path === '/villains') return <CharacterIndex kind="villains" />;
  if (path === '/read') return <ReadIndex />;
  if (path === '/universe') return <UniversePage />;
  if (path === '/art-vault') return <ArtVault />;
  if (path === '/about') return <About />;
  if (path === '/privacy') return <Privacy />;

  const character = path.match(/^\/(heroes|villains)\/([a-z0-9-]+)$/);
  if (character) {
    const kind = character[1] === 'heroes' ? 'heroes' : 'villains';
    return <CharacterDetail key={path} kind={kind} id={character[2]} />;
  }
  const issue = path.match(/^\/read\/([a-z0-9-]+)$/);
  if (issue) return <ReadIssue key={path} slug={issue[1]} />;

  return <NotFound />;
}

export function App() {
  const { path } = useRouter();
  return <Layout>{route(path)}</Layout>;
}
