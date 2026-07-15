export type ForecastPeriod = 1 | 3 | 7;

export type ChartSeriesKey = "temperature" | "precipitation" | "windSpeed";

export interface LatviaWeatherChartCardConfig {
  type: "custom:latvia-weather-chart-card";
  entity: string;
  default_period?: ForecastPeriod;
  show_rain_insight?: boolean;
}

export interface HourlyForecast {
  time: Date;
  temperature: number;
  feelsLike: number;
  precipitation: number;
  precipitationProbability: number;
  windSpeed: number;
  windGust: number;
  windDirection: number;
  iconCode: string;
  condition: string;
}

export interface HassServiceResponse {
  [entityId: string]: {
    forecast?: HassForecastEntry[];
  };
}

export interface ServiceCallResponse<T = unknown> {
  context?: Record<string, unknown>;
  response?: T;
}

export interface HassForecastEntry {
  datetime: string;
  condition?: string;
  icon_code?: string;
  temperature?: number;
  native_temperature?: number;
  precipitation?: number;
  native_precipitation?: number;
  precipitation_probability?: number;
  wind_speed?: number;
  native_wind_speed?: number;
  wind_gust_speed?: number;
  native_wind_gust_speed?: number;
  wind_bearing?: number;
}

export interface HomeAssistant {
  states: Record<string, { state: string; attributes: Record<string, unknown> }>;
  themes: { darkMode: boolean };
  callService(
    domain: string,
    service: string,
    serviceData?: Record<string, unknown>,
    target?: Record<string, unknown>,
    notifyOnError?: boolean,
    returnResponse?: boolean,
  ): Promise<ServiceCallResponse>;
}

export interface LovelaceCard {
  hass?: HomeAssistant;
  setConfig(config: LatviaWeatherChartCardConfig): void;
  getCardSize(): number;
}
