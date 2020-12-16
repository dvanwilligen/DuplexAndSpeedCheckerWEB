from netmiko import ConnectHandler
import datetime

def speedandduplex_cisco(hostname, username, password, secret, port):
    hostname = hostname.strip('\n\t')
    username = username.strip('\n\t')
    password = password.strip('\n\t')
    secret = secret.strip('\n\t')
    port = int(port)
    print("test")
    CurrentDeviceDef = {
        'device_type': 'cisco_ios',
        'host': hostname,
        'username': username,
        'password': password,
        'secret': secret,
        'port': port,
            }
    CurrentDevice = ConnectHandler(**CurrentDeviceDef)
    CurrentDevice.enable()
    CurrentDevice.send_command("terminal length 0")
    hostname = CurrentDevice.send_command("show run | include hostname")
    hostname = hostname.split()
    hostname = hostname[1]
    CurrentDevice.send_command("terminal length 0")
    output1 = []
    output1 = CurrentDevice.send_command("show interfaces status")
    output1 = output1.splitlines()
    FinalOutput = []
    CurrentDevice.disconnect()
    print(len(output1))
    #FinalOutput.append(hostname)
    for line in output1:
        line = line.split()
        FinalOutput.append(line)
    return FinalOutput
