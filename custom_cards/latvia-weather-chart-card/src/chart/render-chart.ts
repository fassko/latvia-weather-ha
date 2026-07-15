import ApexCharts, { type ApexOptions } from "apexcharts";
import type { ForecastPeriod } from "../types";
import {
  type ChartPoint,
  getConditionIconIndexes,
  getDaySegments,
  getDayTickLabels,
  getHourTicksForPeriod,
  getWindDirectionIconStep,
} from "./chart-data";
import { getConditionEmoji, getConditionLabel } from "./condition-icons";
import { METRIC_COLORS, type ChartTheme, WEEKEND_TICK_COLOR } from "./theme";
import { formatLatviaTime } from "./timezone";
import { formatWindSpeed, getWindDirection } from "./wind";

export type ChartSeriesKey = "temperature" | "precipitation" | "windSpeed";

export interface RenderChartOptions {
  container: HTMLElement;
  data: ChartPoint[];
  period: ForecastPeriod;
  theme: ChartTheme;
  hiddenSeries: Set<ChartSeriesKey>;
  onLegendToggle: (series: ChartSeriesKey) => void;
}

const SERIES_LABELS = {
  temperature: "Temperature",
  precipitation: "Precipitation",
  windSpeed: "Wind",
} as const;

function buildAnnotations(
  data: ChartPoint[],
  period: ForecastPeriod,
  theme: ChartTheme,
  hiddenSeries: Set<ChartSeriesKey>,
): ApexOptions["annotations"] {
  const points: NonNullable<ApexOptions["annotations"]>["points"] = [];

  if (!hiddenSeries.has("temperature")) {
    const iconIndexes = getConditionIconIndexes(data, period);
    for (const index of iconIndexes) {
      const point = data[index];
      if (!point?.iconCode) continue;
      points.push({
        x: point.xIndex,
        y: point.temperature,
        marker: { size: 0 },
        label: {
          text: getConditionEmoji(point.iconCode),
          borderWidth: 0,
          style: {
            fontSize: period === 1 ? "16px" : period === 3 ? "14px" : "12px",
            background: "transparent",
            color: theme.text,
          },
          offsetY: -18,
        },
      });
    }
  }

  if (!hiddenSeries.has("windSpeed")) {
    const step = getWindDirectionIconStep(period);
    data.forEach((point, index) => {
      if (index % step !== 0) return;
      points.push({
        x: point.xIndex,
        y: point.windSpeed,
        marker: { size: 0 },
        label: {
          text: "↑",
          borderWidth: 0,
          style: {
            fontSize: period === 1 ? "18px" : period === 3 ? "16px" : "14px",
            fontWeight: "800",
            color: METRIC_COLORS.wind,
            background: "transparent",
          },
          offsetY: 16,
        },
      });
    });
  }

  return { points };
}

function buildTooltip(
  data: ChartPoint[],
  theme: ChartTheme,
): ApexOptions["tooltip"] {
  return {
    theme: "dark",
    shared: true,
    intersect: false,
    custom({ series, seriesIndex, dataPointIndex, w }) {
      const point = data[dataPointIndex];
      if (!point) return "";

      const timeLabel = formatLatviaTime(new Date(point.time), "chartTooltip");
      const condition = point.iconCode
        ? `${getConditionEmoji(point.iconCode)} ${getConditionLabel(point.iconCode)}`
        : "";
      const header = condition ? `${timeLabel}<br/>${condition}` : timeLabel;

      const rows: string[] = [];
      w.config.series.forEach((serie: { name?: string; type?: string }, idx: number) => {
        const value = series[idx]?.[dataPointIndex];
        if (value == null || serie.name == null) return;

        if (serie.name === SERIES_LABELS.temperature) {
          rows.push(
            `<span style="color:${METRIC_COLORS.temperature}">●</span> ${serie.name}: <strong>${Number(value).toFixed(1)}°C</strong>`,
          );
        } else if (serie.name === SERIES_LABELS.precipitation) {
          rows.push(
            `<span style="color:${METRIC_COLORS.precipitation}">■</span> ${serie.name}: <strong>${Number(value).toFixed(2)} mm</strong>`,
          );
        } else if (serie.name === SERIES_LABELS.windSpeed) {
          const direction = getWindDirection(point.windDirection);
          rows.push(
            `<span style="color:${METRIC_COLORS.wind}">●</span> ${serie.name}: <strong>${formatWindSpeed(Number(value))}</strong> from ${direction}`,
          );
        }
      });

      return `<div style="padding:8px 10px;background:${theme.tooltipBg};border:1px solid ${theme.tooltipBorder};border-radius:8px;color:${theme.legend};font-size:13px;line-height:1.5;">${header}<br/>${rows.join("<br/>")}</div>`;
    },
  };
}

export function buildChartOptions({
  data,
  period,
  theme,
  hiddenSeries,
  onLegendToggle,
}: Omit<RenderChartOptions, "container">): ApexOptions {
  const categories = data.map((point) => String(point.xIndex));
  const daySegments = getDaySegments(data);
  const dayTickLabels = getDayTickLabels(daySegments);
  const hourTicks = getHourTicksForPeriod(data, period);
  const spansMultipleDays =
    data.length > 0 && data.some((point) => point.dayKey !== data[0].dayKey);
  const isMultiDay = period > 1 || spansMultipleDays;

  const tempData = hiddenSeries.has("temperature")
    ? data.map(() => null)
    : data.map((point) => Number(point.temperature.toFixed(1)));
  const precipData = hiddenSeries.has("precipitation")
    ? data.map(() => null)
    : data.map((point) => Number(point.precipitation.toFixed(2)));
  const windData = hiddenSeries.has("windSpeed")
    ? data.map(() => null)
    : data.map((point) => Number(point.windSpeed.toFixed(1)));

  const maxPrecip = Math.max(...data.map((point) => point.precipitation), 0.5);
  const maxWind = Math.max(...data.map((point) => point.windSpeed), 1);

  return {
    chart: {
      type: "line",
      height: isMultiDay ? 400 : 320,
      toolbar: { show: false },
      background: "transparent",
      fontFamily: "inherit",
      animations: { enabled: true },
      events: {
        legendClick(_chart, seriesIndex) {
          const keys: ChartSeriesKey[] = ["temperature", "precipitation", "windSpeed"];
          const key = keys[seriesIndex ?? -1];
          if (key) {
            onLegendToggle(key);
          }
          return false;
        },
      },
    },
    colors: [METRIC_COLORS.temperature, METRIC_COLORS.precipitation, METRIC_COLORS.wind],
    stroke: {
      width: [2, 0, 2],
      curve: "smooth",
    },
    plotOptions: {
      bar: {
        columnWidth: period === 1 ? "70%" : period === 3 ? "80%" : "90%",
        borderRadius: 2,
      },
    },
    fill: {
      opacity: [1, 0.7, 1],
    },
    dataLabels: { enabled: false },
    grid: {
      borderColor: theme.grid,
      strokeDashArray: 0,
      xaxis: { lines: { show: false } },
      yaxis: { lines: { show: true } },
    },
    legend: {
      show: true,
      position: "bottom",
      horizontalAlign: "center",
      labels: { colors: theme.legend },
      markers: {
        shape: ["line", "square", "line"],
      },
      onItemClick: {
        toggleDataSeries: false,
      },
    },
    xaxis: {
      type: "category",
      categories,
      tickAmount: hourTicks.length,
      labels: {
        style: { colors: theme.tick, fontSize: isMultiDay ? "10px" : "11px" },
        formatter(value) {
          const index = Number(value);
          const point = data[index];
          if (!point) return "";
          return formatLatviaTime(new Date(point.time), "time");
        },
      },
      axisBorder: { color: theme.dayDivider },
      axisTicks: { show: false },
      tooltip: { enabled: false },
    },
    yaxis: [
      {
        seriesName: SERIES_LABELS.temperature,
        title: { text: "°C", style: { color: theme.tick } },
        labels: { style: { colors: theme.tick } },
        tickAmount: 6,
        decimalsInFloat: 0,
      },
      {
        seriesName: SERIES_LABELS.precipitation,
        opposite: true,
        min: 0,
        max: Math.ceil(maxPrecip * 2) / 2 || 2,
        tickAmount: 6,
        title: { text: "mm", style: { color: theme.tick } },
        labels: { style: { colors: theme.tick } },
      },
      {
        seriesName: SERIES_LABELS.windSpeed,
        opposite: true,
        min: 0,
        max: Math.ceil(maxWind) || 5,
        tickAmount: 6,
        title: { text: "m/s", style: { color: theme.tick } },
        labels: {
          style: { colors: theme.tick },
          formatter: (value) => Number(value).toFixed(1),
        },
      },
    ],
    annotations: buildAnnotations(data, period, theme, hiddenSeries),
    tooltip: buildTooltip(data, theme),
    series: [
      {
        name: SERIES_LABELS.temperature,
        type: "line",
        data: tempData,
      },
      {
        name: SERIES_LABELS.precipitation,
        type: "column",
        data: precipData,
      },
      {
        name: SERIES_LABELS.windSpeed,
        type: "line",
        data: windData,
      },
    ],
    ...(isMultiDay
      ? {
          subtitle: {
            text: daySegments
              .map((segment) => {
                const tick = dayTickLabels.get(segment.midIndex);
                if (!tick) return "";
                return tick.isWeekendDay
                  ? `<span style="color:${WEEKEND_TICK_COLOR}">${tick.label}</span>`
                  : tick.label;
              })
              .filter(Boolean)
              .join("   "),
            offsetY: 12,
            style: {
              fontSize: "12px",
              fontWeight: 500,
              color: theme.tick,
            },
          },
        }
      : {}),
  };
}

export class ChartRenderer {
  private chart: ApexCharts | null = null;
  private container: HTMLElement | null = null;

  async render(options: RenderChartOptions): Promise<void> {
    const apexOptions = buildChartOptions(options);
    const { container } = options;

    if (this.chart && this.container !== container) {
      await this.destroy();
    }

    if (this.chart) {
      try {
        await this.chart.updateOptions(apexOptions, true, true);
        return;
      } catch {
        await this.destroy();
      }
    }

    this.container = container;
    this.chart = new ApexCharts(container, apexOptions);
    await this.chart.render();
  }

  async destroy(): Promise<void> {
    if (this.chart) {
      try {
        await this.chart.destroy();
      } catch {
        // Ignore teardown errors when Lit has already replaced the container.
      }
      this.chart = null;
    }
    this.container = null;
  }
}
