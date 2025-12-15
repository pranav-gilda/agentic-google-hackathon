"""
MCP Expander - Scalable Knowledge Base
Expands MCP capabilities with semantic matching and topic expansion
to handle more topics without hardcoding everything.
"""

from typing import Dict, List, Optional
from mcp_server import EDUCATIONAL_FACTS, _get_educational_fact_impl


class MCPExpander:
    """Expands MCP capabilities with semantic matching and topic inference."""
    
    def __init__(self):
        """Initialize MCP Expander."""
        # Topic aliases and synonyms for better matching
        self.topic_aliases = {
            # Space
            "red planet": "mars",
            "martian": "mars",
            "lunar": "moon",
            "solar": "sun",
            "star": "stars",
            "planet": "planets",
            "jupiter": "planets",
            "saturn": "planets",
            "earth": "planets",
            # Dinosaurs
            "tyrannosaurus": "t-rex",
            "tyrannosaurus rex": "t-rex",
            "triceratops": "triceratops",
            "brachiosaurus": "brachiosaurus",
            "stegosaurus": "stegosaurus",
            "dinosaur": "t-rex",  # Default to T-Rex
            "dinos": "t-rex",
            # Animals
            "elephant": "elephants",
            "whale": "whales",
            "penguin": "penguins",
            "lion": "lions",
            "dolphin": "dolphins",
            # Ocean
            "coral reef": "coral",
            "shark": "sharks",
            "octopus": "octopus",
        }
        
        # Category keywords for semantic matching
        self.category_keywords = {
            "space": ["space", "planet", "mars", "moon", "sun", "star", "solar", "galaxy", "astronaut", "rocket", "orbit"],
            "dinosaurs": ["dinosaur", "dino", "jurassic", "fossil", "prehistoric", "extinct", "t-rex", "triceratops"],
            "animals": ["animal", "wildlife", "creature", "mammal", "elephant", "whale", "penguin", "lion", "dolphin"],
            "ocean": ["ocean", "sea", "marine", "underwater", "coral", "shark", "octopus", "fish", "whale"]
        }
    
    def expand_topic(self, topic: str) -> Optional[str]:
        """
        Expand a topic using aliases and synonyms.
        
        Args:
            topic: The topic to expand
        
        Returns:
            Expanded topic name or None if not found
        """
        topic_lower = topic.lower().strip()
        
        # Check direct match
        if topic_lower in self.topic_aliases:
            return self.topic_aliases[topic_lower]
        
        # Check if topic contains any alias
        for alias, canonical in self.topic_aliases.items():
            if alias in topic_lower:
                return canonical
        
        # Check in knowledge base directly
        for category, facts in EDUCATIONAL_FACTS.items():
            if topic_lower in facts:
                return topic_lower
        
        return None
    
    def infer_category(self, topic: str) -> Optional[str]:
        """
        Infer the category of a topic using keyword matching.
        
        Args:
            topic: The topic to categorize
        
        Returns:
            Category name or None
        """
        topic_lower = topic.lower()
        
        # Check category keywords
        for category, keywords in self.category_keywords.items():
            for keyword in keywords:
                if keyword in topic_lower:
                    return category
        
        return None
    
    def get_fact_with_expansion(self, topic: str) -> Dict:
        """
        Get educational fact with topic expansion and category inference.
        
        Args:
            topic: The topic to get a fact about
        
        Returns:
            Dictionary with fact, topic, category, and expansion info
        """
        original_topic = topic
        expanded_topic = self.expand_topic(topic)
        category = self.infer_category(topic)
        
        # Try to get fact
        if expanded_topic:
            fact = _get_educational_fact_impl(expanded_topic)
            used_topic = expanded_topic
        else:
            # Try category-based fact
            if category and category in EDUCATIONAL_FACTS:
                # Get first fact from category
                first_topic = next(iter(EDUCATIONAL_FACTS[category]))
                fact = _get_educational_fact_impl(first_topic)
                used_topic = first_topic
            else:
                fact = _get_educational_fact_impl(topic)
                used_topic = topic
        
        return {
            "original_topic": original_topic,
            "used_topic": used_topic,
            "category": category,
            "fact": fact,
            "expanded": expanded_topic is not None,
            "category_inferred": category is not None
        }
    
    def detect_topics_in_text(self, text: str) -> List[str]:
        """
        Detect educational topics mentioned in text.
        
        Args:
            text: Text to analyze
        
        Returns:
            List of detected topics
        """
        text_lower = text.lower()
        detected = []
        
        # Check all known topics
        for category, facts in EDUCATIONAL_FACTS.items():
            for topic in facts.keys():
                if topic in text_lower or topic.replace('-', ' ') in text_lower:
                    detected.append(topic)
        
        # Check aliases
        for alias, canonical in self.topic_aliases.items():
            if alias in text_lower and canonical not in detected:
                detected.append(canonical)
        
        # Check category keywords
        for category, keywords in self.category_keywords.items():
            for keyword in keywords:
                if keyword in text_lower:
                    # Find a representative topic from this category
                    if category in EDUCATIONAL_FACTS:
                        rep_topic = next(iter(EDUCATIONAL_FACTS[category]))
                        if rep_topic not in detected:
                            detected.append(rep_topic)
                    break
        
        return list(set(detected))  # Remove duplicates

