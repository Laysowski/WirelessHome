import subprocess


# Check the IP Address
def check_IP(ip):
        pattern = '192.168.0.'
        if ip.find(pattern) != 0: return False  # there is something before the pattern / there is no pattern
        last_oct = ip.replace(pattern, '')  # check the last octet
        if last_oct.find('.') >= 0: return False  # there are more commas
        if not (1 < int(last_oct) < 50): return False  # IP in range <2 - 49>
        return True


# Check the availability (ping response)
def check_PingResponse(ip):
        ping_response = subprocess.Popen(["ping.exe", "-n", "1", ip], stdout=subprocess.PIPE).communicate()[0]
        if('unreachable' in str(ping_response)): return False
        return True


# General function
def validateIP(ip):
        return check_IP(ip) and check_PingResponse(ip)

