#!/usr/bin/env python3
"""
Cache Command Line Interface
Quick commands to manage and monitor cache
"""

import requests
import redis
import sys
import time
from datetime import datetime

BASE_URL = "http://localhost:5000"
REDIS_URL = "redis://localhost:6379/1"

def connect_redis():
    """Connect to Redis"""
    try:
        client = redis.from_url(REDIS_URL)
        client.ping()
        return client
    except Exception as e:
        print(f"❌ Redis connection failed: {e}")
        return None

def show_help():
    """Show available commands"""
    print("""
🚀 Cache Management Commands
============================

Commands:
  status     - Show cache status and configuration
  keys       - Show all cache keys with TTL
  stats      - Show Redis statistics
  test       - Run performance tests
  clear      - Clear all cache
  monitor    - Real-time cache monitoring
  help       - Show this help

Examples:
  python cache_cli.py status
  python cache_cli.py test
  python cache_cli.py keys
  python cache_cli.py clear
""")

def show_status():
    """Show cache status"""
    print("📊 Cache Status")
    print("=" * 40)
    
    # Check Redis connection
    redis_client = connect_redis()
    if not redis_client:
        return
    
    print(f"Redis Status: ✅ Connected")
    print(f"Redis URL: {REDIS_URL}")
    
    # Check Flask app
    try:
        response = requests.get(f"{BASE_URL}/api/admin/cache/status", timeout=5)
        if response.status_code == 200:
            status = response.json()
            print(f"Cache Type: {status.get('cache_type')}")
            print(f"Default Timeout: {status.get('default_timeout')}s")
            print(f"Status: {status.get('status')}")
        else:
            print("Flask App: ❌ Not responding")
    except Exception as e:
        print(f"Flask App: ❌ Error - {e}")

def show_keys():
    """Show all cache keys"""
    print("🗂️  Cache Keys")
    print("=" * 40)
    
    redis_client = connect_redis()
    if not redis_client:
        return
    
    try:
        keys = redis_client.keys("parking_app_*")
        if not keys:
            print("No cache keys found")
            return
        
        print(f"Found {len(keys)} cache keys:")
        print()
        
        for key in sorted(keys):
            key_str = key.decode('utf-8')
            ttl = redis_client.ttl(key)
            size = len(redis_client.get(key) or b'')
            
            print(f"🔑 {key_str}")
            print(f"   TTL: {ttl}s | Size: {size} bytes")
            print()
            
    except Exception as e:
        print(f"❌ Error reading keys: {e}")

def show_stats():
    """Show Redis statistics"""
    print("📈 Redis Statistics")
    print("=" * 40)
    
    redis_client = connect_redis()
    if not redis_client:
        return
    
    try:
        info = redis_client.info()
        
        stats = {
            'Connected Clients': info.get('connected_clients', 'N/A'),
            'Used Memory': info.get('used_memory_human', 'N/A'),
            'Total Keys (DB1)': info.get('db1', {}).get('keys', 0),
            'Uptime': f"{info.get('uptime_in_seconds', 0)}s",
            'Cache Keys': len(redis_client.keys("parking_app_*"))
        }
        
        for key, value in stats.items():
            print(f"{key}: {value}")
            
    except Exception as e:
        print(f"❌ Error reading stats: {e}")

def run_test():
    """Run performance test"""
    print("🧪 Performance Test")
    print("=" * 40)
    
    # Only test admin endpoints that don't require authentication
    endpoints = [
        ("/api/admin/lots", "Admin Lots"),
        ("/api/admin/users", "Admin Users"),
        ("/api/admin/lots/1/slots", "Lot Spots"),
    ]
    
    for endpoint, name in endpoints:
        print(f"\nTesting: {name}")
        print(f"Endpoint: {endpoint}")
        
        # First request (should be slower)
        start = time.time()
        try:
            response1 = requests.get(f"{BASE_URL}{endpoint}", timeout=10)
            time1 = time.time() - start
            status1 = "✅" if response1.status_code == 200 else "❌"
            print(f"  Request 1: {time1:.3f}s {status1}")
        except Exception as e:
            print(f"  Request 1: ❌ Error - {e}")
            continue
        
        # Second request (should be faster if cached)
        start = time.time()
        try:
            response2 = requests.get(f"{BASE_URL}{endpoint}", timeout=10)
            time2 = time.time() - start
            status2 = "✅" if response2.status_code == 200 else "❌"
            print(f"  Request 2: {time2:.3f}s {status2}")
        except Exception as e:
            print(f"  Request 2: ❌ Error - {e}")
            continue
        
        # Check if cache is working
        if time2 < time1 * 0.8:
            improvement = ((time1 - time2) / time1) * 100
            print(f"  Cache: ✅ Working ({improvement:.1f}% improvement)")
        else:
            print(f"  Cache: ⚠️  May not be working")

def clear_cache():
    """Clear all cache"""
    print("🗑️  Clearing Cache")
    print("=" * 40)
    
    try:
        response = requests.post(f"{BASE_URL}/api/admin/cache/clear", timeout=10)
        if response.status_code == 200:
            print("✅ Cache cleared successfully")
        else:
            print(f"❌ Failed to clear cache: {response.status_code}")
    except Exception as e:
        print(f"❌ Error clearing cache: {e}")

def monitor_cache():
    """Real-time cache monitoring"""
    print("👀 Real-time Cache Monitor")
    print("=" * 40)
    print("Press Ctrl+C to stop")
    print()
    
    redis_client = connect_redis()
    if not redis_client:
        return
    
    try:
        while True:
            keys = redis_client.keys("parking_app_*")
            timestamp = datetime.now().strftime("%H:%M:%S")
            
            print(f"[{timestamp}] Cache keys: {len(keys)}", end="\r")
            time.sleep(2)
            
    except KeyboardInterrupt:
        print("\n\n🛑 Monitoring stopped")

def main():
    if len(sys.argv) < 2:
        show_help()
        return
    
    command = sys.argv[1].lower()
    
    if command == "status":
        show_status()
    elif command == "keys":
        show_keys()
    elif command == "stats":
        show_stats()
    elif command == "test":
        run_test()
    elif command == "clear":
        clear_cache()
    elif command == "monitor":
        monitor_cache()
    elif command == "help":
        show_help()
    else:
        print(f"❌ Unknown command: {command}")
        show_help()

if __name__ == "__main__":
    main() 