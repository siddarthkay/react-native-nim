require "json"

package = JSON.parse(File.read(File.join(__dir__, "package.json")))
folly_compiler_flags = '-DFOLLY_NO_CONFIG -DFOLLY_MOBILE=1 -DFOLLY_USE_LIBCPP=1 -Wno-comma -Wno-shorten-64-to-32'

Pod::Spec.new do |s|
  s.name         = "NimBridge"
  s.version      = package["version"]
  s.summary      = package["description"]
  s.description  = <<-DESC
                  A React Native module that bridges Nim code for high-performance operations.
                   DESC
  s.homepage     = "https://github.com/example/nim-bridge"
  s.license      = "MIT"
  s.authors      = { "Your Name" => "yourname@example.com" }
  s.platforms    = { :ios => "15.1" }
  s.source       = { :git => "https://github.com/example/nim-bridge.git", :tag => "#{s.version}" }

  s.source_files = "ios/**/*.{h,m,mm}"
  s.header_mappings_dir = "ios"
  s.public_header_files = "ios/NimBridge.h"
  s.vendored_libraries = "ios/libnim_core.a"

  # Add Nim include paths - will be set by build script if needed
  s.xcconfig = {
    'OTHER_LDFLAGS' => '-pthread'
  }

  # React Native dependencies
  s.dependency "React-Core"

  # Don't install the dependencies when we run `pod install` in the old architecture.
  if ENV['RCT_NEW_ARCH_ENABLED'] == '1' then
    s.compiler_flags = folly_compiler_flags + " -DRCT_NEW_ARCH_ENABLED=1"
    s.pod_target_xcconfig    = {
        "HEADER_SEARCH_PATHS" => "\"$(PODS_ROOT)/boost\"",
        "OTHER_CPLUSPLUSFLAGS" => "-DFOLLY_NO_CONFIG -DFOLLY_MOBILE=1 -DFOLLY_USE_LIBCPP=1",
        "CLANG_CXX_LANGUAGE_STANDARD" => "c++17"
    }
    s.dependency "React-Codegen"
    s.dependency "RCT-Folly"
    s.dependency "RCTRequired"
    s.dependency "RCTTypeSafety"
    s.dependency "ReactCommon/turbomodule/core"
  end
end