import unittest
import os
import sys

def run_tests():
    """Run all Lambda function tests"""
    # Get the current directory
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Define the Lambda directories to test
    lambda_dirs = [
        os.path.join(current_dir, 'lambdas', 'woocommerce_fetcher'),
        os.path.join(current_dir, 'lambdas', 'ga_fetcher'),
        os.path.join(current_dir, 'lambdas', 'metrics_processor'),
        os.path.join(current_dir, 'lambdas', 'api_handler')
    ]
    
    # Initialize the test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all tests to the suite
    for lambda_dir in lambda_dirs:
        if os.path.exists(lambda_dir) and os.path.isdir(lambda_dir):
            # Change directory to the lambda directory
            os.chdir(lambda_dir)
            
            # Check if test file exists
            test_file = os.path.join(lambda_dir, 'test_lambda.py')
            if os.path.exists(test_file):
                print(f"Adding tests from {lambda_dir}")
                
                # Add the lambda directory to the Python path
                sys.path.insert(0, lambda_dir)
                
                # Add tests from the test file
                try:
                    tests = loader.discover(lambda_dir, pattern='test_*.py')
                    suite.addTests(tests)
                except Exception as e:
                    print(f"Error loading tests from {lambda_dir}: {str(e)}")
                
                # Remove the lambda directory from the Python path
                sys.path.pop(0)
            else:
                print(f"No test file found in {lambda_dir}")
    
    # Change back to the original directory
    os.chdir(current_dir)
    
    # Run the tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()

if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1) 