#ifdef RCT_NEW_ARCH_ENABLED
#import "RNNimBridgeSpec.h"

@interface NimBridge : NSObject <NativeNimBridgeSpec>
#else
#import <React/RCTBridgeModule.h>

@interface NimBridge : NSObject <RCTBridgeModule>
#endif

@end