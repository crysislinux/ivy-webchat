package com.ivy.bridge;

import android.app.Application;
import android.content.ComponentName;
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


public class ExternalManager {
    private String TAG = "Webchat.ExternalManager";
    private static final int serverPort = 22334;
    private Socket socket=null;
    private Writer writer;
    private Connection connection ;
    private static BlockingQueue<String> outQueue;
    private GpsManager gm;
    private WebchatManager wm;
    private String identifier = null;
    private String webchatId = null;
    private String vmId = null;
    private Application application = null;

    public ExternalManager(Application application) throws RuntimeException {
        outQueue = new LinkedBlockingQueue<String>(32);
        writer = new Writer();
        connection = new Connection();
        gm = new GpsManager();
        wm = new WebchatManager();
        this.application = application;
        try {
        	Process process =Runtime.getRuntime().exec("getprop androVM.vm_identifier");  
    	    InputStreamReader ir = new InputStreamReader(process.getInputStream());  
    	    BufferedReader input = new BufferedReader(ir);
    	    identifier = input.readLine();
    	    if (identifier == null) {
    	    	throw new RuntimeException("不能得到webchatId");
    	    } 
    	    Log.i(TAG, "webchatId: " + identifier);
    	    
    	    Process process1 =Runtime.getRuntime().exec("getprop androVM.vm_vmId");  
    	    InputStreamReader ir1 = new InputStreamReader(process1.getInputStream());  
    	    BufferedReader input1 = new BufferedReader(ir1);
    	    vmId = input1.readLine();
    	    if (vmId == null) {
    	    	throw new RuntimeException("不能得到vmId");
    	    } 
    	    Log.i(TAG, "vmId: " + vmId);
		} catch (IOException e) {
			// TODO: handle exception
		}
        
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
    

    private String getIdentifier() {
    	if (this.identifier != null)
    		return this.identifier;
    	else
    		return "null";
    }
    

    private String getvmId() {
    	if (this.vmId != null)
    		return this.vmId;
    	else
    		return "null";
    }

    private void setWebchatId(String webchatId) {
    	this.webchatId = webchatId;
    	Log.i(TAG, "set webchatId" + this.webchatId);    }
    
    private String getWebchatId() {
    	if (this.webchatId != null)
    		return this.webchatId;
    	else
			return "null";
    }
    
    private String decorateMessage(String message) {
        return "{\"identifier\":\"" + getIdentifier() + "\", \"webchatId\": \"" +
                getWebchatId() + "\", " + "\"vmId\": \"" +
                getvmId() + "\", " + message.substring(1, message.length());
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
                        socket = new Socket("10.0.3.2", serverPort);
                        //for test
                        //socket = new Socket("127.0.0.1", serverPort);
                        if (!writer.isAlive()) {
                            writer.start();
                        }
                        if (!gm.isAlive()) {
                            gm.start();
                        }
                        if (!wm.isAlive()) {
                            wm.start();
                            application.startInstrumentation(new ComponentName("com.ivy.webchat", "android.test.InstrumentationTestRunner"), null, null);
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
                Log.i(TAG, "连接成功");
                InputStreamReader in;
                BufferedReader reader;
				try {
					in = new InputStreamReader(socket.getInputStream());
					reader = new BufferedReader(in);
				} catch (IOException e2) {
					// TODO Auto-generated catch block
					e2.printStackTrace();
					continue;
				}         
                while(true) {
                    try { 
                        Log.i(TAG, "准备读取消息");
                        String message = reader.readLine();
                        if(message.length() == 0) {
                            Log.e(TAG, "socket 损坏");
                            socket.close();
                            socket = null;
                            break;
                        }else{
                        	Log.i(TAG, message);
                            JsonElement jsonElement = new JsonParser().parse(message);
                            JsonObject jsonObject = jsonElement.getAsJsonObject();
                            try {
                                int cmd = jsonObject.get("cmd").getAsInt();
                                if (Message.CMD_BRIDGE_START <= cmd && cmd < Message.CMD_BRIDGE_END) {
                                    switch (cmd) {
                                        case Message.CMD_SET_GPS_LAT:
                                            float lat = jsonObject.get("lat").getAsFloat();
                                            gm.sendMessage(Message.setGpsLat(lat));
                                            break;
                                        case Message.CMD_SET_GPS_LNG:
                                            float lng = jsonObject.get("lng").getAsFloat();
                                            gm.sendMessage(Message.setGpsLng(lng));
                                            break;
                                        
                                        default:
                                            Log.i(TAG, "命令未实现");
                                    }
                                }
                                else if (cmd == Message.CMD_CLIENT_VALIDATED) {
                                	String webchatId = jsonObject.get("identifier").getAsString();
                                    setWebchatId(webchatId);
                                    sendMessage(Message.BridgeBootOk());
				
                                } else if (Message.CMD_WEBCHAT_START <= cmd && cmd < Message.CMD_WEBCHAT_END) {
                                	Log.i(TAG, "微信消息");
                                    wm.sendMessage(message);
                                }

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
                        writer.println(decorateMessage(message));
                        writer.flush();
                        Log.i(TAG, "成功发送External消息：" + message);
                    }
                } catch (Exception e) {
                    e.printStackTrace();
                    Log.i(TAG, "消息发送异常");
                }
            }
        }
    }
}
