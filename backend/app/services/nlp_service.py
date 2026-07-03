"""
NLP Service - India-specific product extraction and normalization.
Uses a hybrid approach: keyword whitelist + brand database + spaCy NER + negative filtering.
"""
import re
import spacy
import logging
from typing import List, Optional, Set
from rapidfuzz import fuzz
from app.core.config import settings

logger = logging.getLogger(__name__)

# ─── India-specific product keyword whitelist (~200 keywords) ───
PRODUCT_KEYWORDS: Set[str] = {
    # Electronics > Audio
    "earbuds", "earphones", "headphones", "headset", "neckband", "tws",
    "speaker", "soundbar", "subwoofer", "amplifier", "dac",
    # Electronics > Mobile
    "smartphone", "phone", "mobile", "iphone", "pixel", "galaxy",
    "charger", "power bank", "powerbank", "cable", "adapter",
    "screen protector", "phone case", "back cover",
    # Electronics > Computers
    "laptop", "notebook", "macbook", "chromebook", "desktop", "pc",
    "monitor", "keyboard", "mouse", "mousepad", "webcam", "usb hub",
    "ssd", "hard drive", "ram", "graphics card", "gpu", "processor",
    "pen drive", "pendrive", "external hard disk",
    # Electronics > Wearables
    "smartwatch", "smart watch", "fitness band", "fitness tracker",
    "smart ring", "smart glasses",
    # Electronics > TV & Display
    "tv", "television", "smart tv", "projector", "streaming stick",
    "fire stick", "firestick", "chromecast",
    # Electronics > Camera
    "camera", "dslr", "mirrorless", "action camera", "gopro",
    "drone", "gimbal", "tripod", "ring light",
    # Electronics > Gaming
    "console", "playstation", "ps5", "xbox", "nintendo", "switch",
    "gaming chair", "gaming desk", "joystick", "controller",
    "gaming mouse", "gaming keyboard", "gaming headset",
    # Home & Kitchen (India-specific)
    "mixer grinder", "mixer", "grinder", "juicer", "blender",
    "pressure cooker", "cooker", "induction cooktop", "induction",
    "air fryer", "oven", "microwave", "toaster", "sandwich maker",
    "water purifier", "ro purifier", "purifier",
    "inverter ac", "ac", "air conditioner", "split ac", "window ac",
    "ceiling fan", "fan", "table fan", "tower fan",
    "inverter", "ups", "stabilizer", "voltage stabilizer",
    "refrigerator", "fridge", "washing machine",
    "vacuum cleaner", "robot vacuum", "mop",
    "iron", "steam iron", "garment steamer",
    "geyser", "water heater", "immersion rod",
    "chimney", "kitchen chimney", "hob",
    "coffee maker", "coffee machine", "kettle", "electric kettle",
    "rice cooker", "slow cooker",
    "tiffin box", "lunch box", "bottle", "flask", "thermos",
    # Fashion (India-specific)
    "kurta", "kurti", "saree", "sari", "lehenga", "salwar",
    "sherwani", "nehru jacket", "blazer", "suit",
    "jeans", "trousers", "chinos", "shorts",
    "t-shirt", "tshirt", "shirt", "polo",
    "dress", "top", "tunic",
    "sneakers", "shoes", "sandals", "chappals", "juttis", "kolhapuri",
    "boots", "loafers", "heels",
    "backpack", "bag", "handbag", "wallet", "belt",
    "sunglasses", "watch", "bracelet", "necklace", "earrings",
    "dupatta", "stole", "scarf",
    # Beauty & Personal Care (India-specific)
    "serum", "moisturizer", "sunscreen", "face wash", "cleanser",
    "toner", "face mask", "sheet mask",
    "shampoo", "conditioner", "hair oil", "hair serum",
    "lipstick", "foundation", "concealer", "mascara", "kajal",
    "nail polish", "makeup kit", "makeup brush",
    "perfume", "deodorant", "body wash", "body lotion",
    "trimmer", "shaver", "razor", "epilator",
    "hair dryer", "straightener", "curling iron",
    "beard oil", "beard trimmer",
    "face roller", "derma roller",
    # Books & Media
    "book", "kindle", "ebook", "audiobook", "novel",
    # Sports & Fitness
    "yoga mat", "dumbbell", "resistance band", "skipping rope",
    "treadmill", "exercise bike", "elliptical",
    "cricket bat", "cricket ball", "football", "badminton racket",
    "protein powder", "whey protein", "shaker",
    # Baby & Kids
    "stroller", "car seat", "diaper", "baby monitor",
    # Home Decor
    "bedsheet", "pillow", "mattress", "curtain",
    "table lamp", "led strip", "smart bulb",
}

# ─── Popular brands in India (global + Indian brands) ───
BRAND_NAMES: Set[str] = {
    # Indian electronics brands
    "boat", "boAt", "noise", "realme", "oneplus", "micromax", "lava",
    "fire-boltt", "fireboltt", "pTron", "ptron", "mivi", "zebronics",
    "portronics", "ambrane", "syska", "bajaj", "havells", "crompton",
    "orient", "luminous", "v-guard", "usha", "prestige", "butterfly",
    "preethi", "sujata", "kenstar", "blue star", "voltas", "godrej",
    "titan", "fastrack", "wildcraft", "woodland", "bata",
    # Global brands popular in India
    "apple", "samsung", "xiaomi", "oppo", "vivo", "asus", "lenovo",
    "dell", "hp", "acer", "msi", "gigabyte",
    "sony", "jbl", "bose", "sennheiser", "marshall", "harman kardon",
    "logitech", "razer", "corsair", "steelseries", "hyperx",
    "dyson", "philips", "panasonic", "lg", "whirlpool", "bosch", "siemens",
    "nike", "adidas", "puma", "reebok", "skechers", "crocs",
    "zara", "h&m", "uniqlo", "levi's", "levis",
    "nykaa", "mamaearth", "wow", "plum", "dot & key", "minimalist",
    "cetaphil", "cerave", "the ordinary", "olay", "lakme", "maybelline",
    "ikea", "home centre", "amazon basics", "amazonbasics",
    "decathlon", "fitbit", "garmin",
    # Gaming
    "nintendo", "playstation", "xbox", "steam deck",
}

# ─── Negative filter: words that should NEVER be products ───
NEGATIVE_WORDS: Set[str] = {
    # People, places, events
    "modi", "india", "pakistan", "china", "usa", "america", "delhi", "mumbai",
    "bangalore", "bengaluru", "chennai", "kolkata", "hyderabad", "pune",
    "bjp", "congress", "aap", "election", "vote", "government",
    "cricket", "ipl", "world cup",  # events, not products
    "wedding", "marriage", "festival", "diwali", "holi",

    # Generic non-product terms
    "price", "review", "reviews", "best", "worst", "top", "vs", "versus",
    "guide", "list", "recommendation", "recommendations", "suggestion",
    "help", "advice", "opinion", "opinions", "experience", "experiences",
    "question", "questions", "issue", "issues", "problem", "problems",
    "comparison", "alternative", "alternatives", "option", "options",
    "worth", "budget", "cheap", "expensive", "affordable",
    "anyone", "everyone", "someone", "people", "guys", "folks",
    "thing", "things", "stuff", "everything", "nothing", "something",
    "time", "day", "week", "month", "year", "today", "yesterday",
    "good", "bad", "great", "terrible", "amazing", "awful",
    "please", "thanks", "thank", "sorry", "hello", "hi",
    "sale", "offer", "deal", "discount", "coupon",
    "delivery", "shipping", "return", "refund", "warranty",
    "update", "updates", "version", "latest",
}

# ─── India-specific product category taxonomy ───
CATEGORY_TAXONOMY = {
    "Electronics > Audio > Earbuds/TWS": ["earbud", "tws", "airdopes", "neckband"],
    "Electronics > Audio > Headphones": ["headphone", "headset", "over-ear", "on-ear"],
    "Electronics > Audio > Speakers": ["speaker", "soundbar", "subwoofer", "portable speaker"],
    "Electronics > Mobile > Smartphones": ["phone", "smartphone", "mobile", "iphone", "pixel", "galaxy", "redmi", "poco"],
    "Electronics > Mobile > Accessories": ["charger", "power bank", "cable", "adapter", "case", "cover", "screen protector"],
    "Electronics > Computers > Laptops": ["laptop", "notebook", "macbook", "chromebook"],
    "Electronics > Computers > Desktops": ["desktop", "pc", "mini pc"],
    "Electronics > Computers > Peripherals": ["monitor", "keyboard", "mouse", "webcam", "mousepad"],
    "Electronics > Computers > Components": ["ssd", "ram", "gpu", "graphics card", "processor", "motherboard"],
    "Electronics > Wearables": ["smartwatch", "smart watch", "fitness band", "fitness tracker", "smart ring"],
    "Electronics > TV & Display": ["tv", "television", "smart tv", "projector", "fire stick", "chromecast"],
    "Electronics > Camera": ["camera", "dslr", "mirrorless", "action camera", "gopro", "drone"],
    "Electronics > Gaming": ["console", "playstation", "ps5", "xbox", "nintendo", "switch", "gaming"],
    "Home & Kitchen > Cooking": ["mixer", "grinder", "juicer", "blender", "air fryer", "oven", "microwave",
                                  "pressure cooker", "induction", "cooktop", "toaster", "sandwich maker",
                                  "coffee maker", "kettle", "rice cooker"],
    "Home & Kitchen > Appliances": ["refrigerator", "fridge", "washing machine", "vacuum", "iron", "geyser",
                                     "water heater", "chimney", "hob", "dishwasher"],
    "Home & Kitchen > Climate": ["ac", "air conditioner", "fan", "ceiling fan", "cooler", "heater"],
    "Home & Kitchen > Water": ["water purifier", "ro purifier", "purifier"],
    "Home & Kitchen > Power": ["inverter", "ups", "stabilizer"],
    "Fashion > Clothing": ["kurta", "kurti", "saree", "lehenga", "shirt", "t-shirt", "jeans", "dress",
                            "blazer", "jacket", "hoodie", "trousers", "shorts"],
    "Fashion > Footwear": ["sneakers", "shoes", "sandals", "boots", "loafers", "heels", "chappals"],
    "Fashion > Accessories": ["backpack", "bag", "wallet", "belt", "sunglasses", "watch"],
    "Beauty > Skincare": ["serum", "moisturizer", "sunscreen", "face wash", "cleanser", "toner",
                           "face mask", "face roller"],
    "Beauty > Haircare": ["shampoo", "conditioner", "hair oil", "hair serum", "hair dryer", "straightener"],
    "Beauty > Makeup": ["lipstick", "foundation", "concealer", "mascara", "kajal", "makeup"],
    "Beauty > Grooming": ["trimmer", "shaver", "razor", "beard oil", "beard trimmer", "perfume", "deodorant"],
    "Sports & Fitness": ["yoga mat", "dumbbell", "resistance band", "treadmill", "cricket bat",
                          "protein powder", "shaker"],
}


class NLPService:
    """Service for India-specific NLP operations using spaCy + keyword matching"""

    _nlp = None

    @classmethod
    def get_nlp(cls):
        """Lazy load spaCy model"""
        if cls._nlp is None:
            try:
                cls._nlp = spacy.load(settings.SPACY_MODEL)
            except OSError:
                raise RuntimeError(
                    f"spaCy model '{settings.SPACY_MODEL}' not found. "
                    f"Please install it with: python -m spacy download {settings.SPACY_MODEL}"
                )
        return cls._nlp

    @staticmethod
    def normalize_product_name(name: str) -> str:
        """
        Normalize product name for deduplication
        - Convert to lowercase
        - Remove special characters (keep alphanumeric and spaces)
        - Remove common stop words
        """
        # Convert to lowercase
        normalized = name.lower()

        # Remove special characters, keep alphanumeric and spaces
        normalized = re.sub(r'[^a-z0-9\s]', '', normalized)

        # Remove extra whitespace
        normalized = ' '.join(normalized.split())

        # Remove common stop words
        stop_words = {'the', 'a', 'an', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
                      'i', 'my', 'me', 'we', 'our', 'you', 'your', 'it', 'its',
                      'this', 'that', 'these', 'those', 'and', 'or', 'but', 'of', 'for',
                      'in', 'on', 'at', 'to', 'with', 'from', 'by', 'as', 'into'}
        words = normalized.split()
        normalized = ' '.join([w for w in words if w not in stop_words])

        return normalized

    @staticmethod
    def _is_negative(text: str) -> bool:
        """Check if text matches any negative filter word (shouldn't be a product)"""
        text_lower = text.lower().strip()
        words = set(text_lower.split())

        # If the entire text is a single negative word, reject it
        if text_lower in NEGATIVE_WORDS:
            return True

        # If most words are negative, reject (e.g., "best thing ever")
        negative_count = sum(1 for w in words if w in NEGATIVE_WORDS)
        if len(words) > 0 and negative_count / len(words) > 0.6:
            return True

        return False

    @staticmethod
    def _keyword_match(text: str) -> List[str]:
        """
        Match text against product keyword whitelist.
        Returns list of matched product keywords found in the text.
        """
        text_lower = text.lower()
        matches = []

        for keyword in PRODUCT_KEYWORDS:
            # Use word boundary matching for single words
            if len(keyword.split()) == 1:
                pattern = r'\b' + re.escape(keyword) + r'(?:s|es)?\b'
            else:
                pattern = re.escape(keyword)

            if re.search(pattern, text_lower):
                matches.append(keyword)

        return matches

    @staticmethod
    def _brand_match(text: str) -> List[str]:
        """
        Match text against known brand names.
        Returns list of brand names found in the text.
        """
        text_lower = text.lower()
        matches = []

        for brand in BRAND_NAMES:
            brand_lower = brand.lower()
            # Word boundary matching
            pattern = r'\b' + re.escape(brand_lower) + r'\b'
            if re.search(pattern, text_lower):
                matches.append(brand)

        return matches

    @classmethod
    def extract_product_names(cls, text: str) -> List[str]:
        """
        Extract potential product names from text using a hybrid approach:
        1. spaCy NER for ORG/PRODUCT entities
        2. Keyword match against India-specific whitelist
        3. Brand + category pattern matching
        """
        if not text or len(text.strip()) < 5:
            return []

        nlp = cls.get_nlp()
        # Limit text length for spaCy processing
        doc = nlp(text[:2000])

        candidates = []
        seen_normalized = set()

        # ─── Pass 1: spaCy NER entities ───
        for ent in doc.ents:
            if ent.label_ in ["ORG", "PRODUCT"]:
                name = ent.text.strip()
                if name and len(name) > 1 and not cls._is_negative(name):
                    norm = cls.normalize_product_name(name)
                    if norm and norm not in seen_normalized:
                        seen_normalized.add(norm)
                        candidates.append(name)

        # ─── Pass 2: Keyword matching ───
        keyword_matches = cls._keyword_match(text)
        brand_matches = cls._brand_match(text)

        # For each keyword match, try to extract a more specific product name
        # by looking for "brand + keyword" combinations
        text_lower = text.lower()
        for brand in brand_matches:
            for keyword in keyword_matches:
                # Look for "brand keyword" pattern in the text
                brand_lower = brand.lower()
                keyword_lower = keyword.lower()

                # Try various patterns: "brand keyword", "keyword by brand"
                patterns = [
                    rf'\b{re.escape(brand_lower)}\s+\w*\s*{re.escape(keyword_lower)}',
                    rf'\b{re.escape(brand_lower)}\s+[\w\s]{{1,30}}',  # brand + up to 30 chars
                ]

                for pattern in patterns:
                    match = re.search(pattern, text_lower)
                    if match:
                        product_name = match.group().strip()
                        # Find original case from the text
                        start = match.start()
                        end = match.end()
                        original = text[start:end].strip()

                        if original and len(original) > 3 and not cls._is_negative(original):
                            norm = cls.normalize_product_name(original)
                            if norm and len(norm) > 2 and norm not in seen_normalized:
                                seen_normalized.add(norm)
                                candidates.append(original)
                        break  # Use first match for this brand+keyword combo

        # If no brand+keyword combos found, add standalone brand and keyword matches
        if not candidates:
            # Add brand names found (these are likely product mentions)
            for brand in brand_matches:
                norm = cls.normalize_product_name(brand)
                if norm and norm not in seen_normalized and not cls._is_negative(brand):
                    seen_normalized.add(norm)
                    candidates.append(brand)

            # Add keyword matches only if they appear as meaningful noun chunks
            for chunk in doc.noun_chunks:
                chunk_text = chunk.text.strip()
                chunk_lower = chunk_text.lower()

                if len(chunk_text) < 4 or cls._is_negative(chunk_text):
                    continue

                # Check if this noun chunk contains a product keyword
                has_keyword = any(kw in chunk_lower for kw in keyword_matches)
                has_brand = any(b.lower() in chunk_lower for b in brand_matches)

                if has_keyword or has_brand:
                    norm = cls.normalize_product_name(chunk_text)
                    if norm and len(norm) > 2 and norm not in seen_normalized:
                        seen_normalized.add(norm)
                        candidates.append(chunk_text)

        # Final cleanup: remove very short or very long candidates
        final = []
        for name in candidates:
            clean = name.strip()
            if 2 < len(clean) < 80 and not cls._is_negative(clean):
                final.append(clean)

        return final[:10]  # Cap at 10 products per text

    @staticmethod
    def calculate_similarity(name1: str, name2: str) -> float:
        """
        Calculate similarity between two product names (0-1 scale)
        Uses fuzzy string matching with token sort ratio
        """
        normalized1 = NLPService.normalize_product_name(name1)
        normalized2 = NLPService.normalize_product_name(name2)

        # Use token sort ratio for better matching
        similarity = fuzz.token_sort_ratio(normalized1, normalized2)

        return similarity / 100.0  # Convert to 0-1 scale

    @staticmethod
    def is_duplicate(name1: str, name2: str, threshold: Optional[float] = None) -> bool:
        """
        Check if two product names are duplicates
        """
        if threshold is None:
            threshold = settings.PRODUCT_NAME_SIMILARITY_THRESHOLD

        similarity = NLPService.calculate_similarity(name1, name2)
        return similarity >= threshold

    @staticmethod
    def extract_category(text: str, product_name: str) -> Optional[str]:
        """
        Extract product category from text using India-specific taxonomy.
        Checks both the text and the product name against category keywords.
        """
        combined = f"{text} {product_name}".lower()

        best_category = None
        best_match_count = 0

        for category, keywords in CATEGORY_TAXONOMY.items():
            match_count = sum(1 for kw in keywords if kw in combined)
            if match_count > best_match_count:
                best_match_count = match_count
                best_category = category

        return best_category
