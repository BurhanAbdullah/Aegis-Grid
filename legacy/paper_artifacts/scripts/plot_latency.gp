set terminal pdfcairo enhanced font "Arial,12"
set output "../figures/figure_latency.pdf"

set datafile separator ","

set title "End-to-End Latency Comparison"
set xlabel "Scenario"
set ylabel "Latency (ms)"
set grid
set key top right

set style data linespoints

plot "../data/v3_latency_comparison.csv" using 1:2 title "Baseline", \
     "../data/v3_latency_comparison.csv" using 1:3 title "Aegis-Grid", \
     50 title "50 ms Constraint"
