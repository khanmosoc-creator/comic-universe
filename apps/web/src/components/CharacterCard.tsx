import type { CSSProperties } from 'react';
import { Link } from '../lib/router';
import type { Character, CharacterKind } from '../types';

export function CharacterCard({ character, kind, headingLevel = 3 }: { character: Character; kind: CharacterKind; headingLevel?: 2 | 3 }) {
  const Heading = headingLevel === 2 ? 'h2' : 'h3';
  const style = { '--card-color': character.colors.primary, '--card-accent': character.colors.accent } as CSSProperties;
  return (
    <article className={`char-card ${kind === 'villains' ? 'char-card--villain' : ''}`} style={style}>
      <Link to={`/${kind}/${character.id}`} className="char-card-link">
        <img src={character.image} width="800" height="1000" alt="" loading="lazy" decoding="async" />
        <div className="char-card-body">
          <Heading className="char-card-name">{character.name}</Heading>
          <p className="char-card-role">{character.role}</p>
        </div>
      </Link>
    </article>
  );
}

export function StatBars({ stats }: { stats: Character['stats'] }) {
  return (
    <dl className="stats">
      {stats.map((s) => (
        <div className="stat" key={s.label}>
          <dt>{s.label}</dt>
          <dd>
            <span className="stat-bar" aria-hidden="true">
              <span className="stat-fill" style={{ width: `${Math.max(0, Math.min(10, s.value)) * 10}%` }} />
            </span>
            <span className="stat-num">{s.value} out of 10</span>
          </dd>
        </div>
      ))}
    </dl>
  );
}
