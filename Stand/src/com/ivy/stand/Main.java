package com.ivy.stand;

import java.io.IOException;
import java.net.UnknownHostException;

import com.ivy.stand.Communication;
import com.jayway.android.robotium.solo.Solo;

import android.test.ActivityInstrumentationTestCase2;
import android.util.Log;


@SuppressWarnings({ "unchecked", "rawtypes" })
public class Main extends ActivityInstrumentationTestCase2{
	private static final String LAUNCHER_ACTIVITY_FULL_CLASSNAME="com.tencent.mm.ui.LauncherUI";
	private static Class launcherActivityClass;

	static{
		try{
			launcherActivityClass = Class.forName(LAUNCHER_ACTIVITY_FULL_CLASSNAME);
		} catch (ClassNotFoundException e){
			throw new RuntimeException(e); 
		} 
	} 
	public Main() throws ClassNotFoundException{		
		super(launcherActivityClass);
	}
	
	private static Solo solo;
	public static Solo getSolo() {
		return solo;
	}
	
	@Override
	protected void setUp() throws Exception {	
		solo = new Solo(getInstrumentation(),getActivity());
	}
		
	public void testStart() throws InterruptedException, UnknownHostException, IOException {	
		Log.e("weixin", "处理开始-----------------------------------");
		Communication c = new Communication(solo);
		c.start(); 
		c.join();
	}
	
	@Override
	public void tearDown() throws Exception {
		solo.finishOpenedActivities();
	} 
}
