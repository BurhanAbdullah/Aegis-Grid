#!/bin/bash

# Get absolute base directory
BASE_DIR="$(cd "$(dirname "$0")/.." && pwd)"
DATA_DIR="$BASE_DIR/enhanced_data"

mkdir -p "$DATA_DIR"

OUTPUT="$DATA_DIR/reconstruction_enhanced.csv"

echo "packet_loss,N,success_probability" > "$OUTPUT"

for N in 5 10 20 30; do
  for loss in 0.0 0.05 0.1 0.15 0.2 0.25 0.3; do
    
    success=$(python3 - <<END
loss=$loss
N=$N
print((1-loss)**N)
END
)

    echo "$loss,$N,$success" >> "$OUTPUT"
  done
done

echo "Generated: $OUTPUT"
#!/bin/bash

output="../enhanced_data/reconstruction_enhanced.csv"

echo "packet_loss,N,success_probability" > $output

for N in 5 10 20 30; do
  for loss in 0.0 0.05 0.1 0.15 0.2 0.25 0.3; do
    
    # Probability all fragments survive
    success=$(python3 - <<END
import math
loss=$loss
N=$N
print((1-loss)**N)
END
)
    
    echo "$loss,$N,$success" >> $output
  done
done
