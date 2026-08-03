#!/usr/bin/env python3
"""
Master Test Runner Script.
Discovers and executes all unit tests, service tests, FastAPI endpoint tests, edge-case tests,
and Streamlit frontend tests, printing a formatted summary report.
"""

import unittest
import sys
import os
import time

def run_test_suite():
    print("\n" + "="*75)
    print("      TELECOM CUSTOMER CHURN SYSTEM - AUTOMATED TEST SUITE RUNNER      ")
    print("="*75 + "\n")

    loader = unittest.TestLoader()

    # Discover and add test modules
    suite = unittest.TestSuite()
    
    modules_to_test = [
        "tests.test_unit_pipeline",
        "tests.test_services",
        "tests.test_fastapi_endpoints",
        "tests.test_edge_cases",
        "tests.test_db_repository",
        "test_prediction_service",
        "test_api",
        "test_streamlit"
    ]

    for module_name in modules_to_test:
        try:
            mod_suite = loader.loadTestsFromName(module_name)
            suite.addTests(mod_suite)
            print(f"  [+] Loaded test module: '{module_name}'")
        except Exception as e:
            print(f"  [-] Failed to load test module '{module_name}': {e}")

    print("\n" + "-"*75)
    print(" Executing Test Suites...")
    print("-"*75 + "\n")

    start_time = time.time()
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    elapsed_time = time.time() - start_time

    print("\n" + "="*75)
    print("                         TEST SUMMARY REPORT                         ")
    print("="*75)
    print(f"  Tests Run        : {result.testsRun}")
    print(f"  Successful       : {result.testsRun - len(result.failures) - len(result.errors) - len(result.skipped)}")
    print(f"  Failures         : {len(result.failures)}")
    print(f"  Errors           : {len(result.errors)}")
    print(f"  Skipped          : {len(result.skipped)}")
    print(f"  Execution Time   : {elapsed_time:.3f} seconds")
    print("="*75)

    if result.wasSuccessful():
        print("\n  [SUCCESS] ALL SYSTEM TESTS PASSED SUCCESSFULLY!\n")
        return 0
    else:
        print("\n  [FAILURE] SOME TESTS FAILED. CHECK LOG DETAILS ABOVE.\n")
        return 1

if __name__ == "__main__":
    sys.exit(run_test_suite())
