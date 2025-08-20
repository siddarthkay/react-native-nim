Pod::Spec.new do |s|
  s.name           = "NimBridge"
  s.version        = "1.0.0"
  s.summary        = "Nim bridge for React Native"
  s.homepage       = "https://github.com/example/nim-bridge"
  s.license        = "MIT"
  s.authors        = { "Your Name" => "you@example.com" }
  s.platforms      = { :ios => "12.0" }
  s.source         = { :git => "https://github.com/example/nim-bridge.git", :tag => "#{s.version}" }
  s.source_files   = "ios/**/*.{h,m,mm}"
  s.vendored_libraries = File.expand_path("../../nim/libnimbridge.a", __FILE__)
  s.requires_arc   = true
  s.dependency "React-Core"
  
  # Add Nim include paths
  s.xcconfig = {
    'HEADER_SEARCH_PATHS' => '/opt/homebrew/Cellar/nim/2.2.0/nim/lib $(inherited)',
    'OTHER_LDFLAGS' => '-pthread'
  }
end
