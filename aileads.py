import sqlite3
import os
from dotenv import load_dotenv
import time
import json
from pydantic import BaseModel
from google import genai

# ============================================
# 1. SETUP GEMINI CLIENT
# ============================================
# Make sure to set your API key first:
# export GEMINI_API_KEY=""

load_dotenv()

# Now you can access it
api_key = os.environ.get("GEMINI_API_KEY")

# ============================================
# 2. DEFINE STRUCTURED OUTPUT SCHEMA
# ============================================
class LeadAnalysis(BaseModel):
    lead_score: int
    reasoning: str
    custom_whatsapp_opener: str
    pain_point_hypothesis: str

# ============================================
# 3. DATABASE SETUP
# ============================================
def setup_database():
    """Creates the database if it doesn't exist."""
    conn = sqlite3.connect("leads.db")
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS businesses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            category TEXT,
            rating REAL,
            reviews INTEGER,
            website TEXT,
            context TEXT,
            lead_score INTEGER,
            ai_opener TEXT,
            pain_point TEXT,
            status TEXT DEFAULT 'new',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            processed_at TIMESTAMP
        )
    ''')
    conn.commit()
    print("✅ Database initialized successfully")
    return conn

# ============================================
# 4. CORE BOT LOGIC
# ============================================
def process_leads(conn):
    """The Core Bot Logic: Fetch, Analyze, Update."""
    cursor = conn.cursor()
    
    # Grab 5 unprocessed leads at a time
    cursor.execute("""
        SELECT id, name, category, rating, reviews, context, website 
        FROM businesses 
        WHERE status = 'new' 
        LIMIT 5
    """)
    leads = cursor.fetchall()
    
    if not leads:
        print("💤 No new leads to process. Bot sleeping...")
        return False

    print(f"\n🎯 Found {len(leads)} new leads to process\n")

    for lead in leads:
        lead_id, name, category, rating, reviews, context, website = lead
        print(f"🔍 Analyzing: {name} ({category})")
        
        # Build the prompt with the specific lead data
        prompt = f"""
You are a top-tier digital marketing SDR. Analyze this local business:

Name: {name}
Category: {category}
Rating: {rating} stars (based on {reviews} reviews)
Website: {website if website else 'NO WEBSITE FOUND'}
Context/Bio: {context if context else 'No additional context'}

Task:
1. Score them from 1-10 on how likely they need an AI bot, website, or marketing services. 
   (No website + good reviews = high score. Bad reviews = lower score)
2. Give a 1-sentence reasoning for the score.
3. Identify their biggest likely pain point.
4. Write a casual, 1-to-2 sentence WhatsApp opener. DO NOT introduce yourself yet. 
   Just mention something specific about them to get a reply.
"""

        try:
            # Call Gemini using Structured Outputs
            response = client.models.generate_content(
                model='gemini-2.0-flash-exp',
                contents=prompt,
                config={
                    'response_mime_type': 'application/json',
                    'response_schema': LeadAnalysis,
                    'temperature': 0.7  # Slight creativity for the opener
                },
            )
            
            # Extract the structured data
            analysis = json.loads(response.text)
            
            # Update the database with the AI's brainpower
            cursor.execute('''
                UPDATE businesses 
                SET lead_score = ?, 
                    pain_point = ?, 
                    ai_opener = ?, 
                    status = 'ready_for_outreach',
                    processed_at = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (
                analysis['lead_score'], 
                analysis['pain_point_hypothesis'], 
                analysis['custom_whatsapp_opener'], 
                lead_id
            ))
            
            conn.commit()
            
            print(f"✅ Enriched & Scored [{analysis['lead_score']}/10]: {name}")
            print(f"   💡 Pain Point: {analysis['pain_point_hypothesis']}")
            print(f"   💬 Opener: {analysis['custom_whatsapp_opener']}\n")
            
            # Be polite to the API rate limits
            time.sleep(2)
            
        except Exception as e:
            print(f"❌ Error processing {name}: {e}")
            # Mark as failed so we can retry later
            cursor.execute(
                "UPDATE businesses SET status = 'failed' WHERE id = ?", 
                (lead_id,)
            )
            conn.commit()
            
    return True

# ============================================
# 5. HELPER FUNCTIONS
# ============================================
def get_stats(conn):
    """Get statistics about leads in the database."""
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM businesses WHERE status = 'new'")
    new_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM businesses WHERE status = 'ready_for_outreach'")
    ready_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM businesses WHERE status = 'failed'")
    failed_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT AVG(lead_score) FROM businesses WHERE lead_score IS NOT NULL")
    avg_score = cursor.fetchone()[0]
    
    return {
        'new': new_count,
        'ready': ready_count,
        'failed': failed_count,
        'avg_score': round(avg_score, 2) if avg_score else 0
    }

def display_stats(conn):
    """Display current bot statistics."""
    stats = get_stats(conn)
    print("\n" + "="*50)
    print("📊 BOT STATISTICS")
    print("="*50)
    print(f"🆕 New Leads:           {stats['new']}")
    print(f"✅ Ready for Outreach:  {stats['ready']}")
    print(f"❌ Failed:              {stats['failed']}")
    print(f"📈 Average Score:       {stats['avg_score']}/10")
    print("="*50 + "\n")

# ============================================
# 6. MAIN BOT LOOP
# ============================================
if __name__ == "__main__":
    print("="*50)
    print("🚀 AI LEAD-GEN BOT STARTING...")
    print("="*50)
    
    # Check for API key
    if not os.environ.get("GEMINI_API_KEY"):
        print("❌ ERROR: GEMINI_API_KEY not found in environment variables")
        print("Please run: export GEMINI_API_KEY='your_api_key_here'")
        exit(1)
    
    # Initialize database
    db_conn = setup_database()
    
    # Show initial stats
    display_stats(db_conn)
    
    print("🤖 Bot is now monitoring the database...")
    print("💡 Add leads with status='new' and watch them get enriched!\n")
    
    # Continuous Bot Loop
    try:
        while True:
            processed_something = process_leads(db_conn)
            
            if processed_something:
                display_stats(db_conn)
            
            # Sleep for 60 seconds before checking for new leads again
            time.sleep(60)
            
    except KeyboardInterrupt:
        print("\n\n🛑 Bot stopped by user")
        display_stats(db_conn)
        db_conn.close()
        print("👋 Goodbye!")
