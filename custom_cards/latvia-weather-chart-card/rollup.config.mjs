import commonjs from "@rollup/plugin-commonjs";
import resolve from "@rollup/plugin-node-resolve";
import typescript from "@rollup/plugin-typescript";

export default {
  input: "src/latvia-weather-chart-card.ts",
  output: {
    file: "dist/latvia-weather-chart-card.js",
    format: "es",
    sourcemap: true,
  },
  plugins: [resolve({ browser: true }), commonjs(), typescript({ tsconfig: "./tsconfig.json" })],
};
