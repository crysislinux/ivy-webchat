package com.ivy.webchat;
import java.util.ArrayList;

import android.util.Log;
import android.widget.EditText;

import com.jayway.android.robotium.solo.Solo;
import com.jayway.android.robotium.solo.Timeout;

public class ESolo extends Solo {
    private static final String TAG = "Webchat.ESolo";
    private ArrayList<EditText> editTextList;
    public ESolo(android.app.Instrumentation instrumentation, android.app.Activity activity) {
    	super(instrumentation, activity);
    	Timeout.setSmallTimeout(100);
    	editTextList = new ArrayList<EditText>(8);
    }

    public String checkCurrentActivity() {
        return "LoginUI";
    }

    public void detectTextEdit() {
    	Log.i(TAG, "开始查找当前输入框");
    	editTextList.clear();
    	try {
    		EditText editText = getEditText("(.*)", true);
    		if (editText != null) {
    			editTextList.add(editText);
    		}
		} catch (Error e) {
			// TODO: handle exception
			Log.w(TAG, "穷尽所有当前输入框: " + e.toString());
		}
    	
        BridgeManager.sendMessage(Message.textEditChanegd(editTextList.size()));
        Log.i(TAG, "查找当前输入框结束");
    }

    @Override
    public void clickOnText(String text) {
        try {
            super.clickOnText(text);
        } catch (Error e) {
            //e.printStackTrace();
            Log.e(TAG, e.toString());
        } finally {
            detectTextEdit();
        }
    }
    
    public void enterText(String text) {
    	if (editTextList.size() < 1) {
    		Log.e(TAG, "当前没有输入框可供输入");
    		return;
    	}
        try {
        	EditText editText = editTextList.get(0);
        	clearEditText(editText);
            enterText(editText, text);
        } catch (Error e) {
            //e.printStackTrace();
            Log.e(TAG, e.toString());
            detectTextEdit();
        }
    }

    public void enterText(String text, boolean append) {
    	if (editTextList.size() < 1) {
    		Log.e(TAG, "当前没有输入框可供输入");
    		return;
    	}
        try {
        	EditText editText = editTextList.get(0);
        	if (!append) {
        		clearEditText(editText);
        	}	
            enterText(editText, text);
        } catch (Error e) {
            //e.printStackTrace();
            Log.e(TAG, e.toString());
            detectTextEdit();
        }
    }
}
