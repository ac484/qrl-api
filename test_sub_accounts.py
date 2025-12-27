"""
Tests for sub-account functionality
Tests cover configuration, API endpoints, and error handling
"""
import asyncio
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from config import Config
from mexc_client import MEXCClient


class TestSubAccountConfiguration:
    """Test sub-account configuration"""
    
    def test_config_has_sub_account_variables(self):
        """Config should have sub-account environment variables"""
        assert hasattr(Config, 'SUB_ACCOUNT_EMAIL')
        assert hasattr(Config, 'SUB_ACCOUNT_ID')
    
    def test_config_to_dict_includes_sub_account_status(self):
        """Config.to_dict() should include sub-account configuration status"""
        config_dict = Config.to_dict()
        assert 'sub_account_configured' in config_dict
        assert isinstance(config_dict['sub_account_configured'], bool)


class TestMEXCSubAccountAPI:
    """Test MEXC sub-account API methods"""
    
    @pytest.mark.asyncio
    async def test_get_sub_accounts_success(self):
        """get_sub_accounts should return list of sub-accounts on success"""
        client = MEXCClient()
        
        # Mock successful response
        mock_response = [
            {"email": "sub1@example.com", "id": "123"},
            {"email": "sub2@example.com", "id": "456"}
        ]
        
        with patch.object(client, '_request', new_callable=AsyncMock) as mock_request:
            mock_request.return_value = mock_response
            
            result = await client.get_sub_accounts()
            
            # Verify correct endpoint called
            mock_request.assert_called_once_with(
                "GET", 
                "/api/v3/broker/sub-account/list", 
                signed=True
            )
            
            # Verify result
            assert len(result) == 2
            assert result[0]['email'] == "sub1@example.com"
    
    @pytest.mark.asyncio
    async def test_get_sub_accounts_permission_error(self):
        """get_sub_accounts should return empty list on permission error"""
        client = MEXCClient()
        
        # Mock permission error
        with patch.object(client, '_request', new_callable=AsyncMock) as mock_request:
            mock_request.side_effect = Exception("403 Forbidden")
            
            result = await client.get_sub_accounts()
            
            # Should return empty list instead of raising
            assert result == []
    
    @pytest.mark.asyncio
    async def test_get_sub_account_balance_success_with_email(self):
        """get_sub_account_balance should return balance when email is provided"""
        client = MEXCClient()
        
        mock_response = {
            "email": "sub@example.com",
            "balances": [
                {"asset": "QRL", "free": "1000", "locked": "0"},
                {"asset": "USDT", "free": "500", "locked": "0"}
            ]
        }
        
        with patch.object(client, '_request', new_callable=AsyncMock) as mock_request:
            mock_request.return_value = mock_response
            
            result = await client.get_sub_account_balance(email="sub@example.com")
            
            # Verify correct endpoint and params
            mock_request.assert_called_once_with(
                "GET",
                "/api/v3/broker/sub-account/assets",
                params={"email": "sub@example.com"},
                signed=True
            )
            
            assert result['email'] == "sub@example.com"
            assert len(result['balances']) == 2
    
    @pytest.mark.asyncio
    async def test_get_sub_account_balance_success_with_id(self):
        """get_sub_account_balance should return balance when sub_account_id is provided"""
        client = MEXCClient()
        
        mock_response = {
            "id": "123456",
            "balances": [
                {"asset": "QRL", "free": "2000", "locked": "100"}
            ]
        }
        
        with patch.object(client, '_request', new_callable=AsyncMock) as mock_request:
            mock_request.return_value = mock_response
            
            result = await client.get_sub_account_balance(sub_account_id="123456")
            
            # Verify correct endpoint and params
            mock_request.assert_called_once_with(
                "GET",
                "/api/v3/broker/sub-account/assets",
                params={"subAccountId": "123456"},
                signed=True
            )
            
            assert result['id'] == "123456"
    
    @pytest.mark.asyncio
    async def test_get_sub_account_balance_with_both_identifiers(self):
        """get_sub_account_balance should accept both email and ID together"""
        client = MEXCClient()
        
        mock_response = {"email": "sub@example.com", "id": "123", "balances": []}
        
        with patch.object(client, '_request', new_callable=AsyncMock) as mock_request:
            mock_request.return_value = mock_response
            
            result = await client.get_sub_account_balance(
                email="sub@example.com",
                sub_account_id="123456"
            )
            
            # Should send both params
            call_args = mock_request.call_args
            assert "email" in call_args[1]["params"]
            assert "subAccountId" in call_args[1]["params"]
    
    @pytest.mark.asyncio
    async def test_get_sub_account_balance_missing_both_identifiers(self):
        """get_sub_account_balance should raise ValueError if neither email nor ID provided"""
        client = MEXCClient()
        
        with pytest.raises(ValueError, match="Either sub-account email or sub-account ID must be provided"):
            await client.get_sub_account_balance()
        
        with pytest.raises(ValueError, match="Either sub-account email or sub-account ID must be provided"):
            await client.get_sub_account_balance(email="", sub_account_id="")


class TestAccountBalanceEndpoint:
    """Test account balance endpoint improvements"""
    
    @pytest.mark.asyncio
    async def test_account_balance_no_api_keys(self):
        """Should return 401 with helpful message when API keys missing"""
        from main import app
        from fastapi.testclient import TestClient
        
        # Mock missing API keys
        with patch('main.config') as mock_config:
            mock_config.MEXC_API_KEY = None
            mock_config.MEXC_SECRET_KEY = None
            
            client = TestClient(app)
            response = client.get("/account/balance")
            
            assert response.status_code == 401
            data = response.json()
            assert "error" in data["detail"]
            assert "API keys not configured" in data["detail"]["error"]
            assert "help" in data["detail"]
    
    @pytest.mark.asyncio
    async def test_account_balance_ensures_qrl_usdt_present(self):
        """Should always include QRL and USDT in response, even if zero"""
        from main import app
        from fastapi.testclient import TestClient
        
        with patch('main.config') as mock_config, \
             patch('main.mexc_client') as mock_mexc:
            
            # Configure mocks
            mock_config.MEXC_API_KEY = "test_key"
            mock_config.MEXC_SECRET_KEY = "test_secret"
            
            # Mock API response with only BTC (no QRL or USDT)
            mock_mexc.get_account_info = AsyncMock(return_value={
                "balances": [
                    {"asset": "BTC", "free": "0.1", "locked": "0"}
                ]
            })
            
            client = TestClient(app)
            response = client.get("/account/balance")
            
            assert response.status_code == 200
            data = response.json()
            
            # Should have QRL and USDT with zero values
            assert "QRL" in data["balances"]
            assert "USDT" in data["balances"]
            assert data["balances"]["QRL"]["free"] == "0"
            assert data["balances"]["USDT"]["free"] == "0"


def run_tests():
    """Run all tests"""
    import sys
    
    print("=" * 60)
    print("Running Sub-Account Tests")
    print("=" * 60)
    
    # Run pytest
    exit_code = pytest.main([
        __file__,
        "-v",
        "--tb=short",
        "-s"
    ])
    
    sys.exit(exit_code)


if __name__ == "__main__":
    run_tests()
