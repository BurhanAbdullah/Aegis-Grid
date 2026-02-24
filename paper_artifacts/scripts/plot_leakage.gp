set terminal pdfcairo enhanced font "Arial,12"
set output "../figures/figure_information_leakage.pdf"

set datafile separator ","

set title "Information Leakage Under Partial Observation"
set xlabel "Observed Fragments"
set ylabel "Mutual Information I(M;F')"
set grid
set key off

plot "../data/v3_information_leakage.csv" using 1:2 with lines lw 2
