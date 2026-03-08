const fs = require('fs');
const path = require('path');

const SKIP_DIRS = ['node_modules', '.yarn', '.git', 'cache_ios_sim', 'cache_android', 'build', '.cxx', 'dist', '__pycache__', '.kotlin', 'Pods', '.gradle', '.expo', 'jniLibs'];
const SKIP_FILES = ['.DS_Store', 'yarn.lock', 'Podfile.lock', 'nimbase.h', 'main.h', 'nim_core', 'nim_core.h', 'nim_core.json'];
const SKIP_EXTS = ['.log', '.o', '.a'];

function isBinaryFile(filePath) {
  const buf = Buffer.alloc(8192);
  const fd = fs.openSync(filePath, 'r');
  try {
    const bytesRead = fs.readSync(fd, buf, 0, 8192, 0);
    for (let i = 0; i < bytesRead; i++) {
      if (buf[i] === 0) return true;
    }
    return false;
  } finally {
    fs.closeSync(fd);
  }
}

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
    'nimrnmobileapp': appName,
  };

  // Bundle path: replace original io/reactnativenim/app with new bundle path
  const originalBundlePath = 'io/reactnativenim/app';

  copyDir(templateDir, targetDir, replacements, dirReplacements, originalBundlePath, bundlePath);

  // Make shell scripts and gradlew executable
  makeExecutable(targetDir);

  console.log(`  Created ${countFiles(targetDir)} files.`);
}

function copyDir(src, dest, replacements, dirReplacements, originalBundlePath, newBundlePath, relPath) {
  relPath = relPath || '';
  fs.mkdirSync(dest, { recursive: true });

  const entries = fs.readdirSync(src, { withFileTypes: true });

  for (const entry of entries) {
    const srcPath = path.join(src, entry.name);
    const entryRelPath = relPath ? relPath + '/' + entry.name : entry.name;

    // Apply directory name replacements
    let destName = entry.name;
    for (const [placeholder, value] of Object.entries(dirReplacements)) {
      destName = destName.replaceAll(placeholder, value);
    }

    if (entry.isDirectory()) {
      if (SKIP_DIRS.includes(entry.name)) continue;

      // Check if this directory starts the original bundle path
      // e.g., we're at java/io and originalBundlePath starts with io/...
      if (originalBundlePath && isBundlePathRoot(srcPath, originalBundlePath)) {
        // Copy contents of the original bundle path dir into the new bundle path dir
        const origFullPath = path.join(srcPath, ...originalBundlePath.split('/').slice(1));
        const newFullPath = path.join(dest, newBundlePath);
        if (fs.existsSync(origFullPath)) {
          copyDir(origFullPath, newFullPath, replacements, dirReplacements, null, null, entryRelPath + '/' + originalBundlePath.split('/').slice(1).join('/'));
        }
        continue;
      }

      const destPath = path.join(dest, destName);
      copyDir(srcPath, destPath, replacements, dirReplacements, originalBundlePath, newBundlePath, entryRelPath);
    } else {
      if (SKIP_FILES.includes(entry.name)) continue;
      if (SKIP_EXTS.some(ext => entry.name.endsWith(ext))) continue;

      const destPath = path.join(dest, destName);
      copyFile(srcPath, destPath, replacements);
    }
  }
}

function isBundlePathRoot(dirPath, originalBundlePath) {
  // Check if dirPath contains the first segment and the full original bundle path exists under it
  const segments = originalBundlePath.split('/');
  if (path.basename(dirPath) !== segments[0]) return false;
  const fullPath = path.join(dirPath, ...segments.slice(1));
  return fs.existsSync(fullPath);
}

function copyFile(src, dest, replacements) {
  const basename = path.basename(src);

  // Rename gitignore -> .gitignore (npm strips .gitignore from packages)
  if (basename === 'gitignore') {
    dest = path.join(path.dirname(dest), '.gitignore');
  }

  // Ensure parent directory exists (for nested bundle path dirs)
  fs.mkdirSync(path.dirname(dest), { recursive: true });

  if (isBinaryFile(src)) {
    fs.copyFileSync(src, dest);
  } else {
    // Text file: replace placeholders
    let content = fs.readFileSync(src, 'utf-8');
    for (const [placeholder, value] of Object.entries(replacements)) {
      content = content.replaceAll(placeholder, value);
    }
    fs.writeFileSync(dest, content, 'utf-8');
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
