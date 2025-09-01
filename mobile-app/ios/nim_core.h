#ifndef NIM_CORE_BINDINGS_H
#define NIM_CORE_BINDINGS_H

#ifdef __cplusplus
extern "C" {
#endif

// Core API functions
const char* helloWorld(void);
int addNumbers(int a, int b);
const char* getSystemInfo(void);

// Math operations
int mobileFibonacci(int n);
int mobileIsPrime(int n);
const char* mobileFactorize(int n);

// Data operations
const char* mobileCreateUser(int id, const char* name, const char* email);
int mobileValidateEmail(const char* email);

// Runtime management
void mobileNimInit(void);
void mobileNimShutdown(void);
void NimMain(void);

// Version info
const char* getNimCoreVersion(void);

#ifdef __cplusplus
}
#endif

#endif // NIM_CORE_BINDINGS_H
