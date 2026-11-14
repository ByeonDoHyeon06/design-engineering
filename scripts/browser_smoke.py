#!/usr/bin/env python3
"""Optional Playwright viewport smoke test. Screenshots, overflow and JS errors only.

Requires: pip install playwright; playwright install chromium
Usage: python scripts/browser_smoke.py /path/page.html --out /tmp/page-review
Does NOT assess WCAG, perceived aesthetics, UI behavior, or mobile usability.
"""
import argparse
import json
from pathlib import Path
import sys


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('html_file',type=Path)
    parser.add_argument('--out',type=Path,default=Path('/tmp/design-engineering-qa'))
    parser.add_argument('--widths',type=int,nargs='+',default=[1440,390,320])
    parser.add_argument('--height',type=int,default=900)
    args=parser.parse_args()
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print('NOT TESTED: Playwright is unavailable. Install playwright and a compatible browser, or inspect manually.', file=sys.stderr)
        return 2
    target=args.html_file.resolve()
    if not target.is_file():
        print('File not found: '+str(target),file=sys.stderr)
        return 2
    args.out.mkdir(parents=True,exist_ok=True)
    results=[]
    try:
        with sync_playwright() as pw:
            try:
                browser=pw.chromium.launch(headless=True)
            except Exception:
                system_chromium=Path('/usr/bin/chromium')
                if not system_chromium.is_file():
                    raise
                browser=pw.chromium.launch(headless=True, executable_path=str(system_chromium), args=['--no-sandbox'])
            for width in args.widths:
                context=browser.new_context(viewport={'width':width,'height':args.height}, reduced_motion='reduce')
                page=context.new_page()
                errors=[]
                page.on('pageerror',lambda exc: errors.append(str(exc)))
                # Feed standalone HTML into a fresh document to support sandboxes that deny file://.
                # Relative assets/links are not validated by this test; use a local server for those.
                page.set_content(target.read_text(encoding='utf-8'),wait_until='load')
                render_mode='inline_html_relative_assets_not_verified'
                page.screenshot(path=str(args.out/f'viewport-{width}.png'),full_page=True,animations='disabled')
                dims=page.evaluate('''() => ({width:innerWidth,docWidth:document.documentElement.scrollWidth,bodyWidth:document.body.scrollWidth,height:document.documentElement.scrollHeight})''')
                overflow=max(dims['docWidth'],dims['bodyWidth'])>dims['width']+1
                results.append({'viewport_width':width,'measurements':dims,'horizontal_overflow':overflow,'uncaught_js_errors':errors,'render_mode':render_mode,'screenshot':f'viewport-{width}.png'})
                context.close()
            browser.close()
    except Exception as exc:
        print('NOT TESTED: browser could not run: '+str(exc),file=sys.stderr)
        return 2
    report={'target':str(target),'scope':'screenshots + horizontal overflow + uncaught JS errors ONLY','results':results}
    (args.out/'smoke.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(report,ensure_ascii=False,indent=2))
    return 1 if any(x['horizontal_overflow'] or x['uncaught_js_errors'] for x in results) else 0

if __name__=='__main__': raise SystemExit(main())
