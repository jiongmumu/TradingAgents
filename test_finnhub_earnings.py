#!/usr/bin/env python3
"""
Test file for get_earnings_calendar function in finnhub_utils.py
"""

import unittest
from unittest.mock import patch, Mock
import os
import sys
from datetime import datetime, timedelta
import json

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from tradingagents.dataflows.finnhub_utils import get_earnings_calendar


class TestFinnhubEarningsCalendar(unittest.TestCase):
    """Test cases for get_earnings_calendar function."""

    def setUp(self):
        """Set up test fixtures."""
        # Set up test dates
        self.today = datetime.now()
        self.start_date = (self.today - timedelta(days=7)).strftime('%Y-%m-%d')
        self.end_date = (self.today + timedelta(days=7)).strftime('%Y-%m-%d')
        
        # Sample API response data
        self.sample_earnings_data = {
            "earningsCalendar": [
                {
                    "symbol": "AAPL",
                    "reportDate": "2024-01-25",
                    "epsEstimate": 2.10,
                    "hour": "amc"
                },
                {
                    "symbol": "MSFT",
                    "reportDate": "2024-01-26",
                    "epsEstimate": 2.78,
                    "hour": "bmo"
                },
                {
                    "symbol": "GOOGL",
                    "reportDate": "2024-01-27",
                    "epsEstimate": 1.59,
                    "hour": "amc"
                }
            ]
        }

    def test_get_earnings_calendar_success(self):
        """Test successful API call with valid response."""
        with patch('requests.get') as mock_get:
            # Mock successful response
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = self.sample_earnings_data
            mock_get.return_value = mock_response

            # Call the function
            get_earnings_calendar(self.start_date, self.end_date)

            # Verify the API call was made correctly
            mock_get.assert_called_once()
            call_args = mock_get.call_args
            
            # Check URL
            self.assertIn('https://finnhub.io/api/v1/calendar/earnings', call_args[0][0])
            
            # Check parameters
            params = call_args[1]['params']
            self.assertEqual(params['from'], self.start_date)
            self.assertEqual(params['to'], self.end_date)
            self.assertIn('token', params)

    def test_get_earnings_calendar_api_error(self):
        """Test API error handling."""
        with patch('requests.get') as mock_get:
            # Mock error response
            mock_response = Mock()
            mock_response.status_code = 401
            mock_response.text = "Unauthorized"
            mock_get.return_value = mock_response

            # Call the function (should handle error gracefully)
            get_earnings_calendar(self.start_date, self.end_date)

            # Verify the API call was made
            mock_get.assert_called_once()

    def test_get_earnings_calendar_empty_response(self):
        """Test handling of empty earnings calendar."""
        with patch('requests.get') as mock_get:
            # Mock empty response
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"earningsCalendar": []}
            mock_get.return_value = mock_response

            # Call the function
            get_earnings_calendar(self.start_date, self.end_date)

            # Verify the API call was made
            mock_get.assert_called_once()

    def test_get_earnings_calendar_missing_earnings_key(self):
        """Test handling of response without earningsCalendar key."""
        with patch('requests.get') as mock_get:
            # Mock response without earningsCalendar key
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"other_data": "value"}
            mock_get.return_value = mock_response

            # Call the function (should handle missing key gracefully)
            get_earnings_calendar(self.start_date, self.end_date)

            # Verify the API call was made
            mock_get.assert_called_once()

    def test_get_earnings_calendar_missing_api_key(self):
        """Test behavior when FINNHUB_API_KEY is not set."""
        # Store original API key
        original_key = os.getenv('FINNHUB_API_KEY')
        
        # Remove API key temporarily
        if 'FINNHUB_API_KEY' in os.environ:
            del os.environ['FINNHUB_API_KEY']

        with patch('requests.get') as mock_get:
            # Mock response
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = self.sample_earnings_data
            mock_get.return_value = mock_response

            # Call the function
            get_earnings_calendar(self.start_date, self.end_date)

            # Verify the API call was made (should still work but with None token)
            mock_get.assert_called_once()
            call_args = mock_get.call_args
            params = call_args[1]['params']
            self.assertIsNone(params['token'])

        # Restore original API key
        if original_key:
            os.environ['FINNHUB_API_KEY'] = original_key

    def test_get_earnings_calendar_date_format(self):
        """Test that dates are passed in correct format."""
        with patch('requests.get') as mock_get:
            # Mock successful response
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = self.sample_earnings_data
            mock_get.return_value = mock_response

            # Test with different date formats
            test_start = "2024-01-01"
            test_end = "2024-01-31"
            
            get_earnings_calendar(test_start, test_end)

            # Verify dates are passed correctly
            call_args = mock_get.call_args
            params = call_args[1]['params']
            self.assertEqual(params['from'], test_start)
            self.assertEqual(params['to'], test_end)

    def test_get_earnings_calendar_network_error(self):
        """Test handling of network errors."""
        with patch('requests.get') as mock_get:
            # Mock network error
            mock_get.side_effect = Exception("Network error")

            # Call the function (should handle exception gracefully)
            try:
                get_earnings_calendar(self.start_date, self.end_date)
            except Exception as e:
                self.fail(f"Function should handle network errors gracefully: {e}")

    def test_get_earnings_calendar_invalid_json(self):
        """Test handling of invalid JSON response."""
        with patch('requests.get') as mock_get:
            # Mock response with invalid JSON
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.side_effect = json.JSONDecodeError("Invalid JSON", "", 0)
            mock_get.return_value = mock_response

            # Call the function (should handle JSON error gracefully)
            try:
                get_earnings_calendar(self.start_date, self.end_date)
            except Exception as e:
                self.fail(f"Function should handle JSON errors gracefully: {e}")


class TestFinnhubEarningsCalendarIntegration(unittest.TestCase):
    """Integration tests for get_earnings_calendar function."""

    @unittest.skipUnless(os.getenv('FINNHUB_API_KEY'), "FINNHUB_API_KEY not set")
    def test_real_api_call(self):
        """Test with real API call (requires FINNHUB_API_KEY)."""
        # Use a recent date range
        start_date = "2024-01-01"
        end_date = "2024-01-31"
        
        # This test will make a real API call
        get_earnings_calendar(start_date, end_date)
        # If we get here without exception, the test passes

    def test_date_range_validation(self):
        """Test various date range scenarios."""
        with patch('requests.get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"earningsCalendar": []}
            mock_get.return_value = mock_response

            # Test same day
            get_earnings_calendar("2024-01-01", "2024-01-01")
            
            # Test future dates
            get_earnings_calendar("2024-12-01", "2024-12-31")
            
            # Test past dates
            get_earnings_calendar("2023-01-01", "2023-01-31")

            # Verify all calls were made
            self.assertEqual(mock_get.call_count, 3)


def run_tests():
    """Run all tests."""
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test cases
    test_suite.addTest(unittest.makeSuite(TestFinnhubEarningsCalendar))
    test_suite.addTest(unittest.makeSuite(TestFinnhubEarningsCalendarIntegration))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    return result.wasSuccessful()


if __name__ == "__main__":
    print("Testing get_earnings_calendar function...")
    print("=" * 50)
    
    # Check if FINNHUB_API_KEY is set
    if not os.getenv('FINNHUB_API_KEY'):
        print("⚠️  FINNHUB_API_KEY not set. Integration tests will be skipped.")
        print("💡 Set your API key to run integration tests:")
        print("   export FINNHUB_API_KEY='your-api-key-here'")
        print()
    
    # Run tests
    success = run_tests()
    
    if success:
        print("\n✅ All tests passed!")
    else:
        print("\n❌ Some tests failed!")
    
    print("\n" + "=" * 50) 