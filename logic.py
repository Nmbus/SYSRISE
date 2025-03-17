 """
    Librerías y Versiones Recomendadas:
      - selenium==4.8.0         -> Automatización de navegadores
      - paramiko==2.11.0        -> Conexiones SSH a dispositivos remotos
      - mariadb==1.1.8          -> Conexión y manipulación de bases de datos MariaDB
      - Python ==3.13          
    
    Otros módulos utilizados son de la librería estándar:
      - time, re, os, sys, json
    """
    
    # =============================================================================
    # Importación de Módulos
    # =============================================================================
    from selenium import webdriver         # selenium==4.8.0
    from selenium.webdriver.common.keys import Keys
    from selenium.webdriver.common.by import By
    import paramiko                        # paramiko==2.11.0
    import time
    import re
    import os
    import sys
    import mariadb                         # mariadb==1.1.8
    import json
    
    # =============================================================================
    # Variables Globales y Parámetros de Configuración
    # =============================================================================
    
    # Direcciones IP de los servidores específicos
    hostnameRancid = "172.18.12.202"      # Servidor Rancid
    hostnameSyslog  = "172.18.11.242"      # Servidor Syslog
    
    # Variables que se actualizarán con datos del dispositivo o ingresados manualmente
    hostname = ""            # Hostname del dispositivo (se extrae mediante comandos)
    hostnameClient = ""      # IP del dispositivo
    ciudad = ""              # Ciudad asociada al dispositivo
    vendor = ""              # Proveedor del dispositivo
    nodo = ""                # Nodo de la red, extraído del hostname
    nodito = ""              # Identificador adicional derivado del hostname
    ios = ""                 # Tipo o versión de IOS (XE, XR JUNOS)
    equipo = ""              # Tipo de equipo ("Switch" o "Router")
    modelo = ""              # Modelo del dispositivo
    mgmtInt = ""             # Interfaz de gestión del dispositivo
    vrf = ""                 # VRF usado en la configuración
    options = []             # Lista de opciones de configuración (por ejemplo, ["ISE", "Usuario Rancid", "Syslog"])
    shellClient=None
    
    # Instancias de SSHClient para realizar conexiones a distintos dispositivos/servidores
    client  = paramiko.SSHClient()
    rancid  = paramiko.SSHClient()
    syslog  = paramiko.SSHClient()
    
    # =============================================================================
    # Funciones de Automatización Web (Selenium) ##Incompleto
    # =============================================================================
    
    def otsTicket():
        """
        Automatiza el acceso al sistema de tickets (OTS) mediante Selenium.
    
        Descripción:
          - Abre un navegador Chrome.
          - Navega a la URL del SSO (Single Sign-On) del sistema de tickets.
          - Espera a que la página cargue y localiza el campo de usuario mediante su ID.
          - Ingresa el correo "1871713@cwc.com" y hace clic en el botón "Next" para continuar.
    
        Ejemplo:
          >>> otsTicket()
          (Se abrirá una ventana de Chrome y se procederá al inicio de sesión)
        """
        driver = webdriver.Chrome()  # Se inicia el driver de Chrome (requiere tener el chromedriver compatible)
        # Navega a la URL del sistema SSO del servicio de tickets
        driver.get('https://identity.lla.com/app/servicedesk/exk1s9tlsit5TGKwm1d8/sso/saml?SAMLRequest=fZJLT8MwEIT%2FSuR76yaEtLXaSoUKqHhVNHDgghxnAxaOHbwb2v570oSnBFzX88141p6gLE0l5jU92Rt4qQEp2JbGomgPpqz2VjiJGoWVJaAgJdbzywsR9Qei8o6ccoZ9Q%2F4nJCJ40s6yYLmYsocsivJEDhXEB6DyqEjGo2KUJaMoTsaZzAo1zIpsmIzjkAV34LEhp6wxanDEGpYWSVpqRoPosDc46IVhGg1EnIg4vmfBommjraSWeiKqUHCuc7Ckadc3RvaVK7msKt7c6lUryAGfOWyfQxyTQU2H6en5pgzzEUd0fF%2BPBfOPCsfOYl2CX3fs7c3FV4gj%2FPTvsNX7ro60zbV9%2FH9NWSdCcZamq97qep2y2WTvI9rafvZLzoR%2FF0y6d71qrJeLlTNa7YIT50tJfyeH%2FbCd6LxXtFJRW6xA6UJD3hQ3xm2OPUiCKSNfA%2BOzLvTn%2F5m9AQ%3D%3D&RelayState=https%3A%2F%2Fots.lla.com%2Fauth%2Flogin%2Ftype%2Fsaml%3Fnext%3D')
        time.sleep(2)  # Espera 2 segundos para que la página cargue
        # Encuentra el campo de entrada del usuario por su ID y escribe el correo
        username = driver.find_element(By.ID, "input28")
        username.send_keys("1871713@cwc.com")
        # Encuentra el botón "Next" mediante XPath y hace clic para continuar
        lgButton = driver.find_element(By.XPATH, "//input[@value='Next']")
        lgButton.click()
    
    
    # =============================================================================
    # Funciones de Procesamiento de Texto y Expresiones Regulares
    # =============================================================================
    
    def encontrarTodos(text, pattern):
        """
        Encuentra todas las coincidencias de un patrón en un texto.
    
        Parámetros:
          text (str): Texto en el que se realizará la búsqueda.
          pattern (str): Expresión regular que define el patrón a buscar.
    
        Retorna:
          list: Lista de todas las coincidencias encontradas.
          bool: False si no se encontró ninguna coincidencia.
    
        Ejemplo:
          >>> encontrarTodos("172.18.49.9 and 172.18.20.10", r'\b\d+\.\d+\.\d+\.\d+\b')
          ['172.18.49.', '172.18.20.10']
        """
        match = re.findall(pattern, text)
        return match if match else False
    
    
    def encontrarTxt(text, pattern):
        """
        Busca la primera ocurrencia de un patrón y extrae el primer grupo capturado.
    
        Parámetros:
          text (str): Texto en el que se realiza la búsqueda.
          pattern (str): Expresión regular que contiene al menos un grupo de captura.
    
        Retorna:
          str: El contenido del primer grupo capturado si se encuentra coincidencia,
               o una cadena vacía si no se encuentra.
               En caso de error, retorna "Error".
    
        Ejemplo:
          >>> encontrarTxt("hostname: Switch01#", r'([^:#]+)#')
          'Switch01'
        """
        match = re.search(pattern, text)
        try:
            return match.group(1) if match else ""
        except Exception:
            return "Error"
    
    
    # =============================================================================
    # Funciones de Conexión SSH y Ejecución de Comandos
    # =============================================================================
    
    def crearConexionSSH(hostname, ssh_client, port="22", username=None, password=None, vendor="cisco"):
        """
        Establece una conexión SSH a un dispositivo y retorna el canal de shell junto con un mensaje de estado.
    
        Parámetros:
          hostname (str): Dirección IP del dispositivo a conectar.
          ssh_client (paramiko.SSHClient): Instancia de SSHClient para la conexión.
          port (str/int): Puerto SSH (por defecto "22").
          username (str): Nombre de usuario para la autenticación.
          password (str): Contraseña para la autenticación.
          vendor (str): Tipo de dispositivo ("cisco" por defecto). Si es "cisco", se enviará el comando "enable".
    
        Retorna:
          tuple: (shell, output)
                 - shell (paramiko.Channel): Canal de shell para ejecutar comandos (None si falla).
                 - output (str): Mensaje informativo sobre el proceso de conexión.
    
        """
        if not username or not password:
            return None, "Credenciales no proporcionadas."
        output = f"Conectando a {username}@{hostname}:{port}\n"
        try:
            ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh_client.connect(hostname, port, username, password)
            if ssh_client.get_transport().is_active():
                output += "Conexión establecida.\n"
                shell = ssh_client.invoke_shell()
                if vendor == "cisco":
                    shell.send("enable\n")  # Para dispositivos Cisco, entra en modo privilegiado
                time.sleep(1)
            return shell, output
        except Exception as e:
            output += f"No fue posible establecer la conexión: {e}\n"
            return None, output
    
    
    def ingresarComando(comando, shell, cr="\n"):
        """
        Envía un comando al canal SSH y retorna la salida.
    
        Parámetros:
          comando (str): Comando a ejecutar en el dispositivo.
          shell (paramiko.Channel): Canal SSH previamente establecido.
          cr (str): Carácter de final de línea (por defecto "\n").
    
        Retorna:
          str: Salida resultante de la ejecución del comando.
               En caso de error, se añade un mensaje de error a la salida.
    
        Ejemplo:
          >>> salida = ingresarComando("show version", shell)
          >>> print(salida)
          (Salida del comando "show version")
        """
        output = ""
        try:
            shell.send(f"{comando}{cr}")
            time.sleep(3)  # Espera 3 segundos para que se ejecute el comando y se genere la salida
            if shell.recv_ready():
                output = shell.recv(10000).decode("utf-8")
        except Exception as e:
            output += f"Error al ejecutar el comando '{comando}': {e}\n"
        return output
    
    
    # =============================================================================
    # Funciones de Configuración Específica (Rancid, ISE, Syslog)
    # =============================================================================
    
    def userRancid(shell, commandList):
        """
        Verifica la configuración del usuario "rancid" y lo reconfigura si es necesario.
    
        Descripción:
          - Ejecuta "show runn aaa | include rancid" para obtener la configuración actual.
          - Usa una expresión regular para extraer el nombre, nivel de encriptación y contraseña.
          - Si la encriptación o contraseña no son las esperadas, entra en modo configuración para eliminar
            el usuario "rancid" y luego ejecuta los comandos de reconfiguración de commandList.
          - Si no se encuentra la configuración, ejecuta directamente los comandos en commandList.
    
        Parámetros:
          shell (paramiko.Channel): Canal SSH activo.
          commandList (list): Lista de comandos para reconfigurar el usuario "rancid".
    
        """
        auxRancid = ingresarComando("show runn aaa | include rancid", shell)
        pattern = r"username\s+(\S+)\s+privilege\s+\d+\s+secret\s+(\d)\s+(\S+)\s"
        match = re.search(pattern, auxRancid)
        if match:
            user = match.group(1)
            encryption = match.group(2)
            password = match.group(3)
            print(user)
            print(encryption)
            print(password)
            if encryption != "5" or password != "$1$v811$vr0Qt5Y8A6WIeF0LK3V4N0":
                ingresarComando("configure terminal", shell)
                ingresarComando("no username rancid", shell)
                ingresarComando("exit", shell)
                for command in commandList:
                    ingresarComando(command, shell)
        else:
            for command in commandList:
                ingresarComando(command, shell)
    
    
    def configureISE(shell, commandList):
        """
        Ejecuta una serie de comandos para configurar AAA en el dispositivo.
    
        Parámetros:
          shell (paramiko.Channel): Canal SSH activo.
          commandList (list): Lista de comandos para la configuración de AAA.
        """
        for command in commandList:
            ingresarComando(command, shell)
    
    
    def configureSyslog(shell, commandList):
        """
        Ejecuta una serie de comandos para configurar el Syslog en el dispositivo.
    
        Parámetros:
          shell (paramiko.Channel): Canal SSH activo.
          commandList (list): Lista de comandos para la configuración del Syslog.
        """
        for command in commandList:
            ingresarComando(command, shell)
    
    def configurarServidorRancid(shell):
        """
        Extrae información del servidor Rancid
        Descripción:
          - Utiliza comandos "cat" y "grep" para extraer información de /etc/hosts y el archivo router.db.
          - Emplea expresiones regulares para obtener direcciones IP y Hostname.
          - Serializa la información extraída a formato JSON.
          - Ejecuta un script Python (m2a.py), en el servidor Rancid, pasando como parámetros hostnameClient, hostname, ciudad, vendor y la cadena JSON.
    
        Parámetros:
          shell (paramiko.Channel): Canal SSH activo para Rancid.
    
        Ejemplo:
          >>> configurarServidorRancid(shell)
        """
        ingresarComando("cd /usr/local/rancid/var/", shell)
        auxName = ingresarComando("cat /etc/hosts | grep --color=never " + hostname, shell)
        auxIP = ingresarComando("cat /etc/hosts | grep --color=never " + hostnameClient, shell)
        auxRouter = ingresarComando("cat " + ciudad + "/router.db | grep --color=never " + hostname + "[[:punct:]]", shell)
        flagName = encontrarTodos(auxName, r'\b\d+\.\d+\.\d+\.\d+\b')
        flagIP = encontrarTodos(auxIP, r"\b(?:[A-Z\d]+-)+[A-Z\d]+\b")
        flagRouter = encontrarTodos(auxRouter, r"(?:[A-Za-z0-9]+(?:-[A-Za-z0-9]+)*);(?:[^;\r\n]+);(?:[^;\r\n]+)")
        dns = [flagName, flagIP, flagRouter]
        dnsStr = json.dumps(dns)
        cmd = 'python m2a.py "{}" "{}" "{}" "{}" \'{}\''.format(hostnameClient, hostname, ciudad, vendor, dnsStr)
        ingresarComando(cmd, shell)
        print(cmd)
    
    
    # =============================================================================
    # Funciones para Extraer y Procesar Parámetros del Dispositivo
    # =============================================================================
    
    def findParameteres(shell):
        """
        Extrae diversos parámetros del dispositivo conectándose vía SSH y ejecutando comandos.
    
        Proceso:
          - Para dispositivos con IOS "XE" o "XR":
              * Recibe datos del prompt para extraer el hostname.
              * Ejecuta "show ip interface brief" filtrado por hostnameClient para determinar la interfaz de gestión.
              * Busca en la salida la presencia de uno de los prefijos definidos para identificar la interfaz.
              * Si no encuentra la interfaz, asigna "IP Virtual" y extrae el VRF con "show runn | include virtual".
              * Si encuentra la interfaz, extrae el nombre de la interfaz (mgmtInt) y luego el VRF.
              * Extrae el modelo del dispositivo mediante "show version | include processor".
          - Para otros tipos de IOS:
              * Extrae el hostname y el modelo usando "show configuration" y "show version", respectivamente.
          - Llama a encontrarNodo() para obtener un identificador (nodito).
          - Llama a ncSelect(nodito) para obtener la ciudad y el nodo real desde la base de datos.
          - Capitaliza la ciudad y retorna un mensaje de éxito o error.
    
        Parámetros:
          shell (paramiko.Channel): Canal SSH activo.
    
        Retorna:
          str: "Parámetros del dispositivo encontrados" en caso de éxito,
               o "Problema al establecer la conexión, revise credenciales" si ocurre algún error.
    
        Ejemplo:
          >>> mensaje = findParameteres(shell)
          >>> print(mensaje)
          "Parámetros del dispositivo encontrados"
        """
        global mgmtInt, vrf, ciudad, hostname, nodo, nodito, modelo
        mgmtInt = ""
        vrf = ""
        ciudad = ""
        hostname = ""
        prefijos = ["MgmtEth", "GigabitEthernet", "FastEthernet", "TenGigabitEthernet", "Loopback", "Vlan", "Serial", "Port-channel"]
        indice = None
        print(ios)
        try:
            if ios == "XE" or ios == "XR":
                auxHost = shell.recv(20000).decode("utf-8")
                hostname = encontrarTxt(auxHost, r'([^:#]+)#').strip()
                auxMgmtInt = ingresarComando("show ip interface brief | include " + hostnameClient, shell)
                for prefijo in prefijos:
                    try:
                        indice = auxMgmtInt.index(prefijo)
                        break
                    except ValueError:
                        continue
                flag = False
                i = 0
                if indice is None:
                    mgmtInt = "IP Virtual"
                    auxVrf = ingresarComando("show runn | include virtual", shell)
                    vrf = encontrarTxt(auxVrf, r"vrf\s+(\S+)")
                else:
                    while not flag:
                        if auxMgmtInt[indice + i] == " ":
                            flag = True
                        else:
                            mgmtInt += auxMgmtInt[indice + i]
                            i += 1
                    auxVrf = ingresarComando("show runn interface " + mgmtInt + " | include vrf", shell)
                    vrf = encontrarTxt(auxVrf, r"vrf (?:forwarding\s+)?(\S+)")
                auxModel = ingresarComando("show version | include processor", shell)
                modelo = encontrarTxt(auxModel, r'cisco (\S+)')
            else:
                auxHost = ingresarComando("show configuration | match host-name", shell)
                hostname = encontrarTxt(auxHost, r'host-name (\S+)').rstrip(';')
                auxModel = ingresarComando("show version | match model", shell)
                modelo = encontrarTxt(auxModel, r'Model: (\S+)')
            nodito = encontrarNodo()
            ciudad, nodo = ncSelect(nodito)
            ciudad = ciudad.capitalize()
            return "Parámetros del dispositivo encontrados"
        except:
            return "Problema al establecer la conexión, revise credenciales"
    
    
    def encontrarNodo():
        """
        Extrae el identificador de nodo a partir del hostname.
    
        Descripción:
          - Divide el hostname usando guiones o guiones bajos como separadores.
          - Limpia cada parte y decide cuál representa el nodo según la longitud y el número de partes.
    
        Retorna:
          str: La parte del hostname que se considera el nodo.
    
        Ejemplo:
          >>> hostname = "COL-IPIAL-ME3600-01"
          >>> nodo = encontrarNodo()
          >>> print(nodo)
          "IPIAL"
        """
        partes = re.split(r'[-_]', hostname)
        partes = [parte.strip() for parte in partes if parte.strip()]
        print(partes)
        if len(partes) >= 5 and len(partes[0]) == 3 and len(partes[1]) == 3:
            return partes[2]
        elif len(partes) > 1 and len(partes[0]) == 3:
            return partes[1]
        else:
            return partes[0]
    
    
    def ncSelect(auxNodo):
        """
        Consulta la base de datos para obtener la Ciudad y NodoReal a partir del nodo extraído.
    
        Parámetros:
          auxNodo (str): Nodo extraído del hostname.
    
        Retorna:
          tuple: (Ciudad, NodoReal) si se encuentra en la base de datos.
                 (None, None) si no se encuentra.
                 En caso de error, retorna un mensaje de error (str).
    
        Ejemplo:
          >>> ciudad, nodoReal = ncSelect("IPIAL")
          >>> print(ciudad, nodoReal)
          "IPIALES", "IPIAL"
        """
        try:
            conn = mariadb.connect(
                user="root",
                password="Trul-f87",
                host="172.18.93.210",
                port=3306,
                database="ipcol"
            )
            cur = conn.cursor()
            query = "SELECT Ciudad, NodoReal FROM ipcol.ubicacion WHERE Nodo IN ('" + auxNodo + "');"
            cur.execute(query)
            row = cur.fetchone()
            cur.close()
            conn.close()
            if row is None:
                return None, None
            else:
                return row
        except mariadb.Error as e:
            return f"Error connecting to DB: {e}"
    
    
    # =============================================================================
    # Funciones para Generar Listas de Comandos Según el Tipo de Dispositivo
    # =============================================================================
    
    def commandRancid():
        """
        Genera una lista de comandos para configurar el usuario "rancid" en el dispositivo.
    
        Descripción:
          - Dependiendo del valor de 'ios' (XE, XR u otro), se selecciona la sintaxis apropiada para configurar al usuario "rancid".
          - Retorna una lista de comandos que, posteriormente, se ejecutarán para reconfigurar o configurar el usuario rancid.
    
        Retorna:
          list: Lista de comandos para la configuración de rancid.
    
        """
        if ios == "XE":
            command_list = ["configure terminal", "username rancid privilege 15 secret 5 $1$v811$vr0Qt5Y8A6WIeF0LK3V4N0", "exit"]
        elif ios == "XR":
            command_list = ["configure terminal", "username rancid", "secret 5 $1$v811$vr0Qt5Y8A6WIeF0LK3V4N0", "group root-lr", "exit"]
        else:
            command_list = ["configure", 'set system login user rancid full-name "RANCID"', "set system login user rancid uid 2103",
                            "set system login user rancid class CN-ADMIN",
                            'set system login user rancid authentication encrypted-password "$5$Kx5R2kJQ$J1fCLPY6mmDDycl3PHOawYmwQqBXM3ybielOoXBzTlA"', "exit"]
        return command_list
    
    
    def commandISE():
        """
        Genera una lista de comandos para configurar ISE en el dispositivo.
    
        Descripción:
          - Dependiendo del valor de 'ios' (XE, XR u otro), selecciona la sintaxis correcta para la configuración.
          - Incluye comandos para configurar el grupo TACACS, la autenticación, la autorización y otros parámetros de ISE.
    
        Retorna:
          list: Lista de comandos para la configuración de ISE.
    
        """
        if ios == "XE":
            command_list = ["configure terminal", "aaa new-model", "aaa group server tacacs+ ACS",
                            "server-private 172.18.4.27 key 7 0207050B52011B621E1A",
                            "server-private 172.18.9.152 key 7 070E201C170E0D464546",
                            "ip vrf forwarding " + vrf, "ip tacacs source-interface " + mgmtInt,
                            "aaa authentication login default group ACS local", "aaa authorization exec default group ACS local",
                            "aaa authorization commands 1 default group ACS local", "aaa authorization commands 15 default group ACS local",
                            "aaa authorization config-commands", "aaa authorization console", "aaa accounting exec default",
                            "action-type start-stop", "group ACS", "aaa accounting commands 15 default", "action-type start-stop", "group ACS", "exit"]
        elif ios == "XR":
            command_list = ["configure terminal", "aaa accounting exec default start-stop none",
                            "aaa accounting exec vtyACSacc start-stop group ACS none",
                            "aaa accounting commands default start-stop none",
                            "aaa accounting commands vtyACSacc start-stop group ACS none", "aaa group server tacacs+ ACS",
                            "vrf " + vrf, "server-private 172.18.4.27 port 49", "key 7 01120754020C124C7318",
                            "!", "server-private 172.18.9.152 port 49", "key 7 070E201C170E0D464546", "!", "!",
                            "aaa authorization exec default group ACS local", "aaa authorization commands default group ACS none",
                            "aaa authorization commands vtyACSautho group ACS none", "aaa authorization commands vtycommands group ACS none",
                            "aaa authentication login vtyACS group ACS local", "aaa authentication login default group ACS local", "exit"]
        else:
            command_list = ["configure", "set system authentication-order radius",
                            "set system radius-server 172.18.4.27 port 1812",
                            "set system radius-server 172.18.4.27 accounting-port 1813",
                            'set system radius-server 172.18.4.27 secret "$9$A2k-p1R8LNsgJVwmTQz/9uO1REcKMX-b2"',
                            "set system radius-server 172.18.4.27 source-address " + hostnameClient,
                            "set system radius-server 172.18.9.152 port 1812",
                            "set system radius-server 172.18.9.152 accounting-port 1813",
                            'set system radius-server 172.18.9.152 secret "$9$gkoUjF3901htu87N-sYaZUjik5QnCpB"',
                            "set system radius-server 172.18.9.152 source-address " + hostnameClient,
                            "set system accounting events interactive-commands",
                            "set system accounting destination radius server 172.18.4.27 port 1812",
                            "set system accounting destination radius server 172.18.4.27 accounting-port 1813",
                            'set system accounting destination radius server 172.18.4.27 secret "$9$-mV24.mT6CuFnyKvMx7bs24oJikPQ39"',
                            "set system accounting destination radius server 172.18.4.27 source-address " + hostnameClient,
                            "set system accounting destination radius server 172.18.9.152 port 1812",
                            "set system accounting destination radius server 172.18.9.152 accounting-port 1813",
                            'set system accounting destination radius server 172.18.9.152 secret "$9$gkoUjF3901htu87N-sYaZUjik5QnCpB"',
                            "set system accounting destination radius server 172.18.9.152 source-address " + hostnameClient,
                            "set firewall family inet filter protect-re term accept-radius from source-address " + hostnameClient + "/32",
                            "set firewall family inet filter protect-re term accept-radius from source-address 172.18.4.27/32",
                            "set firewall family inet filter protect-re term accept-radius from source-address 172.18.9.152/32",
                            "set firewall family inet filter protect-re term accept-radius from source-port 1812",
                            "set firewall family inet filter protect-re term accept-radius from source-port 1813",
                            "set firewall family inet filter protect-re term accept-radius then accept", "exit"]
        return command_list
    
    
    def commandSyslog():
        """
        Genera la lista de comandos para configurar el Syslog en el dispositivo, ajustando según el IOS.
    
        Descripción:
          - Para IOS XE: Usa comandos de configuración de logging, definiendo el host Syslog y el VRF.
          - Para IOS XR: Configura logging con parámetros de severidad y la interfaz de origen.
          - Para otros sistemas: Configura syslog con comandos propios de la sintaxis del dispositivo.
    
        Retorna:
          list: Lista de comandos específicos para configurar Syslog.
        """
        if ios == "XE":
            command_list = ["configure terminal", "archive", "log config", "logging enable", "notify syslog", "hidekeys",
                            "notify syslog contenttype plaintext", "logging host 172.18.11.242 vrf " + vrf,
                            "logging origin-id hostname", "exit"]
        elif ios == "XR":
            command_list = ["configure terminal", "logging 172.18.11.242 vrf " + vrf + " severity info port default",
                            "logging source-interface " + mgmtInt + " vrf " + vrf, "logging hostnameprefix " + hostname, "exit"]
        else:
            command_list = ["configure", "set system syslog user * any emergency",
                            "set system syslog host 172.18.11.242 any any",
                            "set system syslog host 172.18.11.242 daemon any",
                            "set system syslog host 172.18.11.242 kernel any",
                            "set system syslog host 172.18.11.242 firewall notice",
                            "set system syslog host 172.18.11.242 interactive-commands any",
                            "set system syslog host 172.18.11.242 log-prefix " + hostname,
                            "set system syslog host 172.18.11.242 source-address " + hostnameClient,
                            "set system syslog host 172.18.11.242 explicit-priority",
                            "set system syslog file messages any notice",
                            "set system syslog file messages authorization info",
                            "set system syslog file interactive-commands any any",
                            "set system syslog file interactive-commands explicit-priority", "exit"]
        return command_list
    
    
    def printCommands(commandList):
        """
        Formatea la lista de comandos para mostrarlos con un estilo similar al de un prompt de configuración.
    
        Parámetros:
          commandList (list): Lista de comandos generada para la configuración.
    
        Retorna:
          str: Cadena formateada donde cada comando (excepto el primero y último) se muestra en la forma:
               "{hostname}(config)# {command}<br>"
    
        Ejemplo:
          >>> salida = printCommands(["configure terminal", "username rancid ...", "exit"])
          >>> print(salida)
          COL-IPIAL-ME3600-01(config)# username rancid ...<br>
        """
        output = ""
        for command in commandList[1:-1]:
            output += hostname + "(config)# " + command + "<br>"
        return output
    
    
    # =============================================================================
    # Funciones para Interactuar con la Base de Datos
    # =============================================================================
    
    def ipSelect(host, equipo):
        """
        Consulta la base de datos para obtener la información de un dispositivo según su IP.
        Parámetros:
          host (str): Dirección IP del dispositivo.
          equipo (str): Tipo de dispositivo ("Switch" o "Router").
    
        Retorna:
          dict: Información del dispositivo en formato diccionario si se encuentra.
          None: Si no se encuentra.
          str: Mensaje de error si ocurre un fallo en la conexión.
        """
        print(equipo)
        if equipo == "Switch":
            try:
                conn = mariadb.connect(
                    user="root",
                    password="Trul-f87",
                    host="172.18.93.210",
                    port=3306,
                    database="ipcol"
                )
                cur = conn.cursor()
                query = "SELECT * FROM ipcol.switches WHERE IP_DCN IN ('" + host + "');"
                cur.execute(query)
                row = cur.fetchone()
                columns = [desc[0] for desc in cur.description]
                cur.close()
                conn.close()
                if row is None:
                    return None
                else:
                    device_info = dict(zip(columns, row))
                    return device_info
            except mariadb.Error as e:
                return f"Error connecting to DB: {e}"
        elif equipo == "Router":
            try:
                conn = mariadb.connect(
                    user="root",
                    password="Trul-f87",
                    host="172.18.93.210",
                    port=3306,
                    database="ipcol"
                )
                cur = conn.cursor()
                query = "SELECT row_id, CIUDAD, Nodo, hostname, IP_DCN, ROL, OS_type, Modelo FROM ipcol.routers WHERE IP_DCN IN ('" + host + "');"
                cur.execute(query)
                row = cur.fetchone()
                columns = [desc[0] for desc in cur.description]
                cur.close()
                conn.close()
                if row is None:
                    return None
                else:
                    device_info = dict(zip(columns, row))
                    return device_info
            except mariadb.Error as e:
                return f"Error connecting to DB: {e}"
    
    
    def ipInsert():
        """
        Inserta la información del dispositivo en la base de datos.
        Descripción:
          - Dependiendo del tipo de dispositivo ("Switch" o "Router"), inserta en la tabla correspondiente de la base de datos.
          - Usa parámetros globales (ciudad, nodo, hostname, hostnameClient, vendor, ios, modelo).
    
        Retorna:
          str: Mensaje de éxito indicando que el dispositivo se añadió a la base de datos, o un mensaje de error.
        """
        if equipo == "Switch":
            try:
                conn = mariadb.connect(
                    user="root",
                    password="Trul-f87",
                    host="172.18.93.210",
                    port=3306,
                    database="ipcol"
                )
                cur = conn.cursor()
                query = "INSERT INTO ipcol.switches (CIUDAD, NODO, hostname, IP_DCN, Vendor, OS_TYPE, Modelo) VALUES (%s, %s, %s, %s, %s, %s, %s)"
                objValue = (ciudad, nodo, hostname, hostnameClient, vendor, ios, modelo)
                cur.execute(query, objValue)
                conn.commit()
                cur.close()
                conn.close()
                return f"{hostname} added to DB"
            except mariadb.Error as e:
                return f"Error connecting to DB: {e}"
        elif equipo == "Router":
            try:
                conn = mariadb.connect(
                    user="root",
                    password="Trul-f87",
                    host="172.18.93.210",
                    port=3306,
                    database="ipcol"
                )
                cur = conn.cursor()
                query = "INSERT INTO ipcol.routers (CIUDAD, Nodo, hostname, IP_DCN, OS_type, Modelo) VALUES (%s, %s, %s, %s, %s, %s)"
                objValue = (ciudad, nodo, hostname, hostnameClient, ios, modelo)
                cur.execute(query, objValue)
                conn.commit()
                cur.close()
                conn.close()
                return f"{hostname} added to DB"
            except mariadb.Error as e:
                return f"Error connecting to DB: {e}"
    
    
    def insert_manual_data(ciudadReal, nodoObtenido, nodoReal):
        """
        Inserta manualmente datos de ubicación en la tabla 'ipcol.ubicaciOn'.
        Parámetros:
          ciudadReal (str): Nombre real de la ciudad.
          nodoObtenido (str): Nodo obtenido (por ejemplo, extraído del hostname).
          nodoReal (str): Nodo real (confirmado manualmente).
        Retorna:
          str: Mensaje de éxito o error en la inserción.
    
        Ejemplo:
          >>> mensaje = insert_manual_data("Bogota", "NODO1", "NodoReal1")
          >>> print(mensaje)
          "Datos manuales insertados correctamente"
        """
        try:
            conn = mariadb.connect(
                user="root",
                password="Trul-f87",
                host="172.18.93.210",
                port=3306,
                database="ipcol"
            )
            cur = conn.cursor()
            query = "INSERT INTO ipcol.ubicaciOn (region, Ciudad, Nodo, NodoReal) VALUES (%s, %s, %s, %s)"
            objValue = ("NULL", ciudadReal, nodoObtenido, nodoReal)
            cur.execute(query, objValue)
            conn.commit()
            cur.close()
            conn.close()
            return "Datos manuales insertados correctamente"
        except mariadb.Error as e:
            return f"Error insertando datos manuales: {e}"
    
    
    def get_processed_values():
        """
        Retorna un diccionario con los parámetros procesados del dispositivo.
        Retorna:
          dict: Diccionario con claves y valores de los parámetros procesados:
                - CIUDAD, NODO, Nodito, hostname, IP_DCN, Vendor, OS_TYPE, Modelo, vrf, mgmtInt.
        """
        return {
            "CIUDAD": ciudad,
            "NODO": nodo,
            "Nodito": nodito,
            "hostname": hostname,
            "IP_DCN": hostnameClient,
            "Vendor": vendor,
            "OS_TYPE": ios,
            "Modelo": modelo,
            "vrf" : vrf,
            "mgmtInt" : mgmtInt
        }
    
    
    # =============================================================================
    # Funciones para Ejecución y Configuración Global
    # =============================================================================
    def ejec_funciones():
        """
        Ejecuta la configuración global en función de las opciones definidas en la lista global 'options'.
        Descripción:
          - Si "ISE" está en options, ejecuta la configuración ISE.
          - Si "Usuario Rancid" está en options, ejecuta la configuración del usuario rancid.
          - Si "Servidor Rancid" está en options, establece una conexión SSH con el servidor Rancid,
            configura el servidor y cierra la conexión.
          - Si "Syslog" está en options, ejecuta la configuración Syslog.
          - Finalmente, inserta los datos del dispositivo en la base de datos llamando a ipInsert().
        """
        if "ISE" in options:
            commandList = commandISE()
            configureISE(shellClient, commandList)
        if "Usuario Rancid" in options:
            commandList = commandRancid()
            userRancid(shellClient, commandList)
        if "Servidor Rancid" in options:
            shellRancid, rOut = crearConexionSSH('172.18.12.202', rancid, port="22", username="root", password="Pongal3un0", vendor="Linux")
            configurarServidorRancid(shellRancid)
            shellRancid.close()
            rancid.close()
        if "Syslog" in options:
            commandList = commandSyslog()
            configureSyslog(shellClient, commandList)
        ipInsert()
    
    
    def ejecutar_configuracion(os_type, equipo_type, host, optionsGUI, username, password):
        """
        Orquesta la ejecución de la configuración de un dispositivo. 
        Descripción:
          - Se asignan variables globales (ios, equipo, hostnameClient, options, shellClient) a partir de los parámetros recibidos.
          - Dependiendo del tipo de IOS (XE, XR o de otro), se establece la conexión SSH usando credenciales.
          - Se extraen parámetros del dispositivo usando findParameteres().
          - Según las opciones seleccionadas en optionsGUI (por ejemplo, "ISE", "Usuario Rancid", "Syslog"),
            se genera una lista de comandos y se formatea la salida con printCommands().
          - Retorna dos mensajes: uno general (indicando que la configuración se inició) y otro con la lista formateada de comandos.
    
        Parámetros:
          os_type (str): Tipo de IOS ("XE", "XR", u otro).
          equipo_type (str): Tipo de dispositivo ("Switch" o "Router").
          host (str): Dirección IP del dispositivo.
          optionsGUI (list): Lista de opciones seleccionadas en la interfaz (por ejemplo, ["ISE", "Usuario Rancid", "Syslog"]).
          username (str): Nombre de usuario para la conexión SSH.
          password (str): Contraseña para la conexión SSH.
    
        Retorna:
          tuple: (general_output, cli_output)
            - general_output (str): Mensaje base indicando el inicio de la configuración.
            - cli_output (str): Cadena formateada con los comandos que se ejecutarán.
        """
        global hostnameClient, vendor, ios, options, equipo, shellClient
        ios = os_type
        equipo = equipo_type
        hostnameClient = host
        options = optionsGUI
        cli_output = ""
        general_output = f"Ejecutando configuración para dispositivo con IOS {ios} en {host}\n"
       
        if ios == "XE" or ios == "XR":
            vendor = "cisco"
            shellClient, out_conn = crearConexionSSH(host, client, username=username, password=password)
        else:
            print("Hola")
            vendor = "juniper"
            shellClient, out_conn = crearConexionSSH(host, client, username=username, password=password, vendor="juniper")
        findParameteres(shellClient)
        if "ISE" in options:
            commandList = commandISE()
            cli_output += printCommands(commandList)
        if "Usuario Rancid" in options:
            commandList = commandRancid()
            cli_output += printCommands(commandList)
        if "Syslog" in options:
            commandList = commandSyslog()
            cli_output += printCommands(commandList)
        return general_output, cli_output
