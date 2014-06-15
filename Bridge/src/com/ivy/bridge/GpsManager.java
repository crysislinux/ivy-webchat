package com.ivy.bridge;

import java.io.IOException;
import java.net.Socket;
import java.util.concurrent.BlockingQueue;
import java.util.concurrent.LinkedBlockingQueue;

import android.R.bool;
import android.util.Log;
import Genymotion.Requests.*;

public class GpsManager {
    private String TAG = "Webchat.GpsManager";
    private Socket socket=null;
    private Writer writer = null;
    private Connection connection = null;
    private BlockingQueue<Request> outQueue = null;
    private boolean alive = false;
    private boolean waitResponse = false;

    public GpsManager() {
        outQueue = new LinkedBlockingQueue<Request>(32);
        writer = new Writer();
        connection = new Connection();
    }
    
    public boolean isWaittingResponse() {
    	return waitResponse;
    }
    
    public void setWaitResponse(){
    	waitResponse = true;
    }
    
    public void clearWaitResponse() {
    	waitResponse = false;
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

    public void sendMessage(Request message) {
        try {
            this.outQueue.put(message);
        } catch (InterruptedException e) {
            e.printStackTrace();
        }
    }

    public Request pullMessage() {
        Request message = null;
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
                if (socket == null) {
                    try {
                        socket = new Socket("127.0.0.1", 22666);
                        writer.start();
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
                while(true) {
                    byte[] readBuf = new byte[4096];
                    try {
                        int size = socket.getInputStream().read(readBuf);
                        byte[] buf = new byte[size];
                        System.arraycopy(readBuf, 0, buf, 0, size);
                        Reply reply = Reply.parseFrom(buf);
                        Reply.Type type = reply.getType();
                        switch (type.getNumber()) {
                            case Reply.Type.None_VALUE:
                                Log.i(TAG, "Type: 没有错误");
                                break;
                            case Reply.Type.Error_VALUE:
                                Log.i(TAG, "Type: 错误");
                                break;
                            case Reply.Type.Pong_VALUE:
                                Log.i(TAG, "Type: 不知道什么错误");
                                break;
                            case Reply.Type.Value_VALUE:
                                Log.i(TAG, "Type: 带有返回值");
                                break;
                        }

                        Status status = reply.getStatus();
                        Status.Code code = status.getCode();
                        switch (code.getNumber()) {
                            case Status.Code.Ok_VALUE:
                                Log.i(TAG, "Status: 正常");
                                break;
                            case Status.Code.GenericError_VALUE:
                                Log.i(TAG, "Status: 普通错误");
                                break;
                            case Status.Code.InvalidRequest_VALUE:
                                Log.i(TAG, "Status: 非法错误");
                                break;
                            case Status.Code.OkWithInformation_VALUE:
                                Log.i(TAG, "Status: 正常并带有信息");
                                break;
                            case Status.Code.NotImplemented_VALUE:
                                Log.i(TAG, "Status: 命令未实现");
                                break;
                        }

                        if (reply.hasValue()) {
                            Value value = reply.getValue();
                            Value.Type valueType = value.getType();
                            switch (valueType.getNumber()) {
                                case Value.Type.Bool_VALUE:
                                    Log.i(TAG, "信息类型为Bool");
                                    Log.i(TAG, String.valueOf(value.getBoolValue()));
                                    break;
                                case Value.Type.Int_VALUE:
                                    Log.i(TAG, "信息类型为Int");
                                    Log.i(TAG, String.valueOf(value.getIntValue()));
                                    break;
                                case Value.Type.Float_VALUE:
                                    Log.i(TAG, "信息类型为Float");
                                    Log.i(TAG, String.valueOf(value.getFloatValue()));
                                    break;
                                case Value.Type.String_VALUE:
                                    Log.i(TAG, "信息类型为String");
                                    Log.i(TAG, String.valueOf(value.getStringValue()));
                                    break;
                                case Value.Type.Bytes_VALUE:
                                    Log.i(TAG, "信息类型为Bytes");
                                    Log.i(TAG, String.valueOf(value.getBytesValue()));
                                    break;
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
                    }finally {
                    	clearWaitResponse();
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
            	if (isWaittingResponse()) {
            		try {
						sleep(100);
					} catch (InterruptedException e) {
						// TODO Auto-generated catch block
						e.printStackTrace();
					}
            		continue;
            	}
                try {
                    Request request = pullMessage();
                    if (socket == null) {
                        break;
                    } else{
                        request.writeTo(socket.getOutputStream());
                    }
                    setWaitResponse();
                    Log.i(TAG, "成功发送Gps消息");
                } catch (Exception e) {
                    e.printStackTrace();
                    Log.i(TAG, "消息发送异常");
                    break;
                }
            }
        }
    }
}
