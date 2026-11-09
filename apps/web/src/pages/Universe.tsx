import type { CSSProperties } from 'react';
import { Picture } from '../components/Picture';
import { minions, universe } from '../lib/content';
import { usePageMeta } from '../lib/usePageMeta';

export function UniversePage() {
  usePageMeta('The Mazeverse', 'Explore the Mazeverse: the Compass Core, Lighthouse HQ, Neon City, the Frost Fields, the Splash Sea and the Rustbolt Junkyard.');
  return (
    <>
      <section className="section section--night page-top">
        <div className="wrap feature feature--reverse">
          <div className="feature-copy">
            <p className="kicker kicker--light">The world</p>
            <h1 className="page-title section-title--light">The Mazeverse</h1>
            <p className="lead on-dark">{universe.intro}</p>
          </div>
          <figure className="comic-frame">
            <Picture {...universe.map} alt={universe.map.alt} eager />
          </figure>
        </div>
      </section>

      <section className="section section--cream" aria-labelledby="places-title">
        <div className="wrap">
          <h2 id="places-title" className="section-title">
            Places to visit (if you can find them)
          </h2>
          <ul className="place-grid">
            {universe.places.map((place) => (
              <li key={place.name} className="place-card" style={{ '--place-color': place.color } as CSSProperties}>
                <h3>{place.name}</h3>
                <p>{place.text}</p>
              </li>
            ))}
          </ul>
        </div>
      </section>

      <section className="section section--yellow">
        <div className="wrap two-col">
          <div className="code-box">
            <h2 className="section-title">{universe.code.title}</h2>
            <ol className="code-list">
              {universe.code.rules.map((rule) => (
                <li key={rule}>{rule}</li>
              ))}
            </ol>
          </div>
          <div className="code-box">
            <h2 className="section-title">The {minions.name}</h2>
            <p>{minions.description}</p>
          </div>
        </div>
      </section>

      <section className="section section--cream" aria-labelledby="timeline-title">
        <div className="wrap">
          <h2 id="timeline-title" className="section-title">
            Story so far
          </h2>
          <ol className="timeline">
            {universe.timeline.map((t) => (
              <li key={t.label}>
                <span className="timeline-label">{t.label}</span>
                <span className="timeline-title">{t.title}</span>
                <span className="timeline-status">{t.status}</span>
              </li>
            ))}
          </ol>
        </div>
      </section>
    </>
  );
}
