"""
    Librerías y Versiones Recomendadas:
      - streamlit==1.12.0        -> Para crear interfaces web interactivas.
      - pandas==1.3.3            -> Manipulación y visualización de datos (tablas, DataFrame).
      - base64 (incluida en Python estándar)
      - urllib (incluida en Python estándar)
      - paramiko==2.11.0         -> Conexiones SSH a dispositivos remotos.
      - mariadb==1.1.8           -> Conexión y manipulación de bases de datos MariaDB.
      - time, os, sys, json, re  -> Librerías estándar de Python.
      - streamlit.components.v1  -> Para la incrustación de componentes HTML.
    
    Funciones importadas desde el módulo "logic":
      - ejecutar_configuracion: Orquesta la configuración del dispositivo.
      - ipSelect: Consulta la base de datos para obtener información del dispositivo.
      - get_processed_values: Retorna los parámetros procesados del dispositivo.
      - insert_manual_data: Inserta manualmente datos en la base de datos.
      - ejec_funciones: Orquesta la ejecución de funciones de configuración.
    
    El código se encarga de renderizar una interfaz en Streamlit para:
      - Establecer variables de estado (session_state) y evitar reinicios al renderizar.
      - Mostrar diálogos para ingreso de credenciales, errores, ingreso manual de datos y notificación de configuración.
      - Buscar en la base de datos y ejecutar configuraciones en equipos.
      - Presentar resultados y logs de la ejecución en la interfaz.
    """
    
    import streamlit as st                # streamlit==1.12.0
    import pandas as pd                   # pandas==1.3.3
    import base64
    import os
    import urllib.request
    import streamlit.components.v1 as components
    from logic import ejecutar_configuracion, ipSelect, get_processed_values, insert_manual_data, ejec_funciones
    import time
    
    # =============================================================================
    # Inicialización de Variables en st.session_state
    # =============================================================================
    # Estas variables se usan para guardar el estado de la aplicación y evitar reinicios innecesarios al renderizar.
    
    if "flagDB" not in st.session_state:
        st.session_state["flagDB"] = False  # Activa cuando se utiliza la opción "Buscar en Base de Datos".
    if "wasFound" not in st.session_state:
        st.session_state["wasFound"] = False  # Indica si el equipo fue encontrado en la BD.
    if "mostrar_ise_dialog" not in st.session_state:
        st.session_state["mostrar_ise_dialog"] = False  # Controla la visualización del diálogo de ISE.
    if "flagRegistro" not in st.session_state:
        st.session_state["flagRegistro"] = False  # Se activa cuando el usuario ya ingresó sus credenciales.
    if "errorConexion" not in st.session_state:
        st.session_state["errorConexion"] = False  # Indica si ocurrió un error al conectar con el equipo.
    if "datos_manual" not in st.session_state:
        st.session_state["datos_manual"] = False  # Activa si no se encontró la ciudad o nodo y se requiere ingreso manual.
    
    # =============================================================================
    # Funciones de Utilidad
    # =============================================================================
    
    def normalize_db_result(result):
        """
        Normaliza los nombres de las claves del diccionario obtenido de la base de datos.
    
        Parámetros:
          result (dict): Resultado de la consulta a la BD.
    
        Retorna:
          dict: Diccionario con claves unificadas (ej. "CIUDAD", "NODO", etc.)
    
        Ejemplo:
          >>> normalize_db_result({"ciudad": "Bogota", "Nodo": "NODO1"})
          {'CIUDAD': 'Bogota', 'NODO': 'NODO1', 'Nodito': '', 'hostname': '', 'IP_DCN': '', 'Vendor': '', 'OS_TYPE': '', 'Modelo': '', 'vrf': '', 'mgmtInt': ''}
        """
        if not isinstance(result, dict):
            return result
        return {
            "CIUDAD": result.get("CIUDAD") or result.get("ciudad", ""),
            "NODO": result.get("NODO") or result.get("Nodo", ""),
            "Nodito": result.get("Nodito") or result.get("nodito", ""),
            "hostname": result.get("hostname", ""),
            "IP_DCN": result.get("IP_DCN") or result.get("ip_dcn", ""),
            "Vendor": result.get("Vendor") or result.get("ROL", ""),
            "OS_TYPE": result.get("OS_TYPE") or result.get("OS_type", ""),
            "Modelo": result.get("Modelo") or result.get("modelo", ""),
            "vrf": result.get("vrf", ""),
            "mgmtInt": result.get("mgmtInt", "")
        }
    
    def shorten_url(url):
        """
        Acorta una URL utilizando el servicio TinyURL.
    
        Parámetros:
          url (str): URL larga a acortar.
    
        Retorna:
          str: URL acortada o la URL original en caso de error.
        """
        try:
            api_url = "http://tinyurl.com/api-create.php?url=" + url
            with urllib.request.urlopen(api_url) as response:
                short_url = response.read().decode('utf-8')
            return short_url
        except Exception as e:
            st.error("Error acortando la URL: " + str(e))
            return url
    
    # =============================================================================
    # Diálogos con Streamlit
    # =============================================================================
    
    @st.dialog("Configuración ISE")
    def dialog_ise():
        """
        Muestra un diálogo para la configuración ISE.
    
        Descripción:
          - Presenta un enlace acortado para solicitar el ticket en OTS.
          - Muestra una tabla con la información del equipo a registrar.
          - Incluye un botón para copiar la tabla al portapapeles mediante JavaScript.
          - Permite cerrar el diálogo.
        """
        try:
            long_url = ("https://identity.lla.com/app/servicedesk/exk1s9tlsit5TGKwm1d8/sso/saml?"
                        "SAMLRequest=fZJLT8MwEIT%2FSuR76yRt%2BrDaSqUVUFGgooEDF%2BQmG7Bw7ODdUPj3mIRHkYDrer4Zz9oTlKWuxLymB3MFTzUgBS%2BlNiiagymrnRFWokJhZAkoKBPb%2BflaxN1QVM6SzaxmB8j%2FhEQER8oaFqyWU3aXDYfRYJT0d3I8CEMpiyIe9ZN4GA8glzDsgUyKUe4FPRbcgENPTpk38jhiDSuDJA35URgnnbDXieI0GouoJ5LwlgVL30YZSQ31QFSh4FzlYEjRa1dr2c1syWVVcX%2BrZ5VBDvjI4eUxwjFpVJSkJ2f7MspHHNHy93osmH9WWFiDdQlu27LXV%2BvvEEv45d9im49dHSmTK3P%2F%2F5p2rQjFaZpuOpvLbcpmk3cf0dR2s19yJvxQMGnf9cJbr5Ybq1X2GhxbV0r6OznqRs1E5Z2ikYraYAWZKhTkvrjWdr9wIAmmjFwNjM%2Fa0J%2F%2FZ%2FYG"
                        "&RelayState=https%3A%2F%2Fots.lla.com%2Fauth%2Flogin%2Ftype%2Fsaml%3Fnext%3D")
            short_url = shorten_url(long_url)
        
            st.write("Recuerde solicitar el ticket en OTS, para ello haga clic en el siguiente enlace:")
            st.write(short_url)
            st.write("")
            st.write("La información del equipo a registrar se muestra en la siguiente tabla:")
            if "db_result" in st.session_state and st.session_state["db_result"]:
                data = st.session_state["db_result"]
                df = pd.DataFrame([{
                    "Nodo": data.get("NODO", ""),
                    "Hostname": data.get("hostname", ""),
                    "IP": data.get("IP_DCN", ""),
                    "Vendor": data.get("Vendor", ""),
                    "Modelo": data.get("Modelo", "")
                }])
                html_table = df.to_html(index=False)
                html_code = f"""
                <div>
                    {html_table}
                    <button id="copy-btn" style="margin-top:10px;">Copiar Tabla</button>
                </div>
                <script>
                document.getElementById("copy-btn").addEventListener("click", function() {{
                    const dbResult = {st.session_state.db_result};
                    const simpleHTML = `
                    <div style="font-family: Arial; margin: 15px 0;">
                        <p style="margin-bottom: 10px; color: #333;">Buen día, solicito su colaboración para registrar el siguiente equipo en ISE:</p>
                        <table border="1" style="border-collapse: collapse; width: 100%; margin-bottom: 15px;">
                            <tr>
                                <th style="padding: 8px; background: #f2f2f2;">Nodo</th>
                                <th style="padding: 8px; background: #f2f2f2;">Hostname</th>
                                <th style="padding: 8px; background: #f2f2f2;">IP</th>
                                <th style="padding: 8px; background: #f2f2f2;">Vendor</th>
                                <th style="padding: 8px; background: #f2f2f2;">Modelo</th>
                            </tr>
                            <tr>
                                <td style="padding: 8px;">${{dbResult.NODO}}</td>
                                <td style="padding: 8px;">${{dbResult.hostname}}</td>
                                <td style="padding: 8px;">${{dbResult.IP_DCN}}</td>
                                <td style="padding: 8px;">${{dbResult.Vendor}}</td>
                                <td style="padding: 8px;">${{dbResult.Modelo}}</td>
                            </tr>
                        </table>
                        <p style="margin-top: 10px; color: #333;">Gracias.</p>
                    </div>`;
                    const plainText = `
                    Buen día, solicito su colaboración para registrar el siguiente equipo en ISE:
                    
                    Nodo: ${{dbResult.NODO}}
                    Hostname: ${{dbResult.hostname}}
                    IP: ${{dbResult.IP_DCN}}
                    Vendor: ${{dbResult.Vendor}}
                    Modelo: ${{dbResult.Modelo}}
                    
                    Gracias.`;
                    navigator.clipboard.write([
                        new ClipboardItem({{
                            "text/html": new Blob([simpleHTML], {{ type: "text/html" }}),
                            "text/plain": new Blob([plainText], {{ type: "text/plain" }})
                        }})
                    ]).catch(() => {{
                        const textarea = document.createElement("textarea");
                        textarea.value = plainText;
                        document.body.appendChild(textarea);
                        textarea.select();
                        document.execCommand("copy");
                        document.body.removeChild(textarea);
                    }});
                }});
                </script>
                """
                components.html(html_code, height=300)
            else:
                st.write("No hay datos disponibles para la tabla.")
        
            if st.button("Cerrar"):
                st.session_state["mostrar_ise_dialog"] = False
                st.rerun()
        except Exception as e:
            st.error("Error en el diálogo ISE: " + str(e))
    
    
    @st.dialog("Ingrese sus Credenciales")
    def ingresarCredenciales():
        """
        Diálogo para que el usuario ingrese sus credenciales.
    
        Descripción:
          - Muestra campos para ingresar usuario y contraseña.
          - Al pulsar "Enviar", valida que ambos campos estén completos.
          - Si son válidos, almacena las credenciales en st.session_state y activa la bandera flagRegistro.
          - Refresca la aplicación.
        """
        st.write("Nota: Las credenciales se usan para autenticarse y conectarse a los equipos")
        st.write("Usuario")
        user_input = st.text_input("Usuario", key="userField", label_visibility="hidden")
        st.write("Contraseña")
        password_input = st.text_input("Contraseña", key="passwordField", type="password", label_visibility="hidden")
        if st.button("Enviar"):
            if user_input == "" or password_input == "":
                st.error("Ingrese Usuario y Contraseña")
            else:
                st.session_state["usuario"] = user_input
                st.session_state["password"] = password_input
                st.session_state["flagRegistro"] = True
                st.rerun()
    
    
    @st.dialog("Error de Credenciales o Conectividad")
    def errorCredencialesDialog():
        """
        Diálogo que se muestra cuando las credenciales son incorrectas o falla la conexión.
    
        Descripción:
          - Muestra un mensaje de error.
          - Permite reiniciar el ingreso de credenciales.
        """
        st.error("Revise sus credenciales o la IP del equipo. Por favor, intente de nuevo.")
        if st.button("Volver a Ingresar Credenciales"):
            st.session_state["flagRegistro"] = False
            st.session_state["usuario"] = ""
            st.session_state["password"] = ""
            st.session_state["errorConexion"] = False
            st.rerun()
    
    
    @st.dialog("Ingrese Datos Manualmente")
    def dialog_datos_manuales():
        """
        Diálogo para el ingreso manual de datos del equipo cuando no se reconocen correctamente el nodo o la ciudad.
    
        Descripción:
          - Muestra el valor obtenido para "nodito" (campo deshabilitado) y permite ingresar el nombre real del nodo y la ciudad.
          - Al pulsar "Guardar", llama a insert_manual_data() para insertar la información en la BD.
          - Actualiza st.session_state y refresca la aplicación.
        """
        st.write("No se reconoció correctamente el nodo o la ciudad. Ingrese los datos manualmente.")
        nodo_obtenido = st.session_state.get("nodito", "")
        st.text_input("Nodo Obtenido", value=nodo_obtenido, disabled=True)
        
        nodo_real = st.text_input("Nombre real del Nodo")
        ciudad_manual = st.text_input("Ciudad")
        
        if st.button("Guardar"):
            try:
                resultado = insert_manual_data(ciudad_manual, nodo_obtenido, nodo_real)
                st.success(resultado)
                st.session_state["NODO"] = nodo_real
                st.session_state["CIUDAD"] = ciudad_manual.capitalize()
                st.session_state["datos_manual"] = False
                if "db_result" in st.session_state and isinstance(st.session_state["db_result"], dict):
                    st.session_state["db_result"]["CIUDAD"] = st.session_state["CIUDAD"]
                    st.session_state["db_result"]["NODO"] = st.session_state["NODO"]
                st.rerun()
            except Exception as e:
                st.error("Error al insertar datos manuales: " + str(e))
    
    
    @st.dialog("Configuración Ejecutada")
    def dialog_config_ejecutada():
        """
        Diálogo que indica que la configuración se ejecutó correctamente.
    
        Descripción:
          - Muestra un mensaje de éxito.
          - Permite cerrar el diálogo y refrescar la aplicación.
        """
        st.write("Configuración Ejecutada")
        if st.button("Cerrar"):
            st.rerun()
    
    
    def get_image_base64(image_path):
        """
        Convierte una imagen a una cadena base64 para incrustarla en HTML.
    
        Parámetros:
          image_path (str): Ruta de la imagen en el sistema.
        
        Retorna:
          str: Cadena en formato base64 o una cadena vacía en caso de error.
        """
        try:
            with open(image_path, "rb") as img_file:
                b64_string = base64.b64encode(img_file.read()).decode()
            return f"data:image/png;base64,{b64_string}"
        except Exception as e:
            st.error("Error cargando la imagen: " + str(e))
            return ""
    
    
    def show_loading_overlay(placeholder, image_url):
        """
        Muestra un overlay de carga utilizando HTML y CSS.
    
        Parámetros:
          placeholder: Objeto de Streamlit donde se inyecta el HTML.
          image_url (str): URL de la imagen a mostrar en el overlay.
        """
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
    
    
    def buscarDB(host, equipo):
        """
        Busca información de un dispositivo en la base de datos usando su IP.
    
        Parámetros:
          host (str): IP del dispositivo.
          equipo (str): Tipo ("Switch" o "Router").
    
        Retorna:
          tuple: (new_db_result, wasFound)
                 new_db_result: Diccionario con los datos del dispositivo (normalizados).
                 wasFound: Booleano indicando si se encontró el dispositivo.
        """
        try:
            new_db_result = ipSelect(host, equipo)
            if isinstance(new_db_result, dict):
                new_db_result = normalize_db_result(new_db_result)
            if "db_result" in st.session_state and isinstance(st.session_state["db_result"], dict):
                existing = st.session_state["db_result"]
                if not new_db_result.get("vrf", ""):
                    new_db_result["vrf"] = existing.get("vrf", "")
                if not new_db_result.get("mgmtInt", ""):
                    new_db_result["mgmtInt"] = existing.get("mgmtInt", "")
            st.session_state["db_result"] = new_db_result
            st.session_state["mostrar_db_result"] = True
            wasFound = isinstance(new_db_result, dict)
            st.session_state["wasFound"] = wasFound
            return new_db_result, wasFound
        except Exception as e:
            st.error("Error al buscar en la base de datos: " + str(e))
            return None, False
    
    
    def build_info_text():
        """
        Construye un texto HTML con la información del equipo obtenido de la base de datos.
    
        Retorna:
          str: Texto HTML con datos del dispositivo (IOS, hostname, mgmtInt, vrf, ciudad, nodo, modelo, vendor).
        """
        try:
            data = st.session_state.get("db_result", {})
            ciudad = data.get("CIUDAD", "")
            nodo = data.get("NODO", "")
            hostname = data.get("hostname", "")
            modelo = data.get("Modelo", "")
            vendor = data.get("Vendor", "")
            ios = data.get("OS_TYPE", "")
            ip_dcn = data.get("IP_DCN", "")
            mgmt_int = data.get("mgmtInt", "")
            vrf = data.get("vrf", "")
            info_text = f"""
            Ejecutando configuración para dispositivo con IOS {ios} en {ip_dcn}<br>
            Hostname: {hostname}<br>
            Interfaz Management: {mgmt_int}<br>
            Vrf: {vrf}<br>
            Ciudad: {ciudad}<br>
            Nodo: {nodo}<br>
            Modelo: {modelo}<br>
            Vendor: {vendor}
            """
            return info_text
        except Exception as e:
            return "Error al construir la información del equipo: " + str(e)
    
    # =============================================================================
    # Renderización de la Interfaz
    # =============================================================================
    
    def render_interface():
        """
        Renderiza la interfaz principal de la aplicación Streamlit.
        Descripción:
          - Configura la página (título, layout, estilos).
          - Carga imágenes y aplica estilos CSS personalizados.
          - Define la barra lateral con controles para seleccionar IOS, tipo de equipo, IP y opciones de configuración.
          - Permite al usuario buscar en la base de datos o revisar la configuración.
          - Muestra secciones con resultados de la base de datos y la información del equipo.
          - Muestra una "Consola de Ejecución" que contiene los logs de los comandos ejecutados.
          - Gestiona la lógica para mostrar diálogos (credenciales, error, ingreso manual de datos, configuración ISE).
    
        Retorna:
          None
        """
        try:
            st.set_page_config(page_title="Liberty Networks - SYSRISE", layout="wide")
            script_dir = os.path.dirname(os.path.abspath(__file__))
            image_path = os.path.join(script_dir, "LN.png")
            image_base64 = get_image_base64(image_path)
    
            # ------------------- ESTILOS PERSONALIZADOS (CSS) ------------------- #
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
                div[data-testid="stTextInput"],
                div[data-testid="stSelectbox"],
                div[data-testid="stMultiSelect"] {
                    border-radius: 6px;
                    border: 1px solid #666;
                    background-color: #ffffff;
                    font-family: 'Open Sans', sans-serif;
                    font-size: 14px;
                }
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
    
            # Título de la aplicación con estilo HTML y CSS personalizado.
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
    
            # ------------------- BARRA LATERAL ------------------- #
            with st.sidebar:
                st.image("LN3.png")
                st.markdown("""<hr style="border:none;height:1px;background:#ccc;">""", unsafe_allow_html=True)
                ios = st.selectbox("Seleccione IOS:", ["XE", "XR", "JUNOS"], index=0)
                equipo = st.selectbox("Seleccione tipo de Equipo", ["Switch", "Router"])
                st.session_state["equipo"] = equipo
                host = st.text_input("Ingrese dirección IP:")
                options = st.multiselect(
                    "¿Qué desea configurar?",
                    ["ISE", "Usuario Rancid", "Servidor Rancid", "Syslog", "Servidor Syslog"],
                    placeholder="Seleccione"
                )
    
                # Botón para revisar la configuración (busca en BD y ejecuta configuración)
                if st.button("Revisar Configuración"):
                    if host and options:
                        st.session_state["flagDB"] = False
                        st.session_state["wasFound"] = False
                        st.session_state["selected_options"] = options
    
                        overlay_placeholder = st.empty()
                        show_loading_overlay(overlay_placeholder, image_base64)
    
                        usuario_cred = st.session_state.get("usuario", "")
                        password_cred = st.session_state.get("password", "")
                        if usuario_cred == "" or password_cred == "":
                            st.error("Debe ingresar sus credenciales en el diálogo")
                        else:
                            general_output, cli_output = ejecutar_configuracion(ios, equipo, host, options, usuario_cred, password_cred)
                            overlay_placeholder.empty()
                            
                            processed_data = get_processed_values()
                            # Verifica si la conexión falló o si la información básica está ausente.
                            if "No fue posible establecer la conexión" in general_output or not processed_data or not processed_data.get("hostname"):
                                st.session_state["errorConexion"] = True
                                st.session_state["datos_manual"] = False
                                st.session_state["db_result"] = {}
                                st.session_state["resultado"] = ""
                                st.session_state["shell_log"] = ""
                            else:
                                processed_data = normalize_db_result(processed_data)
                                st.session_state["db_result"] = processed_data
                                st.session_state["mostrar_db_result"] = True
                                st.session_state["resultado"] = general_output
                                st.session_state["shell_log"] = cli_output
                                st.session_state["mostrar_resultado"] = True
                                st.session_state["nodito"] = processed_data.get("Nodito", "")
                                
                                if not processed_data.get("NODO") or not processed_data.get("CIUDAD"):
                                    st.session_state["datos_manual"] = True
    
                                st.markdown(
                                    """
                                    <script>
                                    document.getElementById("scroll-target").scrollIntoView({ behavior: "smooth" });
                                    </script>
                                    """,
                                    unsafe_allow_html=True
                                )
                    else:
                        st.error("Por favor, ingrese la dirección IP y seleccione al menos una opción.")
    
                if st.button("Buscar en Base de Datos"):
                    st.session_state["flagDB"] = True
                    db_result, _ = buscarDB(host, equipo)
    
            # ------------------- SECCIÓN PRINCIPAL DE RESULTADOS ------------------- #
            if not st.session_state.get("errorConexion", False):
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown(
                        """
                        <div class="dispositivo-section">
                            <h2>Resultado Base de Datos</h2>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
                    if st.session_state.get("mostrar_db_result"):
                        db_result = st.session_state["db_result"]
                        if db_result and isinstance(db_result, dict):
                            if st.session_state.get("flagDB"):
                                st.success("Equipo registrado en la BD")
                            else:
                                if st.session_state.get("wasFound"):
                                    st.warning("El equipo se actualizará en la BD con la siguiente información")
                                else:
                                    st.warning("El equipo se registrará en la BD con la siguiente información")
                            df = pd.DataFrame([db_result])
                            if st.session_state.get("flagDB"):
                                df = df.rename(columns={"Vendor": "ROL"})
                                columnas = ["CIUDAD", "NODO", "hostname", "IP_DCN", "ROL", "OS_TYPE", "Modelo"]
                            else:
                                columnas = ["CIUDAD", "NODO", "hostname", "IP_DCN", "Vendor", "OS_TYPE", "Modelo"]
                            df = df[columnas]
                            df_html = df.to_html(classes="custom-table", index=False)
                            st.markdown(
                                f"""
                                <div class="table-container">
                                    {df_html}
                                </div>
                                """,
                                unsafe_allow_html=True
                            )
                        else:
                            st.warning("No se encontraron resultados en la base de datos.")
                with col2:
                    st.markdown(
                        """
                        <div class="resultado-section">
                            <h2>Información del Equipo</h2>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
                    if st.session_state.get("mostrar_resultado"):
                        info_text = build_info_text()
                        st.markdown(
                            f"""<div class="result-config">{info_text}</div>""",
                            unsafe_allow_html=True
                        )
                with st.expander("Consola de Ejecución", expanded=bool(st.session_state.get("shell_log", ""))):
                    st.markdown("Los comandos que se ejecutarán en el equipo se muestran en el CLI. Para continuar con la configuración, oprima el botón Ejecutar.")
                    st.markdown(f"""
                    <div class="shell-container">
                        <button class="copy-btn" onclick="copyConsole()">Copiar</button>
                        <div class="shell-log" id="shell-log-text">{st.session_state.get("shell_log", "")}</div>
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
            else:
                st.session_state["db_result"] = {}
                st.session_state["resultado"] = ""
                st.session_state["shell_log"] = ""
            
            # ------------------- Botón de Ejecución ------------------- #
            if st.button("Ejecutar"):
                try:
                    # Se asume que la conexión SSH (shellClient) ya fue establecida en ejecutar configuracion
                    ejec_funciones()
                    dialog_config_ejecutada()
                    if "ISE" in st.session_state.get("selected_options", []):
                        st.session_state["mostrar_ise_dialog"] = True
                except Exception as e:
                    st.error("Error al ejecutar la configuración: " + str(e))
    
            st.markdown("<div id='scroll-target'></div>", unsafe_allow_html=True)
            
            # Lógica para determinar qué diálogo mostrar según el estado actual.
            dialog_to_show = None
            if not st.session_state.get("flagRegistro", False):
                dialog_to_show = "credenciales"
            elif st.session_state.get("errorConexion", False):
                dialog_to_show = "error"
            elif st.session_state.get("datos_manual", False):
                dialog_to_show = "datos_manual"
            elif st.session_state.get("mostrar_ise_dialog", False):
                dialog_to_show = "ise"
    
            if dialog_to_show == "credenciales":
                ingresarCredenciales()
            elif dialog_to_show == "error":
                errorCredencialesDialog()
            elif dialog_to_show == "datos_manual":
                dialog_datos_manuales()
            elif dialog_to_show == "ise":
                dialog_ise()
        except Exception as e:
            st.error("Ocurrió un error inesperado en la interfaz: " + str(e))
