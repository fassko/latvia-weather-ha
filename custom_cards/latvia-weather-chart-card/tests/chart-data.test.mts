import assert from "node:assert/strict";
import { test } from "node:test";
import {
  filterForecastsByDayCount,
  getConditionIconIndexes,
  getDaySegments,
  getUpcomingHourlyForecasts,
  getUpcomingTodayForecasts,
  sumPrecipitation,
  toChartPoints,
} from "../src/chart/chart-data.ts";
import {
  getConditionKey,
  getConditionEmoji,
} from "../src/chart/condition-icons.ts";
import { getWindDirection } from "../src/chart/wind.ts";
import { formatLaiks, zonedTimeToUtc } from "../src/chart/timezone.ts";
import type { HourlyForecast } from "../src/types.ts";

function sampleForecast(laiks: string, overrides: Partial<HourlyForecast> = {}): HourlyForecast {
  const time = zonedTimeToUtc(
    Number(laiks.slice(0, 4)),
    Number(laiks.slice(4, 6)),
    Number(laiks.slice(6, 8)),
    Number(laiks.slice(8, 10)),
    Number(laiks.slice(10, 12)),
  );

  return {
    time,
    temperature: 21,
    feelsLike: 21,
    precipitation: 0,
    precipitationProbability: 5,
    windSpeed: 2,
    windGust: 4,
    windDirection: 180,
    iconCode: "1101",
    condition: "sunny",
    ...overrides,
  };
}

test("condition and wind helpers map display values", () => {
  assert.equal(getConditionKey("1101"), "101_day");
  assert.equal(getConditionKey("2101"), "101_night");
  assert.equal(getConditionKey("1402"), "402");
  assert.equal(getConditionEmoji("1101"), "☀️");
  assert.equal(getConditionEmoji("2102"), "🌙");
  assert.equal(getWindDirection(0), "N");
  assert.equal(getWindDirection(225), "SW");
  assert.equal(getWindDirection(359), "N");
});

test("upcoming hourly forecasts start from the current Latvia hour", () => {
  const forecasts = [
    "202607090300",
    "202607090400",
    "202607090500",
    "202607090600",
    "202607090700",
  ].map((laiks) => sampleForecast(laiks));

  const upcoming = getUpcomingHourlyForecasts(
    forecasts,
    new Date("2026-07-09T03:45:00.000Z"),
  );

  assert.deepEqual(
    upcoming.map((forecast) => formatLaiks(forecast.time)),
    ["202607090600", "202607090700"],
  );
});

test("24h chart forecasts cover the next 24 hours from the current hour", () => {
  const forecasts = [
    "202607080800",
    "202607081000",
    "202607081200",
    "202607081400",
    "202607090000",
  ].map((laiks) => sampleForecast(laiks));

  const upcoming = getUpcomingTodayForecasts(
    forecasts,
    new Date("2026-07-08T07:30:00.000Z"),
  );

  assert.deepEqual(
    upcoming.map((forecast) => formatLaiks(forecast.time)),
    ["202607081000", "202607081200", "202607081400", "202607090000"],
  );
});

test("filterForecastsByDayCount limits forecast length", () => {
  const forecasts = ["202607080800", "202607090800", "202607100800"].map((laiks) =>
    sampleForecast(laiks),
  );

  const filtered = filterForecastsByDayCount(forecasts, 2);
  assert.equal(filtered.length, 2);
});

test("chart points and day segments group by Latvia day", () => {
  const forecasts = ["202607092100", "202607100100", "202607100300"].map((laiks) =>
    sampleForecast(laiks),
  );
  const points = toChartPoints(forecasts);
  const segments = getDaySegments(points);

  assert.equal(points.length, 3);
  assert.equal(segments.length, 2);
  assert.deepEqual(
    segments.map((segment) => segment.dayKey),
    ["2026-07-09", "2026-07-10"],
  );
});

test("condition icon indexes include scheduled and changed icons", () => {
  const forecasts = [
    sampleForecast("202607081000", { iconCode: "1101" }),
    sampleForecast("202607081100", { iconCode: "1101" }),
    sampleForecast("202607081200", { iconCode: "1301" }),
    sampleForecast("202607081300", { iconCode: "1301" }),
    sampleForecast("202607081400", { iconCode: "1301" }),
  ];
  const points = toChartPoints(forecasts);
  const indexes = getConditionIconIndexes(points, 1);

  assert.ok(indexes.has(0));
  assert.ok(indexes.has(2));
  assert.ok(indexes.has(4));
});

test("sumPrecipitation totals hourly precipitation", () => {
  const forecasts = [
    sampleForecast("202607081000", { precipitation: 0.3 }),
    sampleForecast("202607081100", { precipitation: 1.2 }),
  ];

  assert.equal(sumPrecipitation(forecasts), 1.5);
});
