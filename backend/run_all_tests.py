import os
import sys
import importlib
import time

def main():
    """Run all test scripts"""
    print("=" * 50)
    print("DASHORA BACKEND TESTS")
    print("=" * 50)
    print()
    
    test_scripts = [
        "basic_test.py",
        "google_analytics_test.py",
        "api_test.py"
    ]
    
    results = {}
    
    for script in test_scripts:
        script_name = os.path.splitext(script)[0]
        print(f"Running {script}...")
        print("-" * 50)
        
        try:
            start_time = time.time()
            
            # Import and run the module
            if script.endswith('.py'):
                script = script[:-3]
            module = importlib.import_module(script)
            if hasattr(module, 'main'):
                module.main()
            
            end_time = time.time()
            elapsed = end_time - start_time
            
            results[script] = {
                'status': 'PASSED',
                'time': elapsed
            }
            
        except Exception as e:
            print(f"Error running {script}: {str(e)}")
            results[script] = {
                'status': 'FAILED',
                'error': str(e)
            }
        
        print("-" * 50)
        print()
    
    # Print summary
    print("=" * 50)
    print("TEST SUMMARY")
    print("=" * 50)
    
    passed = 0
    failed = 0
    
    for script, result in results.items():
        status = result['status']
        if status == 'PASSED':
            passed += 1
            if 'time' in result:
                print(f"✅ {script}: PASSED ({result['time']:.2f}s)")
            else:
                print(f"✅ {script}: PASSED")
        else:
            failed += 1
            print(f"❌ {script}: FAILED - {result.get('error', 'Unknown error')}")
    
    print()
    print(f"Tests passed: {passed}/{len(results)}")
    print(f"Tests failed: {failed}/{len(results)}")
    
    # Return exit code
    if failed > 0:
        print("\nSome tests failed!")
        return 1
    else:
        print("\nAll tests passed!")
        return 0

if __name__ == "__main__":
    sys.exit(main()) 