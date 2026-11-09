import { Link } from '../lib/router';
import { usePageMeta } from '../lib/usePageMeta';

export function NotFound() {
  usePageMeta('Wrong turn!');
  return (
    <section className="section section--night page-top">
      <div className="wrap not-found">
        <p className="kicker kicker--light">Error 404</p>
        <h1 className="page-title section-title--light">Whoops — wrong turn in the maze!</h1>
        <p className="lead on-dark">Even Super Zayd takes a wrong turn sometimes. This page doesn't exist (yet).</p>
        <div className="hero-actions">
          <Link to="/" className="btn btn-primary">
            Back to Lighthouse HQ
          </Link>
          <Link to="/read/issue-1" className="btn">
            Read Issue #1
          </Link>
        </div>
      </div>
    </section>
  );
}
