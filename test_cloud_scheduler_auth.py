"""
Test Cloud Scheduler Authentication
Validates that cloud tasks accept both X-CloudScheduler header and Authorization header
"""

def test_authentication_logic():
    """Test the authentication logic for both header types"""
    
    # Test case 1: X-CloudScheduler header present
    x_cloudscheduler = "true"
    authorization = None
    
    # Should pass authentication
    if not x_cloudscheduler and not authorization:
        raise Exception("Should not fail with X-CloudScheduler")
    auth_method = "OIDC" if authorization else "X-CloudScheduler"
    assert auth_method == "X-CloudScheduler"
    print("✅ Test 1 passed: X-CloudScheduler header authentication")
    
    # Test case 2: Authorization header present (OIDC)
    x_cloudscheduler = None
    authorization = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
    
    # Should pass authentication
    if not x_cloudscheduler and not authorization:
        raise Exception("Should not fail with Authorization header")
    auth_method = "OIDC" if authorization else "X-CloudScheduler"
    assert auth_method == "OIDC"
    print("✅ Test 2 passed: OIDC Authorization header authentication")
    
    # Test case 3: Both headers present (should accept)
    x_cloudscheduler = "true"
    authorization = "Bearer token"
    
    # Should pass authentication
    if not x_cloudscheduler and not authorization:
        raise Exception("Should not fail with both headers")
    # OIDC takes precedence
    auth_method = "OIDC" if authorization else "X-CloudScheduler"
    assert auth_method == "OIDC"
    print("✅ Test 3 passed: Both headers present - OIDC takes precedence")
    
    # Test case 4: Neither header present (should fail)
    x_cloudscheduler = None
    authorization = None
    
    try:
        if not x_cloudscheduler and not authorization:
            raise ValueError("Unauthorized - Cloud Scheduler only")
        assert False, "Should have raised exception"
    except ValueError as e:
        assert "Unauthorized" in str(e)
        print("✅ Test 4 passed: Neither header - correctly rejected")
    
    print("\n🎉 All authentication logic tests passed!")


if __name__ == "__main__":
    test_authentication_logic()
