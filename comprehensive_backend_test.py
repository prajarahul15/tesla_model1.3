import requests
import sys
import json
from datetime import datetime

class ComprehensiveAPITester:
    def __init__(self, base_url="https://tesla-forecast.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.tests_run = 0
        self.tests_passed = 0
        self.scenarios = ['best', 'base', 'worst']
        self.available_lineups = []

    def run_test(self, name, method, endpoint, expected_status, data=None):
        """Run a single API test"""
        url = f"{self.api_url}/{endpoint}"
        headers = {'Content-Type': 'application/json'}

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, timeout=30)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers, timeout=30)

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                
                # Try to parse JSON response
                try:
                    response_data = response.json()
                    if isinstance(response_data, dict):
                        print(f"   Response keys: {list(response_data.keys())}")
                    return True, response_data
                except:
                    return True, {}
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   Error: {error_data}")
                except:
                    print(f"   Error text: {response.text[:200]}")
                return False, {}

        except requests.exceptions.Timeout:
            print(f"❌ Failed - Request timeout (30s)")
            return False, {}
        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}

    # Tesla Financial Model Tests
    
    def test_tesla_overview(self):
        """Test Tesla overview endpoint"""
        success, response = self.run_test(
            "Tesla Overview",
            "GET",
            "tesla/overview",
            200
        )
        
        if success and response:
            # Validate response structure
            required_keys = ['tesla_base_data', 'macro_assumptions', 'scenarios', 'forecast_years']
            missing_keys = [key for key in required_keys if key not in response]
            if missing_keys:
                print(f"   ⚠️  Missing keys in response: {missing_keys}")
            else:
                print(f"   ✅ All required keys present")
                
            # Check Tesla base data
            if 'tesla_base_data' in response:
                base_data = response['tesla_base_data']
                print(f"   📊 Tesla 2024 Revenue: ${base_data.get('total_revenue', 0):,.0f}")
                print(f"   📊 Tesla 2024 Deliveries: {base_data.get('total_deliveries', 0):,.0f}")
        
        return success

    def test_scenario_model_generation(self, scenario):
        """Test financial model generation for a scenario"""
        success, response = self.run_test(
            f"Generate {scenario.title()} Model",
            "POST",
            f"tesla/model/{scenario}",
            200
        )
        
        if success and response:
            if response.get('success'):
                print(f"   ✅ Model generated successfully")
                model = response.get('model', {})
                if model:
                    print(f"   📈 Income statements: {len(model.get('income_statements', []))}")
                    print(f"   📊 Balance sheets: {len(model.get('balance_sheets', []))}")
                    print(f"   💰 Cash flows: {len(model.get('cash_flow_statements', []))}")
                    
                    # Check DCF valuation
                    dcf = model.get('dcf_valuation', {})
                    if dcf:
                        price_per_share = dcf.get('price_per_share', 0)
                        print(f"   🎯 DCF Price per Share: ${price_per_share:.2f}")
            else:
                print(f"   ⚠️  Model generation reported failure")
        
        return success

    def test_dcf_valuation(self, scenario):
        """Test DCF valuation endpoint"""
        success, response = self.run_test(
            f"Get {scenario.title()} DCF Valuation",
            "GET",
            f"tesla/model/{scenario}/dcf-valuation",
            200
        )
        
        if success and response:
            dcf = response.get('dcf_valuation', {})
            if dcf:
                price = dcf.get('price_per_share', 0)
                wacc = dcf.get('wacc', 0)
                enterprise_value = dcf.get('enterprise_value', 0)
                print(f"   🎯 Price per Share: ${price:.2f}")
                print(f"   📊 WACC: {wacc*100:.1f}%")
                print(f"   🏢 Enterprise Value: ${enterprise_value:,.0f}")
            else:
                print(f"   ⚠️  No DCF valuation found")
        
        return success

    def test_scenario_comparison(self):
        """Test scenario comparison endpoint"""
        success, response = self.run_test(
            "Scenario Comparison",
            "GET",
            "tesla/comparison",
            200
        )
        
        if success and response:
            models = response.get('models', {})
            comparison = response.get('comparison_summary', {})
            
            print(f"   📊 Models available: {list(models.keys())}")
            
            if comparison:
                revenue_comp = comparison.get('revenue_comparison', {})
                valuation_comp = comparison.get('valuation_comparison', {})
                print(f"   💰 Revenue comparison scenarios: {list(revenue_comp.keys())}")
                print(f"   🎯 Valuation comparison scenarios: {list(valuation_comp.keys())}")
            else:
                print(f"   ⚠️  No comparison summary found")
        
        return success

    # Professional Dashboard API Tests
    
    def test_analytics_overview(self):
        """Test analytics overview endpoint"""
        success, response = self.run_test(
            "Analytics Data Overview",
            "GET",
            "analytics/overview",
            200
        )
        
        if success and response:
            if response.get('success'):
                data = response.get('data', {})
                print(f"   ✅ Overview data retrieved successfully")
                
                # Check for key metrics
                if 'profile_breakdown' in data:
                    profiles = data['profile_breakdown']
                    print(f"   📊 Profiles found: {list(profiles.keys())}")
                
                if 'lineup_analysis' in data:
                    lineups = data['lineup_analysis']
                    print(f"   📈 Lineups analyzed: {len(lineups)}")
                
                if 'monthly_trends' in data:
                    trends = data['monthly_trends']
                    print(f"   📅 Monthly trends: {len(trends)} months")
                    
            else:
                print(f"   ⚠️  Analytics overview reported failure")
        
        return success

    def test_analytics_lineups(self):
        """Test analytics lineups endpoint"""
        success, response = self.run_test(
            "Analytics Available Lineups",
            "GET",
            "analytics/lineups",
            200
        )
        
        if success and response:
            if response.get('success'):
                lineups = response.get('lineups', [])
                print(f"   ✅ Found {len(lineups)} lineups")
                
                # Store lineups for later tests
                self.available_lineups = [lineup['lineup'] for lineup in lineups]
                
                # Display lineup details
                for lineup in lineups[:3]:  # Show first 3
                    print(f"   📊 {lineup['lineup']}: {lineup['records']} records, Profile: {lineup['profile']}")
                    
            else:
                print(f"   ⚠️  Lineups retrieval reported failure")
        
        return success

    def test_economic_variables(self):
        """Test economic variables endpoint"""
        success, response = self.run_test(
            "Economic Variables Data",
            "GET",
            "analytics/economic-variables",
            200
        )
        
        if success and response:
            if response.get('success'):
                data = response.get('data', {})
                print(f"   ✅ Economic variables retrieved successfully")
                
                # Check for economic indicators
                if 'economic_indicators' in data:
                    indicators = data['economic_indicators']
                    print(f"   📈 Economic indicators: {list(indicators.keys())}")
                
                if 'correlation_matrix' in data:
                    matrix = data['correlation_matrix']
                    print(f"   🔗 Correlation matrix size: {len(matrix)}x{len(matrix[0]) if matrix else 0}")
                    
            else:
                print(f"   ⚠️  Economic variables reported failure")
        
        return success

    def test_univariate_forecast(self, lineup, months_ahead=12):
        """Test univariate forecasting"""
        success, response = self.run_test(
            f"Univariate Forecast - {lineup}",
            "POST",
            "analytics/forecast",
            200,
            data={
                "lineup": lineup,
                "forecast_type": "univariate",
                "months_ahead": months_ahead
            }
        )
        
        if success and response:
            if response.get('success'):
                forecast = response.get('forecast', {})
                print(f"   ✅ Univariate forecast generated successfully")
                
                if 'forecast_values' in forecast:
                    values = forecast['forecast_values']
                    print(f"   📈 Forecast values: {len(values)} months")
                
                if 'model_metrics' in forecast:
                    metrics = forecast['model_metrics']
                    print(f"   📊 Model metrics available: {list(metrics.keys())}")
                    
            else:
                print(f"   ⚠️  Univariate forecast reported failure")
        
        return success

    def test_multivariate_forecast(self, lineup, months_ahead=12):
        """Test multivariate forecasting"""
        success, response = self.run_test(
            f"Multivariate Forecast - {lineup}",
            "POST",
            "analytics/forecast",
            200,
            data={
                "lineup": lineup,
                "forecast_type": "multivariate",
                "months_ahead": months_ahead
            }
        )
        
        if success and response:
            if response.get('success'):
                forecast = response.get('forecast', {})
                print(f"   ✅ Multivariate forecast generated successfully")
                
                if 'forecast_values' in forecast:
                    values = forecast['forecast_values']
                    print(f"   📈 Forecast values: {len(values)} months")
                
                if 'economic_impact' in forecast:
                    impact = forecast['economic_impact']
                    print(f"   🌍 Economic variables impact analyzed")
                    
            else:
                print(f"   ⚠️  Multivariate forecast reported failure")
        
        return success

    def test_forecast_comparison(self, lineup, months_ahead=12):
        """Test forecast comparison between methods"""
        success, response = self.run_test(
            f"Forecast Comparison - {lineup}",
            "POST",
            "analytics/compare-forecasts",
            200,
            data={
                "lineup": lineup,
                "months_ahead": months_ahead
            }
        )
        
        if success and response:
            if response.get('success'):
                comparison = response.get('comparison', {})
                print(f"   ✅ Forecast comparison generated successfully")
                
                if 'univariate_forecast' in comparison and 'multivariate_forecast' in comparison:
                    print(f"   📊 Both forecast methods compared")
                
                if 'performance_metrics' in comparison:
                    metrics = comparison['performance_metrics']
                    print(f"   📈 Performance metrics: {list(metrics.keys())}")
                    
            else:
                print(f"   ⚠️  Forecast comparison reported failure")
        
        return success

    def run_comprehensive_test(self):
        """Run all tests in sequence"""
        print("🚀 Starting Comprehensive Tesla Financial Model & Analytics API Testing")
        print(f"📍 Base URL: {self.base_url}")
        print("=" * 80)

        # PART 1: Tesla Financial Model Tests
        print(f"\n🏢 PART 1: TESLA FINANCIAL MODEL TESTING")
        print("=" * 50)
        
        # Test 1: Tesla Overview
        if not self.test_tesla_overview():
            print("❌ Tesla Overview failed - continuing with other tests")

        # Test 2: Generate models for all scenarios
        print(f"\n📈 Testing Model Generation for All Scenarios")
        for scenario in self.scenarios:
            if not self.test_scenario_model_generation(scenario):
                print(f"❌ {scenario} model generation failed")

        # Test 3: Test DCF valuation for all scenarios
        print(f"\n🎯 Testing DCF Valuations")
        for scenario in self.scenarios:
            if not self.test_dcf_valuation(scenario):
                print(f"❌ {scenario} DCF valuation failed")

        # Test 4: Test scenario comparison
        print(f"\n🔄 Testing Scenario Comparison")
        if not self.test_scenario_comparison():
            print(f"❌ Scenario comparison failed")

        # PART 2: Professional Dashboard Tests
        print(f"\n📊 PART 2: PROFESSIONAL DASHBOARD TESTING")
        print("=" * 50)

        # Test 5: Analytics Overview
        if not self.test_analytics_overview():
            print("❌ Analytics Overview failed - continuing with other tests")

        # Test 6: Analytics Lineups
        if not self.test_analytics_lineups():
            print("❌ Analytics Lineups failed - continuing with other tests")

        # Test 7: Economic Variables
        if not self.test_economic_variables():
            print("❌ Economic Variables failed - continuing with other tests")

        # Test 8: Forecasting Tests (if lineups are available)
        if self.available_lineups:
            print(f"\n🔮 Testing Forecasting Capabilities")
            test_lineup = self.available_lineups[0]  # Use first available lineup
            
            # Test univariate forecasting
            if not self.test_univariate_forecast(test_lineup, 12):
                print(f"❌ Univariate forecast failed for {test_lineup}")
            
            # Test multivariate forecasting  
            if not self.test_multivariate_forecast(test_lineup, 12):
                print(f"❌ Multivariate forecast failed for {test_lineup}")
            
            # Test forecast comparison
            if not self.test_forecast_comparison(test_lineup, 12):
                print(f"❌ Forecast comparison failed for {test_lineup}")
        else:
            print("⚠️  No lineups available for forecasting tests")

        return True

def main():
    """Main test execution"""
    tester = ComprehensiveAPITester()
    
    try:
        success = tester.run_comprehensive_test()
        
        # Print final results
        print("\n" + "=" * 80)
        print(f"📊 COMPREHENSIVE TEST RESULTS")
        print(f"✅ Tests passed: {tester.tests_passed}/{tester.tests_run}")
        print(f"📈 Success rate: {(tester.tests_passed/tester.tests_run)*100:.1f}%")
        
        if tester.tests_passed == tester.tests_run:
            print("🎉 ALL TESTS PASSED - Both Tesla Financial Model & Analytics APIs are working correctly!")
            return 0
        elif tester.tests_passed > 0:
            print("⚠️  SOME TESTS PASSED - Check the failed tests above for issues")
            return 1
        else:
            print("❌ ALL TESTS FAILED - Major issues with the APIs")
            return 1
            
    except Exception as e:
        print(f"💥 Test execution failed: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main())