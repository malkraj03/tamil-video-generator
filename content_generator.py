"""
Content Generator for Tamil History and Facts
Generates interesting historical facts and fun facts in Tamil
Uses the expanded content database with diverse categories
"""

import json
import random
import hashlib
from datetime import datetime
from typing import List, Dict
from pathlib import Path
import logging

from content_database import ExpandedContentDatabase

logger = logging.getLogger(__name__)

# File to track used content (prevents repeats)
USED_CONTENT_FILE = "used_content.json"


class TamilContentGenerator:
    """Generate Tamil history and fun facts content"""

    def __init__(self):
        self.db = ExpandedContentDatabase()
        self.used_content = self._load_used_content()

    def _load_used_content(self) -> set:
        """Load previously used content hashes"""
        try:
            if Path(USED_CONTENT_FILE).exists():
                with open(USED_CONTENT_FILE, 'r') as f:
                    data = json.load(f)
                    return set(data.get('used_hashes', []))
        except Exception as e:
            logger.warning(f"Error loading used content: {e}")
        return set()

    def _save_used_content(self):
        """Save used content hashes"""
        try:
            with open(USED_CONTENT_FILE, 'w') as f:
                json.dump({
                    'used_hashes': list(self.used_content),
                    'last_updated': datetime.now().isoformat()
                }, f)
        except Exception as e:
            logger.warning(f"Error saving used content: {e}")

    def _content_hash(self, item: Dict) -> str:
        """Generate a hash for a content item"""
        return hashlib.md5(item['title'].encode('utf-8')).hexdigest()[:12]

    def get_random_content(self, duration_target: int = 300) -> Dict:
        """
        Get random content that fits the target duration.
        Selects from diverse categories and avoids repeats.

        Args:
            duration_target: Target duration in seconds (default 300 = 5 mins)

        Returns:
            Dictionary with content, script, and metadata
        """
        # Get all content from all categories
        all_items = []
        for category, items in self.db.all_content.items():
            for item in items:
                item_copy = item.copy()
                item_copy['_category'] = category
                all_items.append(item_copy)

        # Filter out recently used content
        available_items = [
            item for item in all_items
            if self._content_hash(item) not in self.used_content
        ]

        # If we've used everything, reset
        if len(available_items) < 3:
            logger.info("All content used, resetting content tracker")
            self.used_content.clear()
            available_items = all_items

        # Shuffle for randomness
        random.shuffle(available_items)

        # Select content to fit target duration
        selected_content = []
        total_duration = 0

        for item in available_items:
            if total_duration + item['duration'] <= duration_target:
                selected_content.append(item)
                total_duration += item['duration']
                self.used_content.add(self._content_hash(item))

            if total_duration >= (duration_target * 0.7):
                break

        if not selected_content:
            # Fallback: pick at least 2 items
            selected_content = available_items[:2]
            total_duration = sum(i['duration'] for i in selected_content)

        # Save used content tracking
        self._save_used_content()

        # Determine primary category
        categories_used = list(set(item.get('_category', 'general') for item in selected_content))
        primary_category = categories_used[0] if categories_used else 'general'

        # Create English YouTube title for broader reach; keep date for uniqueness
        date_str = datetime.now().strftime('%d-%m-%Y')
        category_display = primary_category.replace('_', ' ').title()
        title_templates = [
            "Incredible Tamil {category} Facts You Must Know!",
            "Amazing Tamil {category} Stories That Will Surprise You",
            "Top Tamil {category} Secrets Revealed",
            "Fascinating Tamil {category} You Never Knew"
        ]
        title = f"{random.choice(title_templates).format(category=category_display)} | {date_str}"

        # Create script
        script = self._create_script(selected_content)

        return {
            'title': title,
            'description': self._create_description(selected_content),
            'script': script,
            'content': selected_content,
            'total_duration': total_duration,
            'estimated_video_duration': total_duration + 30,
            'tags': self._generate_tags(primary_category),
            'category': primary_category
        }

    def _create_script(self, content_list: List[Dict]) -> str:
        """Create an engaging script from content"""
        intro_lines = [
            "வணக்கம் நண்பர்களே! இந்த வீடியோவில் சுவாரஸ்யமான தமிழ் கதைகளையும் அதிசயங்களையும் கண்டுபிடிக்கலாம்!",
            "எல்லோருக்கும் வணக்கம்! தமிழ் வரலாற்றின் மற்றும் பண்பாட்டின் அற்புதமான பக்கங்களை இன்று பார்க்கப் போகிறோம்!",
            "வணக்கம்! தமிழர்களின் பெருமையையும் சுவாரஸ்யமான உண்மைகளையும் இந்த வீடியோவில் காணலாம்!"
        ]

        script = random.choice(intro_lines) + "\n\n"

        for idx, content in enumerate(content_list, 1):
            script += f"{idx}. {content['title']}\n"
            script += f"{content['content']}\n\n"

        script += "நன்றி! இந்த வீடியோ பிடித்திருந்தால் லைக் செய்யவும், சப்ஸ்கிரைப் செய்யவும் மற்றும் கமெண்ட் செய்யவும்."

        return script

    def _create_description(self, content_list: List[Dict]) -> str:
        """Create YouTube description"""
        description = "தமிழ் வரலாறு மற்றும் சுவையான உண்மைகள்\n\n"
        description += "இந்த வீடியோவில் நாம் பேசும் விஷயங்கள்:\n"

        for idx, content in enumerate(content_list, 1):
            description += f"{idx}. {content['title']}\n"

        description += "\n#தமிழ் #வரலாறு #சுவையான_உண்மைகள் #Tamil #History #Facts"

        return description

    def _generate_tags(self, category: str) -> List[str]:
        """Generate tags"""
        base_tags = ['Tamil', 'தமிழ்', 'வரலாறு', 'History', 'Facts',
                     'Tamil History', 'Fun Facts', 'Tamil Nadu',
                     'தமிழ்_நாடு', 'சுவையான_உண்மைகள்']

        category_tags = {
            'history': ['Ancient Tamil', 'Kingdom', 'Dynasty'],
            'mythology': ['Tamil Gods', 'Mythology', 'Temple'],
            'science': ['Tamil Science', 'Ancient Knowledge'],
            'culture': ['Tamil Culture', 'Art', 'Dance'],
            'lifestyle': ['Health', 'Yoga', 'Wellness'],
            'nature': ['Tamil Nadu Nature', 'Hills', 'Forest'],
            'inventions': ['Tamil Inventions', 'Language'],
            'famous_people': ['Tamil Celebrities', 'Leaders'],
            'festivals': ['Tamil Festivals', 'Pongal', 'Deepavali'],
            'food': ['Tamil Food', 'Recipes', 'Cuisine'],
        }

        return base_tags + category_tags.get(category, [])


if __name__ == "__main__":
    generator = TamilContentGenerator()
    content = generator.get_random_content()
    print(json.dumps(content, ensure_ascii=False, indent=2))
