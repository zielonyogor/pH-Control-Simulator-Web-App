import plotly.subplots as sp
import plotly.graph_objects as go
import plotly.express as px
import plotly.io as pio
from math import sqrt, sin
import random
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
        
def create_plot(acid, cp, cp_level, cp_type, given_pH, control_system):

    A = 1.5   # m^2 - stała powierzchnia podstawy
    B = 0.035   # m^(5/2)/s - współczynnik wypływu

    Tp = 0.1   # s - czas próbkowania
    t_sim = 4000   # s - czas symulacji
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
    if control_system == 'pi':   # wybór systemu regulatora
        Td = 0.0
    else:
        Td = 1.0
    u_pid = [0.0]   # napięcie regulatora PI
    u = [0.0]   # napięcie aktualne
    u_min = 0.0   # napięcie minimalne
    u_max = 10.0   # napięcie maksymalne
    cd_acid = float(cp)  # stężenie kwasu
    
    # stężenie zanieczyszczenia
    if cp_level == 'mild':
        cp_level_variable = 4.5
    else:
        cp_level_variable = (acid.pH_max + acid.pH_min) / 2
    
    cd_pollutant = [acid.calculate_pH_to_cp(cp_level_variable)]
    cd_pollutant_max = acid.calculate_pH_to_cp(cp_level_variable - 0.25)
    cd_pollutant_min = acid.calculate_pH_to_cp(cp_level_variable + 0.25)
    step = cd_pollutant[-1] / 20

    c = [cd_pollutant[0]]  # stężenie startowe dałem jako stężenie zanieczyszczenia żeby nie było skoku na start, ale to też powinno być ustawiane jak wysokość startowa jest jakakolwiek
    pH = [acid.calculate_cp_to_pH(c[0])]    # pH startowe
    pH_doc = float(given_pH)    # pH docelowe
    pH_cp = [acid.calculate_cp_to_pH(cd_pollutant[-1])]
    c_doc = acid.calculate_pH_to_cp(pH_doc)     # stężenie docelowe
    e = [(c_doc - c[0])]     # uchył
    sum_e = [e[0]]      # suma uchyłów żeby za każdym razem w u_pid nie była liczona cała suma

    count = 0
    for _ in range(N):
        if abs(pH[-1] - pH_doc) < 0.04:
            count += 1
            if count > 4000 and round(t[-1], 0) == int(t[-1]) and int(t[-1]) % 200 == 0:
                break
        t.append(t[-1] + Tp)
        e.append((c_doc - c[-1]))
        sum_e.append(sum_e[-1] + e[-1])
        u_pid.append(k_p*(e[-1]+(Tp/Ti)*sum_e[-1]+(Td/Tp)*(e[-1]-e[-2])))
        u.append(max(u_min, min(u_max, u_pid[-1])))
        Qd_acid.append(((Qd_acid_max-Qd_acid_min)/(u_max - u_min))*(u[-1]- u_min) + Qd_acid_min)
        h.append(max(h_min, min(h_max, (Tp*(Qd_acid[-1] + Qd_pollutant[-1] - Qo[-1]))/A + h[-1])))
        
        if cp_type == 'rand':
            cd_pollutant.append(max(cd_pollutant_min, min(cd_pollutant_max, (random.uniform(cd_pollutant[-1] - step, cd_pollutant[-1] + step)))))
        elif cp_type == 'sin':
            cd_pollutant.append((acid.calculate_pH_to_cp(cp_level_variable + sin(t[-1] / 10) / 4)))
        else:
            cd_pollutant.append(cd_pollutant[-1])  

        pH_cp.append(acid.calculate_cp_to_pH(cd_pollutant[-1]))

        c.append(Tp*((Qd_acid[-1]*(cd_acid-c[-1]) + Qd_pollutant[-1]*(cd_pollutant[-1]-c[-1]))/(h[-1]*A))+c[-1])
        pH.append(acid.calculate_cp_to_pH(c[-1]))
        Qd_pollutant.append(Qd_pollutant[-1])   
        Qo.append(B*sqrt(h[-1]))

    pH_doc_list = [pH_doc for i in range(len(t))] 
    pH_cd = [acid.calculate_cp_to_pH(cd_acid) for i in range(len(t))]

    # Tworzenie wykresów

    fig1 = sp.make_subplots(rows=1, cols=1, subplot_titles=['Wykres zależności pH'])
    fig1.add_trace(go.Scatter(x=t, y=pH, mode='lines', name='pH aktualne'), row=1, col=1)
    fig1.add_trace(go.Scatter(x=t, y=pH_doc_list, mode='lines', name='pH docelowe'), row=1, col=1)
    fig1.add_trace(go.Scatter(x=t, y=pH_cd, mode='lines', name='pH dopływu sterowanego'), row=1, col=1)
    fig1.add_trace(go.Scatter(x=t, y=pH_cp, mode='lines', name='pH dopływu kwasu'), row=1, col=1)
    fig1.update_layout(title_font=dict(size=16, color='#F7F3E3'), width=950, height=700, paper_bgcolor="#1c7293", legend=dict(x=0.7, y=0.1, bgcolor='#F7F3E3'), showlegend=True)
    fig1.update_xaxes(color='#F7F3E3', tickcolor='#F7F3E3', tickformat='.0f', title_text='t[s]')
    fig1.update_yaxes(color='#F7F3E3', tickcolor='#F7F3E3', title_text='pH[-]')
    fig1.update_traces(marker=dict(size=1))
    fig1.update_annotations(font=dict(color='#F7F3E3', size=24))

    fig2 = sp.make_subplots(rows=1, cols=1, subplot_titles=['Wykres natężenia dopływów oraz odpływu'])
    fig2.add_trace(go.Scatter(x=t, y=Qd_acid, mode='lines', name='nateżenie dopływu kwasu'), row=1, col=1)
    fig2.add_trace(go.Scatter(x=t, y=Qd_pollutant, mode='lines', name='natężenie dopływu zakłócenia'), row=1, col=1)
    fig2.add_trace(go.Scatter(x=t, y=Qo, mode='lines', name='natężenie odpływu'), row=1, col=1)
    fig2.update_layout(title_font=dict(size=16, color='#F7F3E3'), width=950, height=700, paper_bgcolor="#1c7293", legend=dict(x=0.65, y=0.1, bgcolor='#F7F3E3'), showlegend=True)
    fig2.update_xaxes(color='#F7F3E3', tickcolor='#F7F3E3', tickformat='.0f', title_text='t[s]')
    fig2.update_yaxes(color='#F7F3E3', tickcolor='#F7F3E3', title_text='Q[m³/s]')
    fig2.update_annotations(font=dict(color='#F7F3E3', size=24))
    
    fig3 = sp.make_subplots(rows=1, cols=1, subplot_titles=['Wykres zależności napięć'])
    fig3.add_trace(go.Scatter(x=t, y=u_pid, mode='lines', name='napięcie regulatora'), row=1, col=1)
    fig3.add_trace(go.Scatter(x=t, y=u, mode='lines', name='napięcie aktualne pompy'), row=1, col=1)
    fig3.update_layout(title_font=dict(size=16, color='#F7F3E3'), width=950, height=700, paper_bgcolor="#1c7293", legend=dict(x=0.05, y=0.05, bgcolor='#F7F3E3'), showlegend=True)
    fig3.update_xaxes(color='#F7F3E3', tickcolor='#F7F3E3', tickformat='.0f', title_text='t[s]')
    fig3.update_yaxes(color='#F7F3E3', tickcolor='#F7F3E3', title_text='U[V]')
    fig3.update_annotations(font=dict(color='#F7F3E3', size=24))

    return [fig1, fig2, fig3]
