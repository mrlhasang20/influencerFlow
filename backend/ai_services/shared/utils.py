# Common utilities

import uuid
import hashlib
import re
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import asyncio
import httpx
from functools import wraps
import time

def generate_id(prefix: str = "") -> str:
    """Generate unique ID with optional prefix"""
    unique_id = str(uuid.uuid4())
    return f"{prefix}_{unique_id}" if prefix else unique_id

def generate_hash(text: str) -> str:
    """Generate MD5 hash of text"""
    return hashlib.md5(text.encode()).hexdigest()

def clean_text(text: str) -> str:
    """Clean and normalize text"""
    if not text:
        return ""
    
    # Remove extra whitespace
    text = re.sub(r'\\s+', ' ', text.strip())
    
    # Remove special characters but keep basic punctuation
    text = re.sub(r'[^\\w\\s.,!?-]', '', text)
    
    return text

def extract_hashtags(text: str) -> List[str]:
    """Extract hashtags from text"""
    hashtag_pattern = r'#\\w+'
    hashtags = re.findall(hashtag_pattern, text)
    return [tag.lower() for tag in hashtags]

def extract_mentions(text: str) -> List[str]:
    """Extract @mentions from text"""
    mention_pattern = r'@\\w+'
    mentions = re.findall(mention_pattern, text)
    return [mention.lower() for mention in mentions]

def validate_email(email: str) -> bool:
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def format_currency(amount: float, currency: str = "USD") -> str:
    """Format currency amount"""
    if currency == "USD":
        return f"${amount:,.2f}"
    return f"{amount:,.2f} {currency}"

def parse_budget_range(budget_str: str) -> Dict[str, float]:
    """Parse budget range string like '$1000-2000' """
    try:
        # Remove currency symbols and spaces
        cleaned = re.sub(r'[$,\\s]', '', budget_str.lower())
        
        if '-' in cleaned:
            min_val, max_val = cleaned.split('-')
            return {
                "min": float(min_val),
                "max": float(max_val)
            }
        else:
            # Single value
            value = float(cleaned)
            return {
                "min": value * 0.8,  # 20% below
                "max": value * 1.2   # 20% above
            }
    except Exception:
        return {"min": 0, "max": 0}

def calculate_engagement_rate(likes: int, comments: int, shares: int, followers: int) -> float:
    """Calculate engagement rate"""
    if followers == 0:
        return 0.0
    
    total_engagement = likes + comments + (shares * 2)  # Weight shares more
    rate = (total_engagement / followers) * 100
    return round(rate, 2)

def estimate_reach(followers: int, engagement_rate: float) -> int:
    """Estimate post reach based on followers and engagement"""
    # Simplified reach estimation
    base_reach = followers * 0.1  # 10% organic reach baseline
    engagement_boost = (engagement_rate / 100) * followers * 0.2
    
    estimated_reach = int(base_reach + engagement_boost)
    return min(estimated_reach, followers)  # Can't exceed total followers

def categorize_follower_count(followers: int) -> str:
    """Categorize influencer by follower count"""
    if followers < 1000:
        return "nano"
    elif followers < 10000:
        return "micro"
    elif followers < 100000:
        return "mid-tier"
    elif followers < 1000000:
        return "macro"
    else:
        return "mega"

def calculate_creator_score(
    engagement_rate: float,
    followers: int,
    response_rate: int,
    content_quality: float = 0.8
) -> float:
    """Calculate overall creator score (0-100)"""
    try:
        # Normalize engagement rate (typical range 1-10%)
        engagement_score = min(engagement_rate / 10 * 30, 30)  # Max 30 points
        
        # Follower score (logarithmic scaling)
        import math
        follower_score = min(math.log10(max(followers, 1)) * 5, 25)  # Max 25 points
        
        # Response rate score
        response_score = (response_rate / 100) * 25  # Max 25 points
        
        # Content quality score
        quality_score = content_quality * 20  # Max 20 points
        
        total_score = engagement_score + follower_score + response_score + quality_score
        return round(min(total_score, 100), 2)
        
    except Exception:
        return 50.0  # Default score

def retry_async(max_retries: int = 3, delay: float = 1.0):
    """Async retry decorator"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(max_retries):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_retries - 1:
                        await asyncio.sleep(delay * (2 ** attempt))  # Exponential backoff
                    continue
            
            raise last_exception
        return wrapper
    return decorator

def rate_limit(calls_per_minute: int = 60):
    """Simple rate limiting decorator"""
    def decorator(func):
        call_times = []
        
        @wraps(func)
        async def wrapper(*args, **kwargs):
            nonlocal call_times
            now = time.time()
            
            # Remove calls older than 1 minute
            call_times = [t for t in call_times if now - t < 60]
            
            # Check if we've exceeded the limit
            if len(call_times) >= calls_per_minute:
                raise Exception(f"Rate limit exceeded: {calls_per_minute} calls per minute")
            
            call_times.append(now)
            return await func(*args, **kwargs)
        
        return wrapper
    return decorator

async def make_http_request(
    url: str,
    method: str = "GET",
    headers: Dict = None,
    data: Dict = None,
    timeout: float = 30.0
) -> Optional[Dict]:
    """Make HTTP request with error handling"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.request(
                method=method,
                url=url,
                headers=headers or {},
                json=data,
                timeout=timeout
            )
            response.raise_for_status()
            return response.json()
    except Exception as e:
        print(f"HTTP request error: {e}")
        return None

def format_datetime(dt: datetime, format_str: str = "%Y-%m-%d %H:%M:%S") -> str:
    """Format datetime to string"""
    return dt.strftime(format_str)

def parse_datetime(dt_str: str, format_str: str = "%Y-%m-%d %H:%M:%S") -> Optional[datetime]:
    """Parse datetime from string"""
    try:
        return datetime.strptime(dt_str, format_str)
    except Exception:
        return None

def get_time_ago(dt: datetime) -> str:
    """Get human-readable time ago string"""
    now = datetime.utcnow()
    diff = now - dt
    
    if diff.days > 30:
        return f"{diff.days // 30} months ago"
    elif diff.days > 0:
        return f"{diff.days} days ago"
    elif diff.seconds > 3600:
        return f"{diff.seconds // 3600} hours ago"
    elif diff.seconds > 60:
        return f"{diff.seconds // 60} minutes ago"
    else:
        return "Just now"

def chunks(lst: List, chunk_size: int) -> List[List]:
    """Split list into chunks of specified size"""
    return [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]

def safe_get(dictionary: Dict, key: str, default: Any = None) -> Any:
    """Safely get value from nested dictionary"""
    try:
        keys = key.split('.')
        value = dictionary
        for k in keys:
            value = value[k]
        return value
    except (KeyError, TypeError):
        return default

def sanitize_filename(filename: str) -> str:
    """Sanitize filename for safe storage"""
    # Remove or replace invalid characters
    filename = re.sub(r'[^\\w\\s.-]', '', filename)
    filename = re.sub(r'\\s+', '_', filename)
    return filename[:255]  # Limit length

class Timer:
    """Simple timer context manager"""
    def __init__(self, description: str = "Operation"):
        self.description = description
        self.start_time = None
        
    def __enter__(self):
        self.start_time = time.time()
        return self
        
    def __exit__(self, *args):
        end_time = time.time()
        duration = end_time - self.start_time
        print(f"{self.description} took {duration:.2f} seconds")