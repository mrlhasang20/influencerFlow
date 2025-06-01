from database import init_db, get_db_session, Creator, User
from datetime import datetime, timezone
import uuid
import pandas as pd
import os
import re
import numpy as np

# Category mapping configuration
CREATOR_CATEGORIES = {
    'sports': {
        'keywords': ['football', 'soccer', 'basketball', 'sports', 'athlete', 'fitness', 'workout', 'training'],
        'handles': ['cristiano', 'leomessi', 'neymarjr', 'kingjames', 'nike', 'realmadrid', 'fcbarcelona'],
        'names': ['Ronaldo', 'Messi', 'Neymar', 'LeBron']
    },
    'entertainment': {
        'keywords': ['actor', 'actress', 'movie', 'film', 'tv', 'entertainment', 'comedy', 'show'],
        'handles': ['therock', 'willsmith', 'vindiesel', 'tomholland'],
        'names': ['Johnson', 'Smith', 'Diesel']
    },
    'music': {
        'keywords': ['singer', 'musician', 'artist', 'band', 'music', 'rap', 'pop'],
        'handles': ['arianagrande', 'beyonce', 'justinbieber', 'taylorswift', 'drake', 'billieeilish'],
        'names': ['Grande', 'Swift', 'Bieber']
    },
    'fashion': {
        'keywords': ['model', 'fashion', 'style', 'beauty', 'clothing'],
        'handles': ['kyliejenner', 'kimkardashian', 'kendalljenner', 'gigihadid'],
        'names': ['Jenner', 'Kardashian', 'Hadid']
    },
    'business': {
        'keywords': ['entrepreneur', 'business', 'company', 'brand', 'ceo'],
        'handles': ['nike', 'adidas', 'zara', 'hm', 'victoriassecret'],
    }
}

# Special category assignments for specific creators
SPECIAL_ASSIGNMENTS = {
    'cristiano': ['sports', 'football', 'lifestyle'],
    'leomessi': ['sports', 'football'],
    'neymarjr': ['sports', 'football'],
    'kyliejenner': ['fashion', 'beauty', 'lifestyle', 'business'],
    'kimkardashian': ['fashion', 'lifestyle', 'business', 'entertainment'],
    'therock': ['entertainment', 'fitness', 'lifestyle'],
    'arianagrande': ['music', 'entertainment'],
    'beyonce': ['music', 'entertainment', 'fashion'],
    'selenagomez': ['entertainment', 'music', 'fashion'],
    'justinbieber': ['music', 'entertainment'],
    'natgeo': ['photography', 'nature', 'education', 'travel'],
    'nike': ['sports', 'fashion', 'business'],
    'victoriassecret': ['fashion', 'business', 'lifestyle'],
    'zendaya': ['entertainment', 'fashion', 'lifestyle'],
    'champagnepapi': ['music', 'entertainment', 'lifestyle'],
    'kingjames': ['sports', 'basketball', 'lifestyle'],
    'gigihadid': ['fashion', 'modeling', 'lifestyle'],
}

def convert_to_number(value):
    """Convert string numbers with k, m, b suffixes to actual numbers"""
    if pd.isna(value):
        return 0
    
    value = str(value).strip().lower()
    
    # Remove % if present
    value = value.replace('%', '')
    
    # Handle empty or invalid values
    if not value or value == 'nan':
        return 0
        
    # Convert k, m, b suffixes
    multipliers = {'k': 1000, 'm': 1000000, 'b': 1000000000}
    
    # Extract number and suffix using regex
    match = re.match(r'^([\d.]+)([kmb])?$', value)
    if not match:
        try:
            return float(value)
        except:
            return 0
            
    number, suffix = match.groups()
    number = float(number)
    
    if suffix:
        number *= multipliers[suffix]
        
    return int(number)

def get_creator_categories(name: str, handle: str, followers: int) -> list:
    """Determine categories for a creator based on their profile data"""
    categories = set()
    
    # Clean handle (remove platform prefix if exists)
    clean_handle = re.sub(r'^insta_\d+_', '', handle.lower())
    
    # 1. Check special assignments first
    if clean_handle in SPECIAL_ASSIGNMENTS:
        return SPECIAL_ASSIGNMENTS[clean_handle]
    
    # 2. Check against category definitions
    for category, data in CREATOR_CATEGORIES.items():
        # Check handles
        if clean_handle in data.get('handles', []):
            categories.add(category)
        
        # Check keywords in handle
        for keyword in data.get('keywords', []):
            if keyword in clean_handle:
                categories.add(category)
        
        # Check keywords in name
        for keyword in data.get('keywords', []):
            if keyword.lower() in name.lower():
                categories.add(category)
        
        # Check specific names
        for name_keyword in data.get('names', []):
            if name_keyword.lower() in name.lower():
                categories.add(category)
    
    # 3. Follower count based categorization
    if followers > 50000000:  # 50M+
        categories.add('mega_influencer')
    elif followers > 1000000:  # 1M+
        categories.add('macro_influencer')
    elif followers > 100000:  # 100K+
        categories.add('mid_tier_influencer')
    else:
        categories.add('micro_influencer')
    
    # If no specific categories were found, add a default
    if not categories or len(categories) == 1 and list(categories)[0].endswith('_influencer'):
        categories.add('lifestyle')
    
    return list(categories)

def seed_instagram_creator(session, creator_data):
    """Seed a single Instagram creator using categories from the dataset"""
    try:
        # Extract creator info
        name = creator_data['channel_info']  # Using channel_info as name
        handle = f"insta_{creator_data['rank']}_{creator_data['channel_info']}"
        followers = convert_to_number(str(creator_data['followers']).rstrip('m'))
        engagement_rate = float(str(creator_data['60_day_eng_rate']).rstrip('%'))
        
        # Get category from the data and convert to list
        category = creator_data.get('category', '')
        categories = [cat.strip() for cat in category.split('&')] if category else []
        
        # Create creator object
        creator = Creator(
            id=str(uuid.uuid4()),
            name=name,
            handle=handle,
            platform='Instagram',
            followers=followers,
            engagement_rate=engagement_rate,
            categories=categories,  # Use categories from CSV
            demographics={},
            language='English',
            location=creator_data.get('country', ''),
            is_verified=True,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        
        # Check if creator already exists
        existing_creator = session.query(Creator).filter(
            Creator.handle == handle,
            Creator.platform == 'Instagram'
        ).first()
        
        if existing_creator:
            # Update categories for existing creator
            existing_creator.categories = categories
            session.merge(existing_creator)
            print(f"Updated categories for existing creator: {handle} with {categories}")
            return False
        
        # Add new creator
        session.add(creator)
        print(f"Added new creator: {handle} with categories: {categories}")
        return True
        
    except Exception as e:
        print(f"Error seeding creator {creator_data.get('channel_info', 'unknown')}: {str(e)}")
        return False

def seed_instagram_creators(creators_data):
    """Seed multiple Instagram creators"""
    session = get_db_session()
    try:
        inserted = 0
        skipped = 0
        errors = 0
        
        for _, creator_data in creators_data.iterrows():
            try:
                success = seed_instagram_creator(session, creator_data)
                if success:
                    inserted += 1
                else:
                    skipped += 1
            except Exception as e:
                print(f"Error processing creator: {e}")
                errors += 1
        
        # Commit all changes
        session.commit()
        
        print(f"\nSeeding complete for Instagram:")
        print(f"Inserted: {inserted}")
        print(f"Skipped: {skipped}")
        print(f"Errors: {errors}")
        
    except Exception as e:
        print(f"Error during seeding: {e}")
        session.rollback()
    finally:
        session.close()

def clean_youtube_data(df):
    """Clean and deduplicate YouTube data"""
    # Drop duplicates based on channel name and username
    df = df.drop_duplicates(subset=['Channel Name', 'username'], keep='first')
    
    # Clean up NaN values
    df = df.fillna({
        'Channel Name': '',
        'username': '',
        'Subscribers': 0,
        'Avg. Views': 0,
        'Engagement Rate': 0.0
    })
    
    return df

def map_youtube_data(row):
    """Map YouTube CSV data to Creator schema"""
    # Extract categories from both Main Video Category and More topics
    categories = []
    
    # Add main category if present
    if pd.notna(row["Main Video Category"]) and str(row["Main Video Category"]) != "nan":
        categories.append(str(row["Main Video Category"]).strip())
    
    # Add main topic if present
    if pd.notna(row["Main topic"]) and str(row["Main topic"]) != "nan":
        categories.append(str(row["Main topic"]).strip())
    
    # Add more topics if present
    if pd.notna(row["More topics"]) and str(row["More topics"]) != "nan":
        more_topics = str(row["More topics"]).split(",")
        categories.extend([t.strip() for t in more_topics])
    
    # Clean up categories list - remove duplicates and empty values
    categories = list(set([cat for cat in categories if cat and cat != "nan"]))
    
    # Map content style from Category or default to main category
    content_style = str(row["Category"]).strip() if pd.notna(row["Category"]) else str(row["Main Video Category"]).strip()
    if content_style == "nan" or not content_style:
        content_style = "Other"
    
    # Calculate average engagement rate
    engagement_rate = float(row["Engagement Rate"]) if pd.notna(row["Engagement Rate"]) else 0.0
    
    # Create demographics dictionary
    demographics = {
        "avg_views": float(row["Views Avg."]) if pd.notna(row["Views Avg."]) else 0.0,
        "avg_comments": float(row["Comments Avg"]) if pd.notna(row["Comments Avg"]) else 0.0,
        "boost_index": float(row["Boost Index"]) if pd.notna(row["Boost Index"]) else 0.0
    }
    
    return {
        "name": str(row["Channel Name"]).strip(),
        "handle": str(row["username"]).strip(),
        "platform": "YouTube",
        "followers": int(float(str(row["followers"]).replace(',', ''))),
        "engagement_rate": engagement_rate,
        "categories": categories,
        "content_style": content_style,
        "language": "English",  # Default since not consistently provided
        "location": str(row["Country"]).strip() if pd.notna(row["Country"]) else "Unknown",
        "collaboration_rate": None,
        "response_rate": float(row["Comments Avg"]) / float(row["Views Avg."]) if pd.notna(row["Comments Avg"]) and pd.notna(row["Views Avg."]) and float(row["Views Avg."]) > 0 else 0.0,
        "is_verified": True,  # Assuming all are verified channels
        "demographics": demographics
    }

def map_instagram_categories(row):
    """Map Instagram influencer to categories based on their profile"""
    categories = []
    
    # Map based on engagement patterns and follower count
    if float(row["60_day_eng_rate"].replace('%', '')) > 5:
        categories.append("High Engagement")
    
    # Map based on follower count
    followers = convert_to_number(row["followers"])
    if followers > 100000000:  # 100M
        categories.append("Mega Influencer")
    elif followers > 10000000:  # 10M
        categories.append("Macro Influencer")
    elif followers > 1000000:  # 1M
        categories.append("Mid-Tier Influencer")
    
    # Map based on content and profile
    if "music" in row["channel_info"].lower() or any(x in row["channel_info"].lower() for x in ["singer", "rapper", "dj"]):
        categories.append("Music")
    
    if any(x in row["channel_info"].lower() for x in ["actor", "actress", "movie", "film", "tv"]):
        categories.append("Entertainment")
    
    if any(x in row["channel_info"].lower() for x in ["sport", "player", "athlete", "team"]):
        categories.append("Sports")
    
    if any(x in row["channel_info"].lower() for x in ["model", "fashion", "style"]):
        categories.append("Fashion")
    
    # Add default category if none matched
    if not categories:
        categories.append("Lifestyle")
    
    return list(set(categories))

def map_instagram_data(row):
    """Map Instagram CSV data to Creator schema with improved category mapping"""
    # Clean engagement rate
    engagement_rate = 0.0
    try:
        engagement_rate = float(str(row["60_day_eng_rate"]).replace('%', ''))
    except (ValueError, TypeError):
        # If conversion fails, calculate from avg_likes and followers
        try:
            followers = convert_to_number(row["followers"])
            avg_likes = convert_to_number(row["avg_likes"])
            if followers > 0:
                engagement_rate = (avg_likes / followers) * 100
        except:
            engagement_rate = 0.0
    
    # Get categories
    categories = map_instagram_categories(row)
    
    # Map content style based on primary category
    content_style = categories[0] if categories else "Lifestyle"
    
    # Calculate demographics
    demographics = {
        "avg_likes": convert_to_number(row["avg_likes"]),
        "total_likes": convert_to_number(row["total_likes"]),
        "posts_count": convert_to_number(str(row["posts"]).replace('k', '000')),
        "influence_score": float(row["influence_score"]) if pd.notna(row["influence_score"]) else 0.0
    }
    
    return {
        "name": str(row["channel_info"]),
        "handle": f"insta_{row['rank']}_{row['channel_info'].lower().replace(' ', '_')}",
        "platform": "Instagram",
        "followers": convert_to_number(row["followers"]),
        "engagement_rate": engagement_rate,
        "categories": categories,
        "content_style": content_style,
        "language": "English",
        "location": str(row["country"]) if pd.notna(row["country"]) else "",
        "collaboration_rate": None,
        "response_rate": 0,
        "is_verified": True,
        "demographics": demographics
    }

def assign_instagram_categories(creator_data):
    """Assign relevant categories to Instagram creators based on their profile"""
    categories = []
    
    # Map of keywords to categories
    category_mapping = {
        'sports': ['football', 'soccer', 'basketball', 'athlete', 'sport', 'fitness'],
        'entertainment': ['actor', 'actress', 'movie', 'film', 'tv', 'entertainment', 'comedy'],
        'music': ['singer', 'musician', 'artist', 'band', 'music', 'rap', 'pop'],
        'fashion': ['model', 'fashion', 'style', 'beauty'],
        'business': ['entrepreneur', 'business', 'company', 'brand'],
        'technology': ['tech', 'technology', 'gadget', 'digital'],
        'lifestyle': ['lifestyle', 'travel', 'food', 'cooking'],
        'politics': ['politics', 'government', 'leader', 'president'],
    }
    
    name = creator_data['name'].lower()
    handle = creator_data['handle'].lower()
    
    # Specific assignments based on the data provided
    specific_assignments = {
        'cristiano': ['sports', 'football', 'lifestyle'],
        'kyliejenner': ['fashion', 'beauty', 'lifestyle', 'business'],
        'leomessi': ['sports', 'football'],
        'selenagomez': ['entertainment', 'music', 'fashion'],
        'therock': ['entertainment', 'fitness', 'lifestyle'],
        'kimkardashian': ['fashion', 'entertainment', 'business', 'lifestyle'],
        'arianagrande': ['music', 'entertainment'],
        'beyonce': ['music', 'entertainment', 'fashion'],
        'nike': ['sports', 'fashion', 'business'],
        'natgeo': ['photography', 'nature', 'education', 'travel'],
    }
    
    # Check for specific assignments first
    handle_without_prefix = handle.replace('insta_', '').split('_', 1)[1]
    if handle_without_prefix in specific_assignments:
        return specific_assignments[handle_without_prefix]
    
    # Generic category assignment based on keywords
    for category, keywords in category_mapping.items():
        if any(keyword in name.lower() or keyword in handle_without_prefix for keyword in keywords):
            categories.append(category)
    
    # If no categories were assigned, add a default category
    if not categories:
        categories = ['lifestyle']  # Default category
    
    return categories

def seed_creators_from_csv(csv_path, platform):
    """Seed creators from a CSV file"""
    try:
        # Read CSV file
        df = pd.read_csv(csv_path)
        
        if platform.lower() == 'instagram':
            # Seed Instagram creators
            seed_instagram_creators(df)
            
    except Exception as e:
        print(f"Error reading CSV file: {e}")

def seed_users():
    """Seed initial users"""
    session = get_db_session()
    try:
        # Add demo users
        users = [
            {
                "id": str(uuid.uuid4()),
                "email": "brand@example.com",
                "name": "Demo Brand",
                "hashed_password": "demo_password_hash",
                "role": "brand"
            },
            {
                "id": str(uuid.uuid4()),
                "email": "agency@example.com",
                "name": "Demo Agency",
                "hashed_password": "demo_password_hash",
                "role": "agency"
            }
        ]
        
        for user_data in users:
            # Check if user exists
            existing_user = session.query(User).filter(
                User.email == user_data["email"]
            ).first()
            
            if not existing_user:
                user = User(**user_data)
                session.add(user)
                print(f"Added user: {user_data['email']}")
            else:
                print(f"Skipping existing user: {user_data['email']}")
        
        session.commit()
        
    except Exception as e:
        print(f"Error seeding users: {e}")
        session.rollback()
    finally:
        session.close()

if __name__ == "__main__":
    # Initialize database
    init_db()
    
    # Seed users
    seed_users()
    
    # Update paths to look in the correct location
    data_paths = [
        ("../datas/top_200_youtubers.csv", "YouTube"),
        ("../datas/top_insta_influencers_data_with_categories.csv", "Instagram")
    ]
    
    # Process each data file
    for csv_path, platform in data_paths:
        print(f"\nProcessing {platform} data from {csv_path}...")
        seed_creators_from_csv(csv_path, platform)
    
    print("\nDatabase seeding completed.")

