import type { HourlyForecast } from "../types";
import {
  addDays,
  addHours,
  formatLatviaTime,
  getLatviaDayKey,
  getLatviaStartOfHour,
  getLatviaWallClock,
  isWeekendDay,
} from "./timezone";

export interface ChartPoint {
  xIndex: number;
  dayKey: string;
  temperature: number;
  precipitation: number;
  precipitationProbability: number;
  windSpeed: number;
  windDirection: number;
  iconCode: string;
  time: string;
}

export interface DaySegment {
  dayKey: string;
  label: string;
  start: number;
  end: number;
  midIndex: number;
}

function dayKey(time: Date): string {
  return getLatviaDayKey(time);
}

export function getUpcomingHourlyForecasts(
  forecasts: HourlyForecast[],
  now = new Date(),
): HourlyForecast[] {
  if (forecasts.length === 0) return [];

  const currentHour = getLatviaStartOfHour(now);
  const upcoming = forecasts.filter(
    (forecast) => getLatviaWallClock(forecast.time) >= currentHour,
  );

  if (upcoming.length > 0) return upcoming;
  return forecasts.slice(-1);
}

export function getUpcomingTodayForecasts(
  forecasts: HourlyForecast[],
  now = new Date(),
): HourlyForecast[] {
  if (forecasts.length === 0) return [];

  const currentHour = getLatviaStartOfHour(now);
  const end = addHours(currentHour, 24);
  const next24Hours = getUpcomingHourlyForecasts(forecasts, now).filter(
    (forecast) => getLatviaWallClock(forecast.time) < end,
  );

  if (next24Hours.length > 0) return next24Hours;

  const upcoming = getUpcomingHourlyForecasts(forecasts, now);
  if (upcoming.length > 0) return upcoming.slice(0, 24);

  return forecasts.slice(-1);
}

export function filterForecastsByDayCount(
  forecasts: HourlyForecast[],
  days: number,
): HourlyForecast[] {
  if (forecasts.length === 0) return [];

  const start = forecasts[0].time;
  const end = addDays(start, days);
  return forecasts.filter((forecast) => forecast.time < end);
}

export function sumPrecipitation(forecasts: HourlyForecast[]): number {
  return forecasts.reduce((total, forecast) => total + forecast.precipitation, 0);
}

export function toChartPoints(forecasts: HourlyForecast[]): ChartPoint[] {
  return forecasts.map((forecast, index) => ({
    xIndex: index,
    dayKey: dayKey(forecast.time),
    temperature: forecast.temperature,
    precipitation: forecast.precipitation,
    precipitationProbability: forecast.precipitationProbability,
    windSpeed: forecast.windSpeed,
    windDirection: forecast.windDirection,
    iconCode: forecast.iconCode,
    time: forecast.time.toISOString(),
  }));
}

export function getDaySegments(data: ChartPoint[]): DaySegment[] {
  if (data.length === 0) return [];

  const segments: DaySegment[] = [];
  let current: DaySegment | null = null;

  for (const point of data) {
    if (!current || current.dayKey !== point.dayKey) {
      if (current) segments.push(current);
      current = {
        dayKey: point.dayKey,
        label: formatLatviaTime(new Date(point.time), "chartDay"),
        start: point.xIndex,
        end: point.xIndex,
        midIndex: point.xIndex,
      };
    } else {
      current.end = point.xIndex;
      current.midIndex = Math.floor((current.start + current.end) / 2);
    }
  }

  if (current) segments.push(current);
  return segments;
}

export function getHourTicks(data: ChartPoint[], step = 2): number[] {
  if (data.length === 0) return [];
  const ticks: number[] = [];
  for (let i = 0; i < data.length; i += step) {
    ticks.push(i);
  }
  const lastIndex = data.length - 1;
  if (ticks[ticks.length - 1] !== lastIndex) {
    ticks.push(lastIndex);
  }
  return ticks;
}

export function getForecastsForPeriod(
  forecasts: HourlyForecast[],
  period: 1 | 3 | 7,
): HourlyForecast[] {
  if (period === 1) return getUpcomingTodayForecasts(forecasts);
  return filterForecastsByDayCount(forecasts, period);
}

export function getConditionIconStep(period: 1 | 3 | 7): number {
  if (period === 1) return 2;
  if (period === 3) return 4;
  return 8;
}

export function getConditionIconMinGap(period: 1 | 3 | 7): number {
  if (period === 1) return 1;
  if (period === 3) return 2;
  return 4;
}

export function getWindDirectionIconStep(period: 1 | 3 | 7): number {
  if (period === 1) return 2;
  if (period === 3) return 6;
  return 12;
}

export function getHourTickStep(period: 1 | 3 | 7): number {
  return period === 1 ? 1 : 8;
}

export function getConditionIconIndexes(
  data: ChartPoint[],
  period: 1 | 3 | 7,
): Set<number> {
  const indexes = new Set<number>();
  const step = getConditionIconStep(period);
  const minGap = getConditionIconMinGap(period);
  let lastSelected = Number.NEGATIVE_INFINITY;

  data.forEach((point, index) => {
    const isConditionChange =
      index > 0 && point.iconCode !== data[index - 1]?.iconCode;
    const isScheduledIcon = index % step === 0 || index === data.length - 1;

    if (isScheduledIcon || (isConditionChange && index - lastSelected >= minGap)) {
      indexes.add(index);
      lastSelected = index;
    }
  });

  return indexes;
}

export function getHourTicksForPeriod(
  data: ChartPoint[],
  period: 1 | 3 | 7,
): number[] {
  if (period === 1) return getHourTicks(data, getHourTickStep(period));

  const dayPartHours = new Set([0, 8, 16]);
  const ticks = data
    .filter((point) =>
      dayPartHours.has(
        Number(formatLatviaTime(new Date(point.time), "time").slice(0, 2)),
      ),
    )
    .map((point) => point.xIndex);

  return ticks.length > 0 ? ticks : getHourTicks(data, getHourTickStep(period));
}

export function getTodayRainPoint(data: ChartPoint[]): ChartPoint | null {
  if (data.length === 0) return null;

  const wettestByAmount = data.reduce((best, point) =>
    point.precipitation > best.precipitation ? point : best,
  );

  if (wettestByAmount.precipitation > 0) return wettestByAmount;

  const wettestByChance = data.reduce((best, point) =>
    point.precipitationProbability > best.precipitationProbability ? point : best,
  );

  return wettestByChance.precipitationProbability > 0 ? wettestByChance : null;
}

export function formatChartTooltipLabel(
  payload: Array<{ payload?: ChartPoint }>,
): string {
  const point = payload[0]?.payload;
  if (!point?.time) return "";
  return formatLatviaTime(new Date(point.time), "chartTooltip");
}

export function getDayTickLabels(
  daySegments: DaySegment[],
): Map<number, { label: string; isWeekendDay: boolean }> {
  return new Map(
    daySegments.map((segment) => [
      segment.midIndex,
      {
        label: segment.label,
        isWeekendDay: isWeekendDay(segment.dayKey),
      },
    ]),
  );
}
