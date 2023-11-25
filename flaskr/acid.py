from math import sqrt, log10
from numpy import roots


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
            return(cH*cH*cH*cH + Ka1*cH*cH*cH + Ka1*Ka2*cH*cH + Ka1*Ka2*Ka3*cH)/(Ka1*cH*cH + 2*Ka1*Ka2*cH + 3*Ka1*Ka2*Ka3)
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