#!/bin/bash
set -euo pipefail

echo "=== Docker Build Test for Frontend Fix ==="
echo ""

cd frontend

# Test 1: Verify Dockerfile syntax
echo "1. Verifying Dockerfile syntax..."
if docker build -f Dockerfile.frontend --target scratch -t syntax-test . > /dev/null 2>&1; then
    echo "✅ Dockerfile syntax is valid"
else
    echo "❌ ERROR: Dockerfile has syntax issues"
    exit 1
fi

# Test 2: Test a simplified build (just to verify it can start building)
echo "2. Testing Docker build process..."
if timeout 120 docker build -f Dockerfile.frontend -t frontend-fix-test . > docker_build_test.log 2>&1; then
    echo "✅ Docker build process initiated successfully"
    
    # Clean up the test image
    docker rmi frontend-fix-test > /dev/null 2>&1 || true
    
    # Clean up the log
    rm -f docker_build_test.log
else
    echo "❌ Docker build failed or timed out"
    if [ -f "docker_build_test.log" ]; then
        echo "Build log (last 20 lines):"
        tail -20 docker_build_test.log
        rm -f docker_build_test.log
    fi
    exit 1
fi

cd ..

echo ""
echo "🎉 DOCKER BUILD TEST PASSED!"
echo ""
echo "The frontend Dockerfile can be built successfully."
echo "The 'react-scripts: not found' error should be resolved."

exit 0