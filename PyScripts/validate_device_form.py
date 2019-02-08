import os
import socket
# Check the IP Address
def Check_IP(ip):
        pattern = '192.168.0.'
        if ip.find(pattern) != 0: return False  # there is something before the pattern / there is no pattern
        last_oct = ip.replace(pattern, '')  # check the last octet
        if last_oct.find('.') >= 0: return False  # there are more commas
        if not (1 < int(last_oct) < 50): return False  # IP in range <2 - 49>

        return True


# Check the availability (ping response)
def Check_PingResponse(ip):
        response = os.system("ping -n 1 " + ip)
        if response == 0: return True
        return False


def ValidateIP(ip):
        return Check_IP(ip) and Check_PingResponse(ip)


iptest = '192.168.0.33'
print(Check_IP(iptest))
print(Check_PingResponse(iptest))
print(ValidateIP(iptest))