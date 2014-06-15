package com.ivy.bridge;
import org.stringtemplate.v4.*;
import Genymotion.Requests.*;

public class Message {

    //命令分类
    public final static int CLASS_GPS_ACTION = 0;
    public final static int CLASS_WEBCHAT_ACTION = 1;
    public final static int CLASS_BRIDGE_ACTION = 2;
    public final static int CLASS_ACTION_RESULT = 3;

    public final static int CMD_CLIENT_VALIDATED = 1005;
    
    //命令执行结果 [2000, 3000)
    public final static int CMD_LOGIN_OK = 2000;
    public final static int CMD_LOGIN_FAIL = 2001;
    public final static int CMD_LOGOUT_OK = 2002;
    public final static int CMD_LOGOUT_FAIL = 2003;
    public final static int CMD_FIND_NEARBY_FRIENDS_OK = 2004;
    public final static int CMD_FIND_NEARBY_FRIENDS_FAIL = 2005;
    public final static int CMD_SET_GPS_OK = 2006;
    public final static int CMD_SET_GPS_FAIL = 2007;
    public final static int CMD_GO_BACK_OK = 2008;
    public final static int CMD_ENTER_TEXT_OK = 2009;
    public final static int CMD_ENTER_TEXT_FAIL = 2010;
    public final static int CMD_UNIMPLEMENT = 2011;
    public final static int CMD_TEXT_EDIT_CHANGED = 2012;
    public final static int CMD_BRIDGE_BOOT_OK = 2013;

    //由外部传入需要由Bridge处理的命令 [3000, 4000)
    public final static int CMD_BRIDGE_START = 3000;
    public final static int CMD_SET_GPS_LAT = 3000;
    public final static int CMD_SET_GPS_LNG = 3001;
    public final static int CMD_GET_GPS_LAT = 3002;
    public final static int CMD_GET_GPS_LNG = 3003;
    public final static int CMD_BRIDGE_END = 4000;

    //需要转送到Webchat的命令 [4000, 5000)
    public final static int CMD_WEBCHAT_START = 4000;
    public final static int CMD_LOGIN = 4000;
    public final static int CMD_LOGOUT = 4001;
    public final static int CMD_FIND_NEARBY_FRIENDS = 4002;
    public final static int CMD_GO_BACK = 4003;
    public final static int CMD_ENTER_TEXT = 4004;
    public final static int CMD_WEBCHAT_END = 5000;

    //需要Bridge的内部命令 [5000, 6000)
    public final static int CMD_INTERNAL_START = 5000;

    public final static int CMD_INTERNAL_END = 6000;

    private static Request.Builder request = Request.newBuilder();

    static String gpsSetupOk(String lon, String lat) {
        ST tmp = new ST("{\"cmd\": <cmd>, \"lat\": \"<lat>\", \"lon\": \"<lon>\"}");
        tmp.add("cmd", String.valueOf(Message.CMD_SET_GPS_OK));
        tmp.add("lon", lon);
        tmp.add("lat", lat);
        return tmp.render();
    }
    
    static String BridgeBootOk() {
        ST tmp = new ST("{\"cmd\": <cmd>}");
        tmp.add("cmd", String.valueOf(Message.CMD_BRIDGE_BOOT_OK));
        return tmp.render();
    }

    static Request setGpsLng(float lng) {
        request.clear();
        request.setType(Request.Type.SetParam);
        Parameter.Builder parameter = Parameter.newBuilder();
        parameter.setType(Parameter.Type.GpsLongitude);
        Value.Builder value = Value.newBuilder();
        value.setType(Value.Type.Float);
        value.setFloatValue(lng);
        parameter.mergeValue(value.build());
        request.mergeParameter(parameter.build());
        return request.build();
    }

    static Request setGpsLat(float lat) {
        request.clear();
        request.setType(Request.Type.SetParam);
        Parameter.Builder parameter = Parameter.newBuilder();
        parameter.setType(Parameter.Type.GpsLatitude);
        Value.Builder value = Value.newBuilder();
        value.setType(Value.Type.Float);
        value.setFloatValue(lat);
        parameter.mergeValue(value.build());
        request.mergeParameter(parameter.build());
        return request.build();
    }
}
