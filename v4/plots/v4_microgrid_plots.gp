set terminal pngcairo size 1200,800
set grid
set key outside

set output "v4/plots/frequency.png"
set title "Frequency Degradation Over Time"
set xlabel "Time"
set ylabel "Frequency (Hz)"
plot "v4/data/v4_compare.dat" using 1:4 with lines title "Control Room", \
     "v4/data/v4_compare.dat" using 1:7 with lines title "Substation"

set output "v4/plots/voltage.png"
set title "Voltage Degradation Over Time"
set ylabel "Voltage (pu)"
plot "v4/data/v4_compare.dat" using 1:5 with lines title "Control Room", \
     "v4/data/v4_compare.dat" using 1:8 with lines title "Substation"

set output "v4/plots/stability.png"
set title "Stability Index Over Time"
set ylabel "Stability"
plot "v4/data/v4_compare.dat" using 1:6 with lines title "Control Room", \
     "v4/data/v4_compare.dat" using 1:9 with lines title "Substation"
