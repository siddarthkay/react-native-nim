package com.nimbridge;

import com.facebook.react.bridge.ReactApplicationContext;
import com.facebook.react.bridge.ReactContextBaseJavaModule;
import com.facebook.react.bridge.ReactMethod;
import com.facebook.react.bridge.Promise;
import com.facebook.react.module.annotations.ReactModule;

@ReactModule(name = NimBridgeModule.NAME)
public class NimBridgeModule extends ReactContextBaseJavaModule {
    public static final String NAME = "NimBridge";

    // Load the native library
    static {
        try {
            System.loadLibrary("nim_functions");
            android.util.Log.d("NimBridge", "Native library nim_functions loaded successfully");
        } catch (Exception e) {
            android.util.Log.e("NimBridge", "Failed to load native library nim_functions: " + e.getMessage());
            e.printStackTrace();
        }
    }

    public NimBridgeModule(ReactApplicationContext reactContext) {
        super(reactContext);
    }

    @Override
    public String getName() {
        return NAME;
    }

    // Native method declarations
    private static native String nativeHelloWorld();
    private static native int nativeAddNumbers(int a, int b);
    private static native String nativeGetSystemInfo();
    private static native int nativeMobileFibonacci(int n);
    private static native int nativeMobileIsPrime(int n);
    private static native String nativeMobileFactorize(int n);
    private static native String nativeMobileCreateUser(int id, String name, String email);
    private static native int nativeMobileValidateEmail(String email);
    private static native String nativeGetNimCoreVersion();

    @ReactMethod(isBlockingSynchronousMethod = true)
    public String helloWorld() {
        try {
            return nativeHelloWorld();
        } catch (Exception e) {
            return "Error: " + e.getMessage();
        }
    }

    @ReactMethod(isBlockingSynchronousMethod = true)
    public Double addNumbers(Double a, Double b) {
        try {
            return (double) nativeAddNumbers(a.intValue(), b.intValue());
        } catch (Exception e) {
            return 0.0;
        }
    }

    @ReactMethod(isBlockingSynchronousMethod = true)
    public String getSystemInfo() {
        try {
            return nativeGetSystemInfo();
        } catch (Exception e) {
            return "Error: " + e.getMessage();
        }
    }

    @ReactMethod(isBlockingSynchronousMethod = true)
    public Double mobileFibonacci(Double n) {
        try {
            return (double) nativeMobileFibonacci(n.intValue());
        } catch (Exception e) {
            return 0.0;
        }
    }

    @ReactMethod(isBlockingSynchronousMethod = true)
    public Double mobileIsPrime(Double n) {
        try {
            return (double) nativeMobileIsPrime(n.intValue());
        } catch (Exception e) {
            return 0.0;
        }
    }

    @ReactMethod(isBlockingSynchronousMethod = true)
    public String mobileFactorize(Double n) {
        try {
            return nativeMobileFactorize(n.intValue());
        } catch (Exception e) {
            return "Error: " + e.getMessage();
        }
    }

    @ReactMethod(isBlockingSynchronousMethod = true)
    public String mobileCreateUser(Double id, String name, String email) {
        try {
            return nativeMobileCreateUser(id.intValue(), name, email);
        } catch (Exception e) {
            return "Error: " + e.getMessage();
        }
    }

    @ReactMethod(isBlockingSynchronousMethod = true)
    public Double mobileValidateEmail(String email) {
        try {
            return (double) nativeMobileValidateEmail(email);
        } catch (Exception e) {
            return 0.0;
        }
    }

    @ReactMethod(isBlockingSynchronousMethod = true)
    public String getNimCoreVersion() {
        try {
            return nativeGetNimCoreVersion();
        } catch (Exception e) {
            return "Error: " + e.getMessage();
        }
    }

}
