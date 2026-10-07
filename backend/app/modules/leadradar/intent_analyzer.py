import re
from typing import Dict, Any, List, Tuple

class IntentAnalyzer:
    """
    AI Social Intent & Problem Urgency Analyzer.
    Evaluates buying intent, categorizes problems, and drafts tailored replies.
    """

    HIGH_INTENT_PATTERNS = [
        r"\blooking for\b", r"\brecommend(ation| me| a)?\b", r"\balternative to\b",
        r"\bis there (a|any) tool\b", r"\bis there (a|any) software\b", r"\bany tool that\b",
        r"\bhow do you (guys )?handle\b", r"\bhate (doing|manually)\b", r"\btired of\b",
        r"\bwasting hours\b", r"\bunpaid invoice(s)?\b", r"\bclient ghosted\b",
        r"\bclient (hasn't|has not|wont|won't) pay\b", r"\bhow to get (first )?(users|customers|clients)\b",
        r"\b0 (sales|signups|traction|users)\b", r"\bstruggling to (get|find)\b",
        r"\bfake (1 star|review|google)\b", r"\bgoogle map(s)? review\b",
        r"\bno-show(s)? (rate|problem)\b", r"\bconvert (50|multiple|pdf|invoices) to excel\b",
        r"\bextract (data|tables) from pdf\b", r"\bneed (a |an )?(solution|tool|recommendation)\b"
    ]

    MODERATE_INTENT_PATTERNS = [
        r"\bbest way to\b", r"\bhow do I\b", r"\bwhat do you use for\b",
        r"\bproposal template\b", r"\bdeposit (before|after)\b", r"\bhow to ask for\b",
        r"\bany advice on\b", r"\bworth building\b", r"\bfeedback on\b"
    ]

    SPAM_PATTERNS = [
        r"\bi built (a |this )?\b", r"\bwe just launched\b", r"\bcheck out my\b",
        r"\bpromo code\b", r"\bdiscount on our\b", r"\buse code\b",
        r"\baffiliate link\b", r"\bjoin my discord\b", r"\bfree course\b"
    ]

    @classmethod
    def analyze_post(cls, title: str, content: str = "") -> Dict[str, Any]:
        full_text = f"{title} {content}".lower()
        
        # 1. Base Score calculation
        score = 30  # Baseline
        matched_keywords: List[str] = []

        # Check High-Intent Triggers
        for pattern in cls.HIGH_INTENT_PATTERNS:
            matches = re.findall(pattern, full_text)
            if matches:
                score += 25
                matched_keywords.append(pattern.replace(r"\b", "").replace(r"(", "").replace(r")", ""))

        # Check Moderate-Intent Triggers
        for pattern in cls.MODERATE_INTENT_PATTERNS:
            matches = re.findall(pattern, full_text)
            if matches:
                score += 15
                matched_keywords.append(pattern.replace(r"\b", "").replace(r"(", "").replace(r")", ""))

        # Check Question Indicators
        if "?" in title or "?" in content:
            score += 10

        # Check Spam / Self-Promotion Penalty
        is_spam = False
        for pattern in cls.SPAM_PATTERNS:
            if re.search(pattern, full_text):
                score -= 40
                is_spam = True

        # Clamp Score (0 to 100)
        final_score = max(5, min(99, score))

        # 2. Categorization
        category = cls._determine_category(full_text)

        # 3. Draft Tailored Reply
        suggested_reply = cls._generate_reply(title, content, category, final_score)

        return {
            "intent_score": final_score,
            "category": category,
            "matched_keywords": list(set(matched_keywords)),
            "is_spam": is_spam,
            "suggested_reply": suggested_reply
        }

    @classmethod
    def _determine_category(cls, text: str) -> str:
        if any(k in text for k in ["invoice", "unpaid", "ghost", "freelance", "proposal", "deposit", "client", "contract", "payment"]):
            return "Freelance / Invoices & Escrow"
        elif any(k in text for k in ["review", "google map", "rating", "salon", "clinic", "restaurant", "no show", "appointment"]):
            return "Local Business & Reviews"
        elif any(k in text for k in ["pdf", "excel", "receipt", "extract", "ocr", "bookkeeping", "spreadsheet"]):
            return "Doc & Invoice Automation"
        elif any(k in text for k in ["saas", "traction", "signup", "user", "lead", "distribution", "cold email", "market"]):
            return "SaaS & Growth Leads"
        return "General Business Problem"

    @classmethod
    def _generate_reply(cls, title: str, content: str, category: str, score: int) -> str:
        """
        Drafts a natural, authentic community response based on problem category.
        """
        if category == "Freelance / Invoices & Escrow":
            return (
                "Hey! Dealing with client ghosting / payment friction is honestly the most frustrating part of freelancing. "
                "A strategy that worked wonders for us is shifting to dynamic 1-page proposals that require a 30-50% advance deposit upfront "
                "before starting work. Also automated polite reminders (via WhatsApp or SMS) prevent awkward follow-ups. "
                "We actually built SmartClose for this exact workflow: https://bizflow.ai/smartclose — happy to share our proposal framework if helpful!"
            )
        elif category == "Local Business & Reviews":
            return (
                "Great question! Protecting local ratings from unfair 1-star drops is critical for walk-in traffic. "
                "Instead of asking randomly, placing a Smart QR code at the counter that directs happy customers (4-5 stars) to Google Maps "
                "while routing private feedback for lower ratings keeps your public score protected. "
                "Check out ReviewShield (https://bizflow.ai/reviewshield) if you want a plug-and-play QR system for your venue."
            )
        elif category == "Doc & Invoice Automation":
            return (
                "Manually typing numbers from dozens of supplier PDF invoices into Excel eats up way too many hours every week. "
                "You can automate this without paying for enterprise bloated tools ($100+/mo). "
                "We built DocuClean (https://bizflow.ai/docuclean) specifically for this — you just drag & drop batch PDFs and get clean Excel rows in 5 seconds."
            )
        elif category == "SaaS & Growth Leads":
            return (
                "Getting those first 50 users is tough when cold emails keep landing in spam. "
                "One of the highest-converting channels right now is social intent listening — finding people actively asking for solutions "
                "on Reddit/Twitter and jumping in with helpful, non-spammy value. "
                "We built LeadRadar (https://bizflow.ai/leadradar) to automate live alerts for warm buyer leads. Hope this helps!"
            )
        else:
            return (
                "Spot on! Running into this operational bottleneck slows down so much momentum. "
                "Focusing on simple modular automation for this can save 5-10 hours a week. "
                "Let me know if you'd like to check out how we automated this in BizFlow AI: https://bizflow.ai"
            )

intent_analyzer = IntentAnalyzer()
