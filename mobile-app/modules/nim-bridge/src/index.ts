import NativeNimBridge from './NativeNimBridge';

export interface NimCore {
  // Core API
  helloWorld(): string;
  addNumbers(a: number, b: number): number;
  getSystemInfo(): string;

  // Math operations
  fibonacci(n: number): number;
  isPrime(n: number): boolean;
  factorize(n: number): string;

  // Data operations
  createUser(id: number, name: string, email: string): string;
  validateEmail(email: string): boolean;

  // Version info
  getVersion(): string;
}

export const NimCore: NimCore = {
  helloWorld: () => NativeNimBridge.helloWorld(),
  addNumbers: (a: number, b: number) => NativeNimBridge.addNumbers(a, b),
  getSystemInfo: () => NativeNimBridge.getSystemInfo(),
  fibonacci: (n: number) => NativeNimBridge.fibonacci(n),
  isPrime: (n: number) => NativeNimBridge.isPrime(n),
  factorize: (n: number) => NativeNimBridge.factorize(n),
  createUser: (id: number, name: string, email: string) =>
    NativeNimBridge.createUser(id, name, email),
  validateEmail: (email: string) => NativeNimBridge.validateEmail(email),
  getVersion: () => NativeNimBridge.getVersion(),
};

export default NimCore;