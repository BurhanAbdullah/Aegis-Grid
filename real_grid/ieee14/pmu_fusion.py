def consensus(measurements, tol_f=0.15, tol_v=0.03):
    freqs = [m["freq"] for m in measurements]
    volts = [m["voltage"] for m in measurements]

    f_ref = sum(freqs) / len(freqs)
    v_ref = sum(volts) / len(volts)

    for f, v in zip(freqs, volts):
        if abs(f - f_ref) > tol_f:
            return False
        if abs(v - v_ref) > tol_v:
            return False

    return True
