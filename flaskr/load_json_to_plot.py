import plotly.subplots as sp
import plotly.graph_objects as go
import plotly.express as px
import plotly.io as pio
from math import sqrt
import json
import pandas as pd
pd.options.plotting.backend = "plotly"
pio.templates.default = "ggplot2"

import flaskr.acid as acd

global acid_list
acid_list = []

def load_data_json(filename):
    with open(filename, "r") as read_file:
        data = json.load(read_file)
    for acid in data["acids"]:
        acid_list.append(acd.Acid(acid["name"], acid["symbol"], acid["type"], acid["Ka1"], acid["Ka2"], acid["Ka3"], 
                                acid["mass"], acid["density_eq_cp"], acid["density_eq_cm"], acid["maximum concentration"]))
        
def create_plot(acid):

    if True:
        A = 1.5   # m^2 - stała powierzchnia podstawy
        B = 0.035   # m^(5/2)/s - współczynnik wypływu

        Tp = 0.1   # s - czas próbkowania
        t_sim = 1000   # s - czas symulacji
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

    
    # data = {"Poziom kwasu": h}
    # df = pd.DataFrame(data, index=t)
    # fig1 = px.line(df, labels={"index":"t[s]", "value":"h[m]", "variable":"Funkcja"}, title="Wysokość", width=1050, height=450)

    # data = {"Nateżenie kwasu": Qd_acid,
    #         "Natężenie zakłócenia": Qd_pollutant,
    #         "Natężenie odpływu": Qo}
    # df = pd.DataFrame(data, index=t)
    
    # fig2 = px.line(df, labels={"index":"t[s]", "value":"Q[m³/s]", "variable":"Funkcja"}, title="Natężenie dopływu i odpływu")

    # data = {"Napięcie regulatora" : u_pi,
    #         "Napięcie aktualne": u}
    # df = pd.DataFrame(data, index=t)
    # fig3 = px.line(df, labels={"index":"t[s]", "value":"I[V]", "variable":"Funkcja"}, title="Napięcie")

    # data = {"Początkowe pH" : pH,
    #         "Docelowe pH": pH_doc}
    # df = pd.DataFrame(data, index=t)
    # fig4 = px.line(df, labels={"index":"t[s]", "value":"pH", "variable":"Funkcja"}, title="pH")

    # Create subplots
    fig = sp.make_subplots(rows=2, cols=2, subplot_titles=["Wysokość", "Natężenie dopływu i odpływu", "Napięcie", "pH"])

    # Add traces to each subplot
    fig.add_trace(go.Scatter(x=t, y=h, mode='lines', name='Poziom kwasu'), row=1, col=1)
    fig.add_trace(go.Scatter(x=t, y=Qd_acid, mode='lines', name='Nateżenie kwasu'), row=1, col=2)
    fig.add_trace(go.Scatter(x=t, y=Qd_pollutant, mode='lines', name='Natężenie zakłócenia'), row=1, col=2)
    fig.add_trace(go.Scatter(x=t, y=Qo, mode='lines', name='Natężenie odpływu'), row=1, col=2)
    fig.add_trace(go.Scatter(x=t, y=u_pi, mode='lines', name='Napięcie regulatora'), row=2, col=1)
    fig.add_trace(go.Scatter(x=t, y=u, mode='lines', name='Napięcie aktualne'), row=2, col=1)
    fig.add_trace(go.Scatter(x=t, y=pH, mode='lines', name='Początkowe pH'), row=2, col=2)
    fig.add_trace(go.Scatter(x=t, y=pH_doc_list, mode='lines', name='Docelowe pH'), row=2, col=2)

    # Update layout
    fig.update_layout(width=1230, height=920)


    return fig
