from math import sqrt, log10
from numpy import roots
import json
import matplotlib.pyplot as plt



class Acid:
    def __init__(self, name, symbol, type, Ka1, Ka2, Ka3, mass, density_eq_cp, density_eq_cm, cp_max):
        self.name = name
        self.symbol = symbol
        self.type = type    # 1, 2 or 3 (number of H+)
        self.Ka1 = Ka1
        self.Ka2 = Ka2
        self.Ka3 = Ka3
        self.mass = mass    # molecular weight [g/mol]
        self.density_eq_cp = density_eq_cp  # [g/dm3]
        self.density_eq_cm = density_eq_cm # [g/dm3]
        self.cp_max = cp_max    # maximum concentration percentage 0-1
        # self.cm_max = self.calculate_cp_to_cm(self.cp_max)  # maximum molar concentration [mol/dm3]
        self.pH_min = self.calculate_cp_to_pH(self.cp_max)    # minimum pH (pH for maximum molar concentration)
        self.pH_max = 5     # maximum pH (because H+ << OH-)
        # self.cm_min = self.calculate_pH_to_cm(self.pH_max)    # minimum molar concentration (for maximum pH) [mol/dm3]
        self.cp_min = self.calculate_pH_to_cp(self.pH_max)    # minimum concentration percentage (for maximum pH) 0-1
    def calculate_cm_to_pH(self, c):
        def calculate_pH1(c, *argv):
            Ka1 = argv[0]
            cH = (-Ka1+sqrt(Ka1*Ka1 + 4*c*Ka1))/2
            return -log10(cH)
        def calculate_pH2(c, *argv):
            Ka1 = argv[0]
            Ka2 = argv[1]
            solution_list = roots([1, Ka1, Ka1*Ka2-c*Ka1, -2*c*Ka1*Ka2])
            for solution in solution_list:
                if solution > 0:
                    return -log10(solution)
        def calculate_pH3(c, *argv):
            Ka1 = argv[0]
            Ka2 = argv[1]
            Ka3 = argv[2]
            solution_list = roots([1, Ka1, Ka1*Ka2 - c*Ka1, Ka1*Ka2*Ka3 - 2*c*Ka1*Ka2, -3*c*Ka1*Ka2*Ka3])
            for solution in solution_list:
                if solution > 0:
                    return -log10(solution)
        match self.type:
            case 1:
                return calculate_pH1(c, self.Ka1)
            case 2:
                return calculate_pH2(c, self.Ka1, self.Ka2)
            case 3:
                return calculate_pH3(c, self.Ka1, self.Ka2, self.Ka3)
    def calculate_pH_to_cm(self, pH):
        def calculate_cm1(pH, *args):
            Ka1 = args[0]
            cH = 10**(-pH)
            return (cH*cH + Ka1*cH)/Ka1
        def calculate_cm2(pH, *args):
            Ka1 = args[0]
            Ka2 = args[1]
            cH = 10**(-pH)
            return(cH*cH*cH + Ka1*cH*cH + Ka1*Ka2*cH)/(Ka1*cH + 2*Ka1*Ka2)
        def calculate_cm3(pH, *args):
            Ka1 = args[0]
            Ka2 = args[1]
            Ka3 = args[2]
            cH = 10**(-pH)
            return(cH*cH*cH*cH + Ka1*cH*cH*cH + Ka1*Ka2*cH*cH + Ka1*Ka2*Ka3*cH)/(Ka1*cH*cH + 2*Ka1*Ka2 + 3*Ka1*Ka2*Ka3)
        match self.type:
            case 1:
                return calculate_cm1(pH, self.Ka1)
            case 2:
                return calculate_cm2(pH, self.Ka1, self.Ka2)
            case 3:
                return calculate_cm3(pH, self.Ka1, self.Ka2, self.Ka3)
    def calculate_cm_to_cp(self, cm):
        density = self.calculate_density_cm(cm)
        return (cm*self.mass)/(density*1000)
    def calculate_cp_to_cm(self, cp):
        density = self.calculate_density_cp(cp)
        return (cp*density*1000)/self.mass
    def calculate_cp_to_pH(self, cp):
        return self.calculate_cm_to_pH(self.calculate_cp_to_cm(cp))
    def calculate_pH_to_cp(self, pH):
        return self.calculate_cm_to_cp(self.calculate_pH_to_cm(pH))
    def calculate_density_cp(self, cp):
        density = 0
        count = 0
        for a in reversed(self.density_eq_cp):
            density += a*(cp**count)
            count += 1
        return density
    def calculate_density_cm(self, cm):
        density = 0
        count = 0
        for a in reversed(self.density_eq_cm):
            density += a*(cm**count)
            count += 1
        return density          

def load_data_json(filename):
    with open(filename, "r") as read_file:
        data = json.load(read_file)
    for acid in data["acids"]:
        acid_list.append(Acid(acid["name"], acid["symbol"], acid["type"], acid["Ka1"], acid["Ka2"], acid["Ka3"], 
                                acid["mass"], acid["density_eq_cp"], acid["density_eq_cm"], acid["maximum concentration"]))
        
def choose_acid():
    while True:
        print("Wybierz kwas")
        for i in range(len(acid_list)):
            print("({}) {} - {}".format(i+1, acid_list[i].name, acid_list[i].symbol))
        inp = input()
        try:
            inp = int(inp)
            if inp >= 1 and inp <= len(acid_list):
                return acid_list[inp-1]
            else:
                print("Zle dane")
        except ValueError:
            print("Zle dane")

global acid_list
acid_list = []
load_data_json("flaskr\\acids.json")

acid = None
acid = choose_acid()

A = 1.5   # m^2 - stała powierzchnia podstawy
B = 0.035   # m^(5/2)/s - współczynnik wypływu

Tp = 0.1   # s - czas próbkowania
t_sim = 100000   # s - czas symulacji
N = int(t_sim/Tp) + 1   # ilość testów
t  = [0.0]   # s - wektor czasu

Qd_acid_min = 0.0   # m^3/s - dopływ minimalny kwasu
Qd_acid_max = 0.05   # m^3/s - dopływ maksymalny kwasu

Qd_acid = [0.0]   # m^3/s - natężenie dopływu  kwasu
Qd_pollutant = [0.01]   # m^3/s - natężenie dopływu  zanieczyszczenia

h = [0.0]   # m - poziom cieczy w zbiorniku
h_min = 0.0   # m - poziom minimalny
h_max = 5.0   # m - poziom maksymalny

Qo = [B*sqrt(h[-1])]   # m^3/s - natężenie wypływu

k_p = 0.02   # wzmocnienie regulatora
Ti = 2.5   # czas zdwojenia
u_pi = [0.0]   # napięcie regulatora PI
u = [0.0]   # napięcie aktualne
u_min = 0.0   # napięcie minimalne
u_max = 10.0   # napięcie maksymalne

cd_acid_min = acid.cp_min   # minimalne stężenie kwasu
cd_acid_max = acid.cp_max   # maksymalne stężenie kwasu
cd_acid = 0.3   # stężenie kwasu
cd_pollutant = [0.20]   # stężenie zanieczyszczenia - trzeba dorobić to sinusoidalne, czy inne zmienianie się tej wartości do wyboru (na razie jest stałe)

pH_max = max(acid.calculate_cp_to_pH(cd_acid), acid.calculate_cp_to_pH(cd_pollutant[0]))
pH_min = min(acid.calculate_cp_to_pH(cd_acid), acid.calculate_cp_to_pH(cd_pollutant[0]))

c = [cd_pollutant[0]]  # stężenie startowe dałem jako stężenie zanieczyszczenia żeby nie było skoku na start, ale to też powinno być ustawiane jak wysokość startowa jest jakakolwiek
pH = [acid.calculate_cp_to_pH(c[0])]    # pH startowe
pH_doc = (pH_max + pH_min)/2    # pH docelowe - dałem na razie środek pomiędzy pH_max a pH_min żeby nie trzeba było myśleć tylko działało
c_doc = acid.calculate_pH_to_cp(pH_doc)     # stężenie docelowe
e = [abs(c_doc - c[0])]     # uchył
sum_e = [e[0]]      # suma uchyłów żeby za każdym razem w u_pi nie była liczona cała suma

for _ in range(N):
    t.append(t[-1] + Tp)
    e.append(abs(c_doc - c[-1]))
    sum_e.append(sum_e[-1] + e[-1])
    u_pi.append(k_p*(e[-1]+(Tp/Ti)*sum_e[-1]))  #musimy wybrać czy na pewno chcemy PI
    u.append(max(u_min, min(u_max, u_pi[-1])))
    Qd_acid.append(((Qd_acid_max-Qd_acid_min)/(u_max - u_min))*(u[-1]- u_min) + Qd_acid_min)
    h.append(max(h_min, min(h_max, (Tp*(Qd_acid[-1] + Qd_pollutant[-1] - Qo[-1]))/A + h[-1])))
    cd_pollutant.append(cd_pollutant[-1])   # jak wyżej pisałem że trzeba zaimplementować różne zmienianie tutaj
    c.append(Tp*((Qd_acid[-1]*(cd_acid-c[-1]) + Qd_pollutant[-1]*(cd_pollutant[-1]-c[-1]))/(h[-1]*A))+c[-1])
    pH.append(acid.calculate_cp_to_pH(c[-1]))
    Qd_pollutant.append(Qd_pollutant[-1])   # tu też można zrobić coś żeby to nie było stałe ale w sumie to nie chciał chyba
    Qo.append(B*sqrt(h[-1]))

pH_doc_list = [pH_doc for i in range(len(t))]
c_doc_list = [c_doc for i in range(len(t))]

fig = plt.figure()
gs = fig.add_gridspec(5, hspace=0.7)
axs = gs.subplots()
plt.title(str(acid.name))
axs[0].plot(t, h)
axs[1].plot(t, Qd_acid)
axs[1].plot(t, Qd_pollutant)
axs[1].plot(t, Qo)
axs[2].plot(t, u_pi)
axs[2].plot(t, u)
axs[3].plot(t, pH)
axs[3].plot(t, pH_doc_list)
axs[4].plot(t, c)
axs[4].plot(t, c_doc_list)
axs[0].legend(["h"])
axs[1].legend(["Qd_acid", "Qd_pollutant", "Qo"])
axs[2].legend(["u_pi", "u_n"])
axs[3].legend(["pH", "pH_doc"])
axs[4].legend(["c", "c_doc"])
axs[0].set(xlabel='t [s]', ylabel='h [m]')
axs[1].set(xlabel='t [s]', ylabel='Q [m^3/s]')
axs[2].set(xlabel='t [s]', ylabel='u [V]')
axs[3].set(xlabel='t[s]', ylabel='pH')
axs[4].set(xlabel='t[s]', ylabel='c [%]')
plt.show(block=True)