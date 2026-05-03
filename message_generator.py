# message_generator.py
import json
import random
import re
import math
from pathlib import Path

class MessageGenerator:
    def __init__(self, templates_path="messages/templates.json"):
        self.templates_path = Path(templates_path)
        self.templates = self._load_templates()

    def _load_templates(self):
        if not self.templates_path.exists():
            raise FileNotFoundError(
                f"\n❌ Templates file not found: {self.templates_path}\n"
                f"   Please create messages/templates.json\n"
            )

        with open(self.templates_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        if not data:
            raise ValueError("\n❌ templates.json is empty\n")

        if 'default' not in data:
            raise KeyError(
                "\n❌ 'default' key missing in templates.json\n"
                "   Add a 'default' category to handle unknown business types.\n"
            )

        print(f"📝 Loaded templates for {len(data)} business categories")
        return data

    def _get_category_key(self, category):
        if not category:
            return 'default'

        category_lower = str(category).lower().strip()

        if category_lower in self.templates:
            return category_lower

        for key in self.templates:
            if key == 'default':
                continue
            if key in category_lower or category_lower in key:
                return key

        aliases = {
            'food': 'restaurant',
            'eatery': 'restaurant',
            'cafe': 'restaurant',
            'coffee': 'restaurant',
            'lounge': 'restaurant',
            'bar': 'restaurant',
            'grill': 'restaurant',
            'suya': 'restaurant',
            'fast food': 'restaurant',
            'hair salon': 'salon',
            'barber': 'salon',
            'spa': 'salon',
            'nail': 'salon',
            'beauty': 'salon',
            'clothing': 'boutique',
            'fashion': 'boutique',
            'store': 'supermarket',
            'shop': 'supermarket',
            'market': 'supermarket',
            'pharmacy': 'pharmacy',
            'chemist': 'pharmacy',
            'drugstore': 'pharmacy',
            'clinic': 'hospital',
            'medical': 'hospital',
            'health': 'hospital',
            'dental': 'hospital',
            'church': 'church',
            'ministry': 'church',
            'mosque': 'mosque',
            'islamic': 'mosque',
            'college': 'school',
            'university': 'school',
            'academy': 'school',
            'nursery': 'school',
            'primary': 'school',
            'secondary': 'school',
            'fitness': 'gym',
            'workout': 'gym',
            'hotel': 'hotel',
            'motel': 'hotel',
            'lodge': 'hotel',
            'inn': 'hotel',
            'guest house': 'hotel',
            'properties': 'real estate',
            'homes': 'real estate',
            'mechanic': 'auto repair',
            'automobile': 'auto repair',
            'car wash': 'auto repair',
            'legal': 'law firm',
            'attorney': 'law firm',
            'solicitor': 'law firm',
            'cake': 'bakery',
            'bread': 'bakery',
            'pastry': 'bakery'
        }

        for alias, key in aliases.items():
            if alias in category_lower:
                if key in self.templates:
                    return key

        return 'default'

    def generate_message(self, business):
        category = str(business.get('category', ''))
        key = self._get_category_key(category)
        template = random.choice(self.templates[key])

        return template.format(
            name=str(business.get('name', 'there')),
            rating=str(business.get('rating', 'N/A')),
            rating_count=str(business.get('rating_count', 'many')),
            category=category.title()
        )

    def _safe_phone(self, phone):
        if phone is None:
            return 'N/A'
        if isinstance(phone, float):
            return 'N/A' if math.isnan(phone) else str(int(phone))
        if isinstance(phone, int):
            return str(phone)
        if isinstance(phone, str):
            return phone.strip()
        return 'N/A'

    def _clean_nigerian_phone(self, phone):
        if not phone or phone == 'N/A':
            return None
        digits = re.sub(r'\D', '', phone)
        if len(digits) < 10:
            return None
        if digits.startswith('234'):
            return digits
        elif digits.startswith('0'):
            return '234' + digits[1:]
        elif len(digits) == 10:
            return '234' + digits
        else:
            return '234' + digits[-10:]

    def _clean_value(self, value):
        """Clean NaN and invalid values"""
        if value is None:
            return None
        if isinstance(value, float) and math.isnan(value):
            return None
        return value

    def generate_all_messages(self, businesses):
        messages = []
        skipped = 0

        for business in businesses:
            phone = self._safe_phone(business.get('phone'))
            clean_phone = self._clean_nigerian_phone(phone)

            if not clean_phone:
                skipped += 1
                continue

            messages.append({
                'name': str(business.get('name') or 'Unknown'),
                'phone': clean_phone,
                'original_phone': phone,
                'category': str(business.get('category') or 'business'),
                'has_website': bool(business.get('has_website') or False),
                'website': self._clean_value(business.get('website')),
                'rating': str(business.get('rating') or 'N/A'),
                'rating_count': int(business.get('rating_count') or 0),
                'message': self.generate_message(business)
            })

        print(f"   📱 Generated : {len(messages)} messages")
        print(f"   ⏭️  Skipped   : {skipped} (no phone)")
        return messages

    def save_to_file(self, messages, output_path="output/phone_numbers.json"):
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # ✅ Clean ALL NaN values before saving to JSON
        def clean(value):
            if isinstance(value, float) and math.isnan(value):
                return None
            return value

        cleaned = [
            {k: clean(v) for k, v in msg.items()}
            for msg in messages
        ]

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(cleaned, f, indent=2, ensure_ascii=False)

        no_web = len([m for m in cleaned if not m.get('has_website')])
        with_web = len([m for m in cleaned if m.get('has_website')])

        print(f"💾 Saved {len(cleaned)} messages to {output_path}")
        print(f"   📧 Without website : {no_web}")
        print(f"   🌐 With website    : {with_web}")
        return output_path
