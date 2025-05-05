// TypeScript definitions for Nim Core bindings
// Auto-generated - do not edit manually

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

declare global {
  var NimCore: NimCore;
}

export default global.NimCore;