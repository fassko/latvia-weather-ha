export const METRIC_COLORS = {
  temperature: "#f97316",
  precipitation: "#38bdf8",
  wind: "#10b981",
} as const;

export const WEEKEND_TICK_COLOR = "#dc2626";

export const CHART_COLORS = {
  light: {
    grid: "#e2e8f0",
    tick: "#64748b",
    dayDivider: "#cbd5e1",
    tooltipBg: "#ffffff",
    tooltipBorder: "#e2e8f0",
    legend: "#334155",
    cardBg: "#ffffff",
    cardBorder: "#e2e8f0",
    text: "#0f172a",
    mutedText: "#64748b",
    toggleBg: "#f1f5f9",
    toggleActive: "#0ea5e9",
    toggleText: "#475569",
  },
  dark: {
    grid: "#475569",
    tick: "#94a3b8",
    dayDivider: "#475569",
    tooltipBg: "#1e293b",
    tooltipBorder: "#475569",
    legend: "#cbd5e1",
    cardBg: "#0f172a",
    cardBorder: "#334155",
    text: "#f8fafc",
    mutedText: "#94a3b8",
    toggleBg: "#1e293b",
    toggleActive: "#0ea5e9",
    toggleText: "#cbd5e1",
  },
} as const;

export type ChartTheme = (typeof CHART_COLORS)[keyof typeof CHART_COLORS];

export function getChartTheme(isDark: boolean): ChartTheme {
  return isDark ? CHART_COLORS.dark : CHART_COLORS.light;
}
