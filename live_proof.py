import urllib.request
import json
import xml.etree.ElementTree as ET

url = 'https://www.reddit.com/r/forhire+freelance_forhire+designjobs+SaaS+webdev/new.rss'
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) BizFlowRadar/2.0'})

try:
    with urllib.request.urlopen(req, timeout=12) as resp:
        xml_data = resp.read()
    root = ET.fromstring(xml_data)
    ns = {'atom': 'http://www.w3.org/2005/Atom'}
    entries = root.findall('atom:entry', ns)
    print(f'[*] TOTAL REAL POSTS ON REDDIT RIGHT NOW: {len(entries)}\n')
    for i, e in enumerate(entries[:5], 1):
        title = e.find('atom:title', ns).text if e.find('atom:title', ns) is not None else ''
        link = e.find('atom:link', ns).attrib.get('href', '') if e.find('atom:link', ns) is not None else ''
        author = e.find('atom:author/atom:name', ns).text if e.find('atom:author/atom:name', ns) is not None else ''
        updated = e.find('atom:updated', ns).text if e.find('atom:updated', ns) is not None else ''
        print(f'{i}. TITLE: {title}')
        print(f'   AUTHOR: {author}')
        print(f'   POSTED AT: {updated}')
        print(f'   CLICKABLE URL: {link}\n')
except Exception as err:
    print(f'Error: {err}')
