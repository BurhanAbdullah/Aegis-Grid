set terminal pdfcairo enhanced font "Arial,12"
set output "../figures/figure_reconstruction.pdf"

set datafile separator ","

set title "All-or-Nothing Reconstruction vs Packet Loss"
set xlabel "Packet Loss Rate"
set ylabel "Reconstruction Probability"
set grid
set key top right

plot "../data/v2_reconstruction.csv" using 1:3 index 0 with linespoints lw 2 title "N=5", \
     "../data/v2_reconstruction.csv" using 1:3 index 1 with linespoints lw 2 title "N=10", \
     "../data/v2_reconstruction.csv" using 1:3 index 2 with linespoints lw 2 title "N=20"
set terminal pngcairo size 900,600 enhanced font "Arial,12"
set output "../figures/reconstruction_vs_loss.png"

set title "Reconstruction Probability vs Packet Loss"
set xlabel "Packet Loss Rate"
set ylabel "Reconstruction Probability"
set grid
set key top right

plot "../data/baseline_comparison.csv" using 1:2 with lines lw 2 title "Baseline", \
     "../data/v2_reconstruction.csv" using 1:2 with lines lw 2 title "Aegis-Grid"
