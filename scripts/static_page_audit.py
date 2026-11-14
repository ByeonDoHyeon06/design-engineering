#!/usr/bin/env python3
"""Conservative HTML IA/navigation triage. Not a validator or WCAG audit.

Usage: python scripts/static_page_audit.py page.html [--json]
Exit code 1 only for definite structural defects (duplicate IDs, broken local anchors).
Review warnings are not failures. No network or third-party dependencies.
"""
import argparse
from collections import Counter, defaultdict
from html.parser import HTMLParser
import json
from pathlib import Path
import re

CONTAINERS = {'main', 'section', 'article', 'nav', 'header', 'footer'}
TEXT_TAGS = {'h1', 'h2', 'h3', 'p'}

class PageParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.ids = []
        self.anchors = []
        self.heading_texts = []
        self.paragraphs = []
        self.landmarks = Counter()
        self.containers = []
        self.current_text = None
        self.has_skip = False

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if attrs.get('id'):
            self.ids.append(attrs['id'])
        if tag in CONTAINERS:
            ident = attrs.get('id') or f'{tag}#{len(self.containers)+1}'
            self.containers.append((tag, ident))
            if tag in {'main', 'nav'}:
                self.landmarks[tag] += 1
        if tag == 'a':
            href = attrs.get('href', '')
            if href.startswith('#') and len(href) > 1:
                self.anchors.append(href[1:])
                if re.search(r'^(main|content|본문)', href[1:], flags=re.I) or 'skip' in attrs.get('class',''):
                    self.has_skip = True
        if tag in TEXT_TAGS:
            self.current_text = {'tag': tag, 'value': [], 'context': '/'.join(f'{t}:{ident}' for t,ident in self.containers) or 'document'}

    def handle_data(self, data):
        if self.current_text is not None:
            self.current_text['value'].append(data)

    def handle_endtag(self, tag):
        if self.current_text is not None and tag == self.current_text['tag']:
            value = ' '.join(' '.join(self.current_text['value']).split())
            if value:
                item = (tag,value,self.current_text['context'])
                if tag == 'p': self.paragraphs.append(item)
                else: self.heading_texts.append(item)
            self.current_text = None
        if tag in CONTAINERS:
            for idx in range(len(self.containers)-1,-1,-1):
                if self.containers[idx][0] == tag:
                    del self.containers[idx:]
                    break

def audit(html):
    p=PageParser();p.feed(html)
    findings=[]
    def add(level,code,message,extra=None):
        obj={'level':level,'code':code,'message':message}
        if extra: obj['evidence']=extra
        findings.append(obj)
    for ident,count in Counter(p.ids).items():
        if count>1: add('ERROR','DUPLICATE_ID',f'ID #{ident} occurs {count} times')
    ids=set(p.ids)
    for ident in sorted(set(p.anchors)):
        if ident not in ids: add('ERROR','MISSING_ANCHOR',f'Internal anchor #{ident} has no target ID')
    if p.landmarks['main']==0: add('REVIEW','NO_MAIN','No <main> landmark observed; verify structure')
    if p.landmarks['main']>1: add('REVIEW','MULTIPLE_MAIN','Multiple <main> elements observed; verify semantics')
    if p.landmarks['nav'] and not p.has_skip:
        add('REVIEW','BYPASS_BLOCKS','No obvious skip link found; verify another operable bypass mechanism')
    for kind, items, minimum in [('HEADING',p.heading_texts,1),('PARAGRAPH',p.paragraphs,45)]:
        groups=defaultdict(list)
        for tag,value,context in items:
            if kind=='HEADING' and tag=='h1': continue
            if len(value)<minimum: continue
            norm=re.sub(r'\s+',' ',value.lower()).strip(' .,:·-/')
            groups[norm].append((tag,value,context))
        for group in groups.values():
            contexts={x[2] for x in group}
            if len(contexts)<2: continue
            name=group[0][1]
            add('REVIEW',f'REPEATED_{kind}',
                f'{kind.title()} repeated across {len(contexts)} contexts: {name[:110]}',
                [{'tag':t,'context':ctx} for t,_,ctx in group])
    return {'summary':{'ids':len(p.ids),'local_anchor_links':len(p.anchors),
                       'headings':len(p.heading_texts),'paragraphs':len(p.paragraphs),
                       'errors':sum(x['level']=='ERROR' for x in findings),
                       'review_items':sum(x['level']=='REVIEW' for x in findings)},
            'findings':findings}

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('html_file',type=Path)
    ap.add_argument('--json',action='store_true')
    args=ap.parse_args()
    result=audit(args.html_file.read_text(encoding='utf-8'))
    if args.json:
        print(json.dumps(result,ensure_ascii=False,indent=2))
    else:
        print('STATIC TRIAGE (not a browser/UX/WCAG test)')
        print(result['summary'])
        for x in result['findings']:
            print(f"{x['level']:>6} {x['code']}: {x['message']}")
        if not result['findings']: print('No static flags; dynamic behavior remains UNTESTED')
    return 1 if result['summary']['errors'] else 0

if __name__ == '__main__': raise SystemExit(main())
