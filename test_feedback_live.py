import urllib.request
import json

url = 'https://bizflow-platform.vercel.app/api/leadradar/feedback'
payload = {
    'user_name': 'Alex Morgan (AgencyFlow)',
    'email_or_contact': 'alex@agencyflow.io',
    'niche': 'Web Dev & Next.js',
    'rating': 5,
    'lead_quality_score': 'excellent',
    'missing_community': 'r/freelance_forhire',
    'willingness_to_pay': 'yes',
    'feedback_text': 'This is 10x better than scraping Apollo cold emails. The Tri-Box verified stream saves me 2 hours daily.'
}

req = urllib.request.Request(
    url,
    data=json.dumps(payload).encode('utf-8'),
    headers={'Content-Type': 'application/json', 'User-Agent': 'BizFlowTester/2.0'},
    method='POST'
)

with urllib.request.urlopen(req) as resp:
    res = json.loads(resp.read().decode('utf-8'))
    print('POST RESPONSE:', res)

get_req = urllib.request.Request(url, headers={'User-Agent': 'BizFlowTester/2.0'})
with urllib.request.urlopen(get_req) as resp:
    get_res = json.loads(resp.read().decode('utf-8'))
    print('GET ALL FEEDBACKS:', get_res)
