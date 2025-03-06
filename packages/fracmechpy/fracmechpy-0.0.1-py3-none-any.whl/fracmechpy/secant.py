import numpy as np

def Secant(N, af, ab, W, p_max, p_min, B):
    dP = p_max - p_min
    a_ave = (af + ab) / 2
    a1 = np.insert(a_ave, 0, 0)
    a2 = np.insert(a_ave, a_ave.shape, 0)
    da = np.abs(a2 - a1)[1:-1]  

    N1 = np.insert(N, 0, 0)
    N2 = np.insert(N, N.shape, 0)
    dN = np.abs(N2 - N1)[1:-1]  

    dadN = da / dN  
    alpha = np.zeros(len(dadN))
    dK = np.zeros(len(dadN))

    for i in range(len(dadN)):  
        alpha[i] = a_ave[i] / W
        dK[i] = ((((dP / (B * np.sqrt(W))) * ((2 + alpha[i])))) /
                 ((1 - alpha[i]) ** (3 / 2))) * (0.886 + 4.64 * alpha[i] - 
                 13.32 * alpha[i] ** 2 + 14.72 * alpha[i] ** 3 - 5.6 * alpha[i] ** 4)

    
    for i in range(len(dadN)):  
        alpha_val = a_ave[i] / W
        if 0.25 <= alpha_val <= 0.4 and da[i] > 0.04 * W:
            print(f"Error: da[{i}] ({da[i]}) exceeds 0.04*W ({0.04 * W})")
            return None, None
        elif 0.4 < alpha_val <= 0.6 and da[i] > 0.02 * W:
            print(f"Error: da[{i}] ({da[i]}) exceeds 0.02*W ({0.02 * W})")
            return None, None
        elif alpha_val > 0.6 and da[i] > 0.01 * W:
            print(f"Error: da[{i}] ({da[i]}) exceeds 0.01*W ({0.01 * W})")
            return None, None

    return dadN, dK
