#!/usr/bin/env node
// Writes SUPABASE_URL and SUPABASE_SECRET_KEY into .env.
// The secret is not printed. .env is gitignored.

import { createInterface } from "node:readline";
import { readFile, writeFile } from "node:fs/promises";
import { stdin as input, stdout as output } from "node:process";
import { fileURLToPath } from "node:url";
import path from "node:path";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const envPath = path.join(root, ".env");

function ask(question, { secret = false } = {}) {
  const rl = createInterface({ input, output });
  return new Promise((resolve) => {
    if (secret) {
      rl._writeToOutput = function writeMasked(stringToWrite) {
        if (stringToWrite.startsWith(question) || stringToWrite.includes("\n")) {
          rl.output.write(stringToWrite);
          return;
        }
        rl.output.write("*");
      };
    }
    rl.question(question, (answer) => {
      rl.close();
      if (secret) output.write("\n");
      resolve(answer.trim());
    });
  });
}

function upsert(text, key, value) {
  const line = `${key}=${value}`;
  const pattern = new RegExp(`^${key}=.*$`, "m");
  if (pattern.test(text)) return text.replace(pattern, line);
  const base = text.length === 0 || text.endsWith("\n") ? text : `${text}\n`;
  return `${base}${line}\n`;
}

const url = await ask("Supabase URL (https://….supabase.co): ");
if (!url.startsWith("https://") || !url.includes(".supabase.co")) {
  console.error("That URL does not look like a Supabase project URL. Nothing was written.");
  process.exit(1);
}

const secret = await ask("Secret key (sb_secret_…): ", { secret: true });
if (!secret.startsWith("sb_secret_")) {
  console.error("Expected a secret key starting with sb_secret_. The publishable key will not work here. Nothing was written.");
  process.exit(1);
}

let existing = "";
try {
  existing = await readFile(envPath, "utf8");
} catch (error) {
  if (error.code !== "ENOENT") throw error;
}

let next = upsert(existing, "SUPABASE_URL", url);
next = upsert(next, "SUPABASE_SECRET_KEY", secret);
await writeFile(envPath, next, { mode: 0o600 });

console.log(`Saved SUPABASE_URL and SUPABASE_SECRET_KEY in ${envPath}`);
console.log("The secret was not printed. .env is not committed.");
