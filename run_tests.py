#!/usr/bin/env python3
"""
Test runner script for WSJ Adapter.

This script provides an easy way to run all tests or specific test suites.
"""

import sys
import unittest
import argparse
from pathlib import Path


def discover_tests(test_dir='tests', pattern='test*.py'):
    """
    Discover and return all test suites.
    """
    loader = unittest.TestLoader()
    suite = loader.discover(test_dir, pattern=pattern)
    return suite


def run_specific_test(test_module, test_class=None, test_method=None):
    """
    Run a specific test module, class, or method.
    """
    if test_method and test_class:
        suite = unittest.TestSuite()
        suite.addTest(test_class(test_method))
    elif test_class:
        suite = unittest.TestLoader().loadTestsFromTestCase(test_class)
    else:
        suite = unittest.TestLoader().loadTestsFromName(test_module)
    
    return suite


def main():
    """
    Main test runner function.
    """
    parser = argparse.ArgumentParser(description='Run WSJ Adapter tests')
    parser.add_argument(
        '--verbose', '-v', 
        action='store_true', 
        help='Run tests in verbose mode'
    )
    parser.add_argument(
        '--module', '-m', 
        help='Run tests from a specific module (e.g., test_adapter)'
    )
    parser.add_argument(
        '--pattern', '-p', 
        default='test*.py',
        help='Test file pattern (default: test*.py)'
    )
    parser.add_argument(
        '--failfast', '-f', 
        action='store_true', 
        help='Stop on first failure'
    )
    parser.add_argument(
        '--coverage', '-c', 
        action='store_true', 
        help='Run with coverage analysis (requires coverage package)'
    )
    
    args = parser.parse_args()
    
    # Set verbosity level
    verbosity = 2 if args.verbose else 1
    
    # Check if tests directory exists
    test_dir = Path('tests')
    if not test_dir.exists():
        print(f"Error: Tests directory '{test_dir}' not found")
        sys.exit(1)
    
    # Discover or load specific tests
    if args.module:
        try:
            suite = run_specific_test(f'tests.{args.module}')
        except Exception as e:
            print(f"Error loading test module '{args.module}': {e}")
            sys.exit(1)
    else:
        suite = discover_tests(test_dir, args.pattern)
    
    # Run tests with coverage if requested
    if args.coverage:
        try:
            import coverage
            
            # Start coverage
            cov = coverage.Coverage()
            cov.start()
            
            # Run tests
            runner = unittest.TextTestRunner(
                verbosity=verbosity,
                failfast=args.failfast
            )
            result = runner.run(suite)
            
            # Stop coverage and report
            cov.stop()
            cov.save()
            
            print("\n" + "="*60)
            print("COVERAGE REPORT")
            print("="*60)
            cov.report()
            
            # Save HTML report if available
            try:
                cov.html_report(directory='htmlcov')
                print("\nHTML coverage report saved to 'htmlcov/index.html'")
            except Exception as e:
                print(f"Could not generate HTML report: {e}")
                
        except ImportError:
            print("Error: coverage package not installed. Install with: pip install coverage")
            sys.exit(1)
    else:
        # Run tests normally
        runner = unittest.TextTestRunner(
            verbosity=verbosity,
            failfast=args.failfast
        )
        result = runner.run(suite)
    
    # Print summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Skipped: {len(result.skipped) if hasattr(result, 'skipped') else 0}")
    
    if result.failures:
        print("\nFAILURES:")
        for test, traceback in result.failures:
            print(f"  {test}: {traceback.split('AssertionError:')[-1].strip()}")
    
    if result.errors:
        print("\nERRORS:")
        for test, traceback in result.errors:
            print(f"  {test}: {traceback.split('Exception:')[-1].strip()}")
    
    # Exit with appropriate code
    if result.failures or result.errors:
        print("\nSome tests failed!")
        sys.exit(1)
    else:
        print("\nAll tests passed!")
        sys.exit(0)


if __name__ == '__main__':
    main() 