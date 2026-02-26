set terminal pdfcairo enhanced font "Arial,12"
set output "../figures/figure_system_comparison.pdf"

set datafile separator ","
set style data histograms
set style fill solid border -1
set boxwidth 0.8

set title "System-Level Security Comparison"
set ylabel "Normalized Score"
set xtics rotate by -30

plot "../data/baseline_comparison.csv" using 2:xtic(1) title "LatencyFeasible", \
     "" using 3 title "PartialReconstructionRisk", \
     "" using 4 title "TrafficLeakage", \
     "" using 5 title "FailSecure"
