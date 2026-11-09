import type { CSSProperties } from 'react';
import { CharacterCard, StatBars } from '../components/CharacterCard';
import { Picture } from '../components/Picture';
import { charactersOf, findCharacter, findSketch, minions } from '../lib/content';
import { Link } from '../lib/router';
import { usePageMeta } from '../lib/usePageMeta';
import type { CharacterKind } from '../types';
import { NotFound } from './NotFound';

const COPY: Record<CharacterKind, { title: string; kicker: string; lead: string }> = {
  heroes: {
    title: 'The Maze Guardians',
    kicker: 'Heroes',
    lead: 'Five friends with five very different superpowers — and one shared rule: leave no one lost.',
  },
  villains: {
    title: 'Villains of the Mazeverse',
    kicker: 'Villains',
    lead: 'They want to scramble the maze. They mostly scramble themselves. Kid-friendly trouble only!',
  },
};

export function CharacterIndex({ kind }: { kind: CharacterKind }) {
  const copy = COPY[kind];
  usePageMeta(copy.title, copy.lead);
  const list = charactersOf(kind);
  return (
    <section className={`section ${kind === 'villains' ? 'section--night' : 'section--cream'} page-top`}>
      <div className="wrap">
        <p className={kind === 'villains' ? 'kicker kicker--light' : 'kicker'}>{copy.kicker}</p>
        <h1 className={kind === 'villains' ? 'page-title section-title--light' : 'page-title'}>{copy.title}</h1>
        <p className={kind === 'villains' ? 'lead on-dark' : 'lead'}>{copy.lead}</p>
        <ul className={`card-grid ${kind === 'heroes' ? 'card-grid--five' : 'card-grid--three'}`}>
          {list.map((c) => (
            <li key={c.id}>
              <CharacterCard character={c} kind={kind} headingLevel={2} />
            </li>
          ))}
        </ul>
        {kind === 'villains' && (
          <aside className="minion-box">
            <h2>Also starring: the {minions.name}</h2>
            <p>{minions.description}</p>
          </aside>
        )}
      </div>
    </section>
  );
}

export function CharacterDetail({ kind, id }: { kind: CharacterKind; id: string }) {
  const character = findCharacter(kind, id);
  usePageMeta(character ? character.name : 'Not found', character ? `${character.name} — ${character.role}. ${character.tagline}` : undefined);
  if (!character) return <NotFound />;

  const list = charactersOf(kind);
  const i = list.findIndex((c) => c.id === id);
  const prev = list[(i - 1 + list.length) % list.length];
  const next = list[(i + 1) % list.length];
  const sketch = findSketch(character.inspiredBy);
  const villain = kind === 'villains';
  const style = { '--card-color': character.colors.primary, '--card-accent': character.colors.accent } as CSSProperties;

  return (
    <article className={`section ${villain ? 'section--night' : 'section--cream'} page-top`} style={style}>
      <div className="wrap">
        <nav className="crumbs" aria-label="Breadcrumb">
          <Link to={`/${kind}`}>{villain ? 'All villains' : 'All heroes'}</Link>
        </nav>
        <div className="profile">
          <figure className="profile-art comic-frame comic-frame--portrait">
            <img src={character.image} width="800" height="1000" alt={character.imageAlt} decoding="async" />
          </figure>
          <div className={villain ? 'profile-body profile-body--dark' : 'profile-body'}>
            <p className="kicker">{character.role}</p>
            <h1 className="page-title">{character.name}</h1>
            <p className="speech-quote">“{character.tagline}”</p>

            <h2>Powers</h2>
            <ul className="power-list">
              {character.powers.map((p) => (
                <li key={p}>{p}</li>
              ))}
            </ul>

            {villain && character.scheme && (
              <>
                <h2>The evil scheme</h2>
                <p>{character.scheme}</p>
              </>
            )}
            {villain && character.weakness && (
              <>
                <h2>Weakness</h2>
                <p>{character.weakness}</p>
              </>
            )}

            <h2>Personality</h2>
            <p>{character.personality}</p>

            <h2>Catchphrase</h2>
            <p className="catchphrase">{character.catchphrase}</p>

            <h2>Stats</h2>
            <StatBars stats={character.stats} />

            <h2>Fun facts</h2>
            <ul className="fact-list">
              {character.funFacts.map((f) => (
                <li key={f}>{f}</li>
              ))}
            </ul>

            <p className="meta-line">
              First appearance: <Link to="/read/issue-1">Issue #1 — The Great Maze Scramble</Link>
            </p>
          </div>
        </div>

        {sketch && (
          <aside className="inspired" aria-labelledby="inspired-title">
            <h2 id="inspired-title">Where {character.name} came from</h2>
            <figure className="comic-frame">
              <Picture {...sketch} alt={sketch.alt} />
              <figcaption>
                Inspired by the original sketch “{sketch.title}”. <Link to="/art-vault">See it in the Art Vault</Link>.
              </figcaption>
            </figure>
          </aside>
        )}

        <nav className="pager" aria-label={villain ? 'More villains' : 'More heroes'}>
          <Link to={`/${kind}/${prev.id}`} className="btn">
            <span aria-hidden="true">◀</span> {prev.name}
          </Link>
          <Link to={`/${kind}/${next.id}`} className="btn">
            {next.name} <span aria-hidden="true">▶</span>
          </Link>
        </nav>
      </div>
    </article>
  );
}
