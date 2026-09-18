"""
Expanded Content Database - Diverse Tamil Topics
Includes history, science, culture, mythology, lifestyle, and more
"""

import json
from typing import List, Dict
import random


class ExpandedContentDatabase:
    """Comprehensive Tamil content database with diverse topics"""
    
    def __init__(self):
        self.all_content = self._initialize_all_content()
    
    def _initialize_all_content(self) -> List[Dict]:
        """Initialize comprehensive content database"""
        return {
            'history': self._get_history_content(),
            'mythology': self._get_mythology_content(),
            'science': self._get_science_content(),
            'culture': self._get_culture_content(),
            'lifestyle': self._get_lifestyle_content(),
            'nature': self._get_nature_content(),
            'inventions': self._get_inventions_content(),
            'famous_people': self._get_famous_people_content(),
            'festivals': self._get_festivals_content(),
            'food': self._get_food_content(),
        }
    
    def _get_history_content(self) -> List[Dict]:
        """Tamil history facts"""
        return [
            {
                "title": "சோழ சாம்ராஜ்ஜியம் - தமிழ்நாட்டின் பொற்காலம்",
                "content": "சோழ சாம்ராஜ்ஜியம் கி.பி. 9 ஆம் நூற்றாண்டு முதல் 13 ஆம் நூற்றாண்டு வரை ஆட்சி செய்தது. இந்த சாம்ராஜ்ஜியம் கலை, கட்டடக்கலை மற்றும் வணிகத்தை வளர்த்தது. பிரிஹதீஸ்வரர் கோயில் சோழ கட்டடக்கலையின் சிறந்த உதாரணம்.",
                "duration": 50,
                "category": "history",
                "difficulty": "medium"
            },
            {
                "title": "பாண்டிய சாம்ராஜ்ஜியம் - கடல் வணிகத்தின் மாஸ்டர்",
                "content": "பாண்டிய சாம்ராஜ்ஜியம் தமிழ்நாட்டின் தெற்கு பகுதியில் ஆட்சி செய்தது. இந்த சாம்ராஜ்ஜியம் முத்து மற்றும் பவளங்களுக்கு பிரசித்தமாக இருந்தது. பாண்டிய மன்னர்கள் கடல் வணிகத்தை வளர்த்தனர்.",
                "duration": 48,
                "category": "history",
                "difficulty": "medium"
            },
            {
                "title": "சங்க இலக்கியம் - தமிழ்மொழியின் ஆதாரம்",
                "content": "சங்க இலக்கியம் தமிழ் இலக்கியத்தின் மிகப் பழமையான தொகுப்பாகும். இதில் 2000 ஆண்டுகளுக்கு முன்பே எழுதப்பட்ட கவிதைகள் உள்ளன. சங்க கவிஞர்கள் தமிழ் மொழியை செழுமையாக வளர்த்தனர்.",
                "duration": 50,
                "category": "history",
                "difficulty": "hard"
            },
            {
                "title": "பல்லவ சாம்ராஜ்ஜியம் - கலையின் பிতா",
                "content": "பல்லவ சாம்ராஜ்ஜியம் கி.பி. 3 ஆம் நூற்றாண்டு முதல் 9 ஆம் நூற்றாண்டு வரை ஆட்சி செய்தது. மாமல்லபுரம் கோயில்கள் பல்லவ கட்டடக்கலையின் சிறந்த உதாரணங்களாகும்.",
                "duration": 52,
                "category": "history",
                "difficulty": "medium"
            }
        ]
    
    def _get_mythology_content(self) -> List[Dict]:
        """Tamil mythology and legends"""
        return [
            {
                "title": "முருகன் - தமிழ்மக்களின் தெய்வம்",
                "content": "முருகன் தமிழ் மக்களின் முக்கிய தெய்வமாகும். அவர் வேலாயுதம் என்ற ஆயுதத்தை வைத்திருக்கிறார். முருகன் பூஜை தமிழ்நாட்டில் பெரிய விழாவாக கொண்டாடப்படுகிறது.",
                "duration": 45,
                "category": "mythology",
                "difficulty": "easy"
            },
            {
                "title": "மகாபலிபுரம் - கற்பனையின் நகரம்",
                "content": "மகாபலிபுரம் பல்லவ மன்னர்களால் கட்டப்பட்ட ஒரு புராண நகரமாகும். இங்கு பல்வேறு கோயில்கள் மற்றும் ஐதிஹ்யங்கள் உள்ளன. மகாபலிபுரம் கற்பனை மற்றும் கலையின் சங்கமம்.",
                "duration": 48,
                "category": "mythology",
                "difficulty": "medium"
            },
            {
                "title": "சிவன் - நிலையின் சின்னம்",
                "content": "சிவன் இந்து மதத்தின் முக்கிய தெய்வமாகும். சிவன் நிலையம், அழிவு மற்றும் புनर्जन்ம ஆகியவற்றின் சின்னம். சிவன் பூஜை தமிழ்நாட்டில் மிகவும் பிரபலமாகும்.",
                "duration": 50,
                "category": "mythology",
                "difficulty": "medium"
            }
        ]
    
    def _get_science_content(self) -> List[Dict]:
        """Science and technology facts"""
        return [
            {
                "title": "பண்டைய தமிழ் கணிதம் - பூஜ்ஜியத்தின் கண்டுபிடிப்பு",
                "content": "பண்டைய தமிழர்கள் கணிதத்தில் வல்லுநர்களாக இருந்தனர். அவர்கள் பூஜ்ஜியம் மற்றும் தசம முறையை பயன்படுத்தினர். தமிழ் கணிதம் உலக கணிதத்திற்கு பங்களிப்பு செய்தது.",
                "duration": 45,
                "category": "science",
                "difficulty": "hard"
            },
            {
                "title": "சித்த மருத்துவம் - பண்டைய வைத்தியம்",
                "content": "சித்த மருத்துவம் தமிழ்நாட்டில் உருவான ஒரு பண்டைய மருத்துவ முறையாகும். இது 5000 ஆண்டுகளுக்கு முன்பே உருவாக்கப்பட்டது. சித்த மருத்துவம் இன்றும் பயன்படுத்தப்படுகிறது.",
                "duration": 50,
                "category": "science",
                "difficulty": "medium"
            },
            {
                "title": "தமிழ் வான்கோள் அறிவு - நட்சத்திரங்களின் ரகசியம்",
                "content": "பண்டைய தமிழர்கள் வான்கோள் அறிவில் வல்லுநர்களாக இருந்தனர். அவர்கள் நட்சத்திரங்கள் மற்றும் கிரகங்களைப் பற்றி அறிந்திருந்தனர். தமிழ் வான்கோள் அறிவு உலக வான்கோள் அறிவுக்கு பங்களிப்பு செய்தது.",
                "duration": 48,
                "category": "science",
                "difficulty": "hard"
            }
        ]
    
    def _get_culture_content(self) -> List[Dict]:
        """Tamil culture and traditions"""
        return [
            {
                "title": "பரதநாட்டியம் - தமிழ்நாட்டின் நৃத்தம்",
                "content": "பரதநாட்டியம் தமிழ்நாட்டில் உருவான ஒரு கிளாசிக்கல் நৃத்தமாகும். இந்த நৃத்தம் உலக நৃத்தங்களில் பிரசித்தமாக உள்ளது. பரதநாட்டியம் கோயில்களில் பெண்கள் மூலம் நடனமாடப்பட்டது.",
                "duration": 48,
                "category": "culture",
                "difficulty": "easy"
            },
            {
                "title": "கர்நாடக இசை - தமிழ்நாட்டின் சுரம்",
                "content": "கர்நாடக இசை தமிழ்நாட்டில் உருவான ஒரு கிளாசிக்கல் இசை முறையாகும். இந்த இசை முறை உலக இசையில் பிரசித்தமாக உள்ளது. தமிழ் இசைக் கலைஞர்கள் உலக மஞ்சங்களில் பாடுகின்றனர்.",
                "duration": 48,
                "category": "culture",
                "difficulty": "medium"
            },
            {
                "title": "தமிழ் திரைப்படம் - கலையின் மாற்றம்",
                "content": "தமிழ் திரைப்படம் உலக திரைப்படத்தில் ஒரு முக்கிய இடத்தை வகிக்கிறது. தமிழ் திரைப்படங்கள் பல சர்வதேச விருதுகளை வென்றுள்ளன. தமிழ் திரைப்படம் தமிழ் சংस்கৃதியை உலகிற்கு கொண்டு சென்றுள்ளது.",
                "duration": 50,
                "category": "culture",
                "difficulty": "easy"
            }
        ]
    
    def _get_lifestyle_content(self) -> List[Dict]:
        """Lifestyle and wellness tips"""
        return [
            {
                "title": "யோகா - தமிழ்நாட்டின் ஆரோக்கிய வழி",
                "content": "யோகா பண்டைய தமிழ்நாட்டில் உருவான ஒரு ஆரோக்கிய முறையாகும். யோகா உடல் மற்றும் மனதை வலுவாக்குகிறது. யோகா இன்றும் பல மக்களால் பயன்படுத்தப்படுகிறது.",
                "duration": 45,
                "category": "lifestyle",
                "difficulty": "easy"
            },
            {
                "title": "தமிழ் உணவு - ஆரோக்கியத்தின் ரகசியம்",
                "content": "தமிழ் உணவு உலக உணவுக்கூடத்தில் ஒரு முக்கிய இடத்தை வகிக்கிறது. தமிழ் உணவுகள் அவற்றின் சுவை மற்றும் ஆரோக்கியத்திற்கு பிரசித்தமாக உள்ளன. தமிழ் உணவு பல நூற்றாண்டுகளாக வளர்ந்து வருகிறது.",
                "duration": 45,
                "category": "lifestyle",
                "difficulty": "easy"
            },
            {
                "title": "தமிழ் மூலிகைகள் - প্রকৃதির மருந்து",
                "content": "தமிழ்நாட்டில் பல மூலிகைகள் உள்ளன. இந்த மூலிகைகள் பல நோய்களை குணப்படுத்துகின்றன. தமிழ் மூலிகைகள் பண்டைய காலம் முதல் பயன்படுத்தப்பட்டு வருகின்றன.",
                "duration": 48,
                "category": "lifestyle",
                "difficulty": "medium"
            }
        ]
    
    def _get_nature_content(self) -> List[Dict]:
        """Nature and environment facts"""
        return [
            {
                "title": "தமிழ்நாட்டின் வனங்கள் - பசுமையின் சொர்க்கம்",
                "content": "தமிழ்நாட்டில் பல வனங்கள் உள்ளன. இந்த வனங்கள் பல விலங்குகள் மற்றும் பறவைகளுக்கு வீடாக உள்ளன. தமிழ்நாட்டின் வனங்கள் சுற்றுச்சூழல் பாதுகாப்புக்கு முக்கியமாக உள்ளன.",
                "duration": 45,
                "category": "nature",
                "difficulty": "easy"
            },
            {
                "title": "நீலகிரி - மலைகளின் ராணி",
                "content": "நீலகிரி தமிழ்நாட்டின் மிகவும் அழகான மலைகளாகும். இங்கு பல வகையான தாவரங்கள் மற்றும் விலங்குகள் உள்ளன. நீலகிரி சுற்றுலாவிற்கு ஒரு பிரபலமான இடமாகும்.",
                "duration": 48,
                "category": "nature",
                "difficulty": "easy"
            },
            {
                "title": "கொடைக்கானல் - மেघங்களின் நகரம்",
                "content": "கொடைக்கானல் தமிழ்நாட்டின் மிகவும் அழகான மலை நகரமாகும். இங்கு ஐந்து ஏரிகள் உள்ளன. கொடைக்கானல் மிகவும் குளிர்ந்த வானிலையுடன் உள்ளது.",
                "duration": 45,
                "category": "nature",
                "difficulty": "easy"
            }
        ]
    
    def _get_inventions_content(self) -> List[Dict]:
        """Tamil inventions and contributions"""
        return [
            {
                "title": "தமிழ் எழுத்து - மொழியின் அடிப்படை",
                "content": "தமிழ் எழுத்து உலகின் மிகப் பழமையான எழுத்துக்களில் ஒன்றாகும். தமிழ் எழுத்து மிகவும் விஞ்ஞான ரீதியாக வடிவமைக்கப்பட்டுள்ளது. தமிழ் எழுத்து பல மொழிகளை பாதிக்கிறது.",
                "duration": 50,
                "category": "inventions",
                "difficulty": "hard"
            },
            {
                "title": "தமிழ் மொழி - உலகின் பழமையான மொழி",
                "content": "தமிழ் மொழி உலகின் மிகப் பழமையான மொழிகளில் ஒன்றாகும். இது சுமார் 2000 ஆண்டுகளுக்கு முன்பே இலக்கியங்களாக பதிவு செய்யப்பட்டுள்ளது. தமிழ் மொழி இன்றும் 7 கோடி மக்களால் பேசப்படுகிறது.",
                "duration": 50,
                "category": "inventions",
                "difficulty": "hard"
            }
        ]
    
    def _get_famous_people_content(self) -> List[Dict]:
        """Famous Tamil personalities"""
        return [
            {
                "title": "கமலஹாசன் - தமிழ் சினிமாவின் அரசன்",
                "content": "கமலஹாசன் தமிழ் சினிமாவின் மிகப் பெரிய நடிகர்களில் ஒருவர். அவர் பல சர்வதேச விருதுகளை வென்றுள்ளார். கமலஹாசன் தமிழ் சினிமாவை உலக மঞ்சங்களுக்கு கொண்டு சென்றுள்ளார்.",
                "duration": 48,
                "category": "famous_people",
                "difficulty": "easy"
            },
            {
                "title": "ரஜினிகாந்த் - தமிழ்மக்களின் ஐதிஹ்யம்",
                "content": "ரஜினிகாந்த் தமிழ் சினிமாவின் மிகப் பெரிய நடிகர்களில் ஒருவர். அவர் பல தசாப்தங்களாக தமிழ் சினிமায் பணிபுரிந்துள்ளார். ரஜினிகாந்த் தமிழ் மக்களின் ஐதிஹ்யமாக கருதப்படுகிறார்.",
                "duration": 48,
                "category": "famous_people",
                "difficulty": "easy"
            },
            {
                "title": "பெரியார் - சமூக சீர்திருத்தவாதி",
                "content": "பெரியார் தமிழ் சமூக சீர்திருத்தவாதி மற்றும் தலைவர்களில் ஒருவர். அவர் பெண் உரிமைகள் மற்றும் சமூக நீதிக்கு போராடினார். பெரியார் தமிழ் சமூகத்தில் பெரிய மாற்றத்தை கொண்டு வந்தார்.",
                "duration": 50,
                "category": "famous_people",
                "difficulty": "medium"
            }
        ]
    
    def _get_festivals_content(self) -> List[Dict]:
        """Tamil festivals and celebrations"""
        return [
            {
                "title": "பொங்கல் - தமிழ்மக்களின் விழா",
                "content": "பொங்கல் தமிழ்மக்களின் முக்கிய விழாவாகும். இந்த விழா ஜனவரி மாதத்தில் கொண்டாடப்படுகிறது. பொங்கல் விழாவில் மக்கள் புதிய ஆண்டை வரவேற்கிறார்கள்.",
                "duration": 45,
                "category": "festivals",
                "difficulty": "easy"
            },
            {
                "title": "தீபாவளி - விளக்குகளின் விழா",
                "content": "தீபாவளி தமிழ் மக்களின் மிகப் பெரிய விழாவாகும். இந்த விழாவில் மக்கள் விளக்குகளை ஏற்றுகிறார்கள். தீபாவளி நல்லது மற்றும் கெட்டதுக்கு இடையே நல்லதின் வெற்றியை குறிக்கிறது.",
                "duration": 45,
                "category": "festivals",
                "difficulty": "easy"
            },
            {
                "title": "நவராத்திரி - தெய்வ பூஜையின் விழா",
                "content": "நவராத்திரி தமிழ் மக்களின் ஒரு முக்கிய விழாவாகும். இந்த விழாவில் தெய்வ பூஜை செய்யப்படுகிறது. நவராத்திரி 9 நாட்கள் கொண்டாடப்படுகிறது.",
                "duration": 45,
                "category": "festivals",
                "difficulty": "easy"
            }
        ]
    
    def _get_food_content(self) -> List[Dict]:
        """Tamil food and recipes"""
        return [
            {
                "title": "இட்லி - தமிழ்நாட்டின் பிரபல உணவு",
                "content": "இட்லி தமிழ்நாட்டின் மிகப் பிரபல உணவாகும். இது அரிசி மற்றும் உளுந்தில் இருந்து தயாரிக்கப்படுகிறது. இட்லி ஆரோக்கியமான மற்றும் சுস்வादுவான உணவாகும்.",
                "duration": 40,
                "category": "food",
                "difficulty": "easy"
            },
            {
                "title": "தோசை - தமிழ்நாட்டின் உணவு",
                "content": "தோசை தமிழ்நாட்டின் ஒரு பிரபல உணவாகும். இது அரிசி மற்றும் உளுந்தில் இருந்து தயாரிக்கப்படுகிறது. தோசை பல வகைகளில் தயாரிக்கப்படுகிறது.",
                "duration": 40,
                "category": "food",
                "difficulty": "easy"
            },
            {
                "title": "சாம்பார் - தமிழ்நாட்டின் மசாலா",
                "content": "சாம்பார் தமிழ்நாட்டின் ஒரு பிரபல மசாலாவாகும். இது பல்வேறு மூலிகைகள் மற்றும் மசாலாக்களில் இருந்து தயாரிக்கப்படுகிறது। சாம்பார் ஆரோக்கியமான மற்றும் சுস்வादுவான உணவாகும்.",
                "duration": 42,
                "category": "food",
                "difficulty": "easy"
            }
        ]
    
    def get_random_diverse_content(self, duration_target: int = 900) -> Dict:
        """
        Get random content from diverse categories
        Ensures variety in daily videos
        
        Args:
            duration_target: Target duration in seconds
            
        Returns:
            Dictionary with content and metadata
        """
        # Select random category
        categories = list(self.all_content.keys())
        selected_category = random.choice(categories)
        
        # Get content from selected category
        category_content = self.all_content[selected_category]
        selected_items = random.sample(category_content, min(2, len(category_content)))
        
        # Create script
        script = self._create_script(selected_items, selected_category)
        
        return {
            'title': f"{selected_items[0]['title']} - {selected_category.upper()}",
            'description': self._create_description(selected_items, selected_category),
            'script': script,
            'content': selected_items,
            'category': selected_category,
            'total_duration': sum(item['duration'] for item in selected_items) + 60,
            'tags': self._generate_tags(selected_category),
            'difficulty': selected_items[0]['difficulty']
        }
    
    def _create_script(self, content_list: List[Dict], category: str) -> str:
        """Create script from content"""
        script = f"வணக்கம் நண்பர்களே! இந்த வீடியோவில் நாம் {category} பற்றி பேசப் போகிறோம்.\n\n"
        
        for idx, content in enumerate(content_list, 1):
            script += f"{idx}. {content['title']}\n"
            script += f"{content['content']}\n\n"
        
        script += "நன்றி! இந்த வீடியோ பிடித்திருந்தால் லைக் செய்யவும், சப்ஸ்கிரைப் செய்யவும் மற்றும் கமெண்ட் செய்யவும்."
        
        return script
    
    def _create_description(self, content_list: List[Dict], category: str) -> str:
        """Create YouTube description"""
        description = f"தமிழ் {category} - சுவையான உண்மைகள்\n\n"
        description += "இந்த வீடியோவில் நாம் பேசும் விஷயங்கள்:\n"
        
        for idx, content in enumerate(content_list, 1):
            description += f"{idx}. {content['title']}\n"
        
        description += f"\n#தமிழ் #{category} #சுவையான_உண்மைகள்"
        
        return description
    
    def _generate_tags(self, category: str) -> List[str]:
        """Generate tags based on category"""
        base_tags = ['தமிழ்', 'வரலாறு', 'சுவையான_உண்மைகள்', 'தமிழ்_நாடு']
        category_tags = {
            'history': ['வரலாறு', 'சாம்ராஜ்ஜியம்', 'பண்டைய_தமிழ்'],
            'mythology': ['புராணம்', 'தெய்வம்', 'கதை'],
            'science': ['விஞ்ஞானம்', 'கண்டுபிடிப்பு', 'ஆராய்ச்சி'],
            'culture': ['கலை', 'நৃத்தம்', 'இசை'],
            'lifestyle': ['ஆரோக்கியம்', 'வாழ்க்கை', 'குறிப்புகள்'],
            'nature': ['பகுதி', 'வனம்', 'பசுமை'],
            'inventions': ['கண்டுபிடிப்பு', 'மொழி', 'எழுத்து'],
            'famous_people': ['நபர்', 'நடிகர்', 'தலைவர்'],
            'festivals': ['விழா', 'கொண்டாட்டம்', 'பண்டிகை'],
            'food': ['உணவு', 'சமையல்', 'சுவை']
        }
        
        return base_tags + category_tags.get(category, [])
    
    def get_all_categories(self) -> List[str]:
        """Get all available categories"""
        return list(self.all_content.keys())
    
    def get_content_count(self) -> Dict:
        """Get content count by category"""
        return {
            category: len(content)
            for category, content in self.all_content.items()
        }


if __name__ == "__main__":
    db = ExpandedContentDatabase()
    
    # Show available categories
    print("Available Categories:")
    for category in db.get_all_categories():
        print(f"  - {category}")
    
    print("\nContent Count:")
    for category, count in db.get_content_count().items():
        print(f"  {category}: {count} items")
    
    # Get random content
    content = db.get_random_diverse_content()
    print(f"\nRandom Content: {content['title']}")
    print(f"Category: {content['category']}")
    print(f"Duration: {content['total_duration']} seconds")
