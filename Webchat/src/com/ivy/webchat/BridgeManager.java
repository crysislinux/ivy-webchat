package com.ivy.webchat;

import android.util.Log;

import com.google.gson.JsonElement;
import com.google.gson.JsonObject;
import com.google.gson.JsonParser;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.PrintWriter;
import java.net.Socket;
import java.util.concurrent.BlockingQueue;
import java.util.concurrent.LinkedBlockingQueue;


public class BridgeManager {
    private String TAG = "Webchat.Webchat-BridgeManager";
    private static final int serverPort = 22335;
    private Socket socket=null;
    private Writer writer;
    private Connection connection ;
    private static BlockingQueue<String> outQueue;
    private ESolo solo;

    public BridgeManager() {
        outQueue = new LinkedBlockingQueue<String>(32);
        writer = new Writer();
        connection = new Connection();
        solo = Main.getSolo();
    }

    public void start() {
        connection.start();
    }

    public void waitAll() {
        try {
            connection.join();
            writer.join();
        } catch (InterruptedException e) {
            e.printStackTrace();
        }

    }

    public static void sendMessage(String message) {
        try {
            outQueue.put(message);
        } catch (InterruptedException e) {
            e.printStackTrace();
        }
    }

    public String pullMessage() {
        String message = null;
        try {
            message = outQueue.take();

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
                if (socket == null) {
                    try {
                    	//for test
                        //socket = new Socket("10.0.3.2", serverPort);
                        socket = new Socket("127.0.0.1", serverPort);
                        if (!writer.isAlive()) {
                            writer.start();
                        }
                    } catch (IOException e) {
                        //e.printStackTrace();
                    	try {
							sleep(3000);
              
						} catch (Exception e1) {
								
						}      
                    	Log.w(TAG, "连接失败 " + e.toString());
                        continue;
                    }
                }
                Log.i(TAG, "连接成功");
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
                                switch (cmd) {
                                    case Message.CMD_DETECT_TEXT_EDIT:
                                        solo.detectTextEdit();
                                        break;
                                    case Message.CMD_ENTER_TEXT:
                                    	String text = jsonObject.get("text").getAsString();
                                    	solo.enterText(text);
                                    	break;
                                    case Message.CMD_APPEND_TEXT:
                                    	String text1 = jsonObject.get("text").getAsString();
                                    	solo.enterText(text1, true);
                                    	break;
                                    case Message.CMD_LOGIN:
                                    case Message.CMD_LOGOUT:
                                    case Message.CMD_FIND_NEARBY_FRIENDS:
                                    default:
                                        Log.i(TAG, "命令未实现: " + String.valueOf(cmd));
                                        sendMessage(Message.unimplementCMD(cmd));
                                }

                            } catch (Exception e) {
                                // TODO Auto-generated catch block
                                Log.e(TAG, e.toString());
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
                        Log.i(TAG, "成功发送消息：" + message);
                    }
                } catch (Exception e) {
                    e.printStackTrace();
                    Log.i(TAG, "消息发送异常");
                }
            }
        }
    }
}
