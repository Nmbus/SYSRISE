from selenium import webdriver
import paramiko
import time
import re
import os
import sys
import mariadb


hostnameRancid = "172.18.12.202"
hostnameSyslog  = "172.18.11.242"

hostname = ""
hostnameClient = ""
ciudad = ""
vendor = ""
nodo = ""
ios = ""
modelo = ""
mgmtInt=""
vrf=""

client  = paramiko.SSHClient()
rancid  = paramiko.SSHClient()
syslog  = paramiko.SSHClient()


n2n = {
  "BELLO": "BELLO",             "BGACA": "BGACA",        "BGACN": "CENTRO",
  "BIOMX": "BIOMAX",            "BMACN": "BIMA",         "BQCNT": "CENTRO",
  "BQPRD": "PRADO",             "BQMTP": "METROPARQUE",  "BZT": "BAZURTO",
  "CALPA": "PASOANCHO",         "CALSM": "STA MONICA",   "CELTA": "CELTA",
  "CHA": "CHAPINERO",           "CNCUC": "CENTRO",       "CNIBA": "CENTRO",
  "CNSMA": "CENTRO",            "CNVVC": "7_DE_AGOSTO",  "CNXV3": "CXV",
  "CTX": "CFX",                 "CTXCN": "CFX",          "CZCNT": "CENTRO",
  "GIOTA": "GIRARDOTA",         "IBMCN": "IBM CALLE 100","IPIAL": "IPIALES",
  "ITXZF": "ZONA FRANCA",       "KJICA": "CAJICA",       "LEVEL": "LEVEL3",
  "LZPTE": "PUENTE ARANDA",     "MDECE": "CENTRO",       "MDEFL": "FLYWAN",
  "MDETB": "ETB",               "MDETF": "TELEFONICA",   "MDFLY": "FLYWAN",
  "MDIFX": "IFX",               "MDMAY": "MAYORCA",      "MDMOL": "MOLINOS",
  "MOSQR": "MOSQUERA",          "MTCST": "MONTERIA",     "MUSEO": "MUSESO",
  "NAOSA": "TOCANCIPA_DC",      "NAOSB": "TOCANCIPA_DC", "NAOSBT": "NAOSBT_DC",
  "NBULA": "NEBULA",            "NEPAL": "NEPAL",        "NMBUS": "NIMBUS",
  "NPONT": "NORTHPOINT",        "NSUBA": "SUBA",         "ODATA": "ODATA",
  "PALVE": "PALMIRA VERSALLES", "PASTO": "PASTO",        "PL108": "PL108",
  "PM": "PROMIGAS",             "PPNCN": "NEGRET",       "PTSOL": "PTSOL",
  "RIONG": "RIONEGRO",          "ROD": "RODADERO",       "SANFE": "SANFE",
  "SIBER": "SIBERIA",           "TLPOR": "TELEPORT",     "TFZOF": "ZONA FRANCA - TELEFONICA",
  "TESUR": "TESUR",             "TRI": "TRIARA",         "TRIAR": "TRIARA",
  "VST": "VILLA SANTOS",        "VUPCN": "VALLEDUPAR",   "WBPCN": "WBP",
  "ZFTER": "ZONA FRANCA",       "7AGO": "7_DE_AGOSTO"
}

n2c = {
  "BELLO": "MEDELLIN",      "BGACA": "BUCARAMANGA",   "BGACN": "BUCARAMANGA",
  "BIOMX": "BOGOTA",        "BMACN": "BOGOTA",        "BQCNT": "BARRANQUILLA",
  "BQPRD": "BARRANQUILLA",  "BQMTP": "BARRANQUILLA",  "BZT": "CARTAGENA",
  "CALPA": "CALI",          "CALSM": "CALI",          "CELTA": "BOGOTA",
  "CHA": "BOGOTA",          "CNCUC": "CUCUTA",        "CNIBA": "IBAGUE",
  "CNSMA": "STA_MARTA",     "CNVVC": "VILLAVICENCIO", "CNXV3": "BOGOTA",
  "CTX": "CARTAGENA",       "CTXCN": "CARTAGENA",     "CZCNT": "SINCELEJO",
  "GIOTA": "MEDELLIN",      "IBMCN": "BOGOTA",        "IPIAL": "IPIALES",
  "ITXZF": "BOGOTA",        "KJICA": "BOGOTA",        "LEVEL": "BOGOTA",
  "LZPTE": "BOGOTA",        "MDECE": "MEDELLIN",      "MDEFL": "MEDELLIN",
  "MDETB": "MEDELLIN",      "MDETF": "MEDELLIN",      "MDFLY": "MEDELLIN",
  "MDIFX": "MEDELLIN",      "MDMAY": "MEDELLIN",      "MDMOL": "MEDELLIN",
  "MOSQR": "BOGOTA",        "MTCST": "MONTERIA",      "MUSEO": "BOGOTA",
  "NAOSA": "BOGOTA",        "NAOSB": "BOGOTA",        "NAOSBT": "BOGOTA",
  "NBULA": "BOGOTA",        "NEPAL": "BOGOTA",        "NMBUS": "BOGOTA",
  "NPONT": "BOGOTA",        "NSUBA": "BOGOTA",        "ODATA": "BOGOTA",
  "PALVE": "PALMIRA",       "PASTO": "PASTO",         "PL108": "BOGOTA",
  "PM": "CARTAGENA",        "PPNCN": "POPAYAN",       "PTSOL": "BOGOTA",
  "RIONG": "MEDELLIN",      "ROD": "SANTA MARTA",     "SANFE": "MEDELLIN",
  "SIBER": "BOGOTA",        "TLPOR": "BOGOTA",        "TFZOF": "BOGOTA",
  "TESUR": "BOGOTA",        "TRI": "BOGOTA",          "TRIAR": "BOGOTA",
  "VST": "BARRANQUILLA",    "VUPCN": "VALLEDUPAR",    "WBPCN": "BOGOTA",
  "ZFTER": "BOGOTA"
}



#def otsTicket():
    


def encontrarTodos(text, pattern):
    match = re.findall(pattern, text)
    return match if match else False

def encontrarTxt(text, pattern):
    match = re.search(pattern, text)
    try:
        return match.group(1) if match else ""
    except Exception:
        return "Error"

def crearConexionSSH(hostname, ssh_client, port="22", username="mguzman", password="4s7rRMaq", vendor = "cisco"):
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
            #shell.send(f"s {cr}")
    except Exception as e:
        output += f"Error al ejecutar el comando '{comando}': {e}\n"
    return output

def userRancid(shell, commandList):
    auxRancid = ingresarComando("show runn aaa | include rancid",shell)
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
                ingresarComando("configure terminal",shell) 
                ingresarComando("no username rancid",shell)
                ingresarComando("exit",shell)                
                for command in commandList:
                    ingresarComando(command,shell)
    else:
        for command in commandList:
            ingresarComando(command,shell)
        

def configureISE(shell, commandList):
    for command in commandList:
            ingresarComando(command,shell)
            
def configureSyslog(shell,commandList):
    for command in commandList:
        ingresarComando(command,shell)

def configurarServidorRancid(shell, hostname):
    global ciudad  
    output = ""
    output += ingresarComando("cd /usr/local/rancid/var/", shell)
    auxName   = ingresarComando("cat /etc/hosts | grep " + hostname, shell)
    auxIP     = ingresarComando("cat /etc/hosts | grep " + hostnameClient, shell)
    auxRouter = ingresarComando("cat " + ciudad + "/router.db | grep " + hostname + "[[:punct:]]", shell)
    flagName   = encontrarTodos(auxName, r'\b\d+\.\d+\.\d+\.\d+\b')
    flagIP     = encontrarTodos(auxIP, r"\b(?:[A-Z\d]+-)+[A-Z\d]+\b")
    flagRouter = encontrarTodos(auxRouter, r"(?:[A-Z\d]+-)+[A-Z\d]+\;")
    dns = [flagName, flagIP, flagRouter]
    output += "Datos DNS: " + str(dns) + "\n"
    if dns == [False, False, False]:
        output += ingresarComando("python m2a.py " + hostnameClient + " " + hostname + " " + ciudad + " cisco", shell)
    else:
        output += actualizarRancid(dns)
    return output

def actualizarRancid(dns):
    output = ""
    try:
        with open("prueba.txt", "r") as input_file:
            with open("prueba2.txt", "w") as output_file:
                for line in input_file:
                    flagN = True
                    flagI = True
                    for k in [0, 1]:
                        for selector in dns[k]:
                            if k == 0:
                                if line.strip("\n") == selector + " " + hostname:
                                    flagN = False
                                    break
                            else:
                                if line.strip("\n") == hostnameClient + " " + selector:
                                    flagI = False
                                    break
                    if flagN and flagI:
                        output_file.write(line)
        # os.replace("prueba2.txt", "prueba.txt")
        output += "Actualización de Rancid completada.\n"
    except Exception as e:
        output += f"Error al actualizar Rancid: {e}\n"
    return output

    
def findParameteres(shell,ios):
    global mgmtInt, vrf, ciudad, hostname, nodo, modelo
    mgmtInt=""
    vrf = ""
    ciudad = ""
    hostname = ""
    prefijos = ["MgmtEth", "GigabitEthernet", "FastEthernet", "TenGigabitEthernet", "Loopback", "Vlan", "Serial", "Port-channel"]
    indice = None
    if ios == "XE" or ios == "XR":
        auxHost=shell.recv(20000).decode("utf-8")
        hostname=encontrarTxt(auxHost,r'([^:#]+)#')
        hostname = hostname.strip()
        auxMgmtInt=(ingresarComando("show ip interface brief | include "+hostnameClient,shell))
        for prefijo in prefijos:
            try:
                indice = auxMgmtInt.index(prefijo)
                break;
            except ValueError:
                continue
        flag = False
        i = 0
        if indice == None:
            mgmtInt = "IP Virtual"
            auxVrf = ingresarComando("show runn | include virtual",shell)
            vrf = encontrarTxt(auxVrf,r"vrf\s+(\S+)")
        else:
            while flag == False:
                if auxMgmtInt[indice+i] == " ":
                   flag = True
                else:
                    mgmtInt=mgmtInt+auxMgmtInt[indice+i]
                    i = i+1
            auxVrf = ingresarComando("show runn interface "+mgmtInt+" | include vrf",shell)
            vrf = encontrarTxt(auxVrf,r"vrf (?:forwarding\s+)?(\S+)")
        auxModel = ingresarComando("show version | include processor",shell)
        modelo = encontrarTxt(auxModel,r'cisco (\S+)')
        
    #else:
        #auxHost = ingresarComando("show configuration | match host-name",shell)
        #hostname=encontrarTxt(auxHost,r'host-name (\S+)')
        #hostname = hostname.rstrip(';')
        #auxModel = ingresarComando("show version | match model",shell)
        #modelo = encontrarTxt(auxModel,r'Model: (\S+)')
        auxNodo = encontrarNodo()
        nodo = n2n[auxNodo]
        ciudad = n2c[auxNodo]
    #auxCiudad = "BOG"
    #try:
    #    for cod in ciudades:
    #        if encontrarTxt(hostname,cod) != "":
    #            auxCiudad = cod
    #            break
    #except:
    #        auxCiudad = "BOG"
    #ciudad = ciudades[auxCiudad] 
        
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

    
        
def commandRancid(ios):
    if ios == "XE":
        command_list = ["configure terminal","username rancid privilege 15 secret 5 $1$v811$vr0Qt5Y8A6WIeF0LK3V4N0","exit"]
    elif ios == "XR":
        command_list = ["configure terminal","username rancid","secret 5 $1$v811$vr0Qt5Y8A6WIeF0LK3V4N0","group root-lr","exit"]
    else: 
        command_list = ["configure",'set system login user rancid full-name "RANCID"',"set system login user rancid uid 2103","set system login user rancid class CN-ADMIN", 
        'set system login user rancid authentication encrypted-password "$5$Kx5R2kJQ$J1fCLPY6mmDDycl3PHOawYmwQqBXM3ybielOoXBzTlA"',"exit"]        
    return command_list
    
def commandISE(ios):
    if ios == "XE":
        command_list = ["configure terminal","aaa new-model","aaa group server tacacs+ ACS","server-private 172.18.4.27 key 7 0207050B52011B621E1A",
        "server-private 172.18.9.152 key 7 070E201C170E0D464546","ip vrf forwarding "+vrf, "ip tacacs source-interface "+mgmtInt,
        "aaa authentication login default group ACS local", "aaa authorization exec default group ACS local", "aaa authorization commands 1 default group ACS local",
        "aaa authorization commands 15 default group ACS local", "aaa authorization config-commands", "aaa authorization console","aaa accounting exec default",
        "action-type start-stop","group ACS","aaa accounting commands 15 default","action-type start-stop","group ACS","exit"]
    elif ios == "XR":
        command_list = ["configure terminal","aaa accounting exec default start-stop none","aaa accounting exec vtyACSacc start-stop group ACS none","aaa accounting commands default start-stop none",
        "aaa accounting commands vtyACSacc start-stop group ACS none","aaa group server tacacs+ ACS","vrf "+vrf,"server-private 172.18.4.27 port 49", "key 7 01120754020C124C7318",
        "!","server-private 172.18.9.152 port 49","key 7 070E201C170E0D464546","!","!","aaa authorization exec default group ACS local","aaa authorization commands default group ACS none",
        "aaa authorization commands vtyACSautho group ACS none","aaa authorization commands vtycommands group ACS none","aaa authentication login vtyACS group ACS local",
        "aaa authentication login default group ACS local","exit"]
    else:
        command_list = ["configure","set system authentication-order radius","set system radius-server 172.18.4.27 port 1812","set system radius-server 172.18.4.27 accounting-port 1813",
        'set system radius-server 172.18.4.27 secret "$9$A2k-p1R8LNsgJVwmTQz/9uO1REcKMX-b2"',"set system radius-server 172.18.4.27 source-address "+hostnameClient,
        "set system radius-server 172.18.9.152 port 1812","set system radius-server 172.18.9.152 accounting-port 1813",'set system radius-server 172.18.9.152 secret "$9$gkoUjF3901htu87N-sYaZUjik5QnCpB"',
        "set system radius-server 172.18.9.152 source-address "+hostnameClient, "set system accounting events interactive-commands","set system accounting destination radius server 172.18.4.27 port 1812",
        "set system accounting destination radius server 172.18.4.27 accounting-port 1813",'set system accounting destination radius server 172.18.4.27 secret "$9$-mV24.mT6CuFnyKvMx7bs24oJikPQ39"',
        "set system accounting destination radius server 172.18.4.27 source-address "+hostnameClient,"set system accounting destination radius server 172.18.9.152 port 1812",
        "set system accounting destination radius server 172.18.9.152 accounting-port 1813",'set system accounting destination radius server 172.18.9.152 secret "$9$gkoUjF3901htu87N-sYaZUjik5QnCpB"',
        "set system accounting destination radius server 172.18.9.152 source-address "+hostnameClient,"set firewall family inet filter protect-re term accept-radius from source-address "+hostnameClient+"/32",
        "set firewall family inet filter protect-re term accept-radius from source-address 172.18.4.27/32", "set firewall family inet filter protect-re term accept-radius from source-address 172.18.9.152/32",
        "set firewall family inet filter protect-re term accept-radius from source-port 1812","set firewall family inet filter protect-re term accept-radius from source-port 1813",
        "set firewall family inet filter protect-re term accept-radius then accept","exit"]
    return command_list
    
def commandSyslog(ios):
    if ios == "XE":
        command_list = ["configure terminal","archive","log config","logging enable","notify syslog","hidekeys","notify syslog contenttype plaintext",
        "logging host 172.18.11.242 vrf "+vrf,"logging origin-id hostname","exit"]
    elif ios == "XR":
        command_list = ["configure terminal","logging 172.18.11.242 vrf "+vrf+" severity info port default", "logging source-interface "+mgmtInt+" vrf "+vrf, "logging hostnameprefix "+hostname,"exit"]
    else:
        command_list=["configure","set system syslog user * any emergency","set system syslog host 172.18.11.242 any any","set system syslog host 172.18.11.242 daemon any",
        "set system syslog host 172.18.11.242 kernel any","set system syslog host 172.18.11.242 firewall notice","set system syslog host 172.18.11.242 interactive-commands any",
        "set system syslog host 172.18.11.242 log-prefix "+hostname, "set system syslog host 172.18.11.242 source-address "+hostnameClient,"set system syslog host 172.18.11.242 explicit-priority",
        "set system syslog file messages any notice","set system syslog file messages authorization info","set system syslog file interactive-commands any any",
        "set system syslog file interactive-commands explicit-priority","exit"]
    return command_list
    
def printCommands(commandList):
    output = ""
    for command in commandList[1:-1]:
        output += hostname+"(config)# "+command+"<br>"
    return output
    
def ipSelect(host):
   
    try:
        conn = mariadb.connect(
            user="root",
            password="Trul-f87",
            host="172.18.93.210",
            port=3306,
            database="ipcol"
        )
        cur = conn.cursor()
        query = "SELECT * FROM ipcol.switches WHERE IP_DCN IN ('"+host+"');"
        cur.execute(query)
        row = cur.fetchone() 
        columns = [desc[0] for desc in cur.description]
        if row is None:
            return None
        else:
            device_info = dict(zip(columns, row))
            return device_info
        cur.close()
        conn.close()
    except mariadb.Error as e:
        return f"Error connecting to DB: {e}"
        
        
def ipInsert():
    try:
        conn = mariadb.connect(
            user="root",
            password="Trul-f87",
            host="172.18.93.210",
            port=3306,
            database="ipcol"
        )
        cur = conn.cursor()
        query = "INSERT INTO ipcol.switches (CIUDAD, NODO, hostname, IP_DCN, Vendor, OS_TYPE,Modelo) VALUES (%s, %s, %s, %s, %s, %s, %s)"
        objValue= (ciudad, nodo, hostname, hostnameClient,vendor, ios, modelo)
        cur.execute(query,objValue)
        conn.commit()
        cur.close()
        conn.close()
        return f"{hostname} added to DB"
    except mariadb.Error as e:
        return f"Error connecting to DB: {e}"

def get_processed_values():
    """Devuelve un diccionario con los valores actualizados después del procesamiento."""
    return {
        "CIUDAD": ciudad,
        "NODO": nodo,
        "hostname": hostname,
        "IP_DCN": hostnameClient,
        "Vendor": vendor,
        "OS_TYPE": ios,
        "Modelo": modelo
        }



def process_logic():

    print("Hola")


def ejecutar_configuracion(os_type, host, options):
    global hostnameClient, vendor, ios
    ios = os_type
    hostnameClient = host
    cli_output = ""
    general_output = f"Ejecutando configuración para dispositivo con IOS {ios} en {host}\n"
   
    if ios == "XE" or ios == "XR":
        vendor = "CISCO"
        shellClient, out_conn = crearConexionSSH(host, client)
    else:
        vendor = "JUNIPER"
        shellClient, out_conn = crearConexionSSH(host, client,vendor="juniper" )
    #general_output += "\n"+out_conn
    findParameteres(shellClient,ios)
    general_output += "\nHostname: "+hostname+"<br>Interfaz Management: "+mgmtInt+"<br>Vrf: "+vrf+"<br>Ciudad: "+ciudad+"<br>Nodo: "+nodo+"<br>Modelo: "+modelo+"<br>Vendor: "+vendor
                    
    if "ISE" in options:
        commandList = commandISE(ios)
        cli_output += printCommands(commandList)
        #    #configureISE(shellClient,commandList)
    if "Usuario Rancid" in options:
        commandList = commandRancid(ios)
        cli_output += printCommands(commandList)
            #userRancid(shellClient,commandList)
        #if "Syslog" in options:
        #    commandList = commandSyslog(ios)
        #    cli_output += printCommands(commandList)
        #    #configureSyslog(shellClient,commandList)
    return general_output, cli_output



if __name__ == '__main__':
    options = webdriver.ChromeOptions()
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    driver = webdriver.Chrome(executable_path='C:\ProgramData\Microsoft\Windows\Start Menu\Programs', options=options)
    webDriver.get('https://ots.lla.com/')