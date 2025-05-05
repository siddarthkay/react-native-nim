// Nim Core integration for React Native
// This provides a mock implementation for development and testing

export interface NimCore {
  // Core API
  helloWorld(): string;
  addNumbers(a: number, b: number): number;
  getSystemInfo(): string;
  
  // Math operations
  fibonacci(n: number): number;
  isPrime(n: number): boolean;
  factorize(n: number): number[];
  
  // Data operations
  createUser(id: number, name: string, email: string): string;
  validateEmail(email: string): boolean;
  
  // Version info
  getVersion(): string;
}

// Mock implementation for development
const mockNimCore: NimCore = {
  helloWorld: () => "Hello from Nim Core! 🎉 (Development Mock)",
  
  addNumbers: (a: number, b: number) => a + b,
  
  getSystemInfo: () => "Nim 2.2.0 on iOS (arm64) - Development Environment",
  
  fibonacci: (n: number) => {
    if (n <= 1) return n;
    let a = 0, b = 1;
    for (let i = 2; i <= n; i++) {
      const temp = a + b;
      a = b;
      b = temp;
    }
    return b;
  },
  
  isPrime: (n: number) => {
    if (n <= 1) return false;
    if (n <= 3) return true;
    if (n % 2 === 0 || n % 3 === 0) return false;
    for (let i = 5; i * i <= n; i += 6) {
      if (n % i === 0 || n % (i + 2) === 0) return false;
    }
    return true;
  },
  
  factorize: (n: number) => {
    const factors: number[] = [];
    for (let i = 2; i <= n; i++) {
      while (n % i === 0) {
        factors.push(i);
        n = n / i;
      }
    }
    return factors;
  },
  
  createUser: (id: number, name: string, email: string) => 
    `User{id: ${id}, name: "${name}", email: "${email}"}`,
  
  validateEmail: (email: string) => {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
  },
  
  getVersion: () => "2.2.0-development-mock"
};

// Export the implementation
export const NimCore = mockNimCore;

// Also attach to global for compatibility
if (typeof global !== 'undefined') {
  (global as any).NimCore = mockNimCore;
}