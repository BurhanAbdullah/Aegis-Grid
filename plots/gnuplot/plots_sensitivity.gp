set terminal pngcairo size 1200,700 font "Helvetica,14"
set output "results/sensitivity_loss.png"

set datafile separator ","
set key top left
set grid

set title "Attack Intensity vs Cumulative Loss"
set xlabel "Attack Intensity"
set ylabel "Cumulative Loss"

plot "results/sensitivity_matrix.csv" \
     every ::1 using 1:2 with linespoints lw 3 pt 7 title "Elastic Agent"
