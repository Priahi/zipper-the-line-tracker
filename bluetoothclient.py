import bluetooth

bd_addr = "DC:A6:32:30:25:AC" #pi's bluetooth address here?

port = 1

sock=bluetooth.BluetoothSocket( bluetooth.RFCOMM )
sock.connect((bd_addr, port))

sock.send("hello asdf!!")

print("finished client request")

sock.close()