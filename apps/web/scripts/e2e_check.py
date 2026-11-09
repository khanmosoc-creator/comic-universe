"""End-to-end checks for the comic site — run against a local preview or the live Cloudflare URL.

  pip install playwright && playwright install chromium
  python3 scripts/e2e_check.py https://<project>.pages.dev /tmp/shots [path-to-chrome]

Checks every route (status, h1, images, console errors), the reader (buttons, arrow keys, dots, deep links,
end card, page view), focus management, cookies/storage, third-party requests and mobile layout.
"""
import json, sys
import os
from urllib.parse import urlparse
from playwright.sync_api import sync_playwright

BASE = sys.argv[1].rstrip('/')
SHOTS = sys.argv[2]
CHROME = sys.argv[3] if len(sys.argv) > 3 else None
os.makedirs(SHOTS, exist_ok=True)
host = urlparse(BASE).netloc
ROUTES = {
    '/': "SUPER ZAYD'S", '/heroes': 'THE MAZE GUARDIANS', '/heroes/zayd': 'SUPER ZAYD', '/heroes/dragoncrest': 'DRAGONCREST',
    '/heroes/arrowlight': 'ARROWLIGHT', '/heroes/bubbleguard': 'BUBBLEGUARD', '/heroes/zigzag': 'ZIGZAG',
    '/villains': 'VILLAINS OF THE MAZEVERSE', '/villains/grumblejaw': 'GRUMBLEJAW', '/villains/blizzardbyte': 'BLIZZARDBYTE',
    '/villains/splashfang': 'SPLASHFANG', '/universe': 'THE MAZEVERSE', '/art-vault': 'THE ART VAULT', '/about': 'ABOUT THE COMIC',
    '/privacy': 'PRIVACY POLICY', '/read': 'READ THE COMICS', '/read/issue-1': 'THE GREAT MAZE SCRAMBLE',
    '/read/issue-1?panel=8': 'THE GREAT MAZE SCRAMBLE', '/this-page-does-not-exist': 'WRONG TURN',
}
results, problems = [], []

with sync_playwright() as p:
    browser = p.chromium.launch(executable_path=CHROME, args=['--no-sandbox']) if CHROME else p.chromium.launch()
    ctx = browser.new_context(viewport={'width': 1280, 'height': 900})
    page = ctx.new_page()
    console, foreign = [], []
    page.on('console', lambda m: console.append(f'{m.type}: {m.text}') if m.type in ('error', 'warning') else None)
    page.on('pageerror', lambda e: console.append(f'pageerror: {e}'))
    page.on('request', lambda r: foreign.append(r.url) if urlparse(r.url).netloc not in (host, '') and not r.url.startswith('data:') else None)

    for route, expect in ROUTES.items():
        console.clear()
        resp = page.goto(BASE + route, wait_until='networkidle')
        h1 = page.locator('h1').first.inner_text().upper().replace('’', "'")
        # load lazy images too, then report any that fail to decode
        page.evaluate("document.querySelectorAll('img[loading=lazy]').forEach(i => i.loading = 'eager')")
        page.wait_for_load_state('networkidle')
        broken = page.evaluate("Promise.all([...document.images].map(i => i.decode().then(() => null, () => i.currentSrc || i.src))).then(r => r.filter(Boolean))")
        ok = resp.status == 200 and expect in h1 and not broken and not console
        results.append({'route': route, 'status': resp.status, 'h1': h1.replace('\n', ' '), 'brokenImages': broken, 'console': list(console), 'ok': ok})
        if not ok: problems.append(route)

    # Reader: buttons, keyboard, dots, URL sync, end card, page view
    page.goto(BASE + '/read/issue-1', wait_until='networkidle')
    count = lambda: page.locator('.reader-count').inner_text()
    seen = [count()]
    for _ in range(12):
        page.get_by_role('button', name='Next').or_(page.get_by_role('button', name='Finish')).first.click()
        page.wait_for_timeout(60)
        seen.append(count())
    reader = {'clickedThrough': seen, 'endCard': page.locator('.end-title').count() == 1, 'url': page.url}
    page.get_by_role('button', name='Read it again').click()
    page.keyboard.press('ArrowRight'); page.keyboard.press('ArrowRight')
    reader['afterTwoArrowRight'] = count()
    page.keyboard.press('ArrowLeft')
    reader['afterArrowLeft'] = count()
    page.get_by_role('button', name='Panel 7').click()
    reader['afterDot7'] = count(); reader['urlDot7'] = page.url
    page.get_by_role('button', name='Whole page').click()
    reader['pageViewPanels'] = page.locator('.page-grid .panel').count()
    page.wait_for_timeout(300)
    broken = page.evaluate("Promise.all([...document.images].map(i => i.decode().then(() => null, () => i.src))).then(r => r.filter(Boolean))")
    reader['pageViewBroken'] = broken
    page.get_by_role('button', name='Open panel 3').click()
    reader['afterOpen3'] = count()
    # Client-side nav moves focus to <main>
    page.get_by_role('navigation', name='Main').get_by_role('link', name='Heroes').click()
    page.wait_for_timeout(100)
    reader['focusAfterNav'] = page.evaluate('document.activeElement && document.activeElement.id')
    reader['pathAfterNav'] = urlparse(page.url).path
    reader['cookies'] = ctx.cookies()
    reader['storage'] = page.evaluate('[localStorage.length, sessionStorage.length]')
    page.goto(BASE + '/read/issue-1?panel=4', wait_until='networkidle')
    reader['deepLinkPanel4'] = count()
    page.screenshot(path=f'{SHOTS}/desktop-reader.png')
    page.goto(BASE + '/', wait_until='networkidle'); page.screenshot(path=f'{SHOTS}/desktop-home.png', full_page=True)
    page.goto(BASE + '/heroes/dragoncrest', wait_until='networkidle'); page.screenshot(path=f'{SHOTS}/desktop-hero.png', full_page=True)

    # Mobile
    m = browser.new_context(viewport={'width': 375, 'height': 812}, is_mobile=True, has_touch=True, device_scale_factor=2)
    mp = m.new_page()
    mobile = {}
    for route in ('/', '/read/issue-1', '/heroes/zayd', '/universe', '/privacy', '/art-vault'):
        mp.goto(BASE + route, wait_until='networkidle')
        mobile[route] = mp.evaluate('document.documentElement.scrollWidth <= window.innerWidth')
    mp.goto(BASE + '/', wait_until='networkidle')
    mp.get_by_role('button', name='Menu').click()
    mobile['menuExpanded'] = mp.get_by_role('button', name='Menu').get_attribute('aria-expanded')
    mp.screenshot(path=f'{SHOTS}/mobile-menu.png')
    mp.get_by_role('navigation', name='Main').get_by_role('link', name='Read #1').click()
    mp.wait_for_load_state('networkidle')
    mp.screenshot(path=f'{SHOTS}/mobile-reader.png', full_page=True)
    mp.goto(BASE + '/', wait_until='networkidle'); mp.screenshot(path=f'{SHOTS}/mobile-home.png', full_page=True)
    browser.close()

print(json.dumps({'routes': results, 'reader': reader, 'mobileNoHorizontalScroll': mobile, 'foreignRequests': sorted(set(foreign)), 'problems': problems}, indent=1))
