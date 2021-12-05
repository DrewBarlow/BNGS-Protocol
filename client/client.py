from socket import socket, AF_INET, SOCK_STREAM

# i like bingus :)
bingus: str = """
   ````````                                                       ```.......``  
     ``......```                                              ```.---::.``      
       .--::---..````                                      ```..--:::/:`    `   
       .:::////:--...```                                 ```.--:///////-. `...``
      `-://+oooo+/:---.```                               ```.:+oooo++/::-.``..``
  ```.--::/+osssso/:--.```                                ```-osssso+//:-.``  `.
  `....-::/+osss+/:--.````          ``````````````         ```-+osso+/::-.``    
.`:` ``.:://++/:---.```````````````````````````````   `````````.-:/++//:-`      
 `.-``  -:::--..````````````````````````````````````````..``````...-::/:.`      
    `.   -..`````````..-:::--...---.....```````````.....--...://:-....-- :      
          `````````.-:/oyyyyso+:::::---............---::::/oyhhhs+:...` `-    ``
          `.........:/shyhhhhhhyo///:::------------::://+yhhhhddds/-..  :     ``
           .--.....--+yhhdddddddho+///:::--------:::///ohddddddddy/-.` `-    `.`
            `..------+yhddmmmmddyso+/::::--------::///+shddmmmmmds/-.  :   -`  `
             .:::----:oyddmmmmdyoso+:::-----..----::://osyhddddy+/:-` `-  `     
              .:---::::/++ssssoooo+/:-----......--::::/+ooooo+/::--- `/-        
              `-::::::://///////:::::----.......---::::::::::::::::``.o.` `.`   
               -:::::////////:::-----......```...-----...--:::///: ` :`   .-.`.`
               --:::////////:::--.......````````.......`...-::///`  `-   `-`    
    ``.`      `--:://///////:::--.....```````````.....`...--:///`   :   `-      
    ..        --::://+++++////::---...``````````........---:///`  :.-   -       
     .`       --:::///++++++//:::----..`..........---..--:::/:`  -.-`  -`       
      :      `--:::://++++++//::::::---.-------::::::::::://-   -.`-  -`        
      `.    .----:::://++++++/::::::::::::++++ooooso+/////+/:` .. -` .`         
     ` -` `-------::://///++++////////////+ossyyyssooo+ooo++/:.`. - ..          
     ``.``------:::::::////++++++++++++++++osyhhysooossssoo++/:    `.           
        `------::://///////+++++ooooooooooossyyyssssssssssoo++/`` `-            
        .-------::///++++++++oooooooossssssssyyyyyyyyyyyssooo+/  .:             
      `----------::://///++++++oooooossssssysyyyyyyyyyyyssooo++-.-/`            
.    `------------::::///////++++ooosssssyyyyyyyyyyyyyyysssoo++++..             
`.- ---.....------:::::://////++++ooosssssyyyyyyyyyyyyysssoo++++/               
"""

def main() -> None:
    try:
        # establish a connection, send a greeting since we need a response
        sock: socket = socket(AF_INET, SOCK_STREAM)
        sock.connect(("127.0.0.1", 13037))
        sock.send("HELLO".encode())
        print(bingus)

        # I like this little icon for messages from the server
        print(">|", sock.recv(4096).decode())

        # hold connection open continuously until "BYE" is input
        while True:
            inp = input("|> ")
            print()

            # the app breaks for some reason if we input a newline,
            # so we need a case for it
            if inp == '\n':
                print("!! Bad input, failed to send it to server.")
                continue

            # send our query, then break if we wish to logout
            sock.send(inp.encode())
            if inp.lower() == "bye": break

            # print out the server's response
            out = sock.recv(4096)
            print(f">| {out.decode()}")
        sock.close()
    except:
        print("Failed to connect to the server.")

if __name__ == "__main__":
    main()
