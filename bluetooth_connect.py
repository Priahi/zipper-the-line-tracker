import bluetooth

#target_name = "Amir's MacBook Pro"
target_address = "A4:83:E7:1F:0A:48"
connected = False

port = 3

while (not connected):

    nearby_devices = bluetooth.discover_devices()

    for bdaddr in nearby_devices:
        print(bdaddr, ":", bluetooth.lookup_name(bdaddr))
        if target_address == bdaddr:
            connected = True
            break

print("Found target bluetooth device with address ", target_address)

sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
try:
    sock.connect((target_address, port))
except(bluetooth.BluetoothError):
    print("Failed to connect")

sock.send("hello!")

sock.close()
