set terminal pdfcairo enhanced font "Arial,12"
set output "../figures/figure_adaptation.pdf"

set datafile separator ","

set title "Adaptive Security Parameter Tuning"
set xlabel "Attack Pressure"
set ylabel "Fragment Count"
set grid
set key off

plot "../data/v3_agent_adaptation.csv" using 1:2 with lines lw 2
