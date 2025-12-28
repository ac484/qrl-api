#!/usr/bin/env python3
"""
Validation script for Cloud Task data storage fixes
Validates code structure and method signatures without requiring Redis
"""
import ast
import inspect
import sys

def validate_redis_client_methods():
    """Validate that redis_client.py has the required new methods"""
    print("=" * 80)
    print("Validating redis_client.py methods")
    print("=" * 80)
    
    try:
        with open('redis_client.py', 'r') as f:
            content = f.read()
        
        tree = ast.parse(content)
        
        # Find the RedisClient class
        redis_class = None
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and node.name == 'RedisClient':
                redis_class = node
                break
        
        if not redis_class:
            print("❌ RedisClient class not found")
            return False
        
        # Get all method names
        methods = [n.name for n in redis_class.body if isinstance(n, ast.AsyncFunctionDef)]
        
        # Check for required new methods
        required_methods = [
            'set_raw_mexc_response',
            'get_raw_mexc_response',
            'get_raw_mexc_response_history',
            'set_cached_price',
            'get_cached_price'
        ]
        
        all_found = True
        for method in required_methods:
            if method in methods:
                print(f"✅ Found method: {method}")
            else:
                print(f"❌ Missing method: {method}")
                all_found = False
        
        # Check that set_latest_price still exists (but should be modified)
        if 'set_latest_price' in methods:
            print(f"✅ Found method: set_latest_price (should be modified to remove TTL)")
        else:
            print(f"❌ Missing method: set_latest_price")
            all_found = False
        
        return all_found
        
    except Exception as e:
        print(f"❌ Error validating redis_client.py: {e}")
        return False

def validate_cloud_tasks_imports():
    """Validate that cloud_tasks.py has required imports"""
    print("\n" + "=" * 80)
    print("Validating cloud_tasks.py imports and structure")
    print("=" * 80)
    
    try:
        with open('cloud_tasks.py', 'r') as f:
            content = f.read()
        
        tree = ast.parse(content)
        
        # Check for json import
        imports = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imports.extend([n.name for n in node.names])
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imports.append(node.module)
        
        if 'json' in imports:
            print("✅ Found json import")
        else:
            print("❌ Missing json import")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Error validating cloud_tasks.py: {e}")
        return False

def validate_cloud_tasks_endpoints():
    """Validate that cloud_tasks.py endpoints call new methods"""
    print("\n" + "=" * 80)
    print("Validating cloud_tasks.py endpoint implementations")
    print("=" * 80)
    
    try:
        with open('cloud_tasks.py', 'r') as f:
            content = f.read()
        
        # Check for set_raw_mexc_response calls
        if 'set_raw_mexc_response' in content:
            count = content.count('set_raw_mexc_response')
            print(f"✅ Found {count} calls to set_raw_mexc_response")
        else:
            print("❌ No calls to set_raw_mexc_response found")
            return False
        
        # Check for set_latest_price and set_cached_price
        if 'set_latest_price' in content:
            print("✅ Found calls to set_latest_price")
        else:
            print("❌ No calls to set_latest_price")
        
        if 'set_cached_price' in content:
            print("✅ Found calls to set_cached_price")
        else:
            print("⚠️  No calls to set_cached_price (may be optional)")
        
        # Check for enhanced logging
        if 'exc_info=True' in content:
            print("✅ Found enhanced error logging with exc_info")
        else:
            print("⚠️  No enhanced error logging found")
        
        # Check for JSON dumps in position data
        if 'json.dumps(all_balances)' in content or 'json.dumps' in content:
            print("✅ Found JSON serialization for complex data")
        else:
            print("⚠️  No JSON serialization found")
        
        return True
        
    except Exception as e:
        print(f"❌ Error validating cloud_tasks.py endpoints: {e}")
        return False

def validate_method_signatures():
    """Validate that method signatures are correct"""
    print("\n" + "=" * 80)
    print("Validating method signatures in redis_client.py")
    print("=" * 80)
    
    try:
        with open('redis_client.py', 'r') as f:
            content = f.read()
        
        tree = ast.parse(content)
        
        # Find set_latest_price method
        for node in ast.walk(tree):
            if isinstance(node, ast.AsyncFunctionDef) and node.name == 'set_latest_price':
                # Check that it doesn't have 'ex=' parameter in the body
                func_source = ast.get_source_segment(content, node)
                if func_source:
                    if 'ex=config.CACHE_TTL_PRICE' in func_source:
                        print("❌ set_latest_price still has TTL - should be removed")
                        return False
                    elif 'ex=' not in func_source or '# Store permanently without TTL' in func_source:
                        print("✅ set_latest_price appears to be modified correctly (no TTL)")
                    else:
                        print("⚠️  set_latest_price may have TTL, please review")
        
        return True
        
    except Exception as e:
        print(f"❌ Error validating method signatures: {e}")
        return False

def validate_test_file():
    """Validate that test file exists and has correct structure"""
    print("\n" + "=" * 80)
    print("Validating test_cloud_tasks_storage.py")
    print("=" * 80)
    
    try:
        with open('test_cloud_tasks_storage.py', 'r') as f:
            content = f.read()
        
        tree = ast.parse(content)
        
        # Find test functions
        test_functions = []
        for node in ast.walk(tree):
            if isinstance(node, ast.AsyncFunctionDef) and node.name.startswith('test_'):
                test_functions.append(node.name)
        
        expected_tests = [
            'test_raw_mexc_storage',
            'test_permanent_price_storage',
            'test_complete_position_storage'
        ]
        
        for test in expected_tests:
            if test in test_functions:
                print(f"✅ Found test function: {test}")
            else:
                print(f"❌ Missing test function: {test}")
        
        if len(test_functions) >= len(expected_tests):
            print(f"✅ Total test functions: {len(test_functions)}")
            return True
        else:
            return False
        
    except FileNotFoundError:
        print("❌ test_cloud_tasks_storage.py not found")
        return False
    except Exception as e:
        print(f"❌ Error validating test file: {e}")
        return False

def main():
    """Run all validations"""
    print("\n🚀 Starting Cloud Task Fix Validation\n")
    
    results = []
    
    # Run all validations
    results.append(("Redis client methods", validate_redis_client_methods()))
    results.append(("Cloud tasks imports", validate_cloud_tasks_imports()))
    results.append(("Cloud tasks endpoints", validate_cloud_tasks_endpoints()))
    results.append(("Method signatures", validate_method_signatures()))
    results.append(("Test file", validate_test_file()))
    
    # Summary
    print("\n" + "=" * 80)
    print("VALIDATION SUMMARY")
    print("=" * 80)
    
    all_passed = True
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {name}")
        if not result:
            all_passed = False
    
    print("=" * 80)
    
    if all_passed:
        print("\n✅ All validations passed!")
        print("\nNext steps:")
        print("1. Deploy to Google Cloud Run")
        print("2. Monitor scheduled task execution")
        print("3. Verify data persistence in Redis")
        return 0
    else:
        print("\n❌ Some validations failed - please review the output above")
        return 1

if __name__ == "__main__":
    sys.exit(main())
