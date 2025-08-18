#include <jni.h>
#include <string>

// Import the Nim functions
extern "C" {
    const char* helloWorld();
    int addNumbers(int a, int b);
    const char* getSystemInfo();
    int mobileFibonacci(int n);
    int mobileIsPrime(int n);
    const char* mobileFactorize(int n);
    const char* mobileCreateUser(int id, const char* name, const char* email);
    int mobileValidateEmail(const char* email);
    const char* getNimCoreVersion();
    void mobileNimInit();
    void mobileNimShutdown();
}

// Initialize Nim when the library loads
static bool nimInitialized = false;

void initializeNim() {
    if (!nimInitialized) {
        mobileNimInit();
        nimInitialized = true;
    }
}

extern "C" JNIEXPORT jstring JNICALL
Java_com_nimbridge_NimBridgeModule_nativeHelloWorld(JNIEnv *env, jclass clazz) {
    initializeNim();
    const char* result = helloWorld();
    return env->NewStringUTF(result);
}

extern "C" JNIEXPORT jint JNICALL
Java_com_nimbridge_NimBridgeModule_nativeAddNumbers(JNIEnv *env, jclass clazz, jint a, jint b) {
    initializeNim();
    return addNumbers(a, b);
}

extern "C" JNIEXPORT jstring JNICALL
Java_com_nimbridge_NimBridgeModule_nativeGetSystemInfo(JNIEnv *env, jclass clazz) {
    initializeNim();
    const char* result = getSystemInfo();
    return env->NewStringUTF(result);
}

extern "C" JNIEXPORT jint JNICALL
Java_com_nimbridge_NimBridgeModule_nativeMobileFibonacci(JNIEnv *env, jclass clazz, jint n) {
    initializeNim();
    return mobileFibonacci(n);
}

extern "C" JNIEXPORT jint JNICALL
Java_com_nimbridge_NimBridgeModule_nativeMobileIsPrime(JNIEnv *env, jclass clazz, jint n) {
    initializeNim();
    return mobileIsPrime(n);
}

extern "C" JNIEXPORT jstring JNICALL
Java_com_nimbridge_NimBridgeModule_nativeMobileFactorize(JNIEnv *env, jclass clazz, jint n) {
    initializeNim();
    const char* result = mobileFactorize(n);
    return env->NewStringUTF(result);
}

extern "C" JNIEXPORT jstring JNICALL
Java_com_nimbridge_NimBridgeModule_nativeMobileCreateUser(JNIEnv *env, jclass clazz, jint id, jstring name, jstring email) {
    initializeNim();
    const char* nameStr = env->GetStringUTFChars(name, 0);
    const char* emailStr = env->GetStringUTFChars(email, 0);
    const char* result = mobileCreateUser(id, nameStr, emailStr);
    env->ReleaseStringUTFChars(name, nameStr);
    env->ReleaseStringUTFChars(email, emailStr);
    return env->NewStringUTF(result);
}

extern "C" JNIEXPORT jint JNICALL
Java_com_nimbridge_NimBridgeModule_nativeMobileValidateEmail(JNIEnv *env, jclass clazz, jstring email) {
    initializeNim();
    return mobileValidateEmail(env->GetStringUTFChars(email, 0));
}

extern "C" JNIEXPORT jstring JNICALL
Java_com_nimbridge_NimBridgeModule_nativeGetNimCoreVersion(JNIEnv *env, jclass clazz) {
    initializeNim();
    const char* result = getNimCoreVersion();
    return env->NewStringUTF(result);
}

