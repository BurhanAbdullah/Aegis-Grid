set terminal pngcairo size 1200,700 font "Helvetica,14"
set output "results/sensitivity_status.png"

set datafile separator ","
set grid
set key off

set title "System Outcome vs Attack Intensity"
set xlabel "Attack Intensity"
set ylabel "System State"

set ytics ("Operational" 0, "Locked Down" 1)

plot "results/sensitivity_matrix.csv" \
     every ::1 using 1:(stringcolumn(4) eq "LOCKED_DOWN" ? 1 : 0) \
     with points pt 7 ps 1.8 lc rgb "red"
