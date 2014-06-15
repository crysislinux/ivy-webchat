package com.ivy.bridge;

import android.util.Log;

import com.google.gson.JsonElement;
import com.google.gson.JsonObject;
import com.google.gson.JsonParser;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.PrintWriter;
import java.net.ServerSocket;
import java.net.Socket;
import java.util.concurrent.BlockingQueue;
import java.util.concurrent.LinkedBlockingQueue;


public class WebchatManager {
    private String TAG = "Webchat.WebchatManager";
    private static final int serverPort = 22335;
    private Socket socket=null;
    private ServerSocket serverSocket=null;
    private Writer writer;
    private Connection connection ;
    private BlockingQueue<String> outQueue;
    private boolean alive = false;

    public WebchatManager() {
        outQueue = new LinkedBlockingQueue<String>(32);
        writer = new Writer();
        connection = new Connection();
    }

    public void start() {
        connection.start();
        alive = true;
    }

    public boolean isAlive() {
        return alive;
    }

    public void waitAll() {
        try {
            connection.join();
            writer.join();
        } catch (InterruptedException e) {
            e.printStackTrace();
        }

    }

    public void sendMessage(String message) {
        try {
            this.outQueue.put(message);
        } catch (InterruptedException e) {
            e.printStackTrace();
        }
    }

    public String pullMessage() {
        String message = null;
        try {
            message = this.outQueue.take();

        }   catch (InterruptedException e) {
            e.printStackTrace();
        }
        return message;
    }


    class Connection extends Thread {
        public Connection() {

        }

        public void run() {
            while(true) {
                if (serverSocket == null) {
                    try {
                        serverSocket = new ServerSocket(serverPort);
                    } catch (IOException e) {
                        Log.e(TAG, "创建ServerSocket失败");
                        e.printStackTrace();
                    }
                }
                if (serverSocket != null && socket == null) {
                    try {
                        Log.i(TAG, "等待webchat接入: 22335");
                        socket = serverSocket.accept();
                        if (!writer.isAlive()) {
                            writer.start();
                        }
                    } catch (IOException e) {
                        e.printStackTrace();
                        Log.w(TAG, "连接失败");
                        try {
                            sleep(3000);
                        } catch (InterruptedException e1) {
                            e1.printStackTrace();
                        }
                        continue;
                    }
                }
                Log.i(TAG, "接入成功");
                while(true) {
                    try {
                        InputStreamReader in = new InputStreamReader(socket.getInputStream());
                        BufferedReader reader = new BufferedReader(in);
                        String message = reader.readLine();
                        if(message.length() == 0) {
                            Log.e(TAG, "socket 损坏");
                            socket.close();
                            socket = null;
                            break;
                        }else{
                            JsonElement jsonElement = new JsonParser().parse(message);
                            JsonObject jsonObject = jsonElement.getAsJsonObject();
                            try {
                                int cmd = jsonObject.get("cmd").getAsInt();
                                Log.i(TAG, "接收到webchat消息");
                                ExternalManager.sendMessage(message);
                            } catch (Exception e) {
                                // TODO Auto-generated catch block
                                e.printStackTrace();
                                Log.w(TAG, "消息解析错误");
                            }
                        }
                    } catch (Exception e) {
                        e.printStackTrace();
                        Log.i(TAG, "读取消息异常");
                        try {
                            socket.close();
                        } catch (IOException e1) {
                            e1.printStackTrace();
                        }
                        socket = null;
                        break;
                    }

                }
            }
        }
    }

    class Writer extends Thread {
        public Writer() {

        }

        public void run() {
            while (true) {
                try {
                    String message = pullMessage();
                    if (socket == null) {
                        outQueue.clear();
                    } else{
                        PrintWriter writer = new PrintWriter(socket.getOutputStream());
                        writer.println(message);
                        writer.flush();
                        Log.i(TAG, "成功发送Webchat消息：" + message);
                    }
                } catch (Exception e) {
                    e.printStackTrace();
                    Log.i(TAG, "消息发送异常");
                }
            }
        }
    }
}
