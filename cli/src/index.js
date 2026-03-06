const { prompt } = require('./prompts.js');
const { scaffold } = require('./scaffold.js');
const path = require('path');
const fs = require('fs');

function toPascalCase(str) {
  return str
    .replace(/[-_\s]+(.)?/g, (_, c) => (c ? c.toUpperCase() : ''))
    .replace(/^(.)/, (_, c) => c.toUpperCase());
}

function toKebabCase(str) {
  return str
    .replace(/([a-z])([A-Z])/g, '$1-$2')
    .replace(/[\s_]+/g, '-')
    .toLowerCase();
}

function parseArgs(args) {
  const parsed = { positional: [], flags: {} };
  for (let i = 0; i < args.length; i++) {
    if (args[i].startsWith('--')) {
      const key = args[i].slice(2);
      parsed.flags[key] = args[i + 1] && !args[i + 1].startsWith('--') ? args[++i] : true;
    } else {
      parsed.positional.push(args[i]);
    }
  }
  return parsed;
}

async function main() {
  const { positional, flags } = parseArgs(process.argv.slice(2));
  const templateName = flags.template || 'default';

  console.log('\n  create-react-native-nim\n');
  console.log('  Scaffold a React Native app with Nim business logic\n');

  // Check if project name was passed as argument
  let projectDir = positional[0];

  if (!projectDir) {
    projectDir = await prompt('Project name: ');
    if (!projectDir) {
      console.error('  Project name is required.');
      process.exit(1);
    }
  }

  const slug = toKebabCase(projectDir);
  const appName = toPascalCase(projectDir);

  const defaultBundleId = `com.${slug.replace(/-/g, '')}`;

  console.log(`\n  App name:  ${appName}`);
  console.log(`  Slug:      ${slug}\n`);

  const bundleId = (await prompt(`Bundle identifier (${defaultBundleId}): `)) || defaultBundleId;

  // Resolve template
  const templateDir = resolveTemplateDir(templateName);
  const targetDir = path.resolve(process.cwd(), projectDir);

  if (fs.existsSync(targetDir)) {
    console.error(`\n  Directory "${projectDir}" already exists.`);
    process.exit(1);
  }

  const config = {
    appName,
    slug,
    bundleId,
    projectDir,
    templateDir,
    targetDir,
  };

  console.log(`\n  Scaffolding into ./${projectDir}...\n`);

  try {
    scaffold(config);
    printNextSteps(projectDir);
  } catch (err) {
    console.error(`\n  Error: ${err.message}`);
    process.exit(1);
  }
}

function resolveTemplateDir(templateName) {
  // When running from the repo (development)
  const repoTemplate = path.resolve(__dirname, '../../templates', templateName);
  if (fs.existsSync(repoTemplate)) {
    return repoTemplate;
  }

  // When installed as npm package, templates are bundled
  const pkgTemplate = path.resolve(__dirname, '../templates', templateName);
  if (fs.existsSync(pkgTemplate)) {
    return pkgTemplate;
  }

  // List available templates
  const repoTemplatesDir = path.resolve(__dirname, '../../templates');
  const pkgTemplatesDir = path.resolve(__dirname, '../templates');
  const templatesDir = fs.existsSync(repoTemplatesDir) ? repoTemplatesDir : pkgTemplatesDir;

  if (fs.existsSync(templatesDir)) {
    const available = fs.readdirSync(templatesDir, { withFileTypes: true })
      .filter(d => d.isDirectory())
      .map(d => d.name);
    console.error(`  Template "${templateName}" not found.`);
    console.error(`  Available templates: ${available.join(', ')}`);
  } else {
    console.error('  Could not find templates directory.');
  }
  process.exit(1);
}

function printNextSteps(projectDir) {
  console.log('  Done! Next steps:\n');
  console.log(`    cd ${projectDir}`);
  console.log('    yarn install');
  console.log('    make build-nim');
  console.log('    yarn ios        # or yarn android');
  console.log('');
  console.log('  Prerequisites:');
  console.log('    - Nim 2.0+ (brew install nim)');
  console.log('    - Python 3 (for binding generator)');
  console.log('    - Xcode (for iOS) / Android SDK (for Android)');
  console.log('');
  console.log('  Alternatively, use Nix to get all dependencies:');
  console.log('    nix develop');
  console.log('');
}

module.exports = { main };
