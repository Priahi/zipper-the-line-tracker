package com.example.robotcontroller;

import android.annotation.SuppressLint;
import android.bluetooth.BluetoothAdapter;
import android.bluetooth.BluetoothDevice;
import android.bluetooth.BluetoothSocket;
import android.content.Intent;
import android.graphics.Rect;
import android.os.Build;
import android.os.Handler;
import android.os.Message;
import android.util.Log;
import android.view.MotionEvent;
import android.view.View;
import android.widget.Button;
import android.widget.ImageView;
import android.widget.Toast;
import androidx.annotation.Nullable;
import androidx.annotation.RequiresApi;
import androidx.appcompat.app.AppCompatActivity;
import android.os.Bundle;

import java.io.IOException;
import java.util.Set;
import java.util.UUID;

import java.io.InputStream;
import java.io.OutputStream;

public class MainActivity extends AppCompatActivity {
    private static final int REQUEST_ENABLE_BT = 1;
    private final BluetoothAdapter bluetoothAdapter = BluetoothAdapter.getDefaultAdapter();
    private static final String PI_ADDRESS = "DC:A6:32:30:25:A9";
    private ClientThread clientThread;

    private float dX = 0;
    private float dY = 0;
    private Rect rect;

    private float joystickX;
    private float joystickY;

    @SuppressLint("ClickableViewAccessibility")
    @RequiresApi(api = Build.VERSION_CODES.O)
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        // setting a listener that checks when the connect button is pressed
        Button connect_bt = findViewById(R.id.connect);
        connect_bt.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                // checks if device has bluetooth
                if (bluetoothAdapter != null) {
                    // checks if bluetooth is on and if not, request user to turn on bluetooth
                    if (!bluetoothAdapter.isEnabled()) {
                        Intent enableBtIntent = new Intent(BluetoothAdapter.ACTION_REQUEST_ENABLE);
                        startActivityForResult(enableBtIntent, REQUEST_ENABLE_BT);
                    } else {
                        // if bluetooth is enabled, connect to the robot
                        connectBluetooth();
                    }
                }
            }
        });

        // listener for demo button that sends demo direction to raspberry pi if connection exists
        Button demo = findViewById(R.id.demo);
        demo.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                if (clientThread != null)
                    clientThread.connectedThread.write("Demo".getBytes());
            }
        });

        final ImageView joystick = findViewById(R.id.joystick);
        final ImageView joystick_out = findViewById(R.id.joystick_out);


        // main touch listener for the joystick
        joystick_out.setOnTouchListener(new View.OnTouchListener() {
            @Override
            public boolean onTouch(View v, MotionEvent event) {
                // checks if the user just touched the joystick, if it is moving the joystick or
                // if the user has just let go
                switch (event.getAction()) {
                    case MotionEvent.ACTION_DOWN:
                        // stores the current location of the joystick, corresponding to the centre
                        joystickX = joystick.getLeft();
                        joystickY = joystick.getTop();

                        // checks the displacement of the joystick and the location of the screen
                        // touch
                        dX = joystick.getX() - event.getRawX();
                        dY = joystick.getY() - event.getRawY();
                        return true;

                    // case for when finger is being dragged across screen
                    case MotionEvent.ACTION_MOVE:
                        // if there is an active connection with the server, send the x and y
                        // coordinates of the joystick to the robot
                        if (clientThread != null)
                            clientThread.connectedThread.write(((int) joystick.getX() + "," + (int) joystick.getY()).getBytes());

                        // checks if the joystick is within the bounds of the outer joystick circle
                        // if outside, joystick is centered and the Stop directive is sent to the
                        // robot to cause it to stop
                        if (event.getRawX() > 575 || event.getRawX() < 175 ||
                            event.getRawY() > 1000 || event.getRawY() < 600) {
                            joystick.setX(joystickX);
                            joystick.setY(joystickY);
                            if (clientThread != null)
                                clientThread.connectedThread.write("Stop".getBytes());
                        } else {
                            // if the joystick is within the bounds of the outer circle, the joystick
                            // image is moved to the current location of the screen touch
                            joystick.animate()
                                    .x(event.getRawX() + dX)
                                    .y(event.getRawY() + dY)
                                    .setDuration(0)
                                    .start();
                        }
                        return true;

                    // case for when the screen is let go
                    case MotionEvent.ACTION_UP:
                        // centres the joystick again
                        joystick.animate()
                                .x(joystickX)
                                .y(joystickY)
                                .setDuration(0)
                                .start();
                        // if there is an active connection, direct robot to stop
                        if (clientThread != null)
                            clientThread.connectedThread.write("Stop".getBytes());
                        break;
                }
                return true;
            }
        });
    }

    // method for checking if bluetooth has been enabled upon a request
    @Override
    protected void onActivityResult(int requestCode, int resultCode, @Nullable Intent data) {
        super.onActivityResult(requestCode, resultCode, data);
        if (requestCode == REQUEST_ENABLE_BT) {
            if (resultCode == RESULT_OK) {
                connectBluetooth();
            } else {
                Toast.makeText(this, "Bluetooth not approved", Toast.LENGTH_SHORT);
            }
        }
    }

    // method for searching through paired devices and getting the bluetooth device corresponding
    // to the raspberry pi
    private void connectBluetooth() {
        boolean found = false;
        BluetoothDevice pi = null;
        // gets all devices that have been paired to the current android device
        Set<BluetoothDevice> paired_devices = bluetoothAdapter.getBondedDevices();
        if (paired_devices.size() > 0) {
            // loops through all previously paired devices until pi is found
            for (BluetoothDevice bd : paired_devices) {
                if (bd.getAddress().equals(PI_ADDRESS) || bd.getName().equals("raspberrypi")) {
                    found = true;
                    pi = bd;
                }
            }
        }

        if (!found) {
            Toast.makeText(this, "Device not found", Toast.LENGTH_SHORT).show();
        } else {
            clientThread = new ClientThread(pi);
            clientThread.run();
        }
    }

    private class ClientThread extends Thread {
        private final String TAG = ClientThread.class.getName();
        private final BluetoothSocket mmSocket;
        private final BluetoothDevice mmDevice;
        private boolean connected;
        public ConnectedThread connectedThread;

        private final UUID MY_UUID = UUID.fromString("94f39d29-7d6d-437d-973b-fba39e49d4ee");

        public ClientThread(BluetoothDevice device) {
            // Use a temporary object that is later assigned to mmSocket
            // because mmSocket is final.
            BluetoothSocket tmp = null;
            mmDevice = device;
            connected = false;

            try {
                // Get a BluetoothSocket to connect with the given BluetoothDevice.
                // MY_UUID is the app's UUID string, also used in the server code.
                tmp = device.createRfcommSocketToServiceRecord(MY_UUID);
            } catch (IOException e) {
                Log.e(TAG, "Socket's create() method failed", e);
            }
            mmSocket = tmp;
        }

        public void run() {
            // Cancel discovery because it otherwise slows down the connection.
            bluetoothAdapter.cancelDiscovery();

            try {
                // Connect to the remote device through the socket. This call blocks
                // until it succeeds or throws an exception.
                mmSocket.connect();
            } catch (IOException connectException) {
                // Unable to connect; close the socket and return.
                try {
                    mmSocket.close();
                } catch (IOException closeException) {
                    Log.e(TAG, "Could not close the client socket", closeException);
                }
                return;
            }

            // The connection attempt succeeded. Perform work associated with
            // the connection in a separate thread.
            manageMyConnectedSocket(mmSocket);
        }

        // Closes the client socket and causes the thread to finish.
        public void cancel() {
            try {
                mmSocket.close();
            } catch (IOException e) {
                Log.e(TAG, "Could not close the client socket", e);
            }
        }

        private void manageMyConnectedSocket(BluetoothSocket socket) {
            connected = true;
            Toast.makeText(MainActivity.this,
                    "Successfully connected to device with address: " + mmDevice.getAddress(),
                    Toast.LENGTH_LONG).show();
            connectedThread = new ConnectedThread(socket);
            //connectedThread.run();
        }
    }

    private static final String TAG = "MY_APP_DEBUG_TAG";
    private Handler handler; // handler that gets info from Bluetooth service

    // Defines several constants used when transmitting messages between the
    // service and the UI.
    private interface MessageConstants {
        public static final int MESSAGE_READ = 0;
        public static final int MESSAGE_WRITE = 1;
        public static final int MESSAGE_TOAST = 2;

        // ... (Add other message types here as needed.)
    }

    private class ConnectedThread extends Thread {
        private final BluetoothSocket mmSocket;
        private final InputStream mmInStream;
        private final OutputStream mmOutStream;
        private byte[] mmBuffer; // mmBuffer store for the stream

        public ConnectedThread(BluetoothSocket socket) {
            mmSocket = socket;
            InputStream tmpIn = null;
            OutputStream tmpOut = null;

            handler = new Handler();

            // Get the input and output streams; using temp objects because
            // member streams are final.
            try {
                tmpIn = socket.getInputStream();
            } catch (IOException e) {
                Log.e(TAG, "Error occurred when creating input stream", e);
            }
            try {
                tmpOut = socket.getOutputStream();
            } catch (IOException e) {
                Log.e(TAG, "Error occurred when creating output stream", e);
            }

            mmInStream = tmpIn;
            mmOutStream = tmpOut;
        }

        public void run() {
            mmBuffer = new byte[1024];
            int numBytes; // bytes returned from read()

            // Keep listening to the InputStream until an exception occurs.
            while (true) {
                try {
                    // Read from the InputStream.
                    numBytes = mmInStream.read(mmBuffer);
                    // Send the obtained bytes to the UI activity.
                    Message readMsg = handler.obtainMessage(
                            MessageConstants.MESSAGE_READ, numBytes, -1,
                            mmBuffer);
                    readMsg.sendToTarget();
                } catch (IOException e) {
                    Log.d(TAG, "Input stream was disconnected", e);
                    break;
                }
            }
        }

        // Call this from the main activity to send data to the remote device.
        public void write(byte[] bytes) {
            try {
                mmOutStream.write(bytes);

                // Share the sent message with the UI activity.
                Message writtenMsg = handler.obtainMessage(
                        MessageConstants.MESSAGE_WRITE, -1, -1, mmBuffer);
                writtenMsg.sendToTarget();
            } catch (IOException e) {
                Toast.makeText(MainActivity.this, "Error occurred when sending data", Toast.LENGTH_LONG);
                Log.e(TAG, "Error occurred when sending data", e);

                // Send a failure message back to the activity.
                Message writeErrorMsg =
                        handler.obtainMessage(MessageConstants.MESSAGE_TOAST);
                Bundle bundle = new Bundle();
                bundle.putString("toast",
                        "Couldn't send data to the other device");
                writeErrorMsg.setData(bundle);
                handler.sendMessage(writeErrorMsg);
            }
        }

        // Call this method from the main activity to shut down the connection.
        public void cancel() {
            try {
                mmSocket.close();
            } catch (IOException e) {
                Log.e(TAG, "Could not close the connect socket", e);
            }
        }
    }
}
