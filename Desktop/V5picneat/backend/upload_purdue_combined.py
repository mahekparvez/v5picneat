"""
Upload COMBINED Purdue menu data (459 unique items)
Combines data from Mar 5-7 and Mar 8-11
Run this to populate purdue_menu_v2 with complete dataset
"""

import os
import json
from supabase import create_client, Client

# Initialize Supabase client
url = "https://rqkfivmphtutghokudgh.supabase.co"
key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJxa2Zpdm1waHR1dGdob2t1ZGdoIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzMwMDY0MjEsImV4cCI6MjA4ODU4MjQyMX0.0R6s2qyQwdQoqfrwcSFYYidXTovjVkyYgfCqZPTsslE"
supabase: Client = create_client(url, key)

# Load the combined Purdue data (459 items)
with open('purdue_menu_combined.json', 'r') as f:
    records = json.load(f)

print(f"📊 Uploading {len(records)} Purdue menu items to Supabase...")
print(f"   Source: Mar 5-7 + Mar 8-11 combined (deduplicated)")

# Upload in batches of 50
batch_size = 50
total_uploaded = 0
errors = 0

for i in range(0, len(records), batch_size):
    batch = records[i:i+batch_size]
    
    # Remove 'date' field before upload (not in table schema)
    clean_batch = []
    for item in batch:
        clean_item = {k: v for k, v in item.items() if k != 'date'}
        clean_batch.append(clean_item)
    
    try:
        response = supabase.table('purdue_menu_v2').insert(clean_batch).execute()
        total_uploaded += len(clean_batch)
        print(f"✅ Batch {i//batch_size + 1}: {len(clean_batch)} items (Total: {total_uploaded}/{len(records)})")
    except Exception as e:
        print(f"❌ Error in batch {i//batch_size + 1}: {e}")
        errors += 1

print(f"\n🎉 Upload complete!")
print(f"   ✅ Uploaded: {total_uploaded}/{len(records)} items")
print(f"   ❌ Errors: {errors} batches")

# Verify the upload
try:
    count_response = supabase.table('purdue_menu_v2').select('id', count='exact').execute()
    print(f"\n✅ Verified: {len(count_response.data)} items in database")
    
    # Show breakdown by dining hall
    halls_response = supabase.table('purdue_menu_v2').select('dining_hall').execute()
    halls = {}
    for item in halls_response.data:
        hall = item['dining_hall']
        halls[hall] = halls.get(hall, 0) + 1
    
    print(f"\nBreakdown by dining hall:")
    for hall, count in sorted(halls.items()):
        print(f"  {hall}: {count} items")
    
    print(f"\n🎯 Database now has {len(count_response.data)} Purdue menu items!")
    print(f"   Includes: Earhart, Ford, Hillenbrand, Wiley, Windsor")
    print(f"   Plus: On-the-GO! locations (grab-and-go)")
        
except Exception as e:
    print(f"❌ Error verifying upload: {e}")
