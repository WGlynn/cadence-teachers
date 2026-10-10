"""Publish the Atlas to Vercel (https://cadence-atlas.vercel.app) and verify the live site matches the local build.

What gets published:
  - site/ (the React + three.js web app) when it exists: `npm run build` (which first syncs experiments/atlas.json
    into the app), then site/dist is deployed.
  - otherwise the static experiments/ATLAS.html (with .md links pointed at GitHub).
The static ATLAS.html is still built by build_atlas.py either way; it stays the offline / GitHub Pages copy.

Called automatically at the end of build_atlas.py when this checkout is linked to the Vercel project
(.vercel-atlas/.vercel exists); contributors without the link skip it. Set ATLAS_NO_PUBLISH=1 to skip.
Exits non-zero if the build, the deploy or the live check fails, so a stale site never passes silently."""
import hashlib, os, re, shutil, subprocess, sys, time, urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "experiments", "ATLAS.html")
SITE = os.path.join(ROOT, "site")
DEPLOY = os.path.join(ROOT, ".vercel-atlas")
URL = "https://cadence-atlas.vercel.app/"
GH = "https://github.com/WGlynn/cadence-teachers/blob/main/"
KEEP = {".vercel", ".gitignore"}          # deploy-dir entries that are config, not content


def linked():
    return os.path.isdir(os.path.join(DEPLOY, ".vercel"))


def _fetch(url):
    return urllib.request.urlopen(url, timeout=30).read()


def _clear_deploy_dir():
    for name in os.listdir(DEPLOY):
        if name in KEEP:
            continue
        p = os.path.join(DEPLOY, name)
        shutil.rmtree(p) if os.path.isdir(p) else os.remove(p)


def _stage_app():
    """Build the web app and copy site/dist into the deploy dir."""
    r = subprocess.run("npm run build", cwd=SITE, shell=True, capture_output=True, text=True)
    if r.returncode != 0:
        sys.exit("ATLAS PUBLISH FAILED: site build exited %d\n%s" % (r.returncode, (r.stdout + r.stderr)[-3000:]))
    dist = os.path.join(SITE, "dist")
    _clear_deploy_dir()
    for name in os.listdir(dist):
        s, d = os.path.join(dist, name), os.path.join(DEPLOY, name)
        shutil.copytree(s, d) if os.path.isdir(s) else shutil.copy2(s, d)


def _stage_static():
    html = open(SRC, encoding="utf-8").read()
    # .md links open as rendered GitHub pages instead of raw downloads
    html = re.sub(r'href="(EXP-\d+[a-z]?\.md)"', r'href="%sexperiments/\1"' % GH, html)
    html = html.replace('href="../VS-TRANSFER-PROGRAM.md"', 'href="%sVS-TRANSFER-PROGRAM.md"' % GH)
    _clear_deploy_dir()
    with open(os.path.join(DEPLOY, "index.html"), "w", encoding="utf-8", newline="") as f:
        f.write(html)


def publish():
    app = os.path.isfile(os.path.join(SITE, "package.json"))
    _stage_app() if app else _stage_static()
    index = open(os.path.join(DEPLOY, "index.html"), "rb").read()
    want = hashlib.sha256(index).hexdigest()  # hash the exact bytes that get deployed
    # the app's index references hashed bundles; the live check fetches one of them too
    asset = re.search(rb'src="(/assets/[^"]+\.js)"', index)
    vercel = shutil.which("vercel") or shutil.which("vercel.cmd")
    r = subprocess.run([vercel, "deploy", "--prod", "--yes"], cwd=DEPLOY, capture_output=True, text=True)
    if r.returncode != 0:
        sys.exit("ATLAS PUBLISH FAILED: vercel deploy exited %d\n%s" % (r.returncode, r.stderr[-2000:]))
    for _ in range(8):  # the alias can lag a few seconds behind the deploy
        live = _fetch(URL + "?v=" + want[:8])
        if hashlib.sha256(live).hexdigest() == want:
            if asset:
                local = open(os.path.join(DEPLOY, asset.group(1).decode().lstrip("/")), "rb").read()
                if _fetch(URL.rstrip("/") + asset.group(1).decode()) != local:
                    sys.exit("ATLAS PUBLISH FAILED: live bundle %s differs from the build" % asset.group(1).decode())
            print("published + verified: %s matches local %s build (sha %s)" % (URL, "app" if app else "static", want[:12]))
            return
        time.sleep(5)
    sys.exit("ATLAS PUBLISH FAILED: live page at %s does not match the local build" % URL)


if __name__ == "__main__":
    if not linked():
        sys.exit("not linked to the Vercel project (.vercel-atlas/.vercel missing); nothing to publish")
    publish()
