import sys
import unittest.mock

try:
    import coverage
except ImportError:
    print("The 'coverage' module is not installed. Please install it using 'pip install coverage'.")
    sys.exit(1)

def run_with_coverage():
    # Start coverage with branch coverage enabled
    # We want to measure coverage specifically for the bgp_oracle.py logic
    cov = coverage.Coverage(branch=True, source=['models.bgpd.malformed_packets.bgp_oracle'])
    cov.start()

    try:
        from models.bgpd.malformed_packets.run_parity_fuzzer import execute_comprehensive_suite
        # Patch input to automatically select option 4 (All Suites) to run without blocking
        with unittest.mock.patch('builtins.input', return_value='4'):
            execute_comprehensive_suite()
    except Exception as e:
        print(f"Error during fuzzing suite execution: {e}")
    finally:
        cov.stop()
        cov.save()
        
        print("\n" + "="*50)
        print("          BGP ORACLE BRANCH COVERAGE REPORT          ")
        print("="*50)
        cov.report(show_missing=True)
        print("="*50)

if __name__ == '__main__':
    run_with_coverage()
