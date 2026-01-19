set terminal jpeg size 1600,900 enhanced font "Helvetica,18"
set output "jpg/sensitivity_status.jpg"

set datafile separator ","
set grid
set key off

set title "System Outcome vs Attack Intensity"
set xlabel "Attack Intensity"
set ylabel "System State"
set ytics ("Operational" 0, "Locked Down" 1)

plot "results/sensitivity_matrix.csv" \
     every ::1 using 1:(stringcolumn(4) eq "LOCKED_DOWN" ? 1 : 0) \
     with points pt 7 ps 2 lc rgb "red"
