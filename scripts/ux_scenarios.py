#!/usr/bin/env python3
"""Run scripted user-task checks in Chromium. Scripted checks != user study.

Each scenario specifies a goal, a success criterion, and browser actions.
No task-completion claim can be made when the scenario does not define an
observable assertion.
"""
import argparse,json,sys
from pathlib import Path

ACTIONS={'click','fill','press','assert_visible','assert_hidden','assert_text','assert_url_fragment',
         'assert_focused','assert_no_overflow','assert_count','assert_attribute','assert_in_viewport','assert_not_obscured'}


def validate(spec):
    errors=[]
    if not isinstance(spec.get('scenarios'),list) or not spec['scenarios']:
        errors.append('At least one scenario required')
    ids=set()
    for i,sc in enumerate(spec.get('scenarios',[])):
        where=f'scenarios[{i}]'
        if sc.get('id') in ids or not sc.get('id'):errors.append(where+': missing/duplicate id')
        ids.add(sc.get('id'))
        for field in ['user_goal','success_criterion']:
            if not sc.get(field):errors.append(where+': missing '+field)
        if not any(s.get('action','').startswith('assert_') for s in sc.get('steps',[])):
            errors.append(where+': no observable assertion')
        for j,s in enumerate(sc.get('steps',[])):
            if s.get('action') not in ACTIONS:errors.append(where+': invalid step action at '+str(j))
    return errors


def _browser(pw):
    try:return pw.chromium.launch(headless=True)
    except Exception:
        if Path('/usr/bin/chromium').is_file():
            return pw.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox'])
        raise


def exercise(target,scenario_file,out,viewport=390):
    from playwright.sync_api import sync_playwright
    target=Path(target).resolve()
    spec=json.loads(Path(scenario_file).read_text(encoding='utf-8'))
    errs=validate(spec)
    if errs:raise ValueError('Invalid scenario specification: '+'; '.join(errs))
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    results=[]
    with sync_playwright() as pw:
        browser=_browser(pw)
        try:
            for sc in spec['scenarios']:
                context=browser.new_context(viewport={'width':viewport,'height':900},reduced_motion='reduce')
                page=context.new_page();js_errors=[]
                page.on('pageerror',lambda err:js_errors.append(str(err)))
                page.set_content(target.read_text(encoding='utf-8'),wait_until='load')
                records=[];success=True
                for step in sc['steps']:
                    action=step['action'];sel=step.get('selector','');value=step.get('value','')
                    record={'action':action,'selector':sel,'expected':value}
                    try:
                        if action=='click':page.locator(sel).click(timeout=2500)
                        elif action=='fill':page.locator(sel).fill(value,timeout=2500)
                        elif action=='press':page.locator(sel).press(value,timeout=2500)
                        elif action=='assert_visible':assert page.locator(sel).is_visible(),'not visible'
                        elif action=='assert_hidden':assert page.locator(sel).is_hidden(),'not hidden'
                        elif action=='assert_text':assert value in page.locator(sel).inner_text(timeout=2000),'text not found'
                        elif action=='assert_url_fragment':assert page.evaluate('location.hash')==value,'hash mismatch'
                        elif action=='assert_focused':assert page.locator(sel).evaluate('(el)=>el===document.activeElement'),'focus mismatch'
                        elif action=='assert_no_overflow':
                            assert page.evaluate('document.documentElement.scrollWidth <= innerWidth + 1'),'horizontal overflow'
                        elif action=='assert_count':assert page.locator(sel).count()==int(value),'count mismatch'
                        elif action=='assert_in_viewport':
                            in_view=page.locator(sel).evaluate('''el => {let r=el.getBoundingClientRect(); return r.top>=0 && r.left>=0 && r.top<innerHeight && r.left<innerWidth;}''')
                            assert in_view,'target does not appear in visible viewport'
                        elif action=='assert_not_obscured':
                            unobscured=page.locator(sel).evaluate('''el => {let r=el.getBoundingClientRect(); let x=Math.min(innerWidth-1,Math.max(0,r.left+Math.min(r.width/2,25))); let y=Math.min(innerHeight-1,Math.max(0,r.top+4)); let top=document.elementFromPoint(x,y); return r.top>=0 && top && (el===top || el.contains(top));}''')
                            assert unobscured,'target appears obscured or above viewport'
                        elif action=='assert_attribute':
                            assert page.locator(sel).get_attribute(step['attribute'])==value,'attribute mismatch'
                        record['status']='passed'
                    except Exception as exc:
                        record['status']='failed';record['detail']=str(exc)[:320];success=False
                    records.append(record)
                    if not success:break
                name=f"task-{sc['id']}-{viewport}.png";page.screenshot(path=str(out/name),full_page=False,animations='disabled')
                results.append({'id':sc['id'],'user_goal':sc['user_goal'],
                  'success_criterion':sc['success_criterion'],'outcome':'pass' if success and not js_errors else 'fail',
                  'steps':records,'js_errors':js_errors,'screenshot':name,
                  'scope':'Scripted DOM/browser assertions, NOT representative participant task success'})
                context.close()
        finally:browser.close()
    report={'source':str(target),'width':viewport,'testing_mode':'scripted_browser_not_user_study','results':results,
            'limitations':['No real human participant','Only specified assertions were checked','No independent screen reader test']}
    (out/'ux-results.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    return report


def main():
    ap=argparse.ArgumentParser(description=__doc__);sub=ap.add_subparsers(dest='cmd',required=True)
    a=sub.add_parser('validate');a.add_argument('scenarios')
    b=sub.add_parser('run');b.add_argument('html');b.add_argument('scenarios');b.add_argument('--out',required=True);b.add_argument('--width',type=int,default=390)
    args=ap.parse_args()
    if args.cmd=='validate':
        errors=validate(json.loads(Path(args.scenarios).read_text(encoding='utf8')))
        print(json.dumps({'ok':not errors,'errors':errors},ensure_ascii=False,indent=2));raise SystemExit(bool(errors))
    try:report=exercise(args.html,args.scenarios,args.out,args.width)
    except Exception as exc:
        print('NOT TESTED:',str(exc),file=sys.stderr);raise SystemExit(2)
    print(json.dumps(report,ensure_ascii=False,indent=2));raise SystemExit(any(s['outcome']!='pass' for s in report['results']))
if __name__=='__main__':main()
