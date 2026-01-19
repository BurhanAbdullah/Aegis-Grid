set terminal jpeg size 1600,900 enhanced font "Helvetica,18"
set output "jpg/fog_of_war.jpg"

set grid
set key top left

set title "Fog-of-War Test: Decoy Entropy vs Agent Cost"
set xlabel "Time"
set ylabel "Computational Cost"

plot "results/attack_fog_of_war.dat" using 1:4 with lines lw 4 title "Agent Cost"
