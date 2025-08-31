import React, { useState, useEffect } from 'react';
import {
  StyleSheet,
  Text,
  View,
  TouchableOpacity,
  ScrollView,
  TextInput,
  Alert,
  SafeAreaView,
  StatusBar,
  Dimensions,
} from 'react-native';
import { NimCore } from '../modules/nim-bridge/src/index';

const App: React.FC = () => {
  const [nimStatus, setNimStatus] = useState<string>('Initializing...');
  const [mathInput, setMathInput] = useState<string>('10');
  const [results, setResults] = useState<string[]>([]);
  const [userEmail, setUserEmail] = useState<string>('test@example.com');

  useEffect(() => {
    // Initialize Nim when component mounts
    try {
      setNimStatus('Nim Core Ready (Development)');
      addResult('Nim Core initialized successfully - Development Mock');
      addResult(`Version: ${NimCore.getVersion()}`);
    } catch (error) {
      setNimStatus('Nim Core Error');
      addResult(`Error: ${error instanceof Error ? error.message : String(error)}`);
    }
  }, []);

  const addResult = (result: string) => {
    setResults(prev => [`${new Date().toLocaleTimeString()}: ${result}`, ...prev.slice(0, 9)]);
  };

  const testHelloWorld = () => {
    try {
      const greeting = NimCore.helloWorld();
      addResult(`${greeting}`);
      Alert.alert('Nim Says', greeting);
    } catch (error) {
      addResult(`Hello World failed: ${error instanceof Error ? error.message : String(error)}`);
    }
  };

  const testMathOperations = () => {
    try {
      const num = parseInt(mathInput) || 10;
      
      // Check for Fibonacci overflow
      if (num > 78) {
        Alert.alert(
          'MATH_PROCESSOR LIMIT',
          'Fibonacci calculation exceeds JavaScript MAX_SAFE_INTEGER for values > 78. Results will be inaccurate.',
          [{ text: 'OK' }]
        );
      }
      
      // Test addition
      const sum = NimCore.addNumbers(num, 5);
      addResult(`${num} + 5 = ${sum}`);
      
      // Test Fibonacci
      const fib = NimCore.fibonacci(num);
      addResult(`Fibonacci(${num}) = ${fib}`);
      
      // Test prime check
      const isPrime = NimCore.isPrime(num);
      addResult(`${num} is ${isPrime ? 'prime' : 'not prime'}`);
      
      // Test factorization
      const factors = NimCore.factorize(num);
      addResult(`Factors of ${num}: ${factors}`);
      
    } catch (error) {
      addResult(`Math operations failed: ${error instanceof Error ? error.message : String(error)}`);
    }
  };

  const testDataOperations = () => {
    try {
      // Test email validation
      const isValid = NimCore.validateEmail(userEmail);
      addResult(`Email "${userEmail}" is ${isValid ? 'valid' : 'invalid'}`);
      
      // Test user creation
      const userJson = NimCore.createUser(1, 'John Doe', userEmail);
      addResult(`Created user: ${userJson}`);
      
    } catch (error) {
      addResult(`Data operations failed: ${error instanceof Error ? error.message : String(error)}`);
    }
  };

  const testSystemInfo = () => {
    try {
      const info = NimCore.getSystemInfo();
      const version = NimCore.getVersion();
      addResult(`System: ${info}`);
      addResult(`Nim Core Version: ${version}`);
    } catch (error) {
      addResult(`System info failed: ${error instanceof Error ? error.message : String(error)}`);
    }
  };

  return (
    <SafeAreaView style={styles.container}>
      <StatusBar barStyle="light-content" backgroundColor="#1a1b4a" />
      <ScrollView contentInsetAdjustmentBehavior="automatic" showsVerticalScrollIndicator={false}>
        
        {/* Header with gradient effect */}
        <View style={styles.header}>
          <View style={styles.headerGradient}>
            <Text style={styles.title}>NIM-BRIDGE v1.0</Text>
            <Text style={styles.subtitle}>TERMINAL INTERFACE - BUSINESS LOGIC SUBSYSTEM</Text>
            <View style={[styles.statusBadge, nimStatus.includes('Ready') ? styles.statusSuccess : styles.statusError]}>
              <Text style={styles.statusText}>{nimStatus}</Text>
            </View>
          </View>
        </View>

        {/* Test Buttons */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>[ CORE API TESTS ]</Text>
          
          <TouchableOpacity style={[styles.button, styles.primaryButton]} onPress={testHelloWorld}>
            <Text style={styles.buttonText}>> EXEC HELLO_WORLD</Text>
          </TouchableOpacity>
          
          <TouchableOpacity style={[styles.button, styles.secondaryButton]} onPress={testSystemInfo}>
            <Text style={styles.buttonText}>> QUERY SYSTEM_INFO</Text>
          </TouchableOpacity>
        </View>

        {/* Math Operations */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>[ MATH_PROCESSOR ]</Text>
          
          <TextInput
            style={styles.input}
            value={mathInput}
            onChangeText={setMathInput}
            placeholder="INPUT: NUMERIC_VALUE"
            keyboardType="numeric"
            placeholderTextColor="#666666"
          />
          
          <TouchableOpacity style={[styles.button, styles.accentButton]} onPress={testMathOperations}>
            <Text style={styles.buttonText}>> RUN MATH_SUITE</Text>
          </TouchableOpacity>
        </View>

        {/* Data Operations */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>[ DATA_HANDLER ]</Text>
          
          <TextInput
            style={styles.input}
            value={userEmail}
            onChangeText={setUserEmail}
            placeholder="INPUT: EMAIL_ADDRESS"
            keyboardType="email-address"
            placeholderTextColor="#666666"
          />
          
          <TouchableOpacity style={[styles.button, styles.successButton]} onPress={testDataOperations}>
            <Text style={styles.buttonText}>> PROCESS DATA_VALIDATION</Text>
          </TouchableOpacity>
        </View>

        {/* Results */}
        <View style={[styles.section, styles.resultsSection]}>
          <View style={styles.resultsTitleContainer}>
            <Text style={styles.sectionTitle}>[ OUTPUT_TERMINAL ]</Text>
            <TouchableOpacity 
              style={styles.clearButton} 
              onPress={() => setResults([])}
            >
              <Text style={styles.clearButtonText}>CLEAR</Text>
            </TouchableOpacity>
          </View>
          
          <ScrollView style={styles.resultsContainer} nestedScrollEnabled={true}>
            {results.length === 0 ? (
              <View style={styles.noResultsContainer}>
                <Text style={styles.noResultsTitle}>SYSTEM READY</Text>
                <Text style={styles.noResults}>Execute commands to view output</Text>
              </View>
            ) : (
              results.map((result, index) => (
                <View key={index} style={styles.resultItem}>
                  <Text style={styles.result}>{result}</Text>
                </View>
              ))
            )}
          </ScrollView>
        </View>
        
        <View style={styles.footer}>
          <Text style={styles.footerText}>SYSTEM: NIM-BRIDGE v1.0 | STATUS: OPERATIONAL</Text>
        </View>
        
      </ScrollView>
    </SafeAreaView>
  );
};

const { width } = Dimensions.get('window');

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#1a1a1a',
  },
  header: {
    backgroundColor: '#000000',
    paddingTop: 20,
    paddingBottom: 20,
    borderBottomWidth: 2,
    borderBottomColor: '#00ff00',
  },
  headerGradient: {
    alignItems: 'center',
    paddingHorizontal: 20,
  },
  title: {
    fontSize: 24,
    fontWeight: '400',
    color: '#00ff00',
    marginBottom: 8,
    letterSpacing: 2,
    fontFamily: 'monospace',
  },
  subtitle: {
    fontSize: 12,
    color: '#00cc00',
    marginBottom: 15,
    textAlign: 'center',
    letterSpacing: 1,
    fontFamily: 'monospace',
  },
  statusBadge: {
    paddingHorizontal: 12,
    paddingVertical: 4,
    borderWidth: 1,
    borderColor: '#00ff00',
    backgroundColor: '#000000',
  },
  statusSuccess: {
    borderColor: '#00ff00',
  },
  statusError: {
    borderColor: '#ff0000',
  },
  statusText: {
    color: '#00ff00',
    fontSize: 10,
    fontFamily: 'monospace',
    letterSpacing: 1,
  },
  section: {
    marginHorizontal: 12,
    marginTop: 15,
    padding: 15,
    backgroundColor: '#2a2a2a',
    borderWidth: 1,
    borderColor: '#444444',
    borderRadius: 0,
  },
  resultsSection: {
    marginBottom: 20,
  },
  sectionTitle: {
    fontSize: 14,
    fontWeight: '400',
    marginBottom: 15,
    color: '#00ff00',
    letterSpacing: 1,
    fontFamily: 'monospace',
  },
  resultsTitleContainer: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 15,
  },
  button: {
    paddingVertical: 12,
    paddingHorizontal: 20,
    borderRadius: 0,
    marginVertical: 4,
    borderWidth: 1,
    backgroundColor: '#333333',
  },
  primaryButton: {
    borderColor: '#00ff00',
    backgroundColor: '#001100',
  },
  secondaryButton: {
    borderColor: '#0088ff',
    backgroundColor: '#001122',
  },
  accentButton: {
    borderColor: '#ff8800',
    backgroundColor: '#221100',
  },
  successButton: {
    borderColor: '#88ff00',
    backgroundColor: '#112200',
  },
  clearButton: {
    backgroundColor: '#220000',
    borderWidth: 1,
    borderColor: '#ff0000',
    paddingHorizontal: 12,
    paddingVertical: 6,
  },
  buttonText: {
    color: '#ffffff',
    fontSize: 12,
    fontWeight: '400',
    textAlign: 'center',
    letterSpacing: 1,
    fontFamily: 'monospace',
  },
  clearButtonText: {
    color: '#ff0000',
    fontSize: 10,
    fontFamily: 'monospace',
    letterSpacing: 1,
  },
  input: {
    borderWidth: 1,
    borderColor: '#666666',
    borderRadius: 0,
    paddingVertical: 12,
    paddingHorizontal: 12,
    marginBottom: 15,
    fontSize: 14,
    backgroundColor: '#1a1a1a',
    color: '#00ff00',
    fontFamily: 'monospace',
  },
  resultsContainer: {
    height: 200,
    backgroundColor: '#000000',
    borderWidth: 1,
    borderColor: '#333333',
    padding: 8,
  },
  noResultsContainer: {
    alignItems: 'center',
    justifyContent: 'center',
    flex: 1,
  },
  noResultsTitle: {
    fontSize: 14,
    fontWeight: '400',
    color: '#00ff00',
    marginBottom: 8,
    fontFamily: 'monospace',
    letterSpacing: 1,
  },
  noResults: {
    fontSize: 12,
    color: '#888888',
    textAlign: 'center',
    fontFamily: 'monospace',
  },
  resultItem: {
    backgroundColor: '#111111',
    marginVertical: 1,
    paddingVertical: 4,
    paddingHorizontal: 8,
    borderLeftWidth: 2,
    borderLeftColor: '#00ff00',
  },
  result: {
    fontSize: 11,
    fontFamily: 'monospace',
    color: '#00cc00',
    lineHeight: 16,
  },
  footer: {
    alignItems: 'center',
    paddingVertical: 15,
    marginBottom: 20,
    borderTopWidth: 1,
    borderTopColor: '#333333',
  },
  footerText: {
    fontSize: 10,
    color: '#666666',
    fontFamily: 'monospace',
    letterSpacing: 1,
  },
});

export default App;