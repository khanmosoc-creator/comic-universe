import { ComicReader } from '../components/ComicReader';
import { Picture } from '../components/Picture';
import { findIssue, issues } from '../lib/content';
import { Link } from '../lib/router';
import { usePageMeta } from '../lib/usePageMeta';
import { NotFound } from './NotFound';

export function ReadIndex() {
  usePageMeta('Read the comics', 'Every Super Zayd’s Maze Guardians issue, free to read.');
  return (
    <section className="section section--cream page-top">
      <div className="wrap">
        <p className="kicker">Comics</p>
        <h1 className="page-title">Read the comics</h1>
        <ul className="issue-list">
          {issues.map((issue) => (
            <li key={issue.id} className="issue-item">
              <Link to={`/read/${issue.slug}`} className="feature-cover" aria-label={`Read Issue #${issue.number}: ${issue.title}`}>
                <Picture {...issue.cover} alt={issue.cover.alt} />
              </Link>
              <div>
                <h2>
                  Issue #{issue.number}: {issue.title}
                </h2>
                <p>{issue.synopsis}</p>
                <Link to={`/read/${issue.slug}`} className="btn btn-primary">
                  Read Issue #{issue.number}
                </Link>
              </div>
            </li>
          ))}
          <li className="issue-item issue-item--soon">
            <div className="soon-cover" aria-hidden="true">
              #2
            </div>
            <div>
              <h2>Issue #2: {issues[0].nextIssue.title}</h2>
              <p>{issues[0].nextIssue.teaser}</p>
            </div>
          </li>
        </ul>
      </div>
    </section>
  );
}

export function ReadIssue({ slug }: { slug: string }) {
  const issue = findIssue(slug);
  usePageMeta(issue ? `Issue #${issue.number}: ${issue.title}` : 'Not found', issue?.synopsis);
  if (!issue) return <NotFound />;
  return (
    <section className="section section--purple page-top reader-page">
      <div className="wrap wrap--reader">
        <header className="reader-header">
          <p className="kicker kicker--light">Issue #{issue.number}</p>
          <h1 className="page-title section-title--light">{issue.title}</h1>
          <p className="on-dark">{issue.ageNote}</p>
        </header>
        <ComicReader issue={issue} />
      </div>
    </section>
  );
}
