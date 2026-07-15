import type {
  HassForecastEntry,
  HassServiceResponse,
  HomeAssistant,
  HourlyForecast,
} from "./types";

function readNumber(value: unknown, fallback = 0): number {
  const num = typeof value === "number" ? value : Number(value);
  return Number.isFinite(num) ? num : fallback;
}

function normalizeForecastEntry(entry: HassForecastEntry): HourlyForecast {
  const iconCode = entry.icon_code ?? "";
  return {
    time: new Date(entry.datetime),
    temperature: readNumber(entry.temperature ?? entry.native_temperature),
    feelsLike: readNumber(entry.temperature ?? entry.native_temperature),
    precipitation: readNumber(entry.precipitation ?? entry.native_precipitation),
    precipitationProbability: readNumber(entry.precipitation_probability),
    windSpeed: readNumber(entry.wind_speed ?? entry.native_wind_speed),
    windGust: readNumber(entry.wind_gust_speed ?? entry.native_wind_gust_speed),
    windDirection: readNumber(entry.wind_bearing),
    iconCode,
    condition: entry.condition ?? "",
  };
}

export async function fetchHourlyForecasts(
  hass: HomeAssistant,
  entityId: string,
): Promise<HourlyForecast[]> {
  const result = await hass.callService(
    "weather",
    "get_forecasts",
    { type: "hourly" },
    { entity_id: entityId },
    true,
    true,
  );

  const response = result.response as HassServiceResponse | undefined;
  if (!response) return [];

  const entityForecast = response[entityId]?.forecast;
  if (!entityForecast || entityForecast.length === 0) return [];

  return entityForecast.map(normalizeForecastEntry);
}

export const FORECAST_REFRESH_MS = 15 * 60 * 1000;
