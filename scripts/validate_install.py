#!/usr/bin/env python3
"""Validate a complete Design Engineering installation, not a detached SKILL.md."""
import argparse, json, os, subprocess, sys
from pathlib import Path

REQUIRED_FILES = (
    "SKILL.md", "pyproject.toml", "scripts/de.py", "design_engineering/cli.py", "design_engineering/local_knowledge.py", "scripts/knowledge_index.py", "knowledge/catalog.json",
    "knowledge/sources.json", "knowledge/concepts.json", "knowledge/claims.json", "knowledge/governance.json",
)
REQUIRED_DIRS = ("knowledge/cards", "methods", "templates")

def inspect(root):
    root=Path(root).expanduser().resolve()
    files={}
    for p in REQUIRED_FILES:
        target=root/p
        # Wheel bundles all canonical data under design_engineering/_bundled,
        # while CLI code lives in the parent installed Python package.
        if not target.is_file() and root.name=="_bundled" and root.parent.name=="design_engineering" and p.startswith("design_engineering/"):
            target=root.parent/p.split("/",1)[1]
        files[p]=target.is_file()
    directories={p:(root/p).is_dir() for p in REQUIRED_DIRS}
    skill=root/"SKILL.md"
    size=skill.stat().st_size if skill.is_file() else None
    return {"root":str(root),"skill_bytes":size,"files":files,"directories":directories,
            "complete":all(files.values()) and all(directories.values())}

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--root",default=os.environ.get("CLAUDE_PLUGIN_ROOT") or str(Path(__file__).resolve().parents[1]))
    p.add_argument("--smoke",action="store_true",help="Rebuild index and execute a Korean question")
    p.add_argument("--json",action="store_true")
    a=p.parse_args()
    report=inspect(a.root)
    if a.smoke and report["complete"]:
        base=Path(report["root"])
        results=[]
        for argv in (
            [sys.executable,str(base/"scripts/knowledge_index.py"),"rebuild"],
            [sys.executable,str(base/"scripts/knowledge_index.py"),"search","한글 폰트 줄바꿈과 타이포그래피","--top","5","--json"],
        ):
            x=subprocess.run(argv,cwd=base,text=True,capture_output=True,timeout=90)
            results.append({"command":argv[2:],"returncode":x.returncode,
                            "stdout":x.stdout[-3500:],"stderr":x.stderr[-1200:]})
            if x.returncode:break
        report["smoke"]=results
        report["complete"]=report["complete"] and len(results)==2 and all(x["returncode"]==0 for x in results)
    elif a.smoke:
        report["smoke"]=[];report["error"]="Incomplete installation; no Knowledge commands executed"
    if a.json:print(json.dumps(report,ensure_ascii=False,indent=2))
    else:
        print("Skill root:",report["root"])
        print("SKILL.md bytes:",report["skill_bytes"])
        for key in ("files","directories"):
            for name,ok in report[key].items():print(("OK " if ok else "MISSING ")+name)
        for item in report.get("smoke",[]):print("Smoke",item["command"],"exit",item["returncode"],item["stderr"][-300:])
        print("COMPLETE" if report["complete"] else "INCOMPLETE")
    return 0 if report["complete"] else 1

if __name__=="__main__":sys.exit(main())
