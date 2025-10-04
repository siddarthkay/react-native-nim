require "json"

package = JSON.parse(File.read(File.join(__dir__, "package.json")))

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

  # This one line handles all new architecture dependencies automatically
  install_modules_dependencies(s)
end