import requests
import sys
import json
from datetime import datetime

class TeslaFinancialAPITester:
    def __init__(self, base_url="https://tesla-forecast.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.tests_run = 0
        self.tests_passed = 0
        self.scenarios = ['best', 'base', 'worst']

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

    def test_income_statement(self, scenario):
        """Test income statement endpoint"""
        success, response = self.run_test(
            f"Get {scenario.title()} Income Statement",
            "GET",
            f"tesla/model/{scenario}/income-statement",
            200
        )
        
        if success and response:
            statements = response.get('income_statements', [])
            if statements:
                print(f"   📈 Found {len(statements)} income statements")
                # Check first statement structure
                first_stmt = statements[0]
                revenue = first_stmt.get('total_revenue', 0)
                print(f"   💰 2025 Revenue: ${revenue:,.0f}")
            else:
                print(f"   ⚠️  No income statements found")
        
        return success

    def test_balance_sheet(self, scenario):
        """Test balance sheet endpoint"""
        success, response = self.run_test(
            f"Get {scenario.title()} Balance Sheet",
            "GET",
            f"tesla/model/{scenario}/balance-sheet",
            200
        )
        
        if success and response:
            sheets = response.get('balance_sheets', [])
            if sheets:
                print(f"   📊 Found {len(sheets)} balance sheets")
                first_sheet = sheets[0]
                assets = first_sheet.get('total_assets', 0)
                print(f"   🏦 2025 Total Assets: ${assets:,.0f}")
            else:
                print(f"   ⚠️  No balance sheets found")
        
        return success

    def test_cash_flow(self, scenario):
        """Test cash flow endpoint"""
        success, response = self.run_test(
            f"Get {scenario.title()} Cash Flow",
            "GET",
            f"tesla/model/{scenario}/cash-flow",
            200
        )
        
        if success and response:
            flows = response.get('cash_flow_statements', [])
            if flows:
                print(f"   💸 Found {len(flows)} cash flow statements")
                first_flow = flows[0]
                fcf = first_flow.get('free_cash_flow', 0)
                print(f"   💰 2025 Free Cash Flow: ${fcf:,.0f}")
            else:
                print(f"   ⚠️  No cash flow statements found")
        
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

    def test_sensitivity_analysis(self, scenario):
        """Test sensitivity analysis endpoint"""
        success, response = self.run_test(
            f"Get {scenario.title()} Sensitivity Analysis",
            "GET",
            f"tesla/sensitivity/{scenario}",
            200
        )
        
        if success and response:
            sensitivity = response.get('sensitivity_analysis', {})
            if sensitivity:
                growth_rates = sensitivity.get('growth_rates', [])
                wacc_rates = sensitivity.get('wacc_rates', [])
                price_matrix = sensitivity.get('price_matrix', [])
                print(f"   📈 Growth rates tested: {len(growth_rates)}")
                print(f"   📊 WACC rates tested: {len(wacc_rates)}")
                print(f"   🎯 Price matrix size: {len(price_matrix)}x{len(price_matrix[0]) if price_matrix else 0}")
            else:
                print(f"   ⚠️  No sensitivity analysis found")
        
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

    def run_comprehensive_test(self):
        """Run all tests in sequence"""
        print("🚀 Starting Tesla Financial Model API Testing")
        print(f"📍 Base URL: {self.base_url}")
        print("=" * 60)

        # Test 1: Tesla Overview
        if not self.test_tesla_overview():
            print("❌ Tesla Overview failed - stopping tests")
            return False

        # Test 2: Generate models for all scenarios
        print(f"\n📈 Testing Model Generation for All Scenarios")
        for scenario in self.scenarios:
            if not self.test_scenario_model_generation(scenario):
                print(f"❌ {scenario} model generation failed")
                return False

        # Test 3: Test financial statements for base scenario
        print(f"\n📊 Testing Financial Statements (Base Scenario)")
        base_scenario = 'base'
        
        if not self.test_income_statement(base_scenario):
            print(f"❌ Income statement test failed")
            
        if not self.test_balance_sheet(base_scenario):
            print(f"❌ Balance sheet test failed")
            
        if not self.test_cash_flow(base_scenario):
            print(f"❌ Cash flow test failed")

        # Test 4: Test DCF valuation for all scenarios
        print(f"\n🎯 Testing DCF Valuations")
        for scenario in self.scenarios:
            if not self.test_dcf_valuation(scenario):
                print(f"❌ {scenario} DCF valuation failed")

        # Test 5: Test sensitivity analysis for base scenario
        print(f"\n📈 Testing Sensitivity Analysis")
        if not self.test_sensitivity_analysis(base_scenario):
            print(f"❌ Sensitivity analysis failed")

        # Test 6: Test scenario comparison
        print(f"\n🔄 Testing Scenario Comparison")
        if not self.test_scenario_comparison():
            print(f"❌ Scenario comparison failed")

        return True

def main():
    """Main test execution"""
    tester = TeslaFinancialAPITester()
    
    try:
        success = tester.run_comprehensive_test()
        
        # Print final results
        print("\n" + "=" * 60)
        print(f"📊 FINAL TEST RESULTS")
        print(f"✅ Tests passed: {tester.tests_passed}/{tester.tests_run}")
        print(f"📈 Success rate: {(tester.tests_passed/tester.tests_run)*100:.1f}%")
        
        if success and tester.tests_passed == tester.tests_run:
            print("🎉 ALL TESTS PASSED - Tesla Financial Model API is working correctly!")
            return 0
        else:
            print("❌ SOME TESTS FAILED - Check the issues above")
            return 1
            
    except Exception as e:
        print(f"💥 Test execution failed: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main())