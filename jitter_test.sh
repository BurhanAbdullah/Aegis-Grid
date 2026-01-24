#!/bin/bash
echo "Evaluating Model Resilience under Network Jitter..."
echo "-------------------------------------------------------"

for m in "AegisGrid" "EncryptedOnly" "IEC62351" "IDSAdaptive"; do
    # Run 5 iterations to see stability
    results=()
    for i in {1..5}; do
        # Simulate background noise/jitter by adding random sleep in a subshell
        res=$(python3 -c "import time, random; time.sleep(random.uniform(0.001, 0.01)); import run_live_tests; print(run_live_tests.get_latency('$m'))" 2>/dev/null)
        results+=($res)
    done
    echo "System: $m | Latency Samples: ${results[*]}"
done
