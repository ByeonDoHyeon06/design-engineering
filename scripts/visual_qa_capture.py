#!/usr/bin/env python3
"""Screenshot + geometric smoke evidence. Playwright required. NOT a UX/a11y certification.

Example: python scripts/visual_qa_capture.py page.html --out /tmp/page-qa
Captures equal-condition viewport & full-page renders (1440/390/320) and sticky anchor checks.
"""
import argparse, json, sys
from pathlib import Path


def run(target, out, widths=(1440,390,320), height=900):
    try: from playwright.sync_api import sync_playwright
    except ImportError:
        raise RuntimeError('Playwright unavailable: pip install playwright && playwright install chromium')
    target=Path(target).resolve()
    if not target.is_file(): raise FileNotFoundError(target)
    out=Path(out); out.mkdir(parents=True,exist_ok=True)
    reports=[]
    with sync_playwright() as pw:
        try: browser=pw.chromium.launch(headless=True)
        except Exception:
            p=Path('/usr/bin/chromium')
            if not p.is_file(): raise
            browser=pw.chromium.launch(executable_path=str(p),headless=True,args=['--no-sandbox'])
        for width in widths:
            ctx=browser.new_context(viewport={'width':width,'height':height}, reduced_motion='reduce',device_scale_factor=1)
            page=ctx.new_page(); errors=[]
            page.on('pageerror', lambda e: errors.append(str(e)))
            # Inline render works in hosted sandboxes blocking file://. Relative/external assets are not verified.
            page.set_content(target.read_text(encoding='utf8'),wait_until='load')
            page.evaluate('document.fonts.ready')
            page.screenshot(path=str(out/f'{width}-viewport.png'),full_page=False,animations='disabled')
            page.screenshot(path=str(out/f'{width}-full.png'),full_page=True,animations='disabled')
            metrics=page.evaluate('''() => ({viewport: innerWidth, doc:document.documentElement.scrollWidth,
              body: document.body.scrollWidth, height:document.documentElement.scrollHeight,
              stickyHeaders:[...document.querySelectorAll('header')].filter(h=>['sticky','fixed'].includes(getComputedStyle(h).position))
                .map(h=>({selector:h.id||h.className||'header',height:Math.round(h.getBoundingClientRect().height)}))})''')
            issues=[]
            # Only physically meaningful observation is 'anchor heading hidden under a header', not mere CSS offset arithmetic.
            for section in page.locator('section[id]').all()[:10]:
                sid=section.get_attribute('id');
                if not sid: continue
                section.evaluate('(node)=>node.scrollIntoView({block:"start",behavior:"instant"})')
                landing=page.evaluate('''(id)=>{let el=document.getElementById(id),r=el.getBoundingClientRect();
                  let heads=[...document.querySelectorAll('header')].filter(h=>['sticky','fixed'].includes(getComputedStyle(h).position));
                  let bottom=Math.max(0,...heads.map(h=>h.getBoundingClientRect().bottom));
                  return {sectionTop:Math.round(r.top),headerBottom:Math.round(bottom),overlap:Math.round(Math.max(0,bottom-r.top))};}''',sid)
                if landing['overlap']>2 and abs(landing['sectionTop'])<1000:
                    issues.append({'id':sid,'type':'anchor_header_overlap_review','metrics':landing})
            reports.append({'width':width,'measurements':metrics,'horizontal_overflow':max(metrics['doc'],metrics['body'])>width+1,
              'js_errors':errors,'anchor_review':issues,'screenshots':[f'{width}-viewport.png',f'{width}-full.png'],
              'limitations':'Does not test interaction, accessibility, external assets, user aesthetic ratings or screen-reader operation.'})
            ctx.close()
        browser.close()
    report={'source':str(target),'scope':'inline HTML render geometry + screenshots + page JS errors only; external/relative assets NOT verified','results':reports}
    (out/'visual-qa.json').write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n',encoding='utf8')
    return report


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('file'); parser.add_argument('--out',default='/tmp/design-engineering-visual-qa')
    parser.add_argument('--height',type=int,default=900)
    args=parser.parse_args()
    try: report=run(args.file,args.out,height=args.height)
    except Exception as e:
        print(f'NOT_TESTED: {e}',file=sys.stderr); return 2
    print(json.dumps(report,indent=2,ensure_ascii=False))
    return 1 if any(x['horizontal_overflow'] or x['js_errors'] or x['anchor_review'] for x in report['results']) else 0

if __name__=='__main__': raise SystemExit(main())
