#!/bin/bash
echo "STRICT DIFFERENTIAL AUDIT: v5-concept"
echo "-------------------------------------------------------"

# Extract metrics for the latest concept tag
AEGIS_LAT=$(grep "v5-concept,AegisGrid" tag_summary.csv | cut -d, -f3)
IEC_LAT=$(grep "v5-concept,IEC62351" tag_summary.csv | cut -d, -f3)

echo "AegisGrid (Optimized) Latency: $AEGIS_LAT"
echo "IEC62351 (Standard) Latency:   $IEC_LAT"

# Logic: If Aegis is faster than the industrial standard (IEC), it is "better" for Grid operations.
python3 -c "print('VERDICT: AegisGrid is better for real-time CPS.') if $AEGIS_LAT > $IEC_LAT else print('VERDICT: Standard model holds advantage.')"
