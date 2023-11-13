from math import sqrt, log10
from numpy import roots
import matplotlib.pyplot as plt



class Acid:
    def __init__(self, name, type, Ka1, Ka2, Ka3, mass, density, solubility):
        self.name = name
        self.type = type    # 1, 2 or 3 (number of H+)
        self.Ka1 = Ka1
        self.Ka2 = Ka2
        self.Ka3 = Ka3
        self.mass = mass    # molecular weight [g/mol]
        self.density = density  # [g/dm3]
        self.solubility = solubility    # [g/dm3]
        self.cp_max = solubility/(solubility + 1000)    # maximum concentration percentage 0-1
        self.cm_max = self.calculate_cp_to_cm(self.cp_max)  # maximum molar concentration [mol/dm3]
        self.pH_min = self.calculate_pH(self.cm_max)    # minimum pH (pH for maximum molar concentration)
        self.pH_max = 5     # maximum pH (because H+ << OH-)
        self.cm_min = self.calculate_cm(self.pH_max)    # minimum molar concentration (for maximum pH) [mol/dm3]
        self.cp_min = self.calculate_cp(self.cm_min)    # minimum concentration percentage (for maximum pH) 0-1
    def calculate_pH(self, c):
        match self.type:
            case 1:
                return self.calculate_pH1(c, self.Ka1)
            case 2:
                return self.calculate_pH2(c, self.Ka1, self.Ka2)
            case 3:
                return self.calculate_pH3(c, self.Ka1, self.Ka2, self.Ka3)     
    def calculate_pH1(self, c, *argv):
        Ka1 = argv[0]
        cH = (-Ka1+sqrt(Ka1*Ka1 + 4*c*Ka1))/2
        return -log10(cH)
    def calculate_pH2(self, c, *argv):
        Ka1 = argv[0]
        Ka2 = argv[1]
        solution_list = roots([1, Ka1, Ka1*Ka2-c*Ka1, -2*c*Ka1*Ka2])
        for solution in solution_list:
            if solution > 0:
                return -log10(solution)
    def calculate_pH3(self, c, *argv):
        Ka1 = argv[0]
        Ka2 = argv[1]
        Ka3 = argv[2]
        solution_list = roots([1, Ka1, Ka1*Ka2 - c*Ka1, Ka1*Ka2*Ka3 - 2*c*Ka1*Ka2, -3*c*Ka1*Ka2*Ka3])
        for solution in solution_list:
            if solution > 0:
                return -log10(solution)
    def calculate_cm(self, pH):
        match self.type:
            case 1:
                return self.calculate_cm1(pH, self.Ka1)
            case 2:
                return self.calculate_cm2(pH, self.Ka1, self.Ka2)
            case 3:
                return self.calculate_cm3(pH, self.Ka1, self.Ka2, self.Ka3)
    def calculate_cm1(self, pH, *args):
        Ka1 = args[0]
        cH = 10**(-pH)
        return (cH*cH + Ka1*cH)/Ka1
    def calculate_cm2(self, pH, *args):
        Ka1 = args[0]
        Ka2 = args[1]
        cH = 10**(-pH)
        return(cH*cH*cH + Ka1*cH*cH + Ka1*Ka2*cH)/(Ka1*cH + 2*Ka1*Ka2)
    def calculate_cm3(self, pH, *args):
        Ka1 = args[0]
        Ka2 = args[1]
        Ka3 = args[2]
        cH = 10**(-pH)
        return(cH*cH*cH*cH + Ka1*cH*cH*cH + Ka1*Ka2*cH*cH + Ka1*Ka2*Ka3*cH)/(Ka1*cH*cH + 2*Ka1*Ka2 + 3*Ka1*Ka2*Ka3)
    def calculate_cp(self, cm):
        ms = (self.density*cm*self.mass)/(self.density - cm*self.mass)
        return ms/(1000+ms)
    def calculate_cp_to_cm(self, cp):
        ms = (1000*cp)/(1-cp)
        return ms/(self.mass*(1+(ms/self.density)))
    def calculate_cp_to_pH(self, cp):
        return self.calculate_pH(self.calculate_cp_to_cm(cp))

H2SO3 = Acid("H2SO3",2, 1.4e-2, 6.3e-8, 0, 82.08, 1030, 558.5)
H2SO4 = Acid("H2SO4",2, 1000, 0.012, 0, 98.08, 1840, 1e5)

acid = H2SO3

A = 1.5   # m^2 - stała powierzchnia podstawy
B = 0.035   # m^(5/2)/s - współczynnik wypływu

Tp = 0.1   # s - czas próbkowania
t_sim = 10000   # s - czas symulacji
N = int(t_sim/Tp) + 1   # ilość testów
t  = [0.0]   # s - wektor czasu

Qd_acid_min = 0.0   # m^3/s - dopływ minimalny
Qd_acid_max = 0.05   # m^3/s - dopływ maksymalny

Qd_acid = [0.0]   # m^3/s - natężenie dopływu 
Qd_pollutant = [0.01]   # m^3/s - dopływ minimalny

h = [0.0]   # m - poziom cieczy w zbiorniku
h_min = 0.0   # m - poziom minimalny
h_max = 5.0   # m - poziom maksymalny

Qo = [B*sqrt(h[-1])]   # m^3/s - natężenie wypływu

k_p = 0.02   # wzmocnienie regulatora
Ti = 2.5   # czas zdwojenia
u_pi = [0.0]   # napięcie regulatora
u = [0.0]   # napięcie aktualne
u_min = 0.0   # napięcie minimalne
u_max = 10.0   # napięcie maksymalne



cd_acid = 0.3
cd_pollutant = [0.20]
pH_max = max(acid.calculate_cp_to_pH(cd_acid), acid.calculate_cp_to_pH(cd_pollutant[0]))
pH_min = min(acid.calculate_cp_to_pH(cd_acid), acid.calculate_cp_to_pH(cd_pollutant[0]))

c = [0.0]
pH = [acid.calculate_cp_to_pH(c[0])]
pH_doc = (pH_max + pH_min)/2
c_doc = acid.calculate_cp(acid.calculate_cm(pH_doc))

e = [abs(c_doc - c[0])]
sum_e = [e[0]]

for _ in range(N):
    t.append(t[-1] + Tp)
    e.append(abs(c_doc - c[-1]))
    sum_e.append(sum_e[-1] + e[-1])
    u_pi.append(k_p*(e[-1]+(Tp/Ti)*sum_e[-1]))
    u.append(max(u_min, min(u_max, u_pi[-1])))
    Qd_acid.append(((Qd_acid_max-Qd_acid_min)/(u_max - u_min))*(u[-1]- u_min) + Qd_acid_min)
    h.append(max(h_min, min(h_max, (Tp*(Qd_acid[-1] + Qd_pollutant[-1] - Qo[-1]))/A + h[-1])))
    cd_pollutant.append(cd_pollutant[-1])
    c.append(Tp*((Qd_acid[-1]*(cd_acid-c[-1]) + Qd_pollutant[-1]*(cd_pollutant[-1]-c[-1]))/(h[-1]*A))+c[-1])
    pH.append(acid.calculate_cp_to_pH(c[-1]))
    Qd_pollutant.append(Qd_pollutant[-1])
    Qo.append(B*sqrt(h[-1]))
# można sprawdzić przy jakiej wysokości się zatrzyma  - h = Q_d/B

# h_doc_list = [h_doc for i in range(len(t))]

pH_doc_list = [pH_doc for i in range(len(t))]
# print(len(t), len(h), len(h_doc_list), len(Q_d), len(Qo), len(u_pi), len(u))
fig = plt.figure()
gs = fig.add_gridspec(4, hspace=0.7)
axs = gs.subplots()
axs[0].plot(t, h)
axs[1].plot(t, Qd_acid)
axs[1].plot(t, Qd_pollutant)
axs[1].plot(t, Qo)
axs[2].plot(t, u_pi)
axs[2].plot(t, u)
axs[3].plot(t, pH)
axs[3].plot(t, pH_doc_list)
axs[0].legend(["h"])
axs[1].legend(["Qd_acid", "Qd_pollutant", "Qo"])
axs[2].legend(["u_pi", "u_n"])
axs[3].legend(["c", "c_doc"])
axs[0].set(xlabel='t [s]', ylabel='h [m]')
axs[1].set(xlabel='t [s]', ylabel='Q [m^3/s]')
axs[2].set(xlabel='t [s]', ylabel='u [V]')
axs[3].set(xlabel='t[s]', ylabel='c [%]')
plt.show(block=True)