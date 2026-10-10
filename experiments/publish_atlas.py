"""Publish ATLAS.html to Vercel (https://cadence-atlas.vercel.app) and verify the live page matches the local build.
Called automatically at the end of build_atlas.py when this checkout is linked to the Vercel project
(.vercel-atlas/.vercel exists); contributors without the link skip it. Set ATLAS_NO_PUBLISH=1 to skip.
Exits non-zero if the deploy or the live check fails, so a stale site never passes silently."""
import hashlib, os, re, shutil, subprocess, sys, time, urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "experiments", "ATLAS.html")
DEPLOY = os.path.join(ROOT, ".vercel-atlas")
URL = "https://cadence-atlas.vercel.app/"
GH = "https://github.com/WGlynn/cadence-teachers/blob/main/"


def linked():
    return os.path.isdir(os.path.join(DEPLOY, ".vercel"))


def publish():
    html = open(SRC, encoding="utf-8").read()
    # .md links open as rendered GitHub pages instead of raw downloads
    html = re.sub(r'href="(EXP-\d+[a-z]?\.md)"', r'href="%sexperiments/\1"' % GH, html)
    html = html.replace('href="../VS-TRANSFER-PROGRAM.md"', 'href="%sVS-TRANSFER-PROGRAM.md"' % GH)
    out = os.path.join(DEPLOY, "index.html")
    with open(out, "w", encoding="utf-8", newline="") as f:
        f.write(html)
    want = hashlib.sha256(open(out, "rb").read()).hexdigest()  # hash the exact bytes that get deployed
    vercel = shutil.which("vercel") or shutil.which("vercel.cmd")
    r = subprocess.run([vercel, "deploy", "--prod", "--yes"], cwd=DEPLOY, capture_output=True, text=True)
    if r.returncode != 0:
        sys.exit("ATLAS PUBLISH FAILED: vercel deploy exited %d\n%s" % (r.returncode, r.stderr[-2000:]))
    for _ in range(6):  # the alias can lag a few seconds behind the deploy
        live = urllib.request.urlopen(URL + "?v=" + want[:8], timeout=30).read()
        if hashlib.sha256(live).hexdigest() == want:
            print("published + verified: %s matches local build (sha %s)" % (URL, want[:12]))
            return
        time.sleep(5)
    sys.exit("ATLAS PUBLISH FAILED: live page at %s does not match the local build" % URL)


if __name__ == "__main__":
    if not linked():
        sys.exit("not linked to the Vercel project (.vercel-atlas/.vercel missing); nothing to publish")
    publish()
