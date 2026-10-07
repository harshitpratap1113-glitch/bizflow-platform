import sqlite3
import os
import json
import random
import shutil

DB_DIR = os.path.dirname(os.path.abspath(__file__))
BUNDLED_DB = os.path.join(DB_DIR, "bizflow.db")

if os.environ.get("VERCEL") or os.environ.get("AWS_LAMBDA_FUNCTION_NAME"):
    TMP_DB = "/tmp/bizflow.db"
    if not os.path.exists(TMP_DB):
        if os.path.exists(BUNDLED_DB):
            try:
                shutil.copy2(BUNDLED_DB, TMP_DB)
            except Exception:
                pass
    DB_PATH = TMP_DB
else:
    DB_PATH = BUNDLED_DB

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    cursor = conn.cursor()
    
    # 1. User Business & Intent Profiles
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS user_profiles (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        profile_name TEXT NOT NULL,
        business_type TEXT NOT NULL, -- agency, saas, freelance, consultant, local_biz
        business_name TEXT,
        offering_desc TEXT,
        target_problem TEXT,
        target_keywords TEXT, -- comma separated
        negative_keywords TEXT, -- comma separated (spam/unpaid dealbreakers)
        portfolio_url TEXT,
        pitch_tone TEXT DEFAULT 'helpful', -- helpful, consultative, case_study, direct
        custom_pitch_template TEXT,
        is_active INTEGER DEFAULT 1,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    # 2. Hardened Tri-Box Leads Table: verified, general, spam
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS leads (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        platform TEXT NOT NULL, -- reddit, hackernews, devto, lobsters, lemmy
        platform_id TEXT UNIQUE,
        community TEXT, -- e.g. forhire, SaaS, webdev, etc.
        title TEXT NOT NULL,
        body TEXT,
        author TEXT,
        url TEXT NOT NULL,
        intent_score INTEGER DEFAULT 80,
        intent_category TEXT,
        matched_keywords TEXT,
        suggested_pitch TEXT,
        niche_tags TEXT,
        budget_detected TEXT,
        lead_box TEXT DEFAULT 'verified', -- 'verified' (Kaam ki leads), 'general' (Faltu/Casual discussions), 'spam' (Spam vault)
        is_spam INTEGER DEFAULT 0,
        spam_reason TEXT,
        spam_confidence INTEGER DEFAULT 0,
        status TEXT DEFAULT 'new', -- new, contacted, replied, archived
        created_utc REAL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    # Ensure lead_box column exists
    try:
        cursor.execute("ALTER TABLE leads ADD COLUMN lead_box TEXT DEFAULT 'verified'")
    except Exception:
        pass
    
    # 3. Monitored Target Subreddits & Sources
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS radar_targets (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        platform TEXT NOT NULL,
        target_name TEXT NOT NULL, -- e.g. r/SaaS, r/forhire
        category TEXT, -- hiring, saas, ai, webdev, mobile, ecommerce, devops
        is_active INTEGER DEFAULT 1,
        last_crawled_at TIMESTAMP,
        UNIQUE(platform, target_name)
    )
    """)

    # 4. Outbound Pitch & Campaign Logs
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS pitch_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        lead_id INTEGER,
        profile_id INTEGER,
        pitch_text TEXT NOT NULL,
        sent_status TEXT DEFAULT 'draft', -- draft, sent, copied
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (lead_id) REFERENCES leads (id),
        FOREIGN KEY (profile_id) REFERENCES user_profiles (id)
    )
    """)

    # 5. Connected Webhooks & Notifiers (Telegram, Discord, Slack)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS integrations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        service_name TEXT UNIQUE NOT NULL, -- telegram, discord, slack, webhook
        config_json TEXT NOT NULL,
        is_active INTEGER DEFAULT 1,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # 6. Live User Feedback & Community Feature Requests
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS feedback (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_name TEXT,
        email_or_contact TEXT,
        niche TEXT,
        rating INTEGER DEFAULT 5,
        lead_quality_score TEXT, -- excellent, good, average, bad
        missing_community TEXT,
        willingness_to_pay TEXT, -- yes, maybe, no
        feedback_text TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # 7. Live Visitor & ICP Traffic Analytics (.app Domain Tracker)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS visitor_analytics (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        session_id TEXT,
        ip_address TEXT,
        country TEXT DEFAULT 'United States',
        city TEXT DEFAULT 'San Francisco',
        country_code TEXT DEFAULT 'US',
        device TEXT DEFAULT 'Desktop',
        browser TEXT DEFAULT 'Chrome',
        os TEXT DEFAULT 'Windows',
        path TEXT DEFAULT '/',
        referrer TEXT DEFAULT 'Direct',
        event_type TEXT DEFAULT 'pageview',
        metadata TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # Seed Initial Traffic Baseline if empty
    cursor.execute("SELECT count(*) FROM visitor_analytics")
    if cursor.fetchone()[0] == 0:
        seed_traffic = [
            ("sess_ph_991", "104.28.19.10", "United States", "San Francisco", "US", "Desktop", "Chrome", "macOS", "/", "Product Hunt Launch", "pageview", "Product Hunt Referrer"),
            ("sess_ph_992", "172.56.21.84", "United States", "New York", "US", "Mobile", "Safari", "iOS", "/#radar", "Product Hunt Launch", "pageview", "PH Upvote Stream"),
            ("sess_in_401", "49.37.112.91", "India", "Bengaluru", "IN", "Desktop", "Chrome", "Windows", "/", "Direct (.app domain)", "pageview", "Direct Organic"),
            ("sess_uk_302", "82.132.221.14", "United Kingdom", "London", "GB", "Desktop", "Firefox", "macOS", "/#radar", "Direct (.app domain)", "click_pitch", "1-Click Pitch Generated"),
            ("sess_de_205", "91.64.12.80", "Germany", "Berlin", "DE", "Desktop", "Chrome", "Linux", "/", "Reddit (r/SaaS)", "pageview", "Reddit Community Link"),
            ("sess_in_402", "103.212.158.4", "India", "Gurgaon", "IN", "Desktop", "Edge", "Windows", "/", "Email Outreach", "click_outbound", "Outbound Campaign Click"),
            ("sess_ca_109", "142.114.88.23", "Canada", "Toronto", "CA", "Mobile", "Safari", "iOS", "/", "Product Hunt Launch", "pageview", "PH Mobile Browse"),
            ("sess_au_711", "1.128.109.42", "Australia", "Sydney", "AU", "Desktop", "Chrome", "macOS", "/#radar", "Twitter / X", "pageview", "Twitter Tech Tweet"),
            ("sess_us_882", "73.189.44.12", "United States", "Austin", "US", "Desktop", "Chrome", "Windows", "/", "Email Outreach", "click_pitch", "Agency ICP Visit"),
            ("sess_fr_501", "89.84.14.99", "France", "Paris", "FR", "Desktop", "Safari", "macOS", "/", "Direct (.app domain)", "pageview", "Direct Traffic"),
            ("sess_ae_331", "94.200.41.12", "United Arab Emirates", "Dubai", "AE", "Desktop", "Chrome", "Windows", "/", "Direct (.app domain)", "pageview", "Dubai Dev ICP"),
            ("sess_sg_804", "116.14.55.20", "Singapore", "Singapore", "SG", "Mobile", "Chrome", "Android", "/", "Product Hunt Launch", "pageview", "PH Asia Visit")
        ]
        cursor.executemany("""
        INSERT INTO visitor_analytics (
            session_id, ip_address, country, city, country_code, device, browser, os, path, referrer, event_type, metadata
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, seed_traffic)

    # Seed Default User Profile if empty
    cursor.execute("SELECT count(*) FROM user_profiles")
    if cursor.fetchone()[0] == 0:
        cursor.execute("""
        INSERT INTO user_profiles (
            profile_name, business_type, business_name, offering_desc,
            target_problem, target_keywords, negative_keywords, portfolio_url, pitch_tone
        ) VALUES (
            'Web & App Development Agency',
            'agency',
            'ApexFlow Dev Studio',
            'Full-stack custom web apps, Next.js MVP development, and AI agent integration for high-growth startups.',
            'Founders looking to hire developers or agencies to build MVPs, fix backend bottlenecks, or integrate Stripe/AI.',
            'hire developer, need agency, build mvp, react, next.js, python, fastapi, stripe, ai, budget',
            'unpaid, rev share only, equity only, free work, 0 budget',
            'https://apexflow.dev',
            'helpful'
        )
        """)

    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
    print("Database schema successfully verified!")

