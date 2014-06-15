package com.ivy.bridge;

import android.app.Application;


public class BridgeApplication extends Application {
	ExternalManager externalManager;
	
	@Override
	public void onCreate() {
		ExternalManager externalManager = new ExternalManager(this);
        externalManager.start();
	}
}
