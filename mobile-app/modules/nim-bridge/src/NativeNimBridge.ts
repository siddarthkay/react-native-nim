import type { TurboModule } from 'react-native';
import { TurboModuleRegistry } from 'react-native';

export interface Spec extends TurboModule {
  // Core API
  readonly helloWorld: () => string;
  readonly addNumbers: (a: number, b: number) => number;
  readonly getSystemInfo: () => string;

  // Math operations
  readonly fibonacci: (n: number) => number;
  readonly isPrime: (n: number) => boolean;
  readonly factorize: (n: number) => string;

  // Data operations
  readonly createUser: (id: number, name: string, email: string) => string;
  readonly validateEmail: (email: string) => boolean;

  // Version info
  readonly getVersion: () => string;
}

export default TurboModuleRegistry.getEnforcing<Spec>('NimBridge');