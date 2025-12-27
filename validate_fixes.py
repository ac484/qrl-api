#!/usr/bin/env python3
"""
Validation script for Issue #12 fixes
Verifies all implemented features are working correctly
"""

import sys
import os


def print_header(title):
    """Print a formatted header"""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def print_success(message):
    """Print success message"""
    print(f"✅ {message}")


def print_error(message):
    """Print error message"""
    print(f"❌ {message}")


def validate_configuration():
    """Validate configuration changes"""
    print_header("1. Configuration Validation")
    
    try:
        from config import Config
        
        # Check SUB_ACCOUNT_EMAIL exists
        assert hasattr(Config, 'SUB_ACCOUNT_EMAIL'), "Missing SUB_ACCOUNT_EMAIL"
        print_success("SUB_ACCOUNT_EMAIL configured")
        
        # Check SUB_ACCOUNT_ID exists
        assert hasattr(Config, 'SUB_ACCOUNT_ID'), "Missing SUB_ACCOUNT_ID"
        print_success("SUB_ACCOUNT_ID configured")
        
        # Check to_dict includes sub_account_configured
        config_dict = Config.to_dict()
        assert 'sub_account_configured' in config_dict, "Missing sub_account_configured in to_dict()"
        print_success("Config.to_dict() includes sub_account_configured")
        
        return True
    except Exception as e:
        print_error(f"Configuration validation failed: {e}")
        return False


def validate_mexc_client():
    """Validate MEXC client changes"""
    print_header("2. MEXC Client Validation")
    
    try:
        import inspect
        from mexc_client import MEXCClient
        
        # Check get_sub_accounts method exists
        assert hasattr(MEXCClient, 'get_sub_accounts'), "Missing get_sub_accounts method"
        print_success("get_sub_accounts method exists")
        
        # Check get_sub_account_balance signature
        sig = inspect.signature(MEXCClient.get_sub_account_balance)
        params = list(sig.parameters.keys())
        
        assert 'email' in params, "Missing email parameter"
        print_success("get_sub_account_balance has email parameter")
        
        assert 'sub_account_id' in params, "Missing sub_account_id parameter"
        print_success("get_sub_account_balance has sub_account_id parameter")
        
        # Check parameters are optional
        email_param = sig.parameters['email']
        sub_id_param = sig.parameters['sub_account_id']
        
        assert email_param.default is not inspect.Parameter.empty, "email should be optional"
        print_success("email parameter is optional")
        
        assert sub_id_param.default is not inspect.Parameter.empty, "sub_account_id should be optional"
        print_success("sub_account_id parameter is optional")
        
        return True
    except Exception as e:
        print_error(f"MEXC client validation failed: {e}")
        return False


def validate_api_endpoints():
    """Validate API endpoint improvements"""
    print_header("3. API Endpoints Validation")
    
    try:
        # Import main to trigger route registration
        import main
        
        # Check that FastAPI app exists
        assert hasattr(main, 'app'), "Missing FastAPI app"
        print_success("FastAPI app exists")
        
        # Get all routes
        routes = [route.path for route in main.app.routes]
        
        # Check required endpoints exist
        required_endpoints = [
            '/account/balance',
            '/account/sub-accounts',
            '/account/sub-account/balance'
        ]
        
        for endpoint in required_endpoints:
            assert endpoint in routes, f"Missing endpoint: {endpoint}"
            print_success(f"Endpoint exists: {endpoint}")
        
        return True
    except Exception as e:
        print_error(f"API endpoints validation failed: {e}")
        return False


def validate_documentation():
    """Validate documentation files"""
    print_header("4. Documentation Validation")
    
    try:
        required_docs = {
            'TROUBLESHOOTING.md': 'Troubleshooting guide',
            'docs/SUB_ACCOUNT_GUIDE.md': 'Sub-account usage guide',
            'test_sub_accounts.py': 'Test suite',
            '.env.example': 'Environment variables example'
        }
        
        for filepath, description in required_docs.items():
            assert os.path.exists(filepath), f"Missing {description}: {filepath}"
            print_success(f"{description} exists")
        
        # Check TROUBLESHOOTING.md content
        with open('TROUBLESHOOTING.md', 'r') as f:
            content = f.read()
            assert 'Sub-Accounts Not Loading' in content, "Missing sub-accounts section"
            assert 'Balance Display' in content, "Missing balance display section"
            print_success("TROUBLESHOOTING.md has required sections")
        
        # Check SUB_ACCOUNT_GUIDE.md content
        with open('docs/SUB_ACCOUNT_GUIDE.md', 'r') as f:
            content = f.read()
            assert 'email' in content.lower(), "Missing email documentation"
            assert 'sub_account_id' in content.lower(), "Missing ID documentation"
            print_success("SUB_ACCOUNT_GUIDE.md has required content")
        
        # Check .env.example has sub-account vars
        with open('.env.example', 'r') as f:
            content = f.read()
            assert 'SUB_ACCOUNT_EMAIL' in content, "Missing SUB_ACCOUNT_EMAIL in .env.example"
            assert 'SUB_ACCOUNT_ID' in content, "Missing SUB_ACCOUNT_ID in .env.example"
            print_success(".env.example has sub-account configuration")
        
        return True
    except Exception as e:
        print_error(f"Documentation validation failed: {e}")
        return False


def validate_validation_logic():
    """Validate input validation logic"""
    print_header("5. Input Validation Logic")
    
    try:
        import asyncio
        from mexc_client import MEXCClient
        
        async def test_validation():
            client = MEXCClient()
            
            # Test 1: Both empty should raise ValueError
            try:
                await client.get_sub_account_balance(email='', sub_account_id='')
                return False, "Should raise ValueError for both empty"
            except ValueError:
                print_success("Correctly raises ValueError for both empty")
            
            # Test 2: Both None should raise ValueError
            try:
                await client.get_sub_account_balance(email=None, sub_account_id=None)
                return False, "Should raise ValueError for both None"
            except ValueError:
                print_success("Correctly raises ValueError for both None")
            
            # Test 3: No parameters should raise ValueError
            try:
                await client.get_sub_account_balance()
                return False, "Should raise ValueError for no parameters"
            except ValueError:
                print_success("Correctly raises ValueError for no parameters")
            
            await client.close()
            return True, None
        
        success, error = asyncio.run(test_validation())
        if not success:
            print_error(error)
            return False
        
        return True
    except Exception as e:
        print_error(f"Validation logic test failed: {e}")
        return False


def main():
    """Run all validations"""
    print("\n" + "=" * 70)
    print("  QRL Trading API - Issue #12 Fix Validation")
    print("=" * 70)
    
    results = []
    
    # Run all validation functions
    results.append(("Configuration", validate_configuration()))
    results.append(("MEXC Client", validate_mexc_client()))
    results.append(("API Endpoints", validate_api_endpoints()))
    results.append(("Documentation", validate_documentation()))
    results.append(("Validation Logic", validate_validation_logic()))
    
    # Print summary
    print_header("Validation Summary")
    
    all_passed = True
    for name, passed in results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{name:20s}: {status}")
        if not passed:
            all_passed = False
    
    print("\n" + "=" * 70)
    if all_passed:
        print("🎉 ALL VALIDATIONS PASSED!")
        print("=" * 70)
        return 0
    else:
        print("❌ SOME VALIDATIONS FAILED")
        print("=" * 70)
        return 1


if __name__ == "__main__":
    sys.exit(main())
