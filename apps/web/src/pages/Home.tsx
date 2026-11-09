import { CharacterCard } from '../components/CharacterCard';
import { Picture } from '../components/Picture';
import { gallery, heroes, issues, universe, villains } from '../lib/content';
import { Link } from '../lib/router';
import { usePageMeta } from '../lib/usePageMeta';

export function Home() {
  usePageMeta(null, 'A free, kid-friendly superhero comic. Join Super Zayd and the Maze Guardians as they protect the glowing Mazeverse. Read Issue #1 now!');
  const issue = issues[0];
  const sketch = gallery.items.find((g) => g.id === 'stretch-punch');
  const dragoncrest = heroes.find((h) => h.id === 'dragoncrest');

  return (
    <>
      <section className="hero">
        <img className="hero-art" src="/art/brand/banner.svg" width="1600" height="800" alt="The five Maze Guardians line up in front of Lighthouse HQ on a glowing maze at night" />
        <div className="hero-copy wrap">
          <h1 className="logo-title">
            <span className="logo-top">Super Zayd's</span>
            <span className="logo-main">Maze Guardians</span>
          </h1>
          <p className="hero-tagline">Five friends. One giant glowing maze. Zero chance of getting lost.</p>
          <div className="hero-actions">
            <Link to="/read/issue-1" className="btn btn-primary btn-big">
              Read Issue #1 — free!
            </Link>
            <Link to="/heroes" className="btn btn-big">
              Meet the heroes
            </Link>
          </div>
        </div>
      </section>

      <section className="section section--cream">
        <div className="wrap feature">
          <Link to="/read/issue-1" className="feature-cover" aria-label={`Read Issue #${issue.number}: ${issue.title}`}>
            <Picture {...issue.cover} alt={issue.cover.alt} />
          </Link>
          <div className="feature-copy">
            <p className="kicker">New! Issue #{issue.number}</p>
            <h2 className="section-title">{issue.title}</h2>
            <p className="lead">{issue.tagline}</p>
            <p>{issue.synopsis}</p>
            <p className="meta-line">
              {issue.panels.length} panels · {issue.readingTime}
            </p>
            <Link to="/read/issue-1" className="btn btn-primary">
              Start reading
            </Link>
          </div>
        </div>
      </section>

      <section className="section section--purple" aria-labelledby="team-title">
        <div className="wrap">
          <p className="kicker kicker--light">The team</p>
          <h2 id="team-title" className="section-title section-title--light">
            Meet the Maze Guardians
          </h2>
          <ul className="card-grid card-grid--five">
            {heroes.map((h) => (
              <li key={h.id}>
                <CharacterCard character={h} kind="heroes" />
              </li>
            ))}
          </ul>
        </div>
      </section>

      <section className="section section--cream" aria-labelledby="villains-title">
        <div className="wrap">
          <p className="kicker">Uh-oh</p>
          <h2 id="villains-title" className="section-title">
            Trouble in the maze
          </h2>
          <p className="lead">They're loud, they're splashy, they're very bad at directions.</p>
          <ul className="card-grid card-grid--three">
            {villains.map((v) => (
              <li key={v.id}>
                <CharacterCard character={v} kind="villains" />
              </li>
            ))}
          </ul>
        </div>
      </section>

      {sketch && dragoncrest && (
        <section className="section section--yellow" aria-labelledby="sketch-title">
          <div className="wrap">
            <p className="kicker">From sketch to comic</p>
            <h2 id="sketch-title" className="section-title">
              Every Guardian starts as a drawing
            </h2>
            <div className="sketch-compare">
              <figure className="comic-frame">
                <Picture {...sketch} alt={sketch.alt} />
                <figcaption>The original sketch</figcaption>
              </figure>
              <span className="arrow-burst" aria-hidden="true">
                ➜
              </span>
              <figure className="comic-frame comic-frame--portrait">
                <img src={dragoncrest.image} width="800" height="1000" alt={dragoncrest.imageAlt} loading="lazy" decoding="async" />
                <figcaption>Dragoncrest, comic-ready</figcaption>
              </figure>
            </div>
            <Link to="/art-vault" className="btn">
              Open the Art Vault
            </Link>
          </div>
        </section>
      )}

      <section className="section section--night" aria-labelledby="world-title">
        <div className="wrap feature feature--reverse">
          <div className="feature-copy">
            <p className="kicker kicker--light">The world</p>
            <h2 id="world-title" className="section-title section-title--light">
              Welcome to the Mazeverse
            </h2>
            <p className="on-dark">{universe.intro}</p>
            <Link to="/universe" className="btn btn-primary">
              Explore the Mazeverse
            </Link>
          </div>
          <figure className="comic-frame">
            <Picture {...universe.map} alt={universe.map.alt} />
          </figure>
        </div>
      </section>

      <section className="section section--cream">
        <div className="wrap code-box">
          <h2 className="section-title">{universe.code.title}</h2>
          <ol className="code-list">
            {universe.code.rules.map((rule) => (
              <li key={rule}>{rule}</li>
            ))}
          </ol>
        </div>
      </section>
    </>
  );
}
