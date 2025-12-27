"""
Tests for sub-account functionality
Tests cover configuration, API endpoints, and error handling
Updated for dual-mode (SPOT/BROKER) sub-account system
"""
import asyncio
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from config import Config
from mexc_client import MEXCClient


class TestSubAccountConfiguration:
    """Test sub-account configuration"""
    
    def test_config_has_sub_account_mode_variables(self):
        """Config should have new sub-account mode environment variables"""
        assert hasattr(Config, 'SUB_ACCOUNT_MODE')
        assert hasattr(Config, 'IS_BROKER_ACCOUNT')
        assert hasattr(Config, 'SUB_ACCOUNT_ID')
        assert hasattr(Config, 'SUB_ACCOUNT_NAME')
    
    def test_config_active_sub_account_identifier_spot_mode(self):
        """active_sub_account_identifier should return SUB_ACCOUNT_ID in SPOT mode"""
        with patch.object(Config, 'SUB_ACCOUNT_MODE', 'SPOT'), \
             patch.object(Config, 'IS_BROKER_ACCOUNT', False), \
             patch.object(Config, 'SUB_ACCOUNT_ID', '123456'), \
             patch.object(Config, 'SUB_ACCOUNT_NAME', 'broker_account'):
            
            config = Config()
            assert config.active_sub_account_identifier == '123456'
    
    def test_config_active_sub_account_identifier_broker_mode(self):
        """active_sub_account_identifier should return SUB_ACCOUNT_NAME in BROKER mode"""
        with patch.object(Config, 'SUB_ACCOUNT_MODE', 'BROKER'), \
             patch.object(Config, 'IS_BROKER_ACCOUNT', True), \
             patch.object(Config, 'SUB_ACCOUNT_ID', '123456'), \
             patch.object(Config, 'SUB_ACCOUNT_NAME', 'broker_account'):
            
            config = Config()
            assert config.active_sub_account_identifier == 'broker_account'
    
    def test_config_to_dict_includes_sub_account_status(self):
        """Config.to_dict() should include sub-account configuration status"""
        config_dict = Config.to_dict()
        assert 'sub_account_configured' in config_dict
        assert 'sub_account_mode' in config_dict
        assert 'is_broker_account' in config_dict
        assert isinstance(config_dict['sub_account_configured'], bool)


class TestMEXCSpotAPISubAccount:
    """Test MEXC Spot API sub-account methods"""
    
    @pytest.mark.asyncio
    async def test_get_sub_accounts_spot_success(self):
        """get_sub_accounts_spot should return list of sub-accounts"""
        client = MEXCClient()
        
        mock_response = {
            "subAccounts": [
                {"subAccountId": "123456", "note": "Trading", "status": "ACTIVE"},
                {"subAccountId": "789012", "note": "Savings", "status": "ACTIVE"}
            ],
            "total": 2
        }
        
        with patch.object(client, '_request', new_callable=AsyncMock) as mock_request:
            mock_request.return_value = mock_response
            
            result = await client.get_sub_accounts_spot()
            
            mock_request.assert_called_once_with(
                "GET", 
                "/api/v3/sub-account/list", 
                params={"page": 1, "limit": 10},
                signed=True
            )
            
            assert "subAccounts" in result
            assert len(result["subAccounts"]) == 2
            assert result["total"] == 2
    
    @pytest.mark.asyncio
    async def test_transfer_between_sub_accounts_success(self):
        """transfer_between_sub_accounts should execute universal transfer"""
        client = MEXCClient()
        
        mock_response = {
            "tranId": 123456789,
            "createTime": 1499865549590
        }
        
        with patch.object(client, '_request', new_callable=AsyncMock) as mock_request:
            mock_request.return_value = mock_response
            
            result = await client.transfer_between_sub_accounts(
                from_account_type="SPOT",
                to_account_type="SPOT",
                asset="USDT",
                amount="100",
                from_account="123456",
                to_account="789012"
            )
            
            mock_request.assert_called_once()
            call_args = mock_request.call_args
            assert call_args[0][0] == "POST"
            assert call_args[0][1] == "/api/v3/sub-account/universalTransfer"
            assert call_args[1]["params"]["asset"] == "USDT"
            assert call_args[1]["params"]["amount"] == "100"
            assert result["tranId"] == 123456789
    
    @pytest.mark.asyncio
    async def test_create_sub_account_api_key_success(self):
        """create_sub_account_api_key should create API key"""
        client = MEXCClient()
        
        mock_response = {
            "subAccountId": "123456",
            "apiKey": "test_api_key",
            "secretKey": "test_secret",
            "permissions": ["SPOT"]
        }
        
        with patch.object(client, '_request', new_callable=AsyncMock) as mock_request:
            mock_request.return_value = mock_response
            
            result = await client.create_sub_account_api_key(
                sub_account_id="123456",
                note="Test API",
                permissions=["SPOT"]
            )
            
            assert result["apiKey"] == "test_api_key"
            assert result["secretKey"] == "test_secret"


class TestMEXCBrokerAPISubAccount:
    """Test MEXC Broker API sub-account methods"""
    
    @pytest.mark.asyncio
    async def test_get_broker_sub_accounts_success(self):
        """get_broker_sub_accounts should return broker sub-accounts"""
        client = MEXCClient()
        
        mock_response = {
            "code": "0",
            "message": "",
            "data": [
                {"subAccount": "mexc1", "note": "Account 1", "timestamp": "1597026383085"},
                {"subAccount": "mexc2", "note": "Account 2", "timestamp": "1597026383086"}
            ]
        }
        
        with patch.object(client, '_request', new_callable=AsyncMock) as mock_request:
            mock_request.return_value = mock_response
            
            result = await client.get_broker_sub_accounts()
            
            mock_request.assert_called_once()
            call_args = mock_request.call_args
            assert call_args[0][1] == "/api/v3/broker/sub-account/list"
            assert result["code"] == "0"
            assert len(result["data"]) == 2
    
    @pytest.mark.asyncio
    async def test_get_broker_sub_account_assets_success(self):
        """get_broker_sub_account_assets should return sub-account balance"""
        client = MEXCClient()
        
        mock_response = {
            "balances": [
                {"asset": "BTC", "free": "0.1", "locked": "0.2"},
                {"asset": "USDT", "free": "1000", "locked": "0"}
            ]
        }
        
        with patch.object(client, '_request', new_callable=AsyncMock) as mock_request:
            mock_request.return_value = mock_response
            
            result = await client.get_broker_sub_account_assets("mexc1")
            
            mock_request.assert_called_once()
            call_args = mock_request.call_args
            assert call_args[0][1] == "/api/v3/broker/sub-account/assets"
            assert call_args[1]["params"]["subAccount"] == "mexc1"
            assert len(result["balances"]) == 2
    
    @pytest.mark.asyncio
    async def test_broker_transfer_between_sub_accounts_success(self):
        """broker_transfer_between_sub_accounts should execute transfer"""
        client = MEXCClient()
        
        mock_response = {
            "tranId": 123456789,
            "fromAccount": "mexc1",
            "toAccount": "mexc2",
            "status": "SUCCESS"
        }
        
        with patch.object(client, '_request', new_callable=AsyncMock) as mock_request:
            mock_request.return_value = mock_response
            
            result = await client.broker_transfer_between_sub_accounts(
                from_account="mexc1",
                to_account="mexc2",
                asset="USDT",
                amount="100"
            )
            
            assert result["status"] == "SUCCESS"
            assert result["fromAccount"] == "mexc1"
            assert result["toAccount"] == "mexc2"


class TestUnifiedSubAccountInterface:
    """Test unified sub-account interface methods"""
    
    @pytest.mark.asyncio
    async def test_get_sub_accounts_spot_mode(self):
        """get_sub_accounts should use Spot API in SPOT mode"""
        client = MEXCClient()
        
        mock_spot_response = {
            "subAccounts": [{"subAccountId": "123"}],
            "total": 1
        }
        
        with patch('config.config') as mock_config, \
             patch.object(client, 'get_sub_accounts_spot', new_callable=AsyncMock) as mock_spot:
            
            mock_config.IS_BROKER_ACCOUNT = False
            mock_config.SUB_ACCOUNT_MODE = "SPOT"
            mock_spot.return_value = mock_spot_response
            
            result = await client.get_sub_accounts()
            
            mock_spot.assert_called_once()
            assert len(result) == 1
            assert result[0]["subAccountId"] == "123"
    
    @pytest.mark.asyncio
    async def test_get_sub_accounts_broker_mode(self):
        """get_sub_accounts should use Broker API in BROKER mode"""
        client = MEXCClient()
        
        mock_broker_response = {
            "code": "0",
            "data": [{"subAccount": "mexc1"}]
        }
        
        with patch('config.config') as mock_config, \
             patch.object(client, 'get_broker_sub_accounts', new_callable=AsyncMock) as mock_broker:
            
            mock_config.IS_BROKER_ACCOUNT = True
            mock_config.SUB_ACCOUNT_MODE = "BROKER"
            mock_broker.return_value = mock_broker_response
            
            result = await client.get_sub_accounts()
            
            mock_broker.assert_called_once()
            assert len(result) == 1
            assert result[0]["subAccount"] == "mexc1"
    
    @pytest.mark.asyncio
    async def test_get_sub_account_balance_broker_mode(self):
        """get_sub_account_balance should work in BROKER mode"""
        client = MEXCClient()
        
        mock_response = {"balances": [{"asset": "BTC", "free": "1"}]}
        
        with patch('config.config') as mock_config, \
             patch.object(client, 'get_broker_sub_account_assets', new_callable=AsyncMock) as mock_assets:
            
            mock_config.IS_BROKER_ACCOUNT = True
            mock_config.SUB_ACCOUNT_MODE = "BROKER"
            mock_assets.return_value = mock_response
            
            result = await client.get_sub_account_balance("mexc1")
            
            mock_assets.assert_called_once_with("mexc1")
            assert "balances" in result
    
    @pytest.mark.asyncio
    async def test_get_sub_account_balance_spot_mode_raises(self):
        """get_sub_account_balance should raise NotImplementedError in SPOT mode"""
        client = MEXCClient()
        
        with patch('config.config') as mock_config:
            mock_config.IS_BROKER_ACCOUNT = False
            mock_config.SUB_ACCOUNT_MODE = "SPOT"
            
            with pytest.raises(NotImplementedError, match="Spot API does not support"):
                await client.get_sub_account_balance("123456")


def run_tests():
    """Run all tests"""
    import sys
    
    print("=" * 60)
    print("Running Sub-Account Tests (Dual-Mode System)")
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
