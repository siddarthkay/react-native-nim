const fs = require('fs');
const path = require('path');

const PLACEHOLDER_EXTENSIONS = [
  '.json', '.ts', '.tsx', '.js', '.jsx', '.nim', '.nimble',
  '.py', '.sh', '.mm', '.h', '.cpp', '.kt', '.java', '.txt', '.cfg', '.md',
  '.pbxproj', '.plist', '.xcworkspacedata', '.xcscheme', '.storyboard',
  '.entitlements', '.xcprivacy', '.xml', '.gradle', '.properties', '.bat',
  '.podspec',
];

const SKIP_DIRS = ['node_modules', '.yarn', '.git', 'cache_ios_sim', 'cache_android', 'build', '.cxx', 'dist', '__pycache__', '.kotlin'];
const SKIP_FILES = ['.DS_Store', 'yarn.lock'];

function scaffold(config) {
  const { templateDir, targetDir, appName, slug, bundleId } = config;

  const bundlePath = bundleId.replace(/\./g, '/');

  const replacements = {
    // Template placeholders (used in templatized files)
    '{{APP_NAME}}': appName,
    '{{APP_SLUG}}': slug,
    '{{BUNDLE_ID}}': bundleId,
    // Original project names (used in native ios/android files kept as-is)
    'nimrnmobileapp': appName,
    'nim-rn-mobile-app': slug,
    'io.reactnativenim.app': bundleId,
  };

  // Directory name replacements (template dir name → target dir name)
  const dirReplacements = {
    '{{APP_NAME}}': appName,
    '{{BUNDLE_PATH}}': bundlePath,
  };

  copyDir(templateDir, targetDir, replacements, dirReplacements);

  // Make shell scripts and gradlew executable
  makeExecutable(targetDir);

  console.log(`  Created ${countFiles(targetDir)} files.`);
}

function copyDir(src, dest, replacements, dirReplacements) {
  fs.mkdirSync(dest, { recursive: true });

  const entries = fs.readdirSync(src, { withFileTypes: true });

  for (const entry of entries) {
    const srcPath = path.join(src, entry.name);

    // Apply directory name replacements
    let destName = entry.name;
    for (const [placeholder, value] of Object.entries(dirReplacements)) {
      destName = destName.replaceAll(placeholder, value);
    }

    if (entry.isDirectory()) {
      if (SKIP_DIRS.includes(entry.name)) continue;

      // For {{BUNDLE_PATH}}, the replacement contains '/' so we need to create nested dirs
      const destPath = path.join(dest, destName);
      copyDir(srcPath, destPath, replacements, dirReplacements);
    } else {
      if (SKIP_FILES.includes(entry.name)) continue;

      const destPath = path.join(dest, destName);
      copyFile(srcPath, destPath, replacements);
    }
  }
}

function copyFile(src, dest, replacements) {
  const ext = path.extname(src).toLowerCase();
  const basename = path.basename(src);

  // Rename gitignore -> .gitignore (npm strips .gitignore from packages)
  if (basename === 'gitignore') {
    dest = path.join(path.dirname(dest), '.gitignore');
  }

  // Ensure parent directory exists (for nested bundle path dirs)
  fs.mkdirSync(path.dirname(dest), { recursive: true });

  const textBasenames = ['gitignore', '.envrc', 'Podfile', 'gradlew', 'proguard-rules.pro', '.xcode.env', 'Makefile'];
  if (PLACEHOLDER_EXTENSIONS.includes(ext) || textBasenames.includes(basename)) {
    // Text file: replace placeholders
    let content = fs.readFileSync(src, 'utf-8');
    for (const [placeholder, value] of Object.entries(replacements)) {
      content = content.replaceAll(placeholder, value);
    }
    fs.writeFileSync(dest, content, 'utf-8');
  } else {
    // Binary file: copy as-is
    fs.copyFileSync(src, dest);
  }
}

function makeExecutable(dir) {
  walkFiles(dir, (filePath) => {
    const name = path.basename(filePath);
    if (filePath.endsWith('.sh') || name === 'gradlew') {
      fs.chmodSync(filePath, 0o755);
    }
  });
}

function walkFiles(dir, callback) {
  const entries = fs.readdirSync(dir, { withFileTypes: true });
  for (const entry of entries) {
    const fullPath = path.join(dir, entry.name);
    if (entry.isDirectory()) {
      walkFiles(fullPath, callback);
    } else {
      callback(fullPath);
    }
  }
}

function countFiles(dir) {
  let count = 0;
  walkFiles(dir, () => count++);
  return count;
}

module.exports = { scaffold };
