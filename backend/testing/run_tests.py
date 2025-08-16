#!/usr/bin/env python3
"""
Test runner script for the backend API test suite.
Provides convenient ways to run different test categories.
"""

import subprocess
import sys
import argparse
from pathlib import Path

def run_command(cmd, description, env=None):
    """Run a command and handle errors."""
    print(f"\n{'='*60}")
    print(f"Running: {description}")
    print(f"Command: {' '.join(cmd)}")
    print('='*60)
    
    result = subprocess.run(cmd, cwd=Path(__file__).parent, env=env)
    
    if result.returncode != 0:
        print(f"\n❌ {description} failed with exit code {result.returncode}")
        return False
    else:
        print(f"\n✅ {description} completed successfully")
        return True

def main():
    parser = argparse.ArgumentParser(description='Run backend API tests')
    parser.add_argument('--module', '-m', help='Run specific test module', choices=[
        'schema', 'types', 'filters', 'integration', 'all'
    ], default='all')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    parser.add_argument('--coverage', '-c', action='store_true', help='Run with coverage')
    
    args = parser.parse_args()
    
    # Base pytest command with parent directory in Python path
    base_cmd = ['python', '-m', 'pytest']
    
    # Set PYTHONPATH to include the backend directory
    import os
    env = os.environ.copy()
    backend_dir = str(Path(__file__).parent.parent)
    env['PYTHONPATH'] = backend_dir + (f":{env.get('PYTHONPATH', '')}" if env.get('PYTHONPATH') else "")
    
    if args.verbose:
        base_cmd.append('-v')
    
    if args.coverage:
        base_cmd.extend(['--cov=../api', '--cov-report=term-missing'])
    
    success = True
    
    if args.module == 'all':
        # Run all tests
        cmd = base_cmd + ['.']
        success = run_command(cmd, "All API Tests", env)
    else:
        # Run specific module
        test_file = f'test_{args.module}.py'
        cmd = base_cmd + [test_file]
        success = run_command(cmd, f"{args.module.title()} Tests", env)
    
    if success:
        print("\n🎉 All tests completed successfully!")
        sys.exit(0)
    else:
        print("\n💥 Some tests failed!")
        sys.exit(1)

if __name__ == '__main__':
    main()