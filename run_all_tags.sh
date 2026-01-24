#!/bin/bash
set -e

echo "============================================="
echo "     GIT TAG VALIDATION & EXECUTION TOOL    "
echo "============================================="

ORIGINAL_BRANCH=$(git rev-parse --abbrev-ref HEAD)
RESULT_DIR="tag_results"

mkdir -p "$RESULT_DIR"

TAGS=$(git tag)

if [ -z "$TAGS" ]; then
    echo "No git tags found."
    exit 0
fi

echo "Found tags:"
echo "$TAGS"
echo

for tag in $TAGS; do
    echo "---------------------------------------------"
    echo "Testing tag: $tag"
    echo "---------------------------------------------"

    LOGFILE="$RESULT_DIR/$tag.log"

    {
        echo "Tag: $tag"
        echo "Commit: $(git rev-list -n 1 "$tag")"
        echo "Timestamp: $(date)"
        echo

        echo "Checking out tag..."
        git checkout -q "$tag"

        echo "Verifying required files..."
        REQUIRED_FILES=(
            "model_runner"
            "run_live_tests.py"
            "generate_report.sh"
            "core/crypto/entropy.py"
        )

        for f in "${REQUIRED_FILES[@]}"; do
            if [ ! -f "$f" ]; then
                echo "ERROR: Missing file $f"
                exit 1
            fi
        done

        echo "Setting execute permissions..."
        chmod +x model_runner generate_report.sh 2>/dev/null || true

        echo
        echo "Running validation report..."
        ./generate_report.sh

        if [ -f "gap_analysis.sh" ]; then
            echo
            echo "Running gap analysis..."
            chmod +x gap_analysis.sh
            ./gap_analysis.sh
        fi

        echo
        echo "STATUS: PASS"
    } > "$LOGFILE" 2>&1 || {
        echo "STATUS: FAIL (see $LOGFILE)"
        continue
    }

    echo "Results saved to $LOGFILE"
done

echo
echo "Restoring branch: $ORIGINAL_BRANCH"
git checkout -q "$ORIGINAL_BRANCH"

echo "============================================="
echo "        TAG VALIDATION COMPLETE              "
echo "Logs stored in: $RESULT_DIR"
echo "============================================="
