import type ApexCharts from "apexcharts";

type ApexChartsConstructor = typeof ApexCharts;

declare global {
  interface Window {
    ApexCharts?: ApexChartsConstructor;
  }
}

let apexChartsCtor: ApexChartsConstructor | null = null;
let apexChartsPromise: Promise<ApexChartsConstructor> | null = null;

/** Prefer an already-loaded ApexCharts instance (e.g. apexcharts-card) to avoid SVG.js conflicts. */
export async function getApexCharts(): Promise<ApexChartsConstructor> {
  if (apexChartsCtor) return apexChartsCtor;

  if (typeof window !== "undefined" && window.ApexCharts) {
    apexChartsCtor = window.ApexCharts;
    return apexChartsCtor;
  }

  if (!apexChartsPromise) {
    apexChartsPromise = import("apexcharts").then((module) => {
      const bundled = module.default;
      apexChartsCtor = bundled;

      if (typeof window !== "undefined" && !window.ApexCharts) {
        window.ApexCharts = bundled;
      }

      return typeof window !== "undefined" && window.ApexCharts
        ? window.ApexCharts
        : bundled;
    });
  }

  return apexChartsPromise;
}
