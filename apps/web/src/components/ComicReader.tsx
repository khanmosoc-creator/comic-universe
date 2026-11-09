import { useCallback, useEffect, useRef, useState, type PointerEvent } from 'react';
import { Link, useRouter } from '../lib/router';
import { prefersReducedMotion } from '../lib/usePageMeta';
import type { Issue, Panel } from '../types';
import { Picture } from './Picture';

type Mode = 'panel' | 'page';

function parsePanel(search: string, total: number): number {
  const raw = new URLSearchParams(search).get('panel');
  if (raw === 'end') return total;
  const n = Number.parseInt(raw ?? '1', 10);
  if (!Number.isFinite(n)) return 0;
  return Math.min(Math.max(n - 1, 0), total);
}

function PanelView({ panel, number, total, eager }: { panel: Panel; number: number; total: number; eager: boolean }) {
  return (
    <figure className={`panel panel--${panel.source}`} aria-label={`Panel ${number} of ${total}`}>
      {panel.caption && <p className="caption-box">{panel.caption}</p>}
      <div className="panel-art">
        <Picture {...panel.image} alt={panel.alt} eager={eager} />
        {panel.source === 'owner' && <span className="sketch-tag">Original sketch</span>}
        {panel.sfx && (
          <span className="sfx" aria-hidden="true">
            {panel.sfx}
          </span>
        )}
      </div>
      <figcaption className="dialogue">
        {panel.sfx && <span className="sr-only">Sound effect: {panel.sfx}. </span>}
        {panel.dialogue.map((line, i) => (
          <p key={i} className={`balloon balloon--${line.kind}`}>
            <span className="speaker">{line.speaker}</span>
            <span className="line">{line.text}</span>
          </p>
        ))}
      </figcaption>
    </figure>
  );
}

export function ComicReader({ issue }: { issue: Issue }) {
  const { path, search, navigate } = useRouter();
  const total = issue.panels.length;
  const [index, setIndex] = useState(() => parsePanel(search, total));
  const [mode, setMode] = useState<Mode>('panel');
  const stageRef = useRef<HTMLDivElement>(null);
  const swipeStart = useRef<{ x: number; y: number } | null>(null);
  const firstRun = useRef(true);
  const atEnd = index >= total;

  const go = useCallback((next: number) => setIndex(Math.min(Math.max(next, 0), total)), [total]);

  // Keep the URL shareable: /read/issue-1?panel=4
  useEffect(() => {
    const query = index === 0 ? '' : atEnd ? '?panel=end' : `?panel=${index + 1}`;
    navigate(`${path}${query}`, { replace: true, keepScroll: true });
  }, [index, atEnd, path, navigate]);

  // Bring the stage back into view when a new panel opens below the fold.
  useEffect(() => {
    if (firstRun.current) {
      firstRun.current = false;
      return;
    }
    const el = stageRef.current;
    if (!el || mode !== 'panel') return;
    const top = el.getBoundingClientRect().top;
    if (top < 0 || top > window.innerHeight * 0.6) {
      el.scrollIntoView({ block: 'start', behavior: prefersReducedMotion() ? 'auto' : 'smooth' });
    }
  }, [index, mode]);

  // Warm the cache for the next panel.
  useEffect(() => {
    const next = issue.panels[index + 1];
    if (next) {
      const img = new Image();
      img.src = next.image.src;
    }
  }, [index, issue.panels]);

  // Arrow keys turn the page.
  useEffect(() => {
    if (mode !== 'panel') return;
    const onKey = (event: KeyboardEvent) => {
      if (event.altKey || event.ctrlKey || event.metaKey) return;
      const target = event.target as HTMLElement | null;
      if (target && (target.isContentEditable || ['INPUT', 'TEXTAREA', 'SELECT'].includes(target.tagName))) return;
      if (event.key === 'ArrowRight') {
        event.preventDefault();
        go(index + 1);
      } else if (event.key === 'ArrowLeft') {
        event.preventDefault();
        go(index - 1);
      }
    };
    window.addEventListener('keydown', onKey);
    return () => window.removeEventListener('keydown', onKey);
  }, [go, index, mode]);

  const onPointerDown = (event: PointerEvent<HTMLDivElement>) => {
    if (event.pointerType === 'mouse') return;
    swipeStart.current = { x: event.clientX, y: event.clientY };
  };
  const onPointerUp = (event: PointerEvent<HTMLDivElement>) => {
    const start = swipeStart.current;
    swipeStart.current = null;
    if (!start) return;
    const dx = event.clientX - start.x;
    const dy = event.clientY - start.y;
    if (Math.abs(dx) > 50 && Math.abs(dx) > Math.abs(dy) * 1.5) go(index + (dx < 0 ? 1 : -1));
  };

  const openPanel = (i: number) => {
    setMode('panel');
    go(i);
  };

  return (
    <section className="reader" aria-label={`Issue #${issue.number}: ${issue.title} reader`}>
      <div className="reader-toolbar">
        <p className="reader-count" aria-live="polite">
          {atEnd ? 'The end' : `Panel ${index + 1} of ${total}`}
        </p>
        <div className="view-toggle" role="group" aria-label="Reading view">
          <button type="button" aria-pressed={mode === 'panel'} onClick={() => setMode('panel')}>
            One panel
          </button>
          <button type="button" aria-pressed={mode === 'page'} onClick={() => setMode('page')}>
            Whole page
          </button>
        </div>
      </div>

      {mode === 'panel' ? (
        <>
          <div
            className="reader-stage"
            ref={stageRef}
            onPointerDown={onPointerDown}
            onPointerUp={onPointerUp}
            onPointerCancel={() => (swipeStart.current = null)}
          >
            {atEnd ? (
              <div className="end-card">
                <p className="end-title">The end… for now!</p>
                <p className="end-next">
                  Next time — Issue #{issue.nextIssue.number}: <strong>{issue.nextIssue.title}</strong>
                </p>
                <p>{issue.nextIssue.teaser}</p>
                <div className="end-actions">
                  <button type="button" className="btn btn-primary" onClick={() => go(0)}>
                    Read it again
                  </button>
                  <Link to="/heroes" className="btn">Meet the heroes</Link>
                  <Link to="/art-vault" className="btn">See the original sketches</Link>
                </div>
              </div>
            ) : (
              <PanelView key={issue.panels[index].id} panel={issue.panels[index]} number={index + 1} total={total} eager />
            )}
          </div>

          <div className="reader-controls">
            <button type="button" className="btn nav-btn" onClick={() => go(index - 1)} disabled={index === 0}>
              <span aria-hidden="true">◀</span> Back
            </button>
            <ol className="dots" aria-label="Jump to a panel">
              {issue.panels.map((p, i) => (
                <li key={p.id}>
                  <button
                    type="button"
                    className={i === index ? 'dot active' : 'dot'}
                    aria-label={`Panel ${i + 1}`}
                    aria-current={i === index ? 'step' : undefined}
                    onClick={() => go(i)}
                  />
                </li>
              ))}
            </ol>
            <button type="button" className="btn btn-primary nav-btn" onClick={() => go(index + 1)} disabled={atEnd}>
              {index === total - 1 ? 'Finish' : 'Next'} <span aria-hidden="true">▶</span>
            </button>
          </div>
          <p className="reader-hint">Tip: use the arrow keys, or swipe left and right on a phone or tablet.</p>
        </>
      ) : (
        <ol className="page-grid">
          {issue.panels.map((p, i) => (
            <li key={p.id}>
              <PanelView panel={p} number={i + 1} total={total} eager={false} />
              <button type="button" className="btn btn-small" onClick={() => openPanel(i)}>
                Open panel {i + 1}
              </button>
            </li>
          ))}
        </ol>
      )}
    </section>
  );
}
