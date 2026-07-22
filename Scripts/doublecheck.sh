#!/usr/bin/env bash
set -euo pipefail

echo "=========================================="
echo " Phase 9.2 Governance Verification"
echo "=========================================="
echo

DOC_DIR="homelab/Documentation/services"
VAL_DIR="homelab/Validation/Phase9.2"

echo "1. Checking service.json count..."
JSON_COUNT=$(find "$DOC_DIR" -name service.json | wc -l)
echo "service.json files found: $JSON_COUNT"

if [ "$JSON_COUNT" -eq 19 ]; then
    echo "✅ PASS: 19 service.json files exist"
else
    echo "❌ FAIL: Expected 19 service.json files"
fi

echo
echo "2. Checking service markdown count..."
MD_COUNT=$(find "$DOC_DIR" -mindepth 2 -maxdepth 2 -name "*.md" | wc -l)
echo "Markdown files found: $MD_COUNT"

if [ "$MD_COUNT" -eq 19 ]; then
    echo "✅ PASS: 19 service markdown files exist"
else
    echo "❌ FAIL: Expected 19 markdown files"
fi

echo
echo "3. Checking directory contents..."
find "$DOC_DIR" -maxdepth 2 -type f | sort

echo
echo "4. Validating JSON syntax..."

if command -v jq >/dev/null 2>&1; then
    if find "$DOC_DIR" -name service.json -exec jq empty {} \; ; then
        echo "✅ PASS: All JSON files valid"
    else
        echo "❌ FAIL: Invalid JSON detected"
    fi
else
    echo "⚠️ jq not installed - skipping JSON validation"
fi

echo
echo "5. Checking git changes..."

#git status --short
git -C /config/workspace/homelab status

echo
echo "Expected:"
echo "  homelab/Documentation/"
echo "  homelab/Validation/Phase9.2/"
echo
echo "Investigate if you see:"
echo "  compose files"
echo "  docker configs"
echo "  .env files"
echo "  service deployment files"

echo
echo "6. Checking ADR references..."

ADR_COUNT=$(grep -R "ADR" "$DOC_DIR" 2>/dev/null | wc -l || true)

echo "ADR reference lines found: $ADR_COUNT"

if [ "$ADR_COUNT" -gt 0 ]; then
    echo "✅ ADR references detected"
else
    echo "⚠️ No ADR references found"
fi

echo
echo "7. Checking EchoOS duplicate notices..."

for svc in EchoOS echoos; do
    FILE="$DOC_DIR/$svc/$svc.md"

    if [ -f "$FILE" ]; then
        if grep -q "Duplicate service name detected" "$FILE"; then
            echo "✅ $svc duplicate notice found"
        else
            echo "❌ $svc duplicate notice missing"
        fi
    else
        echo "❌ Missing $FILE"
    fi
done

echo
echo "=========================================="
echo " Verification Complete"
echo "=========================================="