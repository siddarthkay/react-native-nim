import { NativeModules, Platform } from 'react-native';

const LINKING_ERROR =
  `The package 'nim-bridge' doesn't seem to be linked. Make sure: \n\n` +
  Platform.select({ ios: "- You have run 'cd ios && pod install'\n", default: '' }) +
  '- You rebuilt the app after installing the package\n' +
  '- You are not using Expo Go\n';

const NimBridge = NativeModules.NimBridge
  ? NativeModules.NimBridge
  : new Proxy(
      {},
      {
        get() {
          throw new Error(LINKING_ERROR);
        },
      }
    );

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
  helloWorld: () => NimBridge.helloWorld(),
  addNumbers: (a: number, b: number) => NimBridge.addNumbers(a, b),
  getSystemInfo: () => NimBridge.getSystemInfo(),
  fibonacci: (n: number) => NimBridge.mobileFibonacci(n),
  isPrime: (n: number) => Boolean(NimBridge.mobileIsPrime(n)),
  factorize: (n: number) => NimBridge.mobileFactorize(n),
  createUser: (id: number, name: string, email: string) => 
    NimBridge.mobileCreateUser(id, name, email),
  validateEmail: (email: string) => Boolean(NimBridge.mobileValidateEmail(email)),
  getVersion: () => NimBridge.getNimCoreVersion(),
};

export default NimCore;