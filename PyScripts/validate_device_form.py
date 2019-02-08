import os
import socket
# Check the IP Address
def Check_IP(ip):
    pattern = '192.168.0.'
    if ip.find()
    return False


# Check the availability (ping response)
def Check_PingResponse():
    hostname = "google.com"
    response = os.system("ping -n 1 " + hostname)
    retval = False  # false by default
    if response == 0:
        retval = True

    return retval

print(Check_PingResponse())