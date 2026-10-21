"""Validate apps.yml and render the format expected by Frappe Docker."""

import json
import os
import pathlib
import re
import sys

def main():
    # apps.yml deliberately uses a small, explicit YAML subset so the
    # production runner needs only Python's standard library.
    branch = None
    apps = []
    for line in pathlib.Path("apps.yml").read_text().splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        match = re.fullmatch(r"frappe_branch: ([A-Za-z0-9._/-]+)", line)
        if match:
            branch = match.group(1)
            continue
        if line == "apps:":
            continue
        match = re.fullmatch(r"  - name: ([a-z][a-z0-9_]*)", line)
        if match:
            apps.append({"name": match.group(1)})
            continue
        match = re.fullmatch(r"    (url|ref): (\S+)", line)
        if match and apps and match.group(1) not in apps[-1]:
            apps[-1][match.group(1)] = match.group(2)
            continue
        raise ValueError(f"unsupported apps.yml line: {line!r}")
    if branch != "version-15":
        raise ValueError("apps.yml must target Frappe version-15")
    if not apps:
        raise ValueError("apps.yml needs a nonempty apps list")
    names = []
    output = []
    for app in apps:
        if not isinstance(app, dict) or set(app) != {"name", "url", "ref"}:
            raise ValueError("each app needs exactly name, url and ref")
        name, url, ref = (app[key] for key in ("name", "url", "ref"))
        if not isinstance(name, str) or not re.fullmatch(r"[a-z][a-z0-9_]*", name):
            raise ValueError(f"invalid app name: {name!r}")
        if name in names:
            raise ValueError(f"duplicate app: {name}")
        if not isinstance(url, str) or not re.fullmatch(r"https://github.com/[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", url):
            raise ValueError(f"invalid app URL for {name}")
        if not isinstance(ref, str):
            raise ValueError(f"invalid ref for {name}")
        if ref == "$GITHUB_SHA":
            commit = os.environ.get("GITHUB_SHA", "")
            if name != "elsakr_app" or not re.fullmatch(r"[0-9a-f]{40}", commit):
                raise ValueError("GITHUB_SHA must be a full commit SHA")
            # Bench clones branches. The image build verifies the fetched HEAD.
            ref = "main"
        elif not re.fullmatch(r"[A-Za-z0-9._/-]+", ref):
            raise ValueError(f"invalid ref for {name}")
        names.append(name)
        output.append({"url": url, "branch": ref})
    if names[0] != "erpnext" or names[-1] != "elsakr_app" or "arab_erp_theme" not in names:
        raise ValueError("app order must include erpnext, arab_erp_theme and elsakr_app")
    pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "apps.json").write_text(json.dumps(output, indent=2) + "\n")


if __name__ == "__main__":
    main()
