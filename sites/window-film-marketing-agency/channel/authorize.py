#!/usr/bin/env python3
"""One-time YouTube authorization for publish.py.

    YT_CLIENT_ID=... YT_CLIENT_SECRET=... python3 authorize.py
        prints a Google sign-in link. Open it, pick the channel, click Allow. The browser then lands on
        a "can't connect to 127.0.0.1" page: that's expected. Copy that page's full address.
    python3 authorize.py '<the address you copied>'
        trades it for a refresh token. With GITLAB_TOKEN and GITLAB_PROJECT set (e.g. "you/your-project"),
        it saves YT_CLIENT_ID, YT_CLIENT_SECRET and YT_REFRESH_TOKEN as masked CI/CD variables in that
        project and never prints the token. Add --print to print it instead.

The address contains a one-time code that expires within minutes and is useless once exchanged.
Standard library only.
"""
import base64
import hashlib
import json
import os
import secrets
import sys
import urllib.error
import urllib.parse
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
STATE = os.path.join(HERE, ".auth-state.json")
REDIRECT = "http://127.0.0.1:8765/"
SCOPES = "https://www.googleapis.com/auth/youtube.upload https://www.googleapis.com/auth/youtube.readonly"
GITLAB = os.environ.get("GITLAB_URL", "https://gitlab.com")


def need(k):
    v = os.environ.get(k)
    if not v:
        sys.exit(f"{k} is not set")
    return v


def start():
    verifier = secrets.token_urlsafe(64)
    state = secrets.token_urlsafe(16)
    challenge = base64.urlsafe_b64encode(hashlib.sha256(verifier.encode()).digest()).rstrip(b"=").decode()
    json.dump({"verifier": verifier, "state": state}, open(STATE, "w"))
    os.chmod(STATE, 0o600)
    q = urllib.parse.urlencode({"client_id": need("YT_CLIENT_ID"), "redirect_uri": REDIRECT, "response_type": "code", "scope": SCOPES,
                                "access_type": "offline", "prompt": "consent", "state": state,
                                "code_challenge": challenge, "code_challenge_method": "S256"})
    print("Open this link, choose the YouTube channel and click Allow:\n")
    print("https://accounts.google.com/o/oauth2/v2/auth?" + q)


def finish(pasted):
    st = json.load(open(STATE))
    q = urllib.parse.parse_qs(urllib.parse.urlparse(pasted).query) if "://" in pasted else {"code": [pasted], "state": [st["state"]]}
    if "error" in q:
        sys.exit("Google returned: " + q["error"][0])
    if q.get("state", [""])[0] != st["state"]:
        sys.exit("That address is from a different sign-in attempt. Run authorize.py without arguments again.")
    body = urllib.parse.urlencode({"code": q["code"][0], "client_id": need("YT_CLIENT_ID"), "client_secret": need("YT_CLIENT_SECRET"),
                                   "redirect_uri": REDIRECT, "grant_type": "authorization_code", "code_verifier": st["verifier"]}).encode()
    try:
        with urllib.request.urlopen(urllib.request.Request("https://oauth2.googleapis.com/token", data=body)) as r:
            tok = json.load(r)
    except urllib.error.HTTPError as e:
        sys.exit(f"Google refused the code ({e.code}): {e.read()[:300].decode()}. Codes expire in minutes; start over.")
    os.remove(STATE)
    if "refresh_token" not in tok:
        sys.exit("No refresh token returned. Remove the app's access at myaccount.google.com/permissions and run again.")
    values = {"YT_CLIENT_ID": need("YT_CLIENT_ID"), "YT_CLIENT_SECRET": need("YT_CLIENT_SECRET"), "YT_REFRESH_TOKEN": tok["refresh_token"]}
    if "--print" in sys.argv:
        print(json.dumps(values, indent=1))
        return
    project = urllib.parse.quote(need("GITLAB_PROJECT"), safe="")
    for k, v in values.items():
        data = urllib.parse.urlencode({"key": k, "value": v, "masked": "true", "protected": "false"}).encode()
        h = {"PRIVATE-TOKEN": need("GITLAB_TOKEN")}
        base = f"{GITLAB}/api/v4/projects/{project}/variables"
        try:
            urllib.request.urlopen(urllib.request.Request(f"{base}/{k}", data=data, headers=h, method="PUT"))
        except urllib.error.HTTPError as e:
            if e.code != 404:
                sys.exit(f"GitLab refused {k} ({e.code}): {e.read()[:300].decode()}")
            urllib.request.urlopen(urllib.request.Request(base, data=data, headers=h, method="POST"))
        print(f"saved {k} to GitLab (masked)")
    print("Done. publish.py can now upload to this channel.")


if __name__ == "__main__":
    finish(sys.argv[1]) if len(sys.argv) > 1 and sys.argv[1] != "--print" else start()
