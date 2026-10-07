import httpx
import xml.etree.ElementTree as ET
import asyncio
import random

async def test_all_subs():
    subreddits = ["SaaS", "freelance", "SideProject", "smallbusiness", "webdev", "startups"]
    
    for sub in subreddits:
        ua = f"bizflow-leadradar-{sub.lower()}:1.0.0 (by /u/harshit_dev_{random.randint(100,999)})"
        url = f"https://www.reddit.com/r/{sub}/new.rss?limit=15"
        
        try:
            async with httpx.AsyncClient(headers={"User-Agent": ua}, follow_redirects=True, timeout=10.0) as client:
                res = await client.get(url)
                if res.status_code == 200:
                    root = ET.fromstring(res.text)
                    ns = {'atom': 'http://www.w3.org/2005/Atom'}
                    entries = root.findall('atom:entry', ns)
                    print(f"[✓] r/{sub}: SUCCESS ({len(entries)} items)")
                    if entries:
                        title = entries[0].find('atom:title', ns).text
                        print(f"     Latest: {title[:65]}...")
                else:
                    print(f"[!] r/{sub}: HTTP {res.status_code}")
        except Exception as e:
            print(f"[!] r/{sub} error: {e}")
        
        # Pacing
        await asyncio.sleep(2.5)

if __name__ == "__main__":
    asyncio.run(test_all_subs())
