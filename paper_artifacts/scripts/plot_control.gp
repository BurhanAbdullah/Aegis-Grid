set terminal pdfcairo enhanced font "Arial,12"
set output "../figures/figure_control_stability.pdf"

set datafile separator ","

set title "Cyber-Physical Stability Under Attack"
set xlabel "Time"
set ylabel "Frequency Deviation (Hz)"
set grid
set key top right

plot "../data/v4_control_safety.csv" using 1:2 title "Baseline", \
     "../data/v4_control_safety.csv" using 1:3 title "Aegis-Grid"
