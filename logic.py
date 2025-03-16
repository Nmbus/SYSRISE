from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import paramiko
import time
import re
import os
import sys
import mariadb
import json

hostnameRancid = "172.18.12.202"
hostnameSyslog  = "172.18.11.242"

hostname = ""
hostnameClient = ""
ciudad = ""
vendor = ""
nodo = ""
nodito = ""
ios = ""
equipo = ""
modelo = ""
mgmtInt = ""
vrf = ""
options=[]
client  = paramiko.SSHClient()
rancid  = paramiko.SSHClient()
syslog  = paramiko.SSHClient()

def otsTicket():
    driver = webdriver.Chrome()
    driver.get('https://identity.lla.com/app/servicedesk/exk1s9tlsit5TGKwm1d8/sso/saml?SAMLRequest=fZJLT8MwEIT%2FSuR76yaEtLXaSoUKqHhVNHDgghxnAxaOHbwb2v570oSnBFzX88141p6gLE0l5jU92Rt4qQEp2JbGomgPpqz2VjiJGoWVJaAgJdbzywsR9Qei8o6ccoZ9Q%2F4nJCJ40s6yYLmYsocsivJEDhXEB6DyqEjGo2KUJaMoTsaZzAo1zIpsmIzjkAV34LEhp6wxanDEGpYWSVpqRoPosDc46IVhGg1EnIg4vmfBommjraSWeiKqUHCuc7Ckadc3RvaVK7msKt7c6lUryAGfOWyfQxyTQU2H6en5pgzzEUd0fF%2BPBfOPCsfOYl2CX3fs7c3FV4gj%2FPTvsNX7ro60zbV9%2FH9NWSdCcZamq97qep2y2WTvI9rafvZLzoR%2FF0y6d71qrJeLlTNa7YIT50tJfyeH%2FbCd6LxXtFJRW6xA6UJD3hQ3xm2OPUiCKSNfA%2BOzLvTn%2F5m9AQ%3D%3D&RelayState=https%3A%2F%2Fots.lla.com%2Fauth%2Flogin%2Ftype%2Fsaml%3Fnext%3D')
    time.sleep(2)
    username = driver.find_element(By.ID, "input28")
    username.send_keys("1871713@cwc.com")
    lgButton = driver.find_element(By.XPATH, "//input[@value='Next']")
    lgButton.click()

def encontrarTodos(text, pattern):
    match = re.findall(pattern, text)
    return match if match else False

def encontrarTxt(text, pattern):
    match = re.search(pattern, text)
    try:
        return match.group(1) if match else ""
    except Exception:
        return "Error"

def crearConexionSSH(hostname, ssh_client, port="22", username=None, password=None, vendor="cisco"):
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
                shell.send("enable\n")
            time.sleep(1)
        return shell, output
    except Exception as e:
        output += f"No fue posible establecer la conexión: {e}\n"
        return None, output

def ingresarComando(comando, shell, cr="\n"):
    output = ""
    try:
        shell.send(f"{comando}{cr}")
        time.sleep(3)
        if shell.recv_ready():
            output = shell.recv(10000).decode("utf-8")
    except Exception as e:
        output += f"Error al ejecutar el comando '{comando}': {e}\n"
    return output

def userRancid(shell, commandList):
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
    for command in commandList:
        ingresarComando(command, shell)

def configureSyslog(shell, commandList):
    for command in commandList:
        ingresarComando(command, shell)

def configurarServidorRancid(shell):
    ingresarComando("cd /usr/local/rancid/var/", shell)
    auxName = ingresarComando("cat /etc/hosts | grep --color=never " + hostname, shell)
    auxIP = ingresarComando("cat /etc/hosts | grep --color=never " + hostnameClient, shell)
    auxRouter = ingresarComando("cat " + ciudad + "/router.db | grep --color=never " + hostname + "[[:punct:]]", shell)
    flagName = encontrarTodos(auxName, r'\b\d+\.\d+\.\d+\.\d+\b')
    flagIP = encontrarTodos(auxIP, r"\b(?:[A-Z\d]+-)+[A-Z\d]+\b")
    flagRouter = encontrarTodos(auxRouter, r"(?:[A-Za-z0-9]+(?:-[A-Za-z0-9]+)*);(?:[^;\r\n]+);(?:[^;\r\n]+)")
    dns = [flagName, flagIP, flagRouter]
    dnsStr = json.dumps(dns)
    ingresarComando('python m2a.py "{}" "{}" "{}" "{}" \'{}\''.format(hostnameClient, hostname, ciudad, vendor, dnsStr), shell)
    print('python m2a.py "{}" "{}" "{}" "{}" \'{}\''.format(hostnameClient, hostname, ciudad, vendor, dnsStr))

def findParameteres(shell):
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

def commandRancid():
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
    output = ""
    for command in commandList[1:-1]:
        output += hostname + "(config)# " + command + "<br>"
    return output

def ipSelect(host, equipo):
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
            query = "SELECT row_id, CIUDAD, Nodo, hostname,IP_DCN, ROL, OS_type, Modelo FROM ipcol.routers WHERE IP_DCN IN ('" + host + "');"
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
    
def mi_funcion():
    if "ISE" in options:
        commandISE()
    if "Usuario Rancid" in options:
        commandRancid()
    if "Servidor Rancid" in options:
        shellRancid, rOut = crearConexionSSH('172.18.12.202', rancid, port="22", username="root", password="Pongal3un0", vendor="Linux")
        configurarServidorRancid(shellRancid)
        shellRancid.close()
        rancid.close()
    if "Syslog" in options:
        commandSyslog()
    ipInsert()
   
def ejecutar_configuracion(os_type, equipo_type, host, optionsGUI, username, password):
    global hostnameClient, vendor, ios, options, equipo
    ios = os_type
    equipo = equipo_type
    hostnameClient = host
    options = optionsGUI
    cli_output = ""
    # Mensaje base de la configuración
    general_output = f"Ejecutando configuración para dispositivo con IOS {ios} en {host}\n"
   
    if ios == "XE" or ios == "XR":
        vendor = "cisco"
        shellClient, out_conn = crearConexionSSH(host, client, username=username, password=password)
    else:
        print("Hola")
        vendor = "juniper"
        shellClient, out_conn = crearConexionSSH(host, client, username=username, password= password, vendor="juniper")
    findParameteres(shellClient)
    # Imprimir la lista de comandos en la shell según las opciones seleccionadas
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

if __name__ == '__main__':
    hostname = '172.18.76.66'
    hostnameClient = 'COL-IPIAL-ME3600-01'
    shellRancid, rOut = crearConexionSSH('172.18.12.202', rancid, port="22", username="root", password="Pongal3un0", vendor="Linux")
    configurarServidorRancid(shellRancid)
    #print(actualizarRancid(['172.18.76.66','COL-IPIAL-ME3600-01']))
