import streamlit as st
import pandas as pd
import base64
import os
from logic import ejecutar_configuracion, ipSelect, get_processed_values, process_logic
import time



flagRegistro = False
usuario = ""
password = ""
    
def get_image_base64(image_path):
    with open(image_path, "rb") as img_file:
        b64_string = base64.b64encode(img_file.read()).decode()
    return f"data:image/png;base64,{b64_string}"

def show_loading_overlay(placeholder, image_url):

    code = f"""
    <style>
    .loading-overlay {{
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background-color: rgba(0,0,0,0.4);
        z-index: 9999;
        display: flex;
        align-items: center;
        justify-content: center;
    }}
    .loading-overlay img {{
        width: 250px;
        opacity: 0.8;
    }}
    </style>
    <div class="loading-overlay">
        <img src="{image_url}" alt="">
    </div>
    """
    placeholder.markdown(code, unsafe_allow_html=True)


def buscarDB(host):
    db_result = ipSelect(host)
    st.session_state["db_result"] = db_result
    st.session_state["mostrar_db_result"] = True
    wasFound = isinstance(db_result, dict)
    return db_result, wasFound

def render_interface():

    st.set_page_config(page_title="Liberty Networks - SYSRISE", layout="wide")
    script_dir = os.path.dirname(os.path.abspath(__file__))
    image_path = os.path.join(script_dir, "LN.png")
    image_base64 = get_image_base64(image_path)

    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600&family=Open+Sans:wght@400;600&display=swap');

 
        body {
            background-color: #FFF9F4;
            font-family: 'Open Sans', sans-serif;
            font-size: 16px;
        }
        
        [data-testid="stSidebar"] {
            background-color: #FFE5CC;
            color: #333333;
            font-family: 'Open Sans', sans-serif;
            font-size: 15px;
        }
        [data-testid="stSidebar"] * {
            color: #333333 !important;
        }
        div[data-testid="stSelectbox"] label,
        div[data-testid="stTextInput"] label,
        div[data-testid="stMultiSelect"] label {
            font-family: 'Poppins', sans-serif !important;
            font-size: 1.2rem !important;
            text-align: center;
            display: block;
        }
     
        div.stButton > button {
            background: linear-gradient(135deg, #FF8A00 0%, #FFA94D 100%);
            color: #fff;
            border-radius: 6px;
            border: 1px solid #c76d00;
            transition: 0.3s;
            font-family: 'Open Sans', sans-serif;
        }
        div.stButton > button:hover {
            background: linear-gradient(135deg, #FFA94D 0%, #FF8A00 100%);
            border-color: #c76d00;
        }
       
        .dispositivo-section {
            background: linear-gradient(135deg, #FFE5CC, #FFCEAB);
            color: #333;
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 20px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }
        .dispositivo-section h2 {
            font-family: 'Poppins', sans-serif;
            font-size: 1.3rem;
            margin-top: 0;
            text-align: center;
            margin-bottom: 15px;
            color: #333;
        }
     
        .resultado-section {
            background: linear-gradient(135deg, #FFE5CC, #FFC8A0);
            color: #333;
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 20px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }
        .resultado-section h2 {
            font-family: 'Poppins', sans-serif;
            font-size: 1.3rem;
            margin-top: 0;
            text-align: center;
            margin-bottom: 15px;
            color: #333;
        }
     
        .shell-container {
            background-color: #2f2f2f;
            color: #fddfba;
            font-family: 'Courier New', monospace;
            padding: 10px;
            border-radius: 8px;
            border: 2px solid #FF8A00;
            box-shadow: 0px 0px 15px rgba(255, 138, 0, 0.3);
            height: 380px;
            overflow-y: auto;
            margin-top: 15px;
            display: flex;
            flex-direction: column;
            position: relative;
        }
        .copy-btn {
            position: absolute;
            top: 10px;
            right: 10px;
            background-color: #FF8A00;
            color: #fff;
            border: none;
            padding: 5px 10px;
            border-radius: 5px;
            cursor: pointer;
            font-size: 0.9rem;
            transition: 0.3s;
            font-family: 'Open Sans', sans-serif;
        }
        .copy-btn:hover {
            background-color: #ffa533;
        }
       
        .ejecutar-btn {
            /* Este botón se posiciona con un contenedor nativo de Streamlit */
            background: linear-gradient(135deg, #FF8A00, #FFA94D);
            color: #fff;
            border-radius: 6px;
            border: 1px solid #c76d00;
            padding: 5px 10px;
            font-family: 'Open Sans', sans-serif;
            transition: 0.3s;
        }
        .ejecutar-btn:hover {
            background: linear-gradient(135deg, #FFA94D, #FF8A00);
            border-color: #c76d00;
        }
        .shell-log {
            flex-grow: 1;
            line-height: 1.3;
            white-space: pre-wrap;
        }
        .shell-log::after {
            content: "█";
            display: inline-block;
            margin-left: 5px;
            animation: blink 1s steps(2, start) infinite;
        }
        @keyframes blink {
            50% { opacity: 0; }
        }
        /* Inputs */
        div[data-testid="stTextInput"],
        div[data-testid="stSelectbox"],
        div[data-testid="stMultiSelect"] {
            border-radius: 6px;
            border: 1px solid #666;
            background-color: #ffffff;
            font-family: 'Open Sans', sans-serif;
            font-size: 14px;
        }
        /* Tabla */
        .table-container {
            margin-top: 10px;
            overflow-x: auto;
        }
        .custom-table {
            border-collapse: collapse;
            width: 100%;
            font-family: 'Open Sans', sans-serif;
            font-size: 0.9rem;
            background-color: #fff;
            color: #333;
        }
        .custom-table thead {
            background-color: #FFC8A0;
        }
        .custom-table th {
            color: #333;
            text-align: center;
            padding: 8px;
            text-transform: uppercase;
            border-bottom: 2px solid #ffb07a;
        }
        .custom-table td {
            border: 1px solid #ffd9c0;
            padding: 8px;
            text-align: center;
            white-space: normal;
            word-wrap: break-word;
        }
        .custom-table tr:nth-child(even) td {
            background-color: #FFF4EB;
        }
        .custom-table tr:hover td {
            background-color: #ffe8d0;
        }
        /* Sección Resultados */
        .result-config {
            font-family: 'Poppins', sans-serif;
            font-size: 1rem;
            line-height: 1.4;
            color: #333;
            background-color: #fff;
            padding: 10px;
            margin-top: 10px;
            margin-bottom: 0px;
            border-left: 5px solid #c76d00;
            border-radius: 3px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            text-shadow: 0 1px 0 rgba(255,255,255,0.7);
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

  
    st.markdown(
        """
        <h1 style="
            text-align: center;
            margin-top: -80px;
            margin-bottom: 0;
            font-family: 'Poppins', sans-serif;
            font-size: 2.2rem;
            font-weight: 700;
            background: linear-gradient(135deg, #FF8A00, #FFA94D);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            letter-spacing: 1px;
            text-shadow: 0 1px 0 rgba(0,0,0,0.1);
        ">
            Liberty Networks - Configuración de Dispositivos
        </h1>
        """,
        unsafe_allow_html=True
    )
    st.markdown("""<hr style="border:none;height:2px;background:#888; margin-top: -15px;">""", unsafe_allow_html=True)

    
    @st.dialog("Ingrese sus Credenciales")
    def ingresarCredenciales():
        global flagRegistro, usuario, password
        st.write(f"Usuario")
        usuario = st.text_input("Usuario", key = "userField", label_visibility="hidden")
        st.write(f"Contraseña")
        password = st.text_input("Contraseña", key="passwordField", type= "password", label_visibility="hidden")
        if st.button("Enviar"):
            if usuario == "" or password == "":
                st.error("Ingrese Usuario y Contraseña")
            else:
                flagRegistro = True
                st.rerun()

        
    with st.sidebar:
        st.image("LN3.png")
        st.markdown("""<hr style="border:none;height:1px;background:#ccc;">""", unsafe_allow_html=True)
        ios = st.selectbox("Seleccione IOS:", ["XE", "XR", "JUNIPER"])
        host = st.text_input("Ingrese dirección IP:")
        options = st.multiselect(
            "¿Qué desea configurar?",
            ["ISE", "Usuario Rancid", "Servidor Rancid", "Syslog", "Servidor Syslog"],
            placeholder="Seleccione"
        )
        if st.button("Revisar Configuración"):
            if host and options:
                overlay_placeholder = st.empty()
                show_loading_overlay(overlay_placeholder, image_base64)
                general_output, cli_output = ejecutar_configuracion(ios, host, options)
                overlay_placeholder.empty()
                st.session_state["resultado"] = general_output
                st.session_state["shell_log"] = cli_output
                st.session_state["mostrar_resultado"] = True
                processed_data = get_processed_values()
                flagDB=False
                db_result_aux, wasFound = buscarDB(host)
                st.session_state["db_result"] = processed_data
                st.session_state["mostrar_db_result"] = True
                st.markdown("""
                    <script>
                    document.getElementById("scroll-target").scrollIntoView({ behavior: "smooth" });
                    </script>
                    """, unsafe_allow_html=True)
                
            else:
                st.error("Por favor, ingrese la dirección IP y seleccione al menos una opción.")
        if st.button("Buscar en Base de Datos"):
            flagDB = True
            db_result, wasFound = buscarDB(host)
            

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        <div class="dispositivo-section">
            <h2>Resultado Base de Datos</h2>
        </div>
        """, unsafe_allow_html=True)
        if st.session_state.get("mostrar_db_result"):
            db_result = st.session_state["db_result"]
            if db_result and isinstance(db_result, dict):
                if flagDB == True:
                    st.success("Equipo registrado en la DB")
                else:
                    if wasFound == True:
                        st.warning("El equipo se actualizará en la DB con a siguiente información")  
                    else:
                        st.warning("El equipo se regitrará en la DB con la siguiente información")
                df = pd.DataFrame([db_result])
                df = df[["CIUDAD", "NODO", "hostname", "IP_DCN", "Vendor", "OS_TYPE", "Modelo"]]
                df_html = df.to_html(classes="custom-table", index=False)
                st.markdown(
                    f"""
                    <div class="table-container">
                        {df_html}
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.warning("No se encontraron resultados en la base de datos.")
    with col2:
        st.markdown("""
        <div class="resultado-section">
            <h2>Información del Equipo</h2>
        </div>
        """, unsafe_allow_html=True)
        if st.session_state.get("mostrar_resultado"):
            st.markdown(
                f"""<div class="result-config">{st.session_state["resultado"]}</div>""",
                unsafe_allow_html=True)
    
    if "shell_log" not in st.session_state:
        st.session_state["shell_log"] = ""
    shell_log = st.session_state["shell_log"]
    with st.expander("Consola de Ejecución", expanded=bool(shell_log)):
        st.markdown("Hadasda")
        st.markdown(f"""
        <div class="shell-container">
            <button class="copy-btn" onclick="copyConsole()">Copiar</button>
            <div class="shell-log" id="shell-log-text">{shell_log}</div>
        </div>
        <script>
        function copyConsole() {{
            var range = document.createRange();
            var consoleText = document.getElementById('shell-log-text');
            range.selectNode(consoleText);
            var selection = window.getSelection();
            selection.removeAllRanges();
            selection.addRange(range);
            document.execCommand('copy');
            selection.removeAllRanges();
            alert('¡Contenido de la consola copiado al portapapeles!');
        }}
        </script>
        """, unsafe_allow_html=True)
      
        col_shell1, col_shell2 = st.columns([1.3, 0.1])
        with col_shell2:
            if st.button("Ejecutar",key="execute_button"):
                process_logic()
                

 
    st.markdown("<div id='scroll-target'></div>", unsafe_allow_html=True)
    
    if flagRegistro == False:
        ingresarCredenciales()
        print(usuario)
        
        
    #if usuario == "" or password == "":
    #    time.sleep(20)
    #    st.rerun()
        