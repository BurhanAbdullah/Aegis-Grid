#!/usr/bin/env bash
set -e

USD_TO_INR=83.0
DATADIR="data"
OUTDIR="data_inr"

mkdir -p "$OUTDIR"

for f in "$DATADIR"/*.csv "$DATADIR"/*.dat; do
    [ -f "$f" ] || continue
    base=$(basename "$f")

    awk -v r="$USD_TO_INR" '
    BEGIN { OFS="," }
    NR==1 { print; next }
    {
        for (i=1;i<=NF;i++) {
            if ($i ~ /^[0-9.]+$/ && i>=3) {
                $i = sprintf("%.2f", $i * r)
            }
        }
        print
    }' "$f" > "$OUTDIR/$base"
done

gnuplot <<EOF2
set terminal pngcairo size 1400,900 font "Helvetica,16"
set grid
set key inside top left
set output "plots/sensitivity_loss_inr.png"
set title "Attack Intensity vs Cumulative Cost (INR)"
set xlabel "Attack Intensity"
set ylabel "Cumulative Cost (INR)"
plot "$OUTDIR/sensitivity_matrix_elastic.csv" using 1:3 with lines lw 3 title "Elastic Agent (INR)"
EOF2
