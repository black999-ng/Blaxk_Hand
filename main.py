# main.py
import pandas as pd
from scraper import GoogleMapsScraper
from analyzer import BusinessAnalyzer
from profile_manager import ProfileManager
from message_generator import MessageGenerator
from cli_interface import BLAXKCLI
from pathlib import Path
import time

def load_existing_leads():
    """Load previously scraped leads"""
    excel_path = Path('output/top_leads.xlsx')
    existing = []
    
    if excel_path.exists():
        try:
            df = pd.read_excel(excel_path)
            # ✅ Clean NaN values before converting to dict
            df = df.replace({float('nan'): None, pd.NA: None})
            df = df.where(pd.notna(df), None)
            existing = df.to_dict('records')
        except:
            pass
    
    return existing

def merge_leads(existing, new_leads):
    """Merge new leads with existing, remove duplicates"""
    seen_phones = set()
    merged = []
    
    # Add existing first
    for lead in existing:
        phone = lead.get('phone', '')
        if phone and phone != 'N/A':
            seen_phones.add(phone)
            merged.append(lead)
    
    # Add new leads (skip duplicates)
    new_count = 0
    for lead in new_leads:
        phone = lead.get('phone', '')
        if phone and phone != 'N/A' and phone not in seen_phones:
            seen_phones.add(phone)
            merged.append(lead)
            new_count += 1
    
    return merged, new_count

def main():
    cli = BLAXKCLI()
    cli.show_banner()
    
    # Configuration
    SEARCH_QUERIES = [
        "hotel", "lounge", "restaurant", "realtors" 
    ]
    LOCATION = "adamawa, NG"
    
    cli.show_config(LOCATION, len(SEARCH_QUERIES))
    
    # Load existing leads
    cli.step("Loading existing leads...")
    existing_leads = load_existing_leads()
    cli.info(f"Found {len(existing_leads)} existing leads")
    
    # Setup
    cli.step("Initializing Chrome profile...")
    profile_mgr = ProfileManager()
    profile_path = profile_mgr.get_profile(0)
    cli.success("Profile ready")
    
    # Scraping
    cli.step(f"Scraping {len(SEARCH_QUERIES)} business types...")
    scraper = GoogleMapsScraper(LOCATION, profile_path=profile_path, headless=True)
    
    start_time = time.time()
    all_businesses = scraper.scrape_multiple_queries(SEARCH_QUERIES)
    elapsed = time.time() - start_time
    
    print()
    cli.success(f"Scraped {len(all_businesses)} businesses in {elapsed:.1f}s")
    
    if not all_businesses:
        cli.warning("No businesses found")
        return
    
    # Analysis
    cli.step("Analyzing with Gemini AI...")
    analyzer = BusinessAnalyzer()
    new_top_leads = analyzer.analyze_businesses(all_businesses)
    
    if not new_top_leads:
        cli.warning("No leads matched criteria")
        return
    
    # Merge with existing
    cli.step("Merging with existing leads...")
    all_leads, new_count = merge_leads(existing_leads, new_top_leads)
    cli.success(f"Added {new_count} new leads (Total: {len(all_leads)})")
    
    # Generate messages
    cli.step("Generating WhatsApp messages...")
    msg_gen = MessageGenerator()
    messages = msg_gen.generate_all_messages(all_leads)
    
    # Stats
    without_website = len([b for b in all_businesses if not b['has_website']])
    with_website = len([b for b in all_businesses if b['has_website']])
    
    cli.show_stats(len(all_businesses), len(messages), without_website)
    cli.info(f"Businesses WITH websites: {with_website}")
    
    # Save
    Path('output').mkdir(exist_ok=True)
    df = pd.DataFrame(all_leads)
    df = df.replace({float('nan'): None})  # ✅ FIX: Replace NaN with None
    df.to_excel('output/top_leads.xlsx', index=False)
    msg_gen.save_to_file(messages)
    
    cli.success(f"Saved {len(all_leads)} total leads")
    
    # Display results
    cli.show_results_table(all_leads[:10])
    
    cli.console.print(f"\n[bold green]✨ {new_count} new leads added![/bold green]")
    cli.console.print("\n[bold green]Next:[/bold green] [cyan]python send_whatsapp.py[/cyan]\n")

if __name__ == "__main__":
    main()
