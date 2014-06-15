package com.ivy.stand;

import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.io.PrintWriter;
import java.net.ServerSocket;
import java.net.Socket;
import java.util.concurrent.BlockingQueue;
import java.util.concurrent.LinkedBlockingDeque;

import com.jayway.android.robotium.solo.Solo;

import android.location.Location;
import android.location.LocationListener;
import android.os.Bundle;
import android.util.Log;
import android.widget.ListView;

import org.json.JSONException;
import org.json.JSONObject;
import org.json.JSONTokener;

import com.ivy.stand.Message;


public class Communication extends Thread {
	private Socket socket = null;
	private Socket gpsSocket = null;
	private String TAG = "weixin";
	private Solo solo = null;
	private ServerSocket serverSocket = null;
	private Writer writer = null;
	private GpsWriter gpsWriter = null;
	private BlockingQueue<String> outputQueue = null;  //向外部输出的消息
	private BlockingQueue<String> gpsQueue = null;  //向GPS输出的消息
	//private LocationManager lm = null;
	//private LocationWatcher lw = null;
	private Boolean isGpsFirstStart = true;
	
	public Communication(Solo solo) {
		setDaemon(true);
		this.solo = solo;
		this.outputQueue = new LinkedBlockingDeque<String>(32);
		this.gpsQueue = new LinkedBlockingDeque<String>(32);
		//Application app = solo.getCurrentActivity().getApplication();
		//lw = new LocationWatcher();
		//lm = (LocationManager)app.getSystemService(Context.LOCATION_SERVICE);
		//lm.requestLocationUpdates(LocationManager.GPS_PROVIDER, 0, 1, lw);
		//lm.requestLocationUpdates(LocationManager.NETWORK_PROVIDER, 0, 1, lw);
		
	}
	
	public void sendMessage(String message) {
		try {
			this.outputQueue.put(message);
		} catch (InterruptedException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
	}
	
	public String pullMessage() {
		String message = null;
		try {
			message = this.outputQueue.take();
		} catch (InterruptedException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
		return message;
	}
	
	public String pullGpsMessage() {
		String message = null;
		try {
			message = this.gpsQueue.take();
		} catch (InterruptedException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
		return message;
	}
	
	public Boolean login(String username, String password) {
		String currentActivity = solo.getCurrentActivity().getClass().toString();
		Log.i(TAG, currentActivity);
		Boolean success = false;
		solo.clickOnText("切换帐号");
		solo.clickOnText("QQ号/微信号/Email");
		solo.enterText(0, username);
		solo.enterText(1, password);
		//solo.clickOnText("登录");
		solo.clickOnScreen(268, 40);
		success = true;
		if(success) {
			sendMessage(Message.loginOk());
		}else{
			sendMessage(Message.loginFail(null));
		}
		return success;
	}
	
	public Boolean logout() {
		String currentActivity = solo.getCurrentActivity().getClass().toString();
		Log.i(TAG, currentActivity);
		Boolean success = false;
		if(!currentActivity.endsWith("LoginUI")) {
			if (currentActivity.endsWith("NearbyFriendsUI")) {
				solo.goBack();
			}
			solo.clickOnText("我");
			solo.clickOnText("设置");
			solo.clickOnText("退出登录");
			solo.clickOnText("退出登录");
			success = true;
		}
		
		if(success) {
			sendMessage(Message.logoutOk());
		}else{
			sendMessage(Message.logoutFail(null));
		}
		return success;
	}
	
	public Boolean findNearbyFriends() {
		String currentActivity = solo.getCurrentActivity().getClass().toString();
		Log.i(TAG, currentActivity);
		Boolean success = false;
		for(int j=0; j<3; j++) {
			solo.clickOnText("发现");
			solo.clickOnText("附近的人");	
			solo.waitForDialogToClose(10000);
			if(solo.waitForView(ListView.class, 1, 1000)){
				Log.v(TAG, "获得附近人列表成功");
				success = true;
				break;
			}else{
				Log.v(TAG, "获得附近人列表失败");
				solo.goBack();
			}
		}
		//solo.goBack();
		
		if (success) {
			sendMessage(Message.findNearbyFriendsOk());
		}else {
			sendMessage(Message.findNearbyFriendsFail(null));
		}
		
		return success;
	}
	
	public void setGps(String lon, String lat) {
		String message = lat + " " + lon + " 0";
		try {
			this.gpsQueue.put(message);
		} catch (InterruptedException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
		sendMessage(Message.gpsSetupOk(lon, lat));
	}
	
	public void goBack() {
		solo.goBack();
		sendMessage(Message.goBackOk());
	}
		
	public void run() {
		while (true) {
			try {
				if(serverSocket == null) {
					serverSocket = new ServerSocket(12316);
				}
				Log.i(TAG, "等待Stand连接: 12316");
				socket = serverSocket.accept();
				writer = new Writer();
				writer.start();
				Log.i(TAG, "Stand连接成功");
			}
		    catch(Exception e) {
		    	Log.e(TAG, "创建Stand链接失败");
		    	return;
		    }	
			
			try {
				gpsSocket = new Socket("127.0.0.1", 12315);
				gpsWriter = new GpsWriter();
				gpsWriter.start();
				Log.v(TAG, "GPS连接成功");
		    } catch (Exception e) {
				// TODO Auto-generated catch block
				Log.e(TAG, e.toString());
				Log.e(TAG, "GPS连接失败");
				return;
			}
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
			        	JSONTokener jsonParser = new JSONTokener(message);  
						JSONObject jsonObject;
						Log.e(TAG, message);
						try {
							jsonObject = (JSONObject)jsonParser.nextValue();
							int cmd = jsonObject.getInt("cmd");
							final int CMD_LOGIN = 1000;
							final int CMD_LOGOUT = 1001;
							final int CMD_FIND_NEARBY_FRIENDS = 1002;
							final int CMD_TICK = 1;
							final int CMD_SET_GPS = 1003;
							final int CMD_GO_BACK = 1004;
							switch (cmd) {
							case CMD_LOGIN:
								String username = jsonObject.getString("username");
								String password = jsonObject.getString("password");
								login(username, password);
								break;
							
							case CMD_SET_GPS:
								String lon = jsonObject.getString("lon");
								String lat = jsonObject.getString("lat");
								setGps(lon, lat);
								break;
								
							case CMD_LOGOUT:
								logout();
								break;
								
							case CMD_FIND_NEARBY_FRIENDS:
								findNearbyFriends();
								break;
								
							case CMD_GO_BACK:
								goBack();
								break;
							
							case CMD_TICK:
								break;
								
							default:
								Log.e(TAG, "Unknown CMD");
								break;
							}
						} catch (JSONException e) {
							// TODO Auto-generated catch block
							e.printStackTrace();
							Log.w(TAG, "消息解析错误");
						}  
			           	
			        }     
			    } catch (Exception e) {
			        Log.e(TAG, "读取消息异常");
			        e.printStackTrace();
			        break;
			    }
			}
		}
	}
	
	public class Writer extends Thread {
		
		public Writer() {
			setDaemon(true);
		}
		
		public void run() {
			while(true) {
				String message = Communication.this.pullMessage();
				Log.i(TAG, "准备发送消息：" + message);
				if(message == null) {
					continue;
				}
				
				try {
					PrintWriter writer = new PrintWriter(socket.getOutputStream());
					writer.println(message);
				    writer.flush();
				    Log.i(TAG, "成功发送消息：" + message);
				} catch (Exception e) {
					Log.e(TAG, "发送消息失败");
				}
			}
		}
	}
	
public class GpsWriter extends Thread {
		
		public GpsWriter() {
			setDaemon(true);
		}
		
		public void run() {
			while(true) {
				String message = Communication.this.pullGpsMessage();
				Log.i(TAG, "准备发送GPS消息：" + message);
				if(message == null) {
					continue;
				}
				
				try {
					PrintWriter writer = new PrintWriter(gpsSocket.getOutputStream());
					writer.println(message);
				    writer.flush();
				    Log.i(TAG, "成功发送GPS消息：" + message);
				} catch (Exception e) {
					Log.e(TAG, "发送GPS消息失败");
				}
			}
		}
	}
	
	public class LocationWatcher implements LocationListener {

		@Override
		public void onLocationChanged(Location location) {
			// TODO Auto-generated method stub
			if(isGpsFirstStart) {
				isGpsFirstStart = false;
				return;
			}
			Log.e(TAG, "经度:" + String.valueOf(location.getLongitude()) + "  纬度:" + String.valueOf(location.getLatitude()));
			String message = Message.gpsSetupOk(String.valueOf(location.getLongitude()), String.valueOf(location.getLatitude()));
			Communication.this.sendMessage(message);
		}

		@Override
		public void onProviderDisabled(String provider) {
			// TODO Auto-generated method stub
			
		}

		@Override
		public void onProviderEnabled(String provider) {
			// TODO Auto-generated method stub
			
		}

		@Override
		public void onStatusChanged(String provider, int status,Bundle extras) {
			// TODO Auto-generated method stub
			
		}
		
	}
}
