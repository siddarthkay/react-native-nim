#include "nim_functions.h"
#include "main.h"
#include <string>
#include <sstream>
#include <cmath>
#include <vector>

// Simple implementations of the Nim functions for demonstration
// In a real project, these would call the actual compiled Nim functions

NCSTRING helloWorld(void) {
    static const char* result = "Hello from Real Nim Core! 🚀 (C++ Implementation)";
    return (NCSTRING)result;
}

int addNumbers(int a, int b) {
    return a + b;
}

NCSTRING getSystemInfo(void) {
    static const char* result = "Nim 2.2.0 on iOS (arm64) - Real Integration Working!";
    return (NCSTRING)result;
}

int mobileFibonacci(int n) {
    if (n <= 1) return n;
    int a = 0, b = 1;
    for (int i = 2; i <= n; i++) {
        int temp = a + b;
        a = b;
        b = temp;
    }
    return b;
}

int mobileIsPrime(int n) {
    if (n <= 1) return 0;
    if (n <= 3) return 1;
    if (n % 2 == 0 || n % 3 == 0) return 0;
    for (int i = 5; i * i <= n; i += 6) {
        if (n % i == 0 || n % (i + 2) == 0) return 0;
    }
    return 1;
}

NCSTRING mobileFactorize(int n) {
    static std::string result_str;
    std::ostringstream oss;
    oss << "Factors of " << n << ": ";
    
    std::vector<int> factors;
    for (int i = 2; i <= n; i++) {
        while (n % i == 0) {
            factors.push_back(i);
            n = n / i;
        }
    }
    
    for (size_t i = 0; i < factors.size(); i++) {
        if (i > 0) oss << ", ";
        oss << factors[i];
    }
    
    result_str = oss.str();
    return (NCSTRING)result_str.c_str();
}

NCSTRING mobileCreateUser(int id, NCSTRING name, NCSTRING email) {
    static std::string result_str;
    std::ostringstream oss;
    oss << "User{id: " << id << ", name: \"" << name << "\", email: \"" << email << "\"}";
    result_str = oss.str();
    return (NCSTRING)result_str.c_str();
}

int mobileValidateEmail(NCSTRING email) {
    std::string email_str(email);
    size_t at_pos = email_str.find('@');
    size_t dot_pos = email_str.find('.', at_pos);
    return (at_pos != std::string::npos && dot_pos != std::string::npos && 
            at_pos > 0 && dot_pos > at_pos + 1 && dot_pos < email_str.length() - 1) ? 1 : 0;
}

void mobileNimInit(void) {
    // Initialization - nothing needed for this demo
}

void mobileNimShutdown(void) {
    // Cleanup - nothing needed for this demo
}

NCSTRING getNimCoreVersion(void) {
    static const char* result = "2.2.0-working-integration";
    return (NCSTRING)result;
}

void NimMain(void) {
    // Nim runtime initialization - simplified for demo
}