#!/usr/bin/env python3
"""Pull GA4 and Search Console data for the site and print a content-performance summary.

Setup (once): a Google Cloud service account with the Analytics Data API and Search Console
API enabled, added as Viewer on the GA4 property and as restricted user in Search Console.
The key file stays outside the repository.

    pip install google-analytics-data google-api-python-client google-auth
    RNAF_GA_KEY=~/.local/config/rnaf-analytics/key.json python tools/analytics_report.py <GA4 property id>

Writes the raw CSVs next to the summary into the directory given with --out (default: a
temporary directory) and prints: monthly trends, top pages, top and reachable queries,
low-CTR pages, performance by content kind, and Insights without search traffic.

GA4 counts only visitors who accepted the consent dialog, so it is a sample; Search
Console is the number to make content decisions on.
"""
import argparse, collections, csv, datetime, os, pathlib, re, sys, tempfile

from google.oauth2 import service_account


def norm(p):
    p = re.sub(r"^https?://(www\.)?rnaforecast\.com", "", p).split("?")[0].split("#")[0]
    if p.endswith("/index.html"):
        p = p[:-10]
    if not p.endswith(".html") and not p.endswith("/"):
        p += "/"
    return p or "/"


def content_map(repo):
    """Every page and Insight by URL: kind and title, from the RST metadata."""
    meta = {}
    for f in (repo / "content" / "pages").glob("*.rst"):
        s = f.read_text(encoding="utf-8")
        g = lambda k: (re.search(r"^:%s:\s*(.*)$" % k, s, re.M) or [None, ""])[1].strip()
        url = "/" if g("slug") == "index" else f"/{g('slug')}/"
        meta[url] = dict(kind="home" if url == "/" else "page", title=s.splitlines()[0][:70], tags=[], date="")
    for f in (repo / "content" / "insights").glob("*.rst"):
        s = f.read_text(encoding="utf-8")
        g = lambda k: (re.search(r"^:%s:\s*(.*)$" % k, s, re.M) or [None, ""])[1].strip()
        if g("status") == "draft":
            continue
        meta[f"/insights/{g('slug')}/"] = dict(kind="insight", title=s.splitlines()[0][:70], tags=[], date=g("date"))
    return meta


def pull_ga(creds, prop, out, end):
    from google.analytics.data_v1beta import BetaAnalyticsDataClient
    from google.analytics.data_v1beta.types import DateRange, Dimension, Metric, OrderBy, RunReportRequest
    client = BetaAnalyticsDataClient(credentials=creds)

    def report(name, dims, mets, start, order=None):
        req = RunReportRequest(property=f"properties/{prop}", date_ranges=[DateRange(start_date=start, end_date=end)],
                               dimensions=[Dimension(name=d) for d in dims], metrics=[Metric(name=m) for m in mets], limit=100000,
                               order_bys=[OrderBy(metric=OrderBy.MetricOrderBy(metric_name=order), desc=True)] if order else None)
        resp = client.run_report(req)
        with open(out / f"ga_{name}.csv", "w", newline="") as f:
            w = csv.writer(f); w.writerow(dims + mets)
            for r in resp.rows:
                w.writerow([d.value for d in r.dimension_values] + [m.value for m in r.metric_values])

    y1 = (datetime.date.fromisoformat(end) - datetime.timedelta(days=365)).isoformat()
    y2 = (datetime.date.fromisoformat(end) - datetime.timedelta(days=730)).isoformat()
    report("pages_12m", ["pagePath"], ["screenPageViews", "activeUsers", "userEngagementDuration"], y1, "screenPageViews")
    report("sources_12m", ["sessionSource", "sessionMedium"], ["sessions", "activeUsers"], y1, "sessions")
    report("countries_12m", ["country"], ["activeUsers", "sessions"], y1, "activeUsers")
    report("monthly_24m", ["yearMonth"], ["activeUsers", "sessions", "screenPageViews"], y2)
    report("devices_12m", ["deviceCategory"], ["activeUsers"], y1, "activeUsers")


def pull_sc(creds, out, end):
    from googleapiclient.discovery import build
    sc = build("searchconsole", "v1", credentials=creds, cache_discovery=False)
    site = next((s["siteUrl"] for s in sc.sites().list().execute().get("siteEntry", []) if "rnaforecast" in s["siteUrl"]), None)
    if not site:
        sys.exit("the service account has no Search Console access")
    start = (datetime.date.fromisoformat(end) - datetime.timedelta(days=480)).isoformat()

    def query(name, dims):
        rows, start_row = [], 0
        while True:
            resp = sc.searchanalytics().query(siteUrl=site, body={"startDate": start, "endDate": end, "dimensions": dims, "rowLimit": 25000, "startRow": start_row}).execute()
            chunk = resp.get("rows", []); rows += chunk
            if len(chunk) < 25000:
                break
            start_row += 25000
        with open(out / f"sc_{name}.csv", "w", newline="") as f:
            w = csv.writer(f); w.writerow(dims + ["clicks", "impressions", "ctr", "position"])
            for r in rows:
                w.writerow(r["keys"] + [r["clicks"], r["impressions"], round(r["ctr"], 4), round(r["position"], 1)])

    query("pages_16m", ["page"]); query("queries_16m", ["query"]); query("monthly_16m", ["date"])


def summarize(out, meta):
    rows = lambda name: list(csv.DictReader(open(out / name)))
    info = lambda p: meta.get(p.lower()) or dict(kind="other", title=p, tags=[], date="")
    print("=== GA4 monthly (users / sessions / pageviews) ===")
    for r in sorted(rows("ga_monthly_24m.csv"), key=lambda r: r["yearMonth"]):
        print(f"  {r['yearMonth']}  {int(r['activeUsers']):5}  {int(r['sessions']):5}  {int(r['screenPageViews']):6}")
    print("countries 12m:", ", ".join(f"{r['country']} {r['activeUsers']}" for r in rows("ga_countries_12m.csv")[:8]))
    print("sources 12m:", ", ".join(f"{r['sessionSource']}/{r['sessionMedium']} {r['sessions']}" for r in rows("ga_sources_12m.csv")[:6]))
    agg = collections.defaultdict(lambda: [0, 0, 0.0])
    for r in rows("ga_pages_12m.csv"):
        p = norm(r["pagePath"]); agg[p][0] += int(r["screenPageViews"]); agg[p][1] += int(r["activeUsers"]); agg[p][2] += float(r["userEngagementDuration"])
    print("\n=== GA4 top pages, 12 months ===")
    for p, (pv, u, eng) in sorted(agg.items(), key=lambda x: -x[1][0])[:25]:
        print(f"  {pv:6} views {u:6} users {eng/max(pv,1):5.0f} s  {info(p)['kind']:8} {p[:70]}")
    m = collections.defaultdict(lambda: [0, 0])
    for r in rows("sc_monthly_16m.csv"):
        m[r["date"][:7]][0] += int(r["clicks"]); m[r["date"][:7]][1] += int(r["impressions"])
    print("\n=== Search Console monthly clicks / impressions ===")
    for k in sorted(m):
        print(f"  {k}  clicks {m[k][0]:5}  impressions {m[k][1]:7}")
    sp = sorted([(norm(r["page"]), int(r["clicks"]), int(r["impressions"]), float(r["ctr"]), float(r["position"])) for r in rows("sc_pages_16m.csv")], key=lambda x: -x[1])
    print("\n=== Search Console top pages ===")
    for p, c, i, ctr, pos in sp[:25]:
        print(f"  {c:6} clicks {i:7} impr {100*ctr:4.1f}% pos {pos:5.1f}  {info(p)['kind']:8} {p[:65]}")
    print("\n=== many impressions, low CTR ===")
    for p, c, i, ctr, pos in sorted([x for x in sp if x[2] >= 300 and x[3] < 0.02], key=lambda x: -x[2])[:12]:
        print(f"  {c:6} clicks {i:7} impr {100*ctr:4.1f}% pos {pos:5.1f}  {p[:65]}")
    sq = [(r["query"], int(r["clicks"]), int(r["impressions"]), float(r["ctr"]), float(r["position"])) for r in rows("sc_queries_16m.csv")]
    print("\n=== top queries by clicks ===")
    for q, c, i, ctr, pos in sorted(sq, key=lambda x: -x[1])[:20]:
        print(f"  {c:5} {i:6} {100*ctr:4.1f}% {pos:5.1f}  {q}")
    print("\n=== queries with >=150 impressions ranking 4-20 ===")
    for q, c, i, ctr, pos in sorted([x for x in sq if x[2] >= 150 and 4 <= x[4] <= 20], key=lambda x: -x[2])[:20]:
        print(f"  {c:5} {i:6} {100*ctr:4.1f}% {pos:5.1f}  {q}")
    kind_agg, tag_agg = collections.defaultdict(lambda: [0, 0]), collections.defaultdict(lambda: [0, 0, 0])
    for p, c, i, ctr, pos in sp:
        inf = info(p); kind_agg[inf["kind"]][0] += c; kind_agg[inf["kind"]][1] += i
        for t in inf["tags"]:
            tag_agg[t][0] += c; tag_agg[t][1] += i; tag_agg[t][2] += 1
    print("\n=== clicks / impressions by content kind ===")
    for k, (c, i) in sorted(kind_agg.items(), key=lambda x: -x[1][0]):
        print(f"  kind {k:9} clicks {c:6} impressions {i:7}")
    clicks = {p: c for p, c, *_ in sp}
    insights = [p for p, i in meta.items() if i["kind"] == "insight"]
    dead = [p for p in insights if clicks.get(p, 0) <= 1]
    print(f"\n{len(dead)} of {len(insights)} Insights had at most one search click in 16 months")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("property_id"); ap.add_argument("--out", type=pathlib.Path)
    ap.add_argument("--key", default=os.environ.get("RNAF_GA_KEY"), help="service-account JSON (or $RNAF_GA_KEY)")
    a = ap.parse_args()
    if not a.key:
        sys.exit("give --key or set RNAF_GA_KEY")
    out = a.out or pathlib.Path(tempfile.mkdtemp(prefix="rnaf-analytics-")); out.mkdir(parents=True, exist_ok=True)
    creds = service_account.Credentials.from_service_account_file(os.path.expanduser(a.key), scopes=["https://www.googleapis.com/auth/analytics.readonly", "https://www.googleapis.com/auth/webmasters.readonly"])
    end = (datetime.date.today() - datetime.timedelta(days=3)).isoformat()
    pull_ga(creds, a.property_id, out, end); pull_sc(creds, out, end)
    summarize(out, content_map(pathlib.Path(__file__).resolve().parents[1]))
    print(f"\nraw CSVs in {out}")


if __name__ == "__main__":
    main()
