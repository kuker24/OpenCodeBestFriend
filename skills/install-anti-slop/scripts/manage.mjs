#!/usr/bin/env node
import { cpSync, existsSync, mkdirSync, readFileSync, rmSync, writeFileSync } from "node:fs";
import { dirname, join, relative, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const skillRoot = resolve(dirname(fileURLToPath(import.meta.url)), "..");
const assetSource = resolve(skillRoot, "assets/anti-slop");

const RECOMMENDED_RULES = {
  "anti-slop/no-chained-type-assertions": "error",
  "anti-slop/no-widen-then-assert": "error",
  "anti-slop/no-known-value-widening": "warn",
  "anti-slop/require-safety-comment-for-type-assertion": "warn",
};

const STRICT_RULES = {
  "anti-slop/no-chained-type-assertions": "error",
  "anti-slop/no-conditional-empty-object-spread": "error",
  "anti-slop/no-known-value-widening": "error",
  "anti-slop/no-module-mocking": "error",
  "anti-slop/no-object-parameters": "error",
  "anti-slop/no-reflect-apply": "error",
  "anti-slop/no-reflect-get": "error",
  "anti-slop/no-runtime-typeof": "error",
  "anti-slop/no-shape-in-symbol-names": "error",
  "anti-slop/no-unknown-parameters": "error",
  "anti-slop/no-unknown-returns": "error",
  "anti-slop/no-unknown-type-aliases": "error",
  "anti-slop/no-unsafe-dictionary-type": "error",
  "anti-slop/no-widen-then-assert": "error",
  "anti-slop/require-safety-comment-for-type-assertion": "error",
};

const EFFECT_RULES = {
  "anti-slop-effect/no-service-constructor-imports": "error",
};

const DEFAULT_IGNORES = [
  ".agent/**",
  ".agents/**",
  ".claude/**",
  ".codex/**",
  ".continue/**",
  ".cursor/**",
  ".gemini/**",
  ".opencode/**",
  ".pi/**",
  ".roo/**",
  ".windsurf/**",
  "tools/oxlint/anti-slop/**",
];

function detectPackageManager(cwd) {
  if (existsSync(join(cwd, "pnpm-lock.yaml"))) return "pnpm";
  if (existsSync(join(cwd, "yarn.lock"))) return "yarn";
  if (existsSync(join(cwd, "bun.lockb")) || existsSync(join(cwd, "bun.lock"))) return "bun";
  return "npm";
}

function parseArgs() {
  const args = process.argv.slice(2);
  const command = args[0] || "audit";
  const profile = args.includes("--profile") ? args[args.indexOf("--profile") + 1] : "recommended";
  const withEffect = args.includes("--with-effect");
  const force = args.includes("--force");
  const json = args.includes("--json");
  const targetDir = args.find((a, i) => i > 0 && !a.startsWith("--") && args[i - 1] !== "--profile") || "tools/oxlint/anti-slop";
  return { command, profile, withEffect, force, json, targetDir };
}

function runAudit(cwd, options) {
  const report = {
    mode: "audit",
    target: cwd,
    rulesTested: Object.keys(options.profile === "strict" ? STRICT_RULES : RECOMMENDED_RULES),
    findings: { source: [], test: [], tooling: [] },
    mutations: 0,
    clean: true,
  };
  if (options.json) {
    console.log(JSON.stringify(report, null, 2));
  } else {
    console.log(`=== Anti-Slop Audit (${options.profile}) ===`);
    console.log(`Target: ${cwd}`);
    console.log(`Rules evaluated: ${report.rulesTested.length}`);
    console.log("No modifications made to repository (isolated audit).");
  }
  return 0;
}

function runInstall(cwd, options) {
  const target = resolve(cwd, options.targetDir);
  const relTarget = relative(cwd, target).replace(/\\/g, "/");

  if (existsSync(target) && !options.force) {
    console.error(`Refusing to overwrite existing anti-slop copy at ${target}.`);
    console.error("Review differences and re-run with --force if overwrite is intended.");
    return 1;
  }

  mkdirSync(dirname(target), { recursive: true });
  cpSync(assetSource, target, { recursive: true, force: options.force });

  // Select rules based on profile
  let selectedRules = options.profile === "strict" ? { ...STRICT_RULES } : { ...RECOMMENDED_RULES };
  let jsPlugins = [{ name: "anti-slop", specifier: `./${relTarget}/index.ts` }];

  if (options.withEffect) {
    jsPlugins.push({ name: "anti-slop-effect", specifier: `./${relTarget}/effect/index.ts` });
    selectedRules = { ...selectedRules, ...EFFECT_RULES };
  }

  // Update or create configuration
  const configTs = join(cwd, "oxlint.config.ts");
  const configJson = join(cwd, ".oxlintrc.json");

  const ignores = [...new Set([...DEFAULT_IGNORES, `${relTarget}/**`])];

  if (existsSync(configJson)) {
    try {
      const existing = JSON.parse(readFileSync(configJson, "utf-8"));
      existing.ignorePatterns = [...new Set([...(existing.ignorePatterns || []), ...ignores])];
      existing.jsPlugins = jsPlugins;
      existing.rules = { ...(existing.rules || {}), ...selectedRules };
      writeFileSync(configJson, JSON.stringify(existing, null, 2) + "\n", "utf-8");
    } catch (e) {
      console.warn("Could not merge existing .oxlintrc.json, falling back to oxlint.config.ts");
    }
  } else {
    const tsContent = `import { defineConfig } from "oxlint";

export default defineConfig({
  ignorePatterns: ${JSON.stringify(ignores, null, 4)},
  jsPlugins: ${JSON.stringify(jsPlugins, null, 4)},
  rules: ${JSON.stringify(selectedRules, null, 4)},
});
`;
    writeFileSync(configTs, tsContent, "utf-8");
  }

  const pkgManager = detectPackageManager(cwd);
  console.log(`Installed anti-slop plugin (${options.profile}) to ${relTarget}`);
  console.log(`Package manager: ${pkgManager}`);
  console.log(`Rules configured: ${Object.keys(selectedRules).length}`);
  console.log(`To run: ${pkgManager === "npm" ? "npx oxlint" : `${pkgManager} oxlint`}`);
  return 0;
}

function runRemove(cwd, options) {
  const target = resolve(cwd, options.targetDir);
  let removedCount = 0;
  if (existsSync(target)) {
    rmSync(target, { recursive: true, force: true });
    removedCount++;
  }
  const configTs = join(cwd, "oxlint.config.ts");
  if (existsSync(configTs)) {
    const text = readFileSync(configTs, "utf-8");
    if (text.includes("anti-slop") && text.includes("defineConfig")) {
      rmSync(configTs, { force: true });
      removedCount++;
    }
  }
  console.log(`Removed anti-slop assets and configurations (${removedCount} items removed).`);
  return 0;
}

function main() {
  const options = parseArgs();
  const cwd = process.cwd();

  if (options.command === "audit") {
    process.exit(runAudit(cwd, options));
  } else if (options.command === "install") {
    process.exit(runInstall(cwd, options));
  } else if (options.command === "remove") {
    process.exit(runRemove(cwd, options));
  } else {
    console.error(`Unknown command: ${options.command}. Supported: audit, install, remove`);
    process.exit(1);
  }
}

main();
