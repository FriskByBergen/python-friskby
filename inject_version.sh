#!/bin/bash
set -e

CURRENT_VERSION=`cat VERSION`
sed -ie "s/INJECT_VERSION/'$CURRENT_VERSION'/g" setup.py
sed -ie "s/INJECT_VERSION/'$CURRENT_VERSION'/g" friskby/__init__.py

echo "Injected version string '$CURRENT_VERSION' into setup.py and friskby module"
