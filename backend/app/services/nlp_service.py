"""
NLP Service - Product name extraction and normalization
"""
import re
import spacy
from typing import List, Optional, Tuple
from thefuzz import fuzz
from app.core.config import settings


class NLPService:
    """Service for NLP operations using spaCy"""
    
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
        stop_words = {'the', 'a', 'an', 'is', 'are', 'was', 'were', 'be', 'been', 'being'}
        words = normalized.split()
        normalized = ' '.join([w for w in words if w not in stop_words])
        
        return normalized
    
    @staticmethod
    def extract_product_names(text: str) -> List[str]:
        """
        Extract potential product names from text using NLP
        Uses Named Entity Recognition (NER) to find products
        """
        nlp = NLPService.get_nlp()
        doc = nlp(text)
        
        product_names = []
        
        # Extract named entities that might be products
        # Focus on ORG (organizations/brands), PRODUCT (if available), and noun phrases
        for ent in doc.ents:
            # Check if entity is likely a product (ORG, PRODUCT, or brand name)
            if ent.label_ in ["ORG", "PRODUCT"]:
                product_names.append(ent.text.strip())
        
        # Also extract noun phrases that might be products
        # Look for patterns like "new [noun phrase]" or "[brand] [noun]"
        for chunk in doc.noun_chunks:
            if len(chunk.text.split()) >= 2 and len(chunk.text) > 5:
                # Filter out common non-product phrases
                text_lower = chunk.text.lower()
                if not any(word in text_lower for word in ['people', 'someone', 'everyone', 'thing', 'time', 'day']):
                    product_names.append(chunk.text.strip())
        
        # Deduplicate while preserving order
        seen = set()
        unique_names = []
        for name in product_names:
            normalized = NLPService.normalize_product_name(name)
            if normalized and normalized not in seen:
                seen.add(normalized)
                unique_names.append(name)
        
        return unique_names
    
    @staticmethod
    def calculate_similarity(name1: str, name2: str) -> float:
        """
        Calculate similarity between two product names (0-100)
        Uses fuzzy string matching
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
        Extract product category from text
        Simple keyword-based approach (can be enhanced with ML)
        """
        text_lower = text.lower()
        
        # Category keywords mapping
        category_keywords = {
            "Electronics > Audio > Headphones": ["headphone", "earbud", "earphone", "airpod", "headset"],
            "Electronics > Audio > Speakers": ["speaker", "soundbar", "audio system"],
            "Electronics > Mobile > Phones": ["phone", "smartphone", "iphone", "android"],
            "Electronics > Computers > Laptops": ["laptop", "notebook", "macbook"],
            "Electronics > Gaming > Consoles": ["console", "playstation", "xbox", "nintendo"],
            "Electronics > Wearables > Smartwatches": ["watch", "smartwatch", "apple watch"],
            "Fashion > Clothing": ["shirt", "dress", "hoodie", "jacket", "sneaker"],
            "Home > Kitchen": ["coffee maker", "blender", "air fryer"],
        }
        
        for category, keywords in category_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                return category
        
        return None

