set terminal pdfcairo enhanced font "Arial,12"
set output "../figures/figure_entropy.pdf"

set datafile separator ","

set title "Traffic Entropy Convergence"
set xlabel "Observation Window"
set ylabel "Shannon Entropy"
set grid
set key off

plot "../data/v3_traffic_entropy.csv" using 1:2 with lines lw 2
