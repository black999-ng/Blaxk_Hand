# analyzer.py
from google import genai
from google.genai import types
from dotenv import load_dotenv
import os
import json

load_dotenv()

class BusinessAnalyzer:
    def __init__(self):
        self.client = genai.Client(api_key=os.getenv('GEMINI_API_KEY'))
    
    def analyze_businesses(self, businesses):
        """Use Gemini to rank and analyze businesses"""
        
        if not businesses:
            print("⚠️  No businesses provided to analyzer")
            return []
        
        print(f"📥 Received {len(businesses)} total businesses")
        
        # Debug: Check structure of first business
        if businesses:
            first = businesses[0]
            print(f"🔍 First business structure check:")
            print(f"   - has_website: {first.get('has_website')} (type: {type(first.get('has_website'))})")
            print(f"   - rating_count: {first.get('rating_count')} (type: {type(first.get('rating_count'))})")
        
        # Filter: No website + Good ratings
        print(f"\n🔍 Applying filter: has_website=False AND rating_count >= 20")
        
        filtered = []
        for b in businesses:
            has_website = b.get('has_website')
            rating_count = b.get('rating_count', 0)
            
            # Debug each business
            passes_website = has_website is False or has_website == False
            passes_rating = rating_count >= 20
            
            if passes_website and passes_rating:
                filtered.append(b)
        
        print(f"✅ Businesses WITHOUT website: {len([b for b in businesses if not b.get('has_website')])}")
        print(f"✅ Businesses WITH 20+ reviews: {len([b for b in businesses if b.get('rating_count', 0) >= 20])}")
        print(f"✅ Businesses passing BOTH: {len(filtered)}")
        
        # MANUAL FALLBACK: If filter fails, use all businesses with 10+ reviews
        if not filtered:
            print("\n⚠️  Filter returned 0 results")
            print("🔧 MANUAL FALLBACK: Using businesses with 10+ reviews instead")
            
            filtered = [b for b in businesses if b.get('rating_count', 0) >= 10]
            print(f"📊 Fallback found {len(filtered)} businesses")
            
            if not filtered:
                print("⚠️  Even fallback returned 0. Using ALL businesses.")
                filtered = businesses
        
        # Show what we're analyzing
        print(f"\n📊 Analyzing {len(filtered)} businesses:")
        for i, b in enumerate(filtered[:5], 1):
            print(f"   {i}. {b.get('name')} - {b.get('rating_count')} reviews, website={b.get('has_website')}")
        if len(filtered) > 5:
            print(f"   ... and {len(filtered) - 5} more")
        
        # Prepare simplified data
        simplified = [
            {
                'name': b.get('name', 'N/A'),
                'rating': b.get('rating', '0'),
                'rating_count': b.get('rating_count', 0),
                'phone': b.get('phone', 'N/A'),
                'address': b.get('address', 'N/A'),
                'email': b.get('email', 'Not found'),
                'category': b.get('category', 'Unknown')
            }
            for b in filtered
        ]
        
        prompt = f"""
You are a business analyst. Rank these businesses by their potential to need a website and benefit from web design services.

Scoring criteria:
- High review count (50+ reviews = high engagement)
- Good ratings (4.0+ stars)
- Business types that benefit most from websites: restaurants, gyms, salons, services
- Businesses without email are harder to contact (lower priority)

Businesses to analyze:
{json.dumps(simplified, indent=2)}

Return a JSON array with ALL businesses ranked by priority. Add:
- "priority_score": 1-10 (10 = highest priority)
- "recommendation": Brief reason (max 20 words)

Return ONLY valid JSON array, no other text.
"""
        
        try:
            print("\n🤖 Calling Gemini AI...")
            response = self.client.models.generate_content(
                model='gemini-2.5-flash',
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    temperature=0.7
                )
            )
            
            result_text = response.text.strip()
            
            # Remove markdown if present
            if '```' in result_text:
                parts = result_text.split('```')
                for part in parts:
                    if part.strip().startswith('[') or part.strip().startswith('json'):
                        result_text = part.replace('json', '').strip()
                        break
            
            ranked = json.loads(result_text)
            
            if not isinstance(ranked, list):
                raise ValueError("Response is not a list")
            
            if len(ranked) == 0:
                raise ValueError("Empty results from AI")
            
            print(f"✅ AI ranked {len(ranked)} top leads")
            return ranked
            
        except json.JSONDecodeError as e:
            print(f"⚠️  JSON parsing failed: {e}")
            print(f"Raw response: {response.text[:500]}...")
            print("\n🔄 Using manual fallback ranking...")
            return self._fallback_ranking(filtered)
        
        except Exception as e:
            print(f"❌ Gemini API Error: {type(e).__name__}: {e}")
            print("\n🔄 Using manual fallback ranking...")
            return self._fallback_ranking(filtered)
    
    def _fallback_ranking(self, filtered):
        """Fallback ranking when AI fails"""
        print("📊 Sorting by review count...")
        
        if not filtered:
            print("⚠️  No businesses to rank!")
            return []
        
        sorted_leads = sorted(
            filtered,
            key=lambda x: x.get('rating_count', 0),
            reverse=True
        )
        
        for i, lead in enumerate(sorted_leads):
            lead['priority_score'] = max(1, 10 - (i // (len(sorted_leads) // 10 + 1)))
            lead['recommendation'] = f"High engagement with {lead.get('rating_count', 0)} reviews"
        
        print(f"✅ Fallback ranked {len(sorted_leads)} leads")
        return sorted_leads
