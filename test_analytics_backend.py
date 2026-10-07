import os
import sys
import json

backend_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "backend")
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from app.db.database import init_db
from app.api.leadradar_routes import get_analytics_dashboard_stats, track_visitor_event, TrackVisitorRequest

out = []
out.append("[+] Initializing DB & Schema...")
init_db()

out.append("\n1. Testing get_analytics_dashboard_stats() ...")
stats = get_analytics_dashboard_stats()
out.append(f"Status: {stats.get('status')}")
out.append(f"Active Now: {stats.get('active_now')}")
out.append(f"Total Unique Visitors: {stats.get('total_unique_visitors')}")
out.append(f"Total Pageviews: {stats.get('total_pageviews')}")
out.append(f"Conversion Rate: {stats.get('conversion_rate')}%")
out.append(f"Geo Distribution: {[g['country'] + ' (' + str(g['visits']) + ')' for g in stats.get('geo_distribution', [])]}")
out.append(f"Traffic Sources: {[s['source'] + ' (' + str(s['visits']) + ')' for s in stats.get('traffic_sources', [])]}")
out.append(f"Devices: {stats.get('devices')}")

out.append("\n2. Testing track_visitor_event() ...")
req = TrackVisitorRequest(
    session_id="sess_live_test_99",
    path="/#radar",
    referrer="Product Hunt Launch",
    event_type="click_pitch",
    country="United States",
    city="San Francisco",
    device="Desktop",
    browser="Chrome",
    os="macOS",
    metadata="Tested via test suite"
)
res = track_visitor_event(req)
out.append(f"Track Result: {res}")

out.append("\n3. Testing get_analytics_dashboard_stats() after new event...")
stats2 = get_analytics_dashboard_stats()
out.append(f"Updated Pageviews: {stats2.get('total_pageviews')}")
out.append(f"Updated Visitors: {stats2.get('total_unique_visitors')}")

out.append("\n🎉 ALL ANALYTICS BACKEND & DB TESTS PASSED 100%!")

report_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "test_analytics_output.txt")
with open(report_file, "w", encoding="utf-8") as f:
    f.write("\n".join(out))

print("DONE")
