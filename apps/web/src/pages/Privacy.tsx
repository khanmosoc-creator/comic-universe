import { Link } from '../lib/router';
import { usePageMeta } from '../lib/usePageMeta';

const UPDATED = 'November 9, 2026';

export function Privacy() {
  usePageMeta('Privacy policy', 'Plain-language privacy policy for Super Zayd’s Maze Guardians.');
  return (
    <section className="section section--cream page-top">
      <div className="wrap prose">
        <p className="kicker">Privacy</p>
        <h1 className="page-title">Privacy policy</h1>
        <p className="meta-line">Last updated: {UPDATED}</p>

        <div className="kid-box">
          <h2>The short version (for kids)</h2>
          <p>
            This website is for reading comics. It never asks for your name, your email, your photo or anything else about you.
            There is nothing to sign up for and nothing to type in. Just read and have fun!
          </p>
        </div>

        <h2>What this website is</h2>
        <p>
          Super Zayd's Maze Guardians is a free comic website for children and families. It is a “static” website: the same
          pages, pictures and stories are sent to everyone, and nothing on the site changes based on who is reading.
        </p>

        <h2>What we do not collect</h2>
        <p>We do not ask for, collect or keep personal information from readers. In particular, the website has:</p>
        <ul>
          <li>no accounts, logins, sign-ups or reader profiles;</li>
          <li>no forms, comments, chat, uploads or newsletter sign-ups;</li>
          <li>no advertising and no behavioural profiling;</li>
          <li>no analytics tools, tracking pixels, or social media buttons or embeds;</li>
          <li>no cookies set by this website, and nothing saved in your browser's storage;</li>
          <li>no AI chat or AI picture tools for readers.</li>
        </ul>
        <p>
          The pictures, fonts and code all load from this website itself. The website does not ask your browser to contact other
          companies while you read.
        </p>

        <h2>Information handled by our hosting provider</h2>
        <p>
          Like every website, this one has to be delivered over the internet. It is hosted on <strong>Cloudflare Pages</strong>.
          When your device asks for a page, Cloudflare's systems automatically receive standard technical information that any
          web server receives — such as your device's IP address, the browser type, the page requested and the time of the
          request. Cloudflare uses this to deliver the pages and to protect the site from attacks and abuse, and may keep it in
          its logs for a limited time under its own policies. Cloudflare may also set strictly necessary security cookies if it
          detects suspicious traffic.
        </p>
        <p>
          We have not turned on Cloudflare's optional Web Analytics for this website, and we do not use this technical
          information to identify, profile or contact readers. You can read how Cloudflare handles this information in the{' '}
          <a href="https://www.cloudflare.com/privacypolicy/" rel="noopener noreferrer">
            Cloudflare Privacy Policy
          </a>{' '}
          (this link leaves our website).
        </p>

        <h2>Other providers</h2>
        <p>
          The website's source code is stored on GitHub so we can build and publish it. GitHub is not involved when you read the
          comic and does not receive information about readers from this website.
        </p>

        <h2>Children's privacy</h2>
        <p>
          This website is designed for children. Because it offers no way to submit information, we do not knowingly collect
          personal information from children. If we ever add a feature that would collect information from readers, we will
          update this policy first and follow the law that applies — including, in the United States, the Children's Online
          Privacy Protection Act (COPPA), which can require a parent's permission before any information is collected from a
          child under 13.
        </p>

        <h2>Changes to this policy</h2>
        <p>
          If anything about how the website works changes, we will update this page and change the “Last updated” date at the
          top.
        </p>

        <h2>Contact</h2>
        <p>
          The website does not currently offer a contact form, so that it doesn't collect any messages from readers. A business
          contact address for parents and guardians will be listed on this page as soon as one is available.
        </p>

        <p>
          <Link to="/" className="btn">
            Back to the comic
          </Link>
        </p>
      </div>
    </section>
  );
}
