import { Picture } from '../components/Picture';
import { gallery } from '../lib/content';
import { usePageMeta } from '../lib/usePageMeta';

export function ArtVault() {
  usePageMeta('Art Vault', 'The original hand-drawn sketches that inspired Super Zayd’s Maze Guardians Issue #1.');
  return (
    <section className="section section--cream page-top">
      <div className="wrap">
        <p className="kicker">Behind the scenes</p>
        <h1 className="page-title">The Art Vault</h1>
        <p className="lead">{gallery.intro}</p>
        <ul className="vault-grid">
          {gallery.items.map((item) => (
            <li key={item.id}>
              <figure className="comic-frame vault-item">
                <Picture {...item} alt={item.alt} />
                <figcaption>
                  <strong className="vault-title">{item.title}</strong>
                  <span>{item.note}</span>
                  <span className="vault-used">Used in: {item.usedIn}</span>
                </figcaption>
              </figure>
            </li>
          ))}
        </ul>
      </div>
    </section>
  );
}
