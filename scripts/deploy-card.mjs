import { copyFileSync, mkdirSync } from "node:fs";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const rootDir = resolve(dirname(fileURLToPath(import.meta.url)), "..");
const builtCard = resolve(
  rootDir,
  "custom_cards/latvia-weather-chart-card/dist/latvia-weather-chart-card.js",
);
const targets = [
  resolve(
    rootDir,
    "custom_components/latvia_weather/frontend/latvia-weather-chart-card.js",
  ),
  resolve(rootDir, "dist/latvia-weather-chart-card.js"),
];

for (const target of targets) {
  mkdirSync(dirname(target), { recursive: true });
  copyFileSync(builtCard, target);
  console.log(`Copied chart card to ${target}`);
}
