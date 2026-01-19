set terminal pngcairo size 1200,700 font "Helvetica,14"
set output "results/fog_of_war.png"

set grid
set key top left

set title "Fog-of-War Test: Decoy Entropy vs Agent Cost"
set xlabel "Time"
set ylabel "Computational Cost"

plot "results/attack_fog_of_war.dat" using 1:4 with lines lw 3 title "Agent Cost"
