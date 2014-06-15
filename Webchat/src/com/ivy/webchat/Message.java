package com.ivy.webchat;

import org.stringtemplate.v4.ST;

public class Message {

    //命令分类
    public final static int CLASS_GPS_ACTION = 0;
    public final static int CLASS_WEBCHAT_ACTION = 1;
    public final static int CLASS_BRIDGE_ACTION = 2;
    public final static int CLASS_ACTION_RESULT = 3;

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
    public final static int CMD_DETECT_TEXT_EDIT = 4005;
    public final static int CMD_APPEND_TEXT = 4006;
    public final static int CMD_WEBCHAT_END = 5000;

    //需要Bridge的内部命令 [5000, 6000)
    public final static int CMD_INTERNAL_START = 5000;

    public final static int CMD_INTERNAL_END = 6000;

    public static String gpsSetupOk(String lon, String lat) {
        ST tmp = new ST("{\"cmd\": <cmd>, \"lat\": \"<lat>\", \"lon\": \"<lon>\"}");
        tmp.add("cmd", String.valueOf(Message.CMD_SET_GPS_OK));
        tmp.add("lon", lon);
        tmp.add("lat", lat);
        return tmp.render();
    }

    public static String unimplementCMD(int cmd) {
        ST tmp = new ST("{\"cmd\": <cmd>, \"uCmd\": <uCmd>}");
        tmp.add("cmd", String.valueOf(Message.CMD_UNIMPLEMENT));
        tmp.add("uCmd", cmd);
        return tmp.render();
    }

    public static String textEditChanegd(int num) {
        ST tmp = new ST("{\"cmd\": <cmd>, \"num\": <num>}");
        tmp.add("cmd", String.valueOf(Message.CMD_TEXT_EDIT_CHANGED));
        tmp.add("num", num);
        return tmp.render();
    }
}
