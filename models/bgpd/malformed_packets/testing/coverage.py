import sys
import tempfile

try:
    import coverage
except ImportError:
    print("The 'coverage' module is not installed. Please install it using 'pip install coverage'.")
    sys.exit(1)

def run_with_coverage():
    # Measure branch coverage of the Python oracle, independently of FRR.
    cov = coverage.Coverage(branch=True, source=['models.bgpd.malformed_packets.bgp_oracle'])
    cov.start()

    try:
        from models.bgpd.malformed_packets.run_parity_fuzzer import execute_comprehensive_suite
        with tempfile.TemporaryDirectory() as tmp:
            execute_comprehensive_suite(suite="all", dry_run=True,
                                        fail_on_deviation=True,
                                        out_path=f"{tmp}/parity.json")
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
