package com.ivy.stand;
import org.stringtemplate.v4.*;

public class Message {
	public final static int CMD_LOGIN_OK = 2000;
	public final static int CMD_LOGIN_FAIL = 2001;
	public final static int CMD_LOGOUT_OK = 2002;
	public final static int CMD_LOGOUT_FAIL = 2003;
	public final static int CMD_FIND_NEARBY_FRIENDS_OK = 2004;
	public final static int CMD_FIND_NEARBY_FRIENDS_FAIL = 2005;
	public final static int CMD_SET_GPS_OK = 2006;
	public final static int CMD_SET_GPS_FAIL = 2007;
	public final static int CMD_GO_BACK_OK = 2008;
	
	
	static String gpsSetupOk(String lon, String lat) {
		ST tmp = new ST("{\"cmd\": <cmd>, \"lat\": \"<lat>\", \"lon\": \"<lon>\"}");
		tmp.add("cmd", String.valueOf(Message.CMD_SET_GPS_OK));
		tmp.add("lon", lon);
		tmp.add("lat", lat);
		return tmp.render();
	}
	
	
	static String loginOk() {
		ST tmp = new ST("{\"cmd\": <cmd>}");
		tmp.add("cmd", String.valueOf(Message.CMD_LOGIN_OK));
		return tmp.render();
	}
	
	static String loginFail(String info) {
		ST tmp = new ST("{\"cmd\": <cmd>, \"info\": \"<info>\"}");
		tmp.add("cmd", String.valueOf(Message.CMD_LOGIN_FAIL));
		if (info == null){
			info = "";
		}
		tmp.add("info", info);
		return tmp.render();
	}
	
	static String logoutOk() {
		ST tmp = new ST("{\"cmd\": <cmd>}");
		tmp.add("cmd", String.valueOf(Message.CMD_LOGOUT_OK));
		return tmp.render();
	}
	
	static String logoutFail(String info) {
		ST tmp = new ST("{\"cmd\": <cmd>, \"info\": \"<info>\"}");
		tmp.add("cmd", String.valueOf(Message.CMD_LOGOUT_FAIL));
		if (info == null){
			info = "";
		}
		tmp.add("info", info);
		return tmp.render();
	}
	
	static String findNearbyFriendsOk() {
		ST tmp = new ST("{\"cmd\": <cmd>}");
		tmp.add("cmd", String.valueOf(Message.CMD_FIND_NEARBY_FRIENDS_OK));
		return tmp.render();
	}
	
	static String findNearbyFriendsFail(String info) {
		ST tmp = new ST("{\"cmd\": <cmd>, \"info\": \"<info>\"}");
		tmp.add("cmd", String.valueOf(Message.CMD_FIND_NEARBY_FRIENDS_FAIL));
		if (info == null){
			info = "";
		}
		tmp.add("info", info);
		return tmp.render();
	}
	
	static String goBackOk() {
		ST tmp = new ST("{\"cmd\": <cmd>}");
		tmp.add("cmd", String.valueOf(Message.CMD_GO_BACK_OK));
		return tmp.render();
	}
}
