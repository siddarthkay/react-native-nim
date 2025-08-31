import {AppRegistry, Platform} from 'react-native';
import App from './src/App';
import {name as appName} from './package.json';

// Register with platform-specific name
const componentName: string = Platform.OS === 'android' ? 'main' : appName;
AppRegistry.registerComponent(componentName, () => App);