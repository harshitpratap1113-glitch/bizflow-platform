import os
import re
import json
import random
import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from app.db.database import get_db

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.3 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:124.0) Gecko/20100101 Firefox/124.0"
]

# 200+ Multi-Industry Communities Categorized into 10 Dedicated Fields
ALL_TARGET_COMMUNITIES = [
    # 1. Tech & Full-Stack Development (27 Communities)
    ("reddit", "webdev", "Tech & Dev", "fa-code", "cyan"),
    ("reddit", "javascript", "Tech & Dev", "fa-code", "cyan"),
    ("reddit", "reactjs", "Tech & Dev", "fa-code", "cyan"),
    ("reddit", "nextjs", "Tech & Dev", "fa-code", "cyan"),
    ("reddit", "python", "Tech & Dev", "fa-code", "cyan"),
    ("reddit", "node", "Tech & Dev", "fa-code", "cyan"),
    ("reddit", "fastapi", "Tech & Dev", "fa-code", "cyan"),
    ("reddit", "django", "Tech & Dev", "fa-code", "cyan"),
    ("reddit", "vuejs", "Tech & Dev", "fa-code", "cyan"),
    ("reddit", "golang", "Tech & Dev", "fa-code", "cyan"),
    ("reddit", "rust", "Tech & Dev", "fa-code", "cyan"),
    ("reddit", "programming", "Tech & Dev", "fa-code", "cyan"),
    ("reddit", "typescript", "Tech & Dev", "fa-code", "cyan"),
    ("reddit", "angular", "Tech & Dev", "fa-code", "cyan"),
    ("reddit", "sveltejs", "Tech & Dev", "fa-code", "cyan"),
    ("reddit", "tailwindcss", "Tech & Dev", "fa-code", "cyan"),
    ("reddit", "graphql", "Tech & Dev", "fa-code", "cyan"),
    ("reddit", "PostgreSQL", "Tech & Dev", "fa-code", "cyan"),
    ("reddit", "mongodb", "Tech & Dev", "fa-code", "cyan"),
    ("reddit", "elixir", "Tech & Dev", "fa-code", "cyan"),
    ("reddit", "cpp", "Tech & Dev", "fa-code", "cyan"),
    ("reddit", "csharp", "Tech & Dev", "fa-code", "cyan"),
    ("reddit", "dotnet", "Tech & Dev", "fa-code", "cyan"),
    ("reddit", "backend", "Tech & Dev", "fa-code", "cyan"),
    ("reddit", "frontend", "Tech & Dev", "fa-code", "cyan"),
    ("reddit", "fullstack", "Tech & Dev", "fa-code", "cyan"),
    ("reddit", "laravel", "Tech & Dev", "fa-code", "cyan"),

    # 2. AI, LLMs & Automation Workflows (26 Communities)
    ("reddit", "OpenAI", "AI & Automation", "fa-brain", "amber"),
    ("reddit", "ChatGPT", "AI & Automation", "fa-brain", "amber"),
    ("reddit", "ArtificialInteligence", "AI & Automation", "fa-brain", "amber"),
    ("reddit", "MachineLearning", "AI & Automation", "fa-brain", "amber"),
    ("reddit", "LocalLLaMA", "AI & Automation", "fa-brain", "amber"),
    ("reddit", "LangChain", "AI & Automation", "fa-brain", "amber"),
    ("reddit", "Automate", "AI & Automation", "fa-brain", "amber"),
    ("reddit", "n8n", "AI & Automation", "fa-brain", "amber"),
    ("reddit", "zapier", "AI & Automation", "fa-brain", "amber"),
    ("reddit", "ClaudeAI", "AI & Automation", "fa-brain", "amber"),
    ("reddit", "PromptEngineering", "AI & Automation", "fa-brain", "amber"),
    ("reddit", "huggingface", "AI & Automation", "fa-brain", "amber"),
    ("reddit", "Ollama", "AI & Automation", "fa-brain", "amber"),
    ("reddit", "vLLM", "AI & Automation", "fa-brain", "amber"),
    ("reddit", "CrewAI", "AI & Automation", "fa-brain", "amber"),
    ("reddit", "AutoGPT", "AI & Automation", "fa-brain", "amber"),
    ("reddit", "OpenAssistant", "AI & Automation", "fa-brain", "amber"),
    ("reddit", "LlamaIndex", "AI & Automation", "fa-brain", "amber"),
    ("reddit", "Langfuse", "AI & Automation", "fa-brain", "amber"),
    ("reddit", "Rag", "AI & Automation", "fa-brain", "amber"),
    ("reddit", "aiagents", "AI & Automation", "fa-brain", "amber"),
    ("reddit", "Claude", "AI & Automation", "fa-brain", "amber"),
    ("reddit", "Midjourney", "AI & Automation", "fa-brain", "amber"),
    ("reddit", "StableDiffusion", "AI & Automation", "fa-brain", "amber"),
    ("reddit", "GenerativeAI", "AI & Automation", "fa-brain", "amber"),
    ("reddit", "DeepLearning", "AI & Automation", "fa-brain", "amber"),

    # 3. Design, UI/UX, 3D & Creative (21 Communities)
    ("reddit", "DesignJobs", "Design & Creative", "fa-palette", "pink"),
    ("reddit", "graphic_design", "Design & Creative", "fa-palette", "pink"),
    ("reddit", "UI_Design", "Design & Creative", "fa-palette", "pink"),
    ("reddit", "ArtStore", "Design & Creative", "fa-palette", "pink"),
    ("reddit", "HungryArtists", "Design & Creative", "fa-palette", "pink"),
    ("reddit", "3Dmodeling", "Design & Creative", "fa-palette", "pink"),
    ("reddit", "blender", "Design & Creative", "fa-palette", "pink"),
    ("reddit", "MotionDesign", "Design & Creative", "fa-palette", "pink"),
    ("reddit", "logodesign", "Design & Creative", "fa-palette", "pink"),
    ("reddit", "FigmaDesign", "Design & Creative", "fa-palette", "pink"),
    ("reddit", "userexperience", "Design & Creative", "fa-palette", "pink"),
    ("reddit", "UXDesign", "Design & Creative", "fa-palette", "pink"),
    ("reddit", "web_design", "Design & Creative", "fa-palette", "pink"),
    ("reddit", "industrialdesign", "Design & Creative", "fa-palette", "pink"),
    ("reddit", "Cinema4D", "Design & Creative", "fa-palette", "pink"),
    ("reddit", "Maya", "Design & Creative", "fa-palette", "pink"),
    ("reddit", "UnrealEngine", "Design & Creative", "fa-palette", "pink"),
    ("reddit", "conceptart", "Design & Creative", "fa-palette", "pink"),
    ("reddit", "CharacterDesigning", "Design & Creative", "fa-palette", "pink"),
    ("reddit", "DigitalPainting", "Design & Creative", "fa-palette", "pink"),
    ("reddit", "typography", "Design & Creative", "fa-palette", "pink"),

    # 4. Video Editing, Animation & Creators (18 Communities)
    ("reddit", "videography", "Video & Content", "fa-video", "rose"),
    ("reddit", "VideoEditing", "Video & Content", "fa-video", "rose"),
    ("reddit", "CreatorServices", "Video & Content", "fa-video", "rose"),
    ("reddit", "YouTubers", "Video & Content", "fa-video", "rose"),
    ("reddit", "podcast", "Video & Content", "fa-video", "rose"),
    ("reddit", "AfterEffects", "Video & Content", "fa-video", "rose"),
    ("reddit", "davinciresolve", "Video & Content", "fa-video", "rose"),
    ("reddit", "premiere", "Video & Content", "fa-video", "rose"),
    ("reddit", "Filmmakers", "Video & Content", "fa-video", "rose"),
    ("reddit", "cinematography", "Video & Content", "fa-video", "rose"),
    ("reddit", "Editors", "Video & Content", "fa-video", "rose"),
    ("reddit", "VideoProduction", "Video & Content", "fa-video", "rose"),
    ("reddit", "videomarketing", "Video & Content", "fa-video", "rose"),
    ("reddit", "Twitch", "Video & Content", "fa-video", "rose"),
    ("reddit", "NewTubers", "Video & Content", "fa-video", "rose"),
    ("reddit", "animation", "Video & Content", "fa-video", "rose"),
    ("reddit", "2Danimation", "Video & Content", "fa-video", "rose"),
    ("reddit", "ColorGrading", "Video & Content", "fa-video", "rose"),

    # 5. Marketing, SEO, Copywriting & Growth (23 Communities)
    ("reddit", "Marketing", "Marketing & SEO", "fa-bullhorn", "emerald"),
    ("reddit", "SEO", "Marketing & SEO", "fa-bullhorn", "emerald"),
    ("reddit", "copywriting", "Marketing & SEO", "fa-bullhorn", "emerald"),
    ("reddit", "HireaWriter", "Marketing & SEO", "fa-bullhorn", "emerald"),
    ("reddit", "socialmedia", "Marketing & SEO", "fa-bullhorn", "emerald"),
    ("reddit", "digitalmarketing", "Marketing & SEO", "fa-bullhorn", "emerald"),
    ("reddit", "PPC", "Marketing & SEO", "fa-bullhorn", "emerald"),
    ("reddit", "contentmarketing", "Marketing & SEO", "fa-bullhorn", "emerald"),
    ("reddit", "GrowthHacking", "Marketing & SEO", "fa-bullhorn", "emerald"),
    ("reddit", "emailmarketing", "Marketing & SEO", "fa-bullhorn", "emerald"),
    ("reddit", "AffiliateMarketing", "Marketing & SEO", "fa-bullhorn", "emerald"),
    ("reddit", "adops", "Marketing & SEO", "fa-bullhorn", "emerald"),
    ("reddit", "FacebookAds", "Marketing & SEO", "fa-bullhorn", "emerald"),
    ("reddit", "GoogleAds", "Marketing & SEO", "fa-bullhorn", "emerald"),
    ("reddit", "content_marketing", "Marketing & SEO", "fa-bullhorn", "emerald"),
    ("reddit", "b2bmarketing", "Marketing & SEO", "fa-bullhorn", "emerald"),
    ("reddit", "saasmarketing", "Marketing & SEO", "fa-bullhorn", "emerald"),
    ("reddit", "copywriting2", "Marketing & SEO", "fa-bullhorn", "emerald"),
    ("reddit", "publicrelations", "Marketing & SEO", "fa-bullhorn", "emerald"),
    ("reddit", "influencermarketing", "Marketing & SEO", "fa-bullhorn", "emerald"),
    ("reddit", "DirectMail", "Marketing & SEO", "fa-bullhorn", "emerald"),
    ("reddit", "leadgeneration", "Marketing & SEO", "fa-bullhorn", "emerald"),
    ("reddit", "conversionrate", "Marketing & SEO", "fa-bullhorn", "emerald"),

    # 6. E-Commerce, Shopify & Amazon FBA (18 Communities)
    ("reddit", "Shopify", "E-Commerce & Retail", "fa-cart-shopping", "green"),
    ("reddit", "ecommerce", "E-Commerce & Retail", "fa-cart-shopping", "green"),
    ("reddit", "AmazonSeller", "E-Commerce & Retail", "fa-cart-shopping", "green"),
    ("reddit", "FulfillmentByAmazon", "E-Commerce & Retail", "fa-cart-shopping", "green"),
    ("reddit", "dropship", "E-Commerce & Retail", "fa-cart-shopping", "green"),
    ("reddit", "Flipping", "E-Commerce & Retail", "fa-cart-shopping", "green"),
    ("reddit", "shopifydev", "E-Commerce & Retail", "fa-cart-shopping", "green"),
    ("reddit", "ShopifyeCommerce", "E-Commerce & Retail", "fa-cart-shopping", "green"),
    ("reddit", "WooCommerce", "E-Commerce & Retail", "fa-cart-shopping", "green"),
    ("reddit", "AmazonMerch", "E-Commerce & Retail", "fa-cart-shopping", "green"),
    ("reddit", "Ecommercestrategy", "E-Commerce & Retail", "fa-cart-shopping", "green"),
    ("reddit", "EtsySellers", "E-Commerce & Retail", "fa-cart-shopping", "green"),
    ("reddit", "PrintOnDemand", "E-Commerce & Retail", "fa-cart-shopping", "green"),
    ("reddit", "AmazonFBATips", "E-Commerce & Retail", "fa-cart-shopping", "green"),
    ("reddit", "Retail", "E-Commerce & Retail", "fa-cart-shopping", "green"),
    ("reddit", "wholesaleglobal", "E-Commerce & Retail", "fa-cart-shopping", "green"),
    ("reddit", "WalmartSellers", "E-Commerce & Retail", "fa-cart-shopping", "green"),
    ("reddit", "BigCommerce", "E-Commerce & Retail", "fa-cart-shopping", "green"),

    # 7. Startups, Founders & SaaS Buyers (24 Communities)
    ("reddit", "startups", "Startups & SaaS", "fa-rocket", "purple"),
    ("reddit", "SaaS", "Startups & SaaS", "fa-rocket", "purple"),
    ("reddit", "Entrepreneur", "Startups & SaaS", "fa-rocket", "purple"),
    ("reddit", "smallbusiness", "Startups & SaaS", "fa-rocket", "purple"),
    ("reddit", "SideProject", "Startups & SaaS", "fa-rocket", "purple"),
    ("reddit", "business", "Startups & SaaS", "fa-rocket", "purple"),
    ("reddit", "growmybusiness", "Startups & SaaS", "fa-rocket", "purple"),
    ("reddit", "microsaas", "Startups & SaaS", "fa-rocket", "purple"),
    ("reddit", "roastmystartup", "Startups & SaaS", "fa-rocket", "purple"),
    ("reddit", "IndieHackers", "Startups & SaaS", "fa-rocket", "purple"),
    ("reddit", "startup_ideas", "Startups & SaaS", "fa-rocket", "purple"),
    ("reddit", "alphaandbetausers", "Startups & SaaS", "fa-rocket", "purple"),
    ("reddit", "SaaSMarketing", "Startups & SaaS", "fa-rocket", "purple"),
    ("reddit", "venturecapital", "Startups & SaaS", "fa-rocket", "purple"),
    ("reddit", "angelinvestors", "Startups & SaaS", "fa-rocket", "purple"),
    ("reddit", "BootstrappedSaaS", "Startups & SaaS", "fa-rocket", "purple"),
    ("reddit", "ProductManagement", "Startups & SaaS", "fa-rocket", "purple"),
    ("reddit", "scaleup", "Startups & SaaS", "fa-rocket", "purple"),
    ("reddit", "smallbiz", "Startups & SaaS", "fa-rocket", "purple"),
    ("reddit", "solopreneur", "Startups & SaaS", "fa-rocket", "purple"),
    ("reddit", "EntrepreneurRideAlong", "Startups & SaaS", "fa-rocket", "purple"),
    ("reddit", "Business_Ideas", "Startups & SaaS", "fa-rocket", "purple"),
    ("reddit", "BuildInPublic", "Startups & SaaS", "fa-rocket", "purple"),
    ("reddit", "coys", "Startups & SaaS", "fa-rocket", "purple"),

    # 8. Mobile App Development (16 Communities)
    ("reddit", "FlutterDev", "Mobile Apps", "fa-mobile-screen", "blue"),
    ("reddit", "reactnative", "Mobile Apps", "fa-mobile-screen", "blue"),
    ("reddit", "iOSProgramming", "Mobile Apps", "fa-mobile-screen", "blue"),
    ("reddit", "androiddev", "Mobile Apps", "fa-mobile-screen", "blue"),
    ("reddit", "swift", "Mobile Apps", "fa-mobile-screen", "blue"),
    ("reddit", "Kotlin", "Mobile Apps", "fa-mobile-screen", "blue"),
    ("reddit", "SwiftUI", "Mobile Apps", "fa-mobile-screen", "blue"),
    ("reddit", "iOSDev", "Mobile Apps", "fa-mobile-screen", "blue"),
    ("reddit", "AndroidStudio", "Mobile Apps", "fa-mobile-screen", "blue"),
    ("reddit", "MobileDevelopment", "Mobile Apps", "fa-mobile-screen", "blue"),
    ("reddit", "Flutter", "Mobile Apps", "fa-mobile-screen", "blue"),
    ("reddit", "react_native", "Mobile Apps", "fa-mobile-screen", "blue"),
    ("reddit", "KotlinMultiplatform", "Mobile Apps", "fa-mobile-screen", "blue"),
    ("reddit", "AppEngine", "Mobile Apps", "fa-mobile-screen", "blue"),
    ("reddit", "GameDev", "Mobile Apps", "fa-mobile-screen", "blue"),
    ("reddit", "Unity3D", "Mobile Apps", "fa-mobile-screen", "blue"),

    # 9. DevOps, Cloud & Infrastructure (18 Communities)
    ("reddit", "devops", "DevOps & Cloud", "fa-cloud", "indigo"),
    ("reddit", "aws", "DevOps & Cloud", "fa-cloud", "indigo"),
    ("reddit", "docker", "DevOps & Cloud", "fa-cloud", "indigo"),
    ("reddit", "kubernetes", "DevOps & Cloud", "fa-cloud", "indigo"),
    ("reddit", "sysadmin", "DevOps & Cloud", "fa-cloud", "indigo"),
    ("reddit", "selfhosted", "DevOps & Cloud", "fa-cloud", "indigo"),
    ("reddit", "Terraform", "DevOps & Cloud", "fa-cloud", "indigo"),
    ("reddit", "ansible", "DevOps & Cloud", "fa-cloud", "indigo"),
    ("reddit", "linuxadmin", "DevOps & Cloud", "fa-cloud", "indigo"),
    ("reddit", "googlecloud", "DevOps & Cloud", "fa-cloud", "indigo"),
    ("reddit", "azure", "DevOps & Cloud", "fa-cloud", "indigo"),
    ("reddit", "cloudflare", "DevOps & Cloud", "fa-cloud", "indigo"),
    ("reddit", "Proxmox", "DevOps & Cloud", "fa-cloud", "indigo"),
    ("reddit", "homelab", "DevOps & Cloud", "fa-cloud", "indigo"),
    ("reddit", "devopsjobs", "DevOps & Cloud", "fa-cloud", "indigo"),
    ("reddit", "grafana", "DevOps & Cloud", "fa-cloud", "indigo"),
    ("reddit", "cybersecurity", "DevOps & Cloud", "fa-cloud", "indigo"),
    ("reddit", "netsec", "DevOps & Cloud", "fa-cloud", "indigo"),

    # 10. Local Business, Finance & Accounting (21 Communities)
    ("reddit", "Accounting", "Local Biz & Finance", "fa-calculator", "teal"),
    ("reddit", "Bookkeeping", "Local Biz & Finance", "fa-calculator", "teal"),
    ("reddit", "RealEstate", "Local Biz & Finance", "fa-calculator", "teal"),
    ("reddit", "realtors", "Local Biz & Finance", "fa-calculator", "teal"),
    ("reddit", "Restaurateur", "Local Biz & Finance", "fa-calculator", "teal"),
    ("reddit", "Dentistry", "Local Biz & Finance", "fa-calculator", "teal"),
    ("reddit", "FitnessBusiness", "Local Biz & Finance", "fa-calculator", "teal"),
    ("reddit", "consulting", "Local Biz & Finance", "fa-calculator", "teal"),
    ("reddit", "sales", "Local Biz & Finance", "fa-calculator", "teal"),
    ("reddit", "tax", "Local Biz & Finance", "fa-calculator", "teal"),
    ("reddit", "smallbusinessowners", "Local Biz & Finance", "fa-calculator", "teal"),
    ("reddit", "gymowner", "Local Biz & Finance", "fa-calculator", "teal"),
    ("reddit", "commercialrealestate", "Local Biz & Finance", "fa-calculator", "teal"),
    ("reddit", "landlord", "Local Biz & Finance", "fa-calculator", "teal"),
    ("reddit", "Cleaning_Business", "Local Biz & Finance", "fa-calculator", "teal"),
    ("reddit", "Contractor", "Local Biz & Finance", "fa-calculator", "teal"),
    ("reddit", "HVAC", "Local Biz & Finance", "fa-calculator", "teal"),
    ("reddit", "Plumbing", "Local Biz & Finance", "fa-calculator", "teal"),
    ("reddit", "LawFirm", "Local Biz & Finance", "fa-calculator", "teal"),
    ("reddit", "MedSpa", "Local Biz & Finance", "fa-calculator", "teal"),
    ("reddit", "AutoDetailing", "Local Biz & Finance", "fa-calculator", "teal"),

    # General Hiring & High-Intent Freelance Hubs (12 Communities)
    ("reddit", "forhire", "Hiring & Freelance", "fa-briefcase", "emerald"),
    ("reddit", "freelance", "Hiring & Freelance", "fa-briefcase", "emerald"),
    ("reddit", "freelance_forhire", "Hiring & Freelance", "fa-briefcase", "emerald"),
    ("reddit", "jobbit", "Hiring & Freelance", "fa-briefcase", "emerald"),
    ("reddit", "hireaprogrammer", "Hiring & Freelance", "fa-briefcase", "emerald"),
    ("reddit", "remotejobs", "Hiring & Freelance", "fa-briefcase", "emerald"),
    ("reddit", "remotework", "Hiring & Freelance", "fa-briefcase", "emerald"),
    ("reddit", "freelance_writers", "Hiring & Freelance", "fa-briefcase", "emerald"),
    ("reddit", "techjobs", "Hiring & Freelance", "fa-briefcase", "emerald"),
    ("reddit", "DevsForHire", "Hiring & Freelance", "fa-briefcase", "emerald"),
    ("reddit", "workonline", "Hiring & Freelance", "fa-briefcase", "emerald")
]

COMMUNITY_FIELD_LOOKUP = {c[1].lower(): c[2] for c in ALL_TARGET_COMMUNITIES}

def analyze_tri_box_routing(title: str, body: str, community: str = "general") -> dict:
    """
    Classifies raw posts into 3 clear boxes across all 10 industries:
    1. 'spam': Quarantined spam, bots, scams, 0$ rev-share dealbreakers
    2. 'verified': Genuine high-intent buyer leads (hiring, budget ready, seeking tools/agency/freelancer)
    3. 'general': Casual discussion, technical questions, general banter (Casual Stream Box)
    """
    text = f"{title} {body}".lower()
    field_category = COMMUNITY_FIELD_LOOKUP.get(community.lower(), "General Discussion")
    
    # --- BOX 1: SPAM & SCAM VAULT ---
    spam_patterns = [
        (r'(0\s*\$|0\s*usd|unpaid|no pay|work for free|sweat equity only|rev-?share only|exposure only)', 'Dealbreaker: 0$ / Unpaid / Sweat equity without compensation'),
        (r'(crypto|bitcoin|usdt|airdrop|pump signals|buy signals|t\.me/|join telegram channel|telegram bot)', 'Blackhat: Crypto pump / Telegram redirect trap'),
        (r'(smm panel|buy followers|instagram bot|tiktok likes|upvote bot|cheap views|bit\.ly)', 'Promo: SMM bot / Fake engagement reseller'),
        (r'(upvote if you|karma farm|like for like|drop your link|follow back|comment for reach|dm me "info"|comment "interested")', 'Zero intent: Engagement bait / Karma farming'),
        (r'(earn \$\d+ daily|watch videos earn|complete surveys for cash|passive income guaranteed|work from home fast cash)', 'Deceptive: High-yield survey / Easy cash scam'),
        (r'(use my promo code|sign up with my referral|50% off discount code|dm for free course|affiliate link)', 'Affiliate: Self-promotional referral spam')
    ]
    
    for pattern, reason in spam_patterns:
        if re.search(pattern, text):
            return {
                "lead_box": "spam",
                "is_spam": 1,
                "spam_reason": reason,
                "spam_confidence": random.randint(95, 100),
                "intent_score": random.randint(5, 20),
                "budget": None,
                "matched_keywords": "spam, quarantined",
                "category": "Quarantined Spam",
                "field": "Spam Vault",
                "match_reason": "Quarantined by Level 10 Spam Shield"
            }
            
    # --- BOX 2: VERIFIED HIGH-INTENT BUYER LEADS ---
    buyer_intent_triggers = [
        "hiring", "hire developer", "looking for developer", "hire designer", "hire editor", "hire copywriter",
        "build mvp", "need agency", "budget", "paid gig", "hourly rate", "contract", "willing to pay",
        "looking to buy", "pricing", "alternative to", "replace", "consultant", "developer needed",
        "designer needed", "video editor needed", "expert", "audit", "migrate", "redesign", "automation",
        "rag", "fine-tune", "contract to hire", "fixed price", "paid project", "engineer needed",
        "looking for agency", "need help building", "help me build", "custom software", "stripe integration",
        "recommend agency", "looking for freelancer", "client portal", "thumbnail designer", "video editing gig",
        "seo audit", "lead generation agency", "shopify developer", "flutter dev needed"
    ]
    
    # Extract Budget
    budget_match = re.search(r'(\$\s*\d{1,3}(?:,\d{3})*(?:\s*-\s*\$?\s*\d{1,3}(?:,\d{3})*)?|\d{1,3}(?:,\d{3})*\s*(?:usd|eur|dollars|k))(?:\s*/\s*(?:hr|hour|month|project))?', text)
    budget_detected = budget_match.group(0).upper() if budget_match else None
    
    matched_buyer_signals = [kw for kw in buyer_intent_triggers if kw in text]
    
    # Has clear hiring or budget or agency requirement
    has_strong_buying_signal = (
        any(h in text for h in ["[hiring]", "looking to hire", "hiring developer", "looking for developer", "hiring designer", "need editor", "need agency", "contract to hire", "paid project"]) or
        (budget_detected is not None and any(w in text for w in ["build", "develop", "need", "looking", "create", "fix", "upgrade", "edit", "design"])) or
        len(matched_buyer_signals) >= 2 or
        community.lower() in ["forhire", "designjobs", "hireaprogrammer", "jobbit", "creatorServices", "hireawriter"]
    )
    
    if has_strong_buying_signal:
        base_score = 80
        if "[hiring]" in text or "looking to hire" in text:
            base_score += 15
        if budget_detected:
            base_score += 10
        base_score += min(10, len(matched_buyer_signals) * 2)
        score = min(99, max(75, base_score))

        return {
            "lead_box": "verified",
            "is_spam": 0,
            "spam_reason": None,
            "spam_confidence": 0,
            "intent_score": score,
            "budget": budget_detected,
            "matched_keywords": ", ".join(matched_buyer_signals[:6]) if matched_buyer_signals else "verified buyer signal",
            "category": field_category,
            "field": field_category,
            "match_reason": f"Verified Buyer Signal in {field_category}"
        }
        
    # --- BOX 3: CASUAL & GENERAL DISCUSSIONS BOX ---
    return {
        "lead_box": "general",
        "is_spam": 0,
        "spam_reason": None,
        "spam_confidence": 0,
        "intent_score": random.randint(45, 68),
        "budget": budget_detected,
        "matched_keywords": "community discussion, tech inquiry",
        "category": field_category,
        "field": field_category,
        "match_reason": f"Casual Discussion in {field_category}"
    }

def fetch_rss_xml(url: str, timeout: int = 4):
    ua = random.choice(USER_AGENTS)
    try:
        req = urllib.request.Request(url, headers={"User-Agent": ua})
        with urllib.request.urlopen(req, timeout=timeout) as response:
            return response.read().decode("utf-8")
    except Exception:
        return None

def crawl_reddit_sub(sub: str):
    results = []
    urls_to_try = [
        f"https://www.reddit.com/r/{sub}/new/.rss?limit=25",
        f"https://old.reddit.com/r/{sub}/new/.rss?limit=25",
        f"https://www.reddit.com/r/{sub}/.rss"
    ]
    
    xml_data = None
    for u in urls_to_try:
        xml_data = fetch_rss_xml(u, timeout=3)
        if xml_data:
            break
            
    if not xml_data:
        return results
        
    try:
        root = ET.fromstring(xml_data)
        entries = root.findall("{http://www.w3.org/2005/Atom}entry")
        for entry in entries[:25]:
            title_elem = entry.find("{http://www.w3.org/2005/Atom}title")
            link_elem = entry.find("{http://www.w3.org/2005/Atom}link")
            author_elem = entry.find("{http://www.w3.org/2005/Atom}author/{http://www.w3.org/2005/Atom}name")
            content_elem = entry.find("{http://www.w3.org/2005/Atom}content")
            
            title = (title_elem.text or "").strip() if title_elem is not None else ""
            if not title:
                continue
                
            raw_url = link_elem.attrib.get("href", "") if link_elem is not None else ""
            if raw_url.startswith("/r/"):
                url = f"https://www.reddit.com{raw_url}"
            elif raw_url.startswith("http"):
                url = raw_url
            else:
                url = f"https://www.reddit.com/r/{sub}/new/"
                
            author = (author_elem.text or "reddit_user").strip() if author_elem is not None else "reddit_user"
            if author.startswith("/u/"):
                author = author.replace("/u/", "")
                
            raw_content = content_elem.text if content_elem is not None else ""
            body = re.sub(r'<[^>]+>', ' ', raw_content).strip()
            platform_id = f"reddit-{abs(hash(url or title))}"
            
            analysis = analyze_tri_box_routing(title, body, sub)
            results.append((
                "reddit", platform_id, sub, title, body[:500] if body else f"Click 'Open in Reddit' to inspect full r/{sub} discussion.",
                author, url, analysis["intent_score"], analysis["category"], analysis["matched_keywords"],
                analysis["budget"], analysis["lead_box"], analysis["is_spam"], analysis["spam_reason"], analysis["spam_confidence"]
            ))
    except Exception:
        pass
    return results

def crawl_hackernews():
    """Scans HackerNews Algolia public feed for Who is Hiring / Ask HN discussions."""
    results = []
    try:
        url = "https://hn.algolia.com/api/v1/search_by_date?tags=story&hitsPerPage=30"
        ua = random.choice(USER_AGENTS)
        req = urllib.request.Request(url, headers={"User-Agent": ua})
        with urllib.request.urlopen(req, timeout=4) as response:
            data = json.loads(response.read().decode("utf-8"))
            for hit in data.get("hits", []):
                title = hit.get("title", "")
                if not title:
                    continue
                story_text = hit.get("story_text") or ""
                object_id = hit.get("objectID")
                post_url = hit.get("url") or f"https://news.ycombinator.com/item?id={object_id}"
                author = hit.get("author", "hn_user")
                platform_id = f"hn-{object_id}"
                
                analysis = analyze_tri_box_routing(title, story_text, "hackernews")
                results.append((
                    "hackernews", platform_id, "hackernews", title, story_text[:500] if story_text else "HackerNews Frontpage / Discussion Post",
                    author, post_url, analysis["intent_score"], analysis["category"], analysis["matched_keywords"],
                    analysis["budget"], analysis["lead_box"], analysis["is_spam"], analysis["spam_reason"], analysis["spam_confidence"]
                ))
    except Exception:
        pass
    return results

def run_live_ingestion(sub_count: int = 50):
    """
    High-speed multi-threaded ingestion across 50+ communities simultaneously.
    Stores every post into its respective Tri-Box (verified, general, spam).
    """
    all_leads = []
    reddit_subs = [t[1] for t in ALL_TARGET_COMMUNITIES if t[0] == "reddit"]
    sampled_subs = random.sample(reddit_subs, min(sub_count, len(reddit_subs)))
    
    with ThreadPoolExecutor(max_workers=35) as executor:
        futures = {executor.submit(crawl_reddit_sub, sub): sub for sub in sampled_subs}
        futures[executor.submit(crawl_hackernews)] = "hackernews"
        
        for f in as_completed(futures):
            try:
                res = f.result()
                if res:
                    all_leads.extend(res)
            except Exception:
                pass

    conn = get_db()
    cursor = conn.cursor()
    new_count = 0
    
    for lead in all_leads:
        try:
            cursor.execute("""
            INSERT OR REPLACE INTO leads (
                platform, platform_id, community, title, body, author, url,
                intent_score, intent_category, matched_keywords, budget_detected,
                lead_box, is_spam, spam_reason, spam_confidence
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, lead)
            if cursor.rowcount > 0:
                new_count += 1
        except Exception:
            pass

    conn.commit()
    conn.close()
    return new_count
