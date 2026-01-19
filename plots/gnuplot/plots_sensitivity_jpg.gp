set terminal jpeg size 1600,900 enhanced font "Helvetica,18"
set output "jpg/sensitivity_loss.jpg"

set datafile separator ","
set grid
set key top left

set title "Attack Intensity vs Cumulative Loss"
set xlabel "Attack Intensity"
set ylabel "Cumulative Loss"

plot "results/sensitivity_matrix.csv" \
     every ::1 using 1:2 with linespoints lw 4 pt 7 title "Elastic Agent"
