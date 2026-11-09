import { Link } from '../lib/router';
import { usePageMeta } from '../lib/usePageMeta';

export function About() {
  usePageMeta('About & credits', 'About Super Zayd’s Maze Guardians: how the comic is made, credits and a note for grown-ups.');
  return (
    <section className="section section--cream page-top">
      <div className="wrap prose">
        <p className="kicker">About</p>
        <h1 className="page-title">About the comic</h1>
        <p className="lead">
          Super Zayd's Maze Guardians is an original superhero comic for kids and families about five friends who keep the
          glowing Mazeverse from getting scrambled. It is all about teamwork, kindness, silly jokes and finding your way.
        </p>

        <h2>How the art is made</h2>
        <p>Every issue mixes two kinds of artwork, and the comic tells you which is which:</p>
        <ul>
          <li>
            <strong>Original sketches.</strong> Hand drawings supplied by the comic's creators. They appear exactly as drawn — only
            trimmed and resized — and are marked “Original sketch” in the reader. You can see them all in the{' '}
            <Link to="/art-vault">Art Vault</Link>.
          </li>
          <li>
            <strong>Studio art.</strong> The character portraits, the cover and the other story panels were made with AI help as
            original vector drawings, created offline and then chosen by the comic's owner. No other comic's characters, costumes or
            logos are used.
          </li>
        </ul>

        <h2>Credits</h2>
        <ul>
          <li>Story, characters and the Mazeverse: the Super Zayd's Maze Guardians team.</li>
          <li>Original sketches: the Maze Guardians junior art department.</li>
          <li>Studio art: AI-assisted vector illustrations, reviewed by the owner.</li>
          <li>
            Lettering font: Poppins by the Poppins Project Authors, used under the SIL Open Font License 1.1 (the{' '}
            <a href="/fonts/OFL.txt">license text</a> is included with this site).
          </li>
        </ul>

        <h2>A note for parents and grown-ups</h2>
        <ul>
          <li>There are no ads, no accounts, no sign-ups, no chat, no comments and nothing to upload or submit.</li>
          <li>We don't use analytics, tracking pixels or social media widgets, and the site doesn't set cookies.</li>
          <li>Pictures and fonts are all served from this website itself, not from other companies.</li>
          <li>The stories are gentle: villains get bonked, bounced and splashed — nobody gets hurt.</li>
        </ul>
        <p>
          Read the full <Link to="/privacy">privacy policy</Link> for the details, including what our hosting provider handles to
          keep the site running.
        </p>
      </div>
    </section>
  );
}
