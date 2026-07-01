import streamlit as st
import pandas as pd

# 1. CONFIGURACIÓN INICIAL DE LA PÁGINA (Obligatoria)
st.set_page_config(
    page_title="Dashboard Exergoeconómico CSP", 
    layout="wide", 
    initial_sidebar_state="expanded"
)

# Estilos CSS limpios para las tarjetas KPI de la parte superior
st.markdown("""
    <style>
    .kpi-card {
        background-color: #f8f9fa;
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #0056b3;
        box-shadow: 2px 2px 8px rgba(0,0,0,0.08);
        text-align: center;
        margin-bottom: 15px;
    }
    .kpi-title { font-size: 14px; color: #6c757d; font-weight: bold; text-transform: uppercase; }
    .kpi-value { font-size: 28px; color: #111; font-weight: bold; margin-top: 5px; }
    </style>
""", unsafe_allow_html=True)

# --- ENCABEZADO ---
st.title("☀️ Analizador Exergoeconómico Planta CSP Atacama")
st.markdown("#### Planta CSP Torre Central (50 MWe Nominal) | Datos Reales del Proyecto")
st.markdown("---")

# --- BARRA LATERAL: ENTRADA LIBRE DE VARIABLES ---
st.sidebar.header("🛠️ Parámetros Operacionales Libres")
st.sidebar.markdown("Escribe manualmente cualquier valor numérico para simular escenarios extremos fuera de diseño:")

# Controles libres con ingreso de teclado por el usuario
potencia_nominal = st.sidebar.number_input("Potencia Turbina Base [MW]:", min_value=1.0, max_value=500.0, value=52.63, step=1.0)
calor_hx2_base = st.sidebar.number_input("Aporte Térmico HX2 Base [MWt]:", min_value=1.0, max_value=1000.0, value=146.2, step=5.0)
costo_sales = st.sidebar.number_input("Costo Unitario de Sales [USD/kg]:", min_value=0.1, max_value=50.0, value=2.5, step=0.1)
horas_tes = st.sidebar.number_input("Autonomía del Almacenamiento [Horas]:", min_value=0.0, max_value=48.0, value=6.0, step=0.5)

st.sidebar.markdown("---")
condicion = st.sidebar.radio(
    "Factor de Escala por Irradiancia:",
    ["Diseño Nominal (DNI Alta)", "Operación Transitoria (DNI Media)", "Operación Nocturna (Solo TES)"]
)

tecnologia_tes = st.sidebar.selectbox(
    "Tecnología del Bloque TES:",
    ["Convencional (2 Tanques Sales)", "Latente (Lecho Empacado PB-LHTES)"]
)

# --- LÓGICA DE CÁLCULO DINÁMICA ---
if condicion == "Diseño Nominal (DNI Alta)":
    f_escala = 1.0
    txt_condicion = "Alta Irradiancia Directa"
elif condicion == "Operación Transitoria (DNI Media)":
    f_escala = 0.7
    txt_condicion = "Paso de Nubes / Tarde"
else:
    f_escala = 0.4
    txt_condicion = "Descarga de Energía Nocturna"

# Ajustes por tecnología TES
if tecnologia_tes == "Convencional (2 Tanques Sales)":
    lcoe_base = 84.5
    dest_tes = 4.2
    c_costo_base = 0.05  # Costo exergético base en USD/kWh de tu informe
else:
    lcoe_base = 76.2
    dest_tes = 2.1
    c_costo_base = 0.045

# Ecuaciones adaptativas basadas en tus entradas libres
potencia_mwe = potencia_nominal * f_escala
calor_hx2 = calor_hx2_base * f_escala
factor_planta = min(35.0 + (horas_tes * 4.3) * f_escala, 98.0)
lcoe_final = lcoe_base + (costo_sales - 2.5) * 2.2 + (horas_tes * 0.75) - (f_escala * 9.0)

# --- VISUALIZACIÓN DE TARJETAS KPI ---
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.markdown(f"<div class='kpi-card'><div class='kpi-title'>Potencia Eléctrica</div><div class='kpi-value'>{potencia_mwe:.2f} MW</div></div>", unsafe_allow_html=True)
with col2:
    st.markdown(f"<div class='kpi-card'><div class='kpi-title'>Aporte Térmico HX2</div><div class='kpi-value'>{calor_hx2:.1f} MWt</div></div>", unsafe_allow_html=True)
with col3:
    st.markdown(f"<div class='kpi-card'><div class='kpi-title'>Factor de Planta</div><div class='kpi-value'>{factor_planta:.1f} %</div></div>", unsafe_allow_html=True)
with col4:
    st.markdown(f"<div class='kpi-card'><div class='kpi-title'>LCOE Estimado</div><div class='kpi-value'>${lcoe_final:.2f} /MWh</div></div>", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# --- BLOQUE CENTRAL: TRES GRÁFICOS E INDICADORES ---
col_izq, col_der = st.columns(2)

with col_izq:
    st.subheader("💥 Destrucción de Exergía por Componente")
    st.markdown("Pérdidas termodinámicas reales ($EX_{fuel} - EX_{producto}$):")
    
    v_campo = 35.8 * f_escala
    v_hx2 = 20.84 * (calor_hx2 / 146.2) # Escalado proporcional libre
    v_turbina = 29.21 * (potencia_mwe / 52.63)
    v_condensador = 13.44 * f_escala
    v_tes = dest_tes
    total_ex = v_campo + v_hx2 + v_turbina + v_condensador + v_tes
    
    st.write(f"**Campo Helióstatos & Receptor:** {v_campo:.1f} MW")
    st.progress(min(v_campo / 100.0, 1.0))
    
    st.write(f"**Intercambiador HX2 (Gen. Vapor):** {v_hx2:.1f} MW")
    st.progress(min(v_hx2 / 100.0, 1.0))
    
    st.write(f"**Turbina de Vapor T1:** {v_turbina:.1f} MW")
    st.progress(min(v_turbina / 100.0, 1.0))
    
    st.write(f"**Condensador HX3:** {v_condensador:.1f} MW")
    st.progress(min(v_condensador / 100.0, 1.0))
    
    st.write(f"**Sistema de Almacenamiento TES:** {v_tes:.1f} MW")
    st.progress(min(v_tes / 100.0, 1.0))
    
    st.info(f"**Exergía Total Destruida en la Planta:** {total_ex:.1f} MW")

with col_der:
    st.subheader("📉 Matriz de Sensibilidad de Costos (LCOE vs TES)")
    st.markdown("Comportamiento proyectado del LCOE según las horas ingresadas:")
    
    horas_muestras = [4, 6, 8, 10, 12, 14]
    lista_horas, lista_estados, lista_lcoe = [], [], []
    
    for h in horas_muestras:
        lcoe_item = lcoe_base + (costo_sales - 2.5) * 2.2 + (h * 0.75) - (f_escala * 9.0)
        estado = "⭐ ACTUAL" if h == horas_tes else "Simulado"
        lista_horas.append(f"{h} horas")
        lista_estados.append(estado)
        lista_lcoe.append(f"${lcoe_item:.2f} USD/MWh")
    
    df_sensibilidad = pd.DataFrame({
        "Capacidad Almacenamiento": lista_horas,
        "Estado del Punto": lista_estados,
        "LCOE Proyectado": lista_lcoe
    })
    st.dataframe(df_sensibilidad, use_container_width=True, hide_index=True)

# --- NUEVA SECCIÓN GRÁFICA: COSTO ECONÓMICO DE LA DESTRUCCIÓN ---
st.markdown("---")
st.subheader("💰 GRÁFICO LIBRE: Costo Monetario de la Destrucción de Exergía ($C_{dest}$ en USD/h)")
st.markdown("Muestra cuánto dinero se está perdiendo por hora en los equipos debido a las irreversibilidades operacionales:")

# Valores económicos calculados en tu informe Parte 2 escalados dinámicamente
c_dest_hx2 = 1042.0 * (v_hx2 / 20.84) * (costo_sales / 2.5)
c_dest_turbina = 1460.5 * (v_turbina / 29.21)
c_dest_condensador = 472.0 * f_escala
c_dest_tes = dest_tes * 1000 * c_costo_base

total_dinero_perdido = c_dest_hx2 + c_dest_turbina + c_dest_condensador + c_dest_tes

col_g1, col_g2 = st.columns([2, 1])

with col_g1:
    # Gráfico de barras de costos nativo usando st.progress relativos al peor componente
    max_costo = max(c_dest_hx2, c_dest_turbina, c_dest_condensador, c_dest_tes, 1.0)
    
    st.write(f"**Pérdidas en Turbina de Vapor T1:** ${c_dest_turbina:.2f} USD/h")
    st.progress(c_dest_turbina / max_costo)
    
    st.write(f"**Pérdidas en Generador de Vapor HX2:** ${c_dest_hx2:.2f} USD/h")
    st.progress(c_dest_hx2 / max_costo)
    
    st.write(f"**Pérdidas en Condensador HX3:** ${c_dest_condensador:.2f} USD/h")
    st.progress(c_dest_condensador / max_costo)
    
    st.write(f"**Pérdidas en Sistema de Almacenamiento TES:** ${c_dest_tes:.2f} USD/h")
    st.progress(c_dest_tes / max_costo)

with col_g2:
    st.metric(
        label="COSTO TOTAL POR IRREVERSIBILIDADES", 
        value=f"${total_dinero_perdido:.2f} USD/h",
        delta=f"Costo Sales: {costo_sales} USD/kg",
        delta_color="normal"
    )
    st.markdown("""
    **Interpretación para la defensa:** La Turbina de Vapor y el Intercambiador $HX_2$ representan las mayores pérdidas monetarias del ciclo térmico. Ajustando el costo de las sales o la escala de la turbina se visualiza el impacto inmediato en la penalización económica horaria.
    """)

# --- CONCLUSIONES DIDÁCTICAS ---
st.markdown("---")
st.subheader("💡 Conclusiones")
col_c1, col_c2 = st.columns(2)
with col_c1:
    st.markdown(f"""
    * **Análisis Térmico Activo:** En el estado de **{condicion}** operando bajo la modalidad de *{txt_condicion}*, la destrucción de exergía del bloque receptor-campo equivale al **{ (v_campo/total_ex)*100:.1f}%** del total de las irreversibilidades de la planta.
    """)
with col_c2:
    st.markdown(f"""
    * **Optimización Económica:** Configurando el sistema con **{tecnologia_tes}** y una autonomía de **{horas_tes} horas**, la planta logra un factor de planta de **{factor_planta:.1f}%**, equilibrando el costo total por MWh generado a un valor competitivo de **${lcoe_final:.2f} USD/MWh**.
    """)
