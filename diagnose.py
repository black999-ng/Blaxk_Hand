# debug_main.py
from scraper import GoogleMapsScraper
from analyzer import BusinessAnalyzer
from profile_manager import ProfileManager
import json

# Setup
profile_mgr = ProfileManager()
profile_path = profile_mgr.get_profile(0)

# Scrape
scraper = GoogleMapsScraper("Kaduna, NG", profile_path=profile_path, headless=False)
businesses = scraper.scrape_multiple_queries(["restaurant"])

print(f"\n📊 Scraped {len(businesses)} businesses")

# Check data structure
print("\n🔍 Checking first business structure:")
if businesses:
    first = businesses[0]
    print(json.dumps(first, indent=2))
    
    # Check required fields
    required = ['name', 'rating', 'rating_count', 'phone', 'has_website']
    missing = [field for field in required if field not in first]
    
    if missing:
        print(f"\n❌ Missing fields: {missing}")
    else:
        print(f"\n✅ All required fields present")
        
        # Check values
        print(f"\n📋 Field values:")
        print(f"   name: {first['name']}")
        print(f"   rating: {first['rating']}")
        print(f"   rating_count: {first['rating_count']} (type: {type(first['rating_count'])})")
        print(f"   phone: {first['phone']}")
        print(f"   has_website: {first['has_website']} (type: {type(first['has_website'])})")
        print(f"   category: {first.get('category', 'MISSING')}")

# Pass to analyzer
print("\n" + "="*60)
print("PASSING TO ANALYZER...")
print("="*60)

analyzer = BusinessAnalyzer()
results = analyzer.analyze_businesses(businesses)

print(f"\n📊 Analyzer returned: {len(results)} leads")

if results:
    print("\n✅ SUCCESS! First result:")
    print(json.dumps(results[0], indent=2))
else:
    print("\n❌ Analyzer returned empty list")
    
    # Check why
    filtered = [b for b in businesses if not b['has_website'] and b['rating_count'] >= 20]
    print(f"\n🔍 Filter would pass: {len(filtered)} businesses")
    
    if filtered:
        print("\n💡 Filtered businesses:")
        for b in filtered[:3]:
            print(f"   - {b['name']}: {b['rating_count']} reviews, website={b['has_website']}")
