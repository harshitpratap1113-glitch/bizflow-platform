import urllib.request
import json
import xml.etree.ElementTree as ET

subreddits = ['freelance', 'agency', 'SaaS', 'Entrepreneur', 'webdev']
queries = ['finding clients', 'lead generation', 'how to get clients', 'upwork']

print('='*60)
print('🔥 LIVE TARGET USERS NEEDING BIZFLOW LEADRADAR RIGHT NOW')
print('='*60)

for sub in subreddits:
    url = f'https://www.reddit.com/r/{sub}/search.rss?q=finding+clients+OR+lead+generation&restrict_sr=on&sort=new'
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) BizFlowResearch/2.0'})
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            xml_data = resp.read()
        root = ET.fromstring(xml_data)
        ns = {'atom': 'http://www.w3.org/2005/Atom'}
        entries = root.findall('atom:entry', ns)
        print(f'\n📌 Subreddit: r/{sub} (Found: {len(entries)} recent discussions)')
        for e in entries[:2]:
            title = e.find('atom:title', ns).text if e.find('atom:title', ns) is not None else ''
            link = e.find('atom:link', ns).attrib.get('href', '') if e.find('atom:link', ns) is not None else ''
            author = e.find('atom:author/atom:name', ns).text if e.find('atom:author/atom:name', ns) is not None else ''
            print(f'   • Title: {title}')
            print(f'     User to DM for feedback: {author}')
            print(f'     Direct Link: {link}')
    except Exception as err:
        pass
