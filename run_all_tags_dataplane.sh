#!/bin/bash
set -e

RESULT_DIR="tag_results_real"
ORIGINAL_BRANCH=$(git rev-parse --abbrev-ref HEAD)

mkdir -p "$RESULT_DIR"

echo "============================================="
echo " REAL DATA-PLANE TAG VALIDATION HARNESS"
echo "============================================="

for tag in $(git tag); do
    echo "Testing tag: $tag"

    git checkout "$tag" > /dev/null 2>&1

    {
        echo "Tag: $tag"
        for model in AegisGrid EncryptedOnly IEC62351 IDSAdaptive; do
            echo "System: $model"
            python3 dataplane_test.py "$model"
            echo "-----------------------------------"
        done
    } > "$RESULT_DIR/$tag.log"

done

git checkout "$ORIGINAL_BRANCH" > /dev/null 2>&1

echo "============================================="
echo " COMPLETE"
echo "Results in: $RESULT_DIR"
echo "============================================="
