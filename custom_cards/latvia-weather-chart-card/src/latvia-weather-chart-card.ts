import { css, html, LitElement, nothing } from "lit";
import { property, state } from "lit/decorators.js";
import {
  getForecastsForPeriod,
  getTodayRainPoint,
  sumPrecipitation,
  toChartPoints,
} from "./chart/chart-data";
import { ChartRenderer, type ChartSeriesKey } from "./chart/render-chart";
import { getChartTheme } from "./chart/theme";
import { formatLatviaTime } from "./chart/timezone";
import { fetchHourlyForecasts, FORECAST_REFRESH_MS } from "./forecast-service";
import type {
  ForecastPeriod,
  HomeAssistant,
  HourlyForecast,
  LatviaWeatherChartCardConfig,
  LovelaceCard,
} from "./types";

const CHART_PREFS_STORAGE_KEY = "latvia-weather-chart-prefs";

interface ChartPreferences {
  period: ForecastPeriod;
  hiddenSeries: ChartSeriesKey[];
}

function isForecastPeriod(value: unknown): value is ForecastPeriod {
  return value === 1 || value === 3 || value === 7;
}

function isChartSeriesKey(value: unknown): value is ChartSeriesKey {
  return value === "temperature" || value === "precipitation" || value === "windSpeed";
}

function parseChartPreferences(value: string | null): ChartPreferences | null {
  if (!value) return null;

  try {
    const parsed = JSON.parse(value) as Partial<ChartPreferences>;
    return {
      period: isForecastPeriod(parsed.period) ? parsed.period : 1,
      hiddenSeries: Array.isArray(parsed.hiddenSeries)
        ? parsed.hiddenSeries.filter(isChartSeriesKey)
        : [],
    };
  } catch {
    return null;
  }
}

function getInitialChartPreferences(defaultPeriod: ForecastPeriod): ChartPreferences {
  if (typeof window === "undefined") {
    return { period: defaultPeriod, hiddenSeries: [] };
  }

  const stored = parseChartPreferences(localStorage.getItem(CHART_PREFS_STORAGE_KEY));
  if (!stored) return { period: defaultPeriod, hiddenSeries: [] };

  return {
    period: stored.period,
    hiddenSeries: stored.hiddenSeries,
  };
}

export class LatviaWeatherChartCard extends LitElement implements LovelaceCard {
  @property({ attribute: false }) public hass?: HomeAssistant;

  @state() private config!: LatviaWeatherChartCardConfig;
  @state() private forecasts: HourlyForecast[] = [];
  @state() private period: ForecastPeriod = 1;
  @state() private hiddenSeries = new Set<ChartSeriesKey>();
  @state() private loading = true;
  @state() private error: string | null = null;

  private chartRenderer: ChartRenderer | null = null;
  private refreshTimer: number | null = null;
  private unsubscribeEntity: (() => void) | null = null;
  private renderGeneration = 0;

  static getStubConfig(hass: HomeAssistant): LatviaWeatherChartCardConfig {
    const weatherEntity = Object.keys(hass.states).find((entityId) =>
      entityId.startsWith("weather."),
    );

    return {
      type: "custom:latvia-weather-chart-card",
      entity: weatherEntity ?? "weather.riga",
    };
  }

  public setConfig(config: LatviaWeatherChartCardConfig): void {
    if (!config.entity) {
      throw new Error("Entity must be specified");
    }

    const defaultPeriod = isForecastPeriod(config.default_period)
      ? config.default_period
      : 1;
    const prefs = getInitialChartPreferences(defaultPeriod);

    this.config = {
      show_rain_insight: true,
      ...config,
    };
    this.period = prefs.period;
    this.hiddenSeries = new Set(prefs.hiddenSeries);
  }

  public getCardSize(): number {
    return this.period > 1 ? 5 : 4;
  }

  connectedCallback(): void {
    super.connectedCallback();
    void this.loadForecasts();
    this.refreshTimer = window.setInterval(() => {
      void this.loadForecasts();
    }, FORECAST_REFRESH_MS);
  }

  disconnectedCallback(): void {
    super.disconnectedCallback();
    if (this.refreshTimer != null) {
      window.clearInterval(this.refreshTimer);
      this.refreshTimer = null;
    }
    this.unsubscribeEntity?.();
    this.unsubscribeEntity = null;
    void this.chartRenderer?.destroy();
    this.chartRenderer = null;
  }

  protected updated(changed: Map<string, unknown>): void {
    if (changed.has("hass") && this.hass) {
      void this.loadForecasts();
    }

    if (
      changed.has("forecasts") ||
      changed.has("period") ||
      changed.has("hiddenSeries") ||
      changed.has("hass")
    ) {
      void this.scheduleRenderChart();
    }
  }

  private get isDark(): boolean {
    return this.hass?.themes.darkMode ?? false;
  }

  private get theme() {
    return getChartTheme(this.isDark);
  }

  private persistPreferences(): void {
    localStorage.setItem(
      CHART_PREFS_STORAGE_KEY,
      JSON.stringify({
        period: this.period,
        hiddenSeries: Array.from(this.hiddenSeries),
      }),
    );
  }

  private async loadForecasts(): Promise<void> {
    if (!this.hass || !this.config?.entity) return;

    try {
      this.error = null;
      const forecasts = await fetchHourlyForecasts(this.hass, this.config.entity);
      this.forecasts = forecasts;
      this.loading = false;
    } catch (err) {
      this.error = err instanceof Error ? err.message : "Failed to load forecast";
      this.loading = false;
    }
  }

  private async scheduleRenderChart(): Promise<void> {
    const generation = ++this.renderGeneration;
    await this.updateComplete;
    if (generation !== this.renderGeneration) return;

    const container = this.renderRoot.querySelector<HTMLElement>("#chart-container");
    if (!container || this.forecasts.length === 0) return;

    const periodForecasts = getForecastsForPeriod(this.forecasts, this.period);
    const data = toChartPoints(periodForecasts);
    if (data.length === 0) return;

    if (!this.chartRenderer) {
      this.chartRenderer = new ChartRenderer();
    }

    try {
      await this.chartRenderer.render({
        container,
        data,
        period: this.period,
        theme: this.theme,
        hiddenSeries: this.hiddenSeries,
        onLegendToggle: (series) => this.toggleSeries(series),
      });
      this.error = null;
    } catch (err) {
      console.error("Latvia Weather chart render failed", err);
      this.error = err instanceof Error ? err.message : "Failed to render chart";
    }
  }

  private setPeriod(period: ForecastPeriod): void {
    this.period = period;
    this.persistPreferences();
  }

  private toggleSeries(series: ChartSeriesKey): void {
    const next = new Set(this.hiddenSeries);
    if (next.has(series)) {
      next.delete(series);
    } else {
      next.add(series);
    }
    this.hiddenSeries = next;
    this.persistPreferences();
  }

  private getRainInsight(data: ReturnType<typeof toChartPoints>): string | null {
    if (this.config.show_rain_insight === false || this.period !== 1) return null;

    const rainPoint = getTodayRainPoint(data);
    if (!rainPoint) return "No rain expected in the next 24 hours";

    if (rainPoint.precipitation > 0) {
      const time = formatLatviaTime(new Date(rainPoint.time), "time");
      return `Rain mostly around ${time}: ${rainPoint.precipitation.toFixed(1)} mm, ${rainPoint.precipitationProbability}% chance`;
    }

    const time = formatLatviaTime(new Date(rainPoint.time), "time");
    return `Highest rain chance around ${time}: ${rainPoint.precipitationProbability}%`;
  }

  protected render() {
    const theme = this.theme;
    const periodForecasts = getForecastsForPeriod(this.forecasts, this.period);
    const data = toChartPoints(periodForecasts);
    const totalPrecip = sumPrecipitation(periodForecasts);
    const rainInsight = this.getRainInsight(data);

    const periodOptions: { value: ForecastPeriod; label: string }[] = [
      { value: 1, label: "24h" },
      { value: 3, label: "3 days" },
      { value: 7, label: "7 days" },
    ];

    return html`
      <ha-card>
        <div class="card-shell">
          <div class="header">
            <div class="titles">
              <h2>Temperature & precipitation</h2>
              ${data.length > 0
                ? html`<p class="subtitle">${totalPrecip.toFixed(1)} mm total</p>`
                : nothing}
              ${rainInsight
                ? html`<p class="insight">${rainInsight}</p>`
                : nothing}
            </div>
            <div class="period-toggle" role="group" aria-label="Forecast period">
              ${periodOptions.map(
                (option) => html`
                  <button
                    type="button"
                    aria-pressed=${this.period === option.value}
                    class=${this.period === option.value ? "active" : ""}
                    @click=${() => this.setPeriod(option.value)}
                  >
                    ${option.label}
                  </button>
                `,
              )}
            </div>
          </div>

          ${this.loading
            ? html`<p class="status">Loading forecast...</p>`
            : nothing}
          ${this.error ? html`<p class="error">${this.error}</p>` : nothing}
          ${!this.loading && data.length === 0
            ? html`<p class="status">No forecast data available.</p>`
            : nothing}

          <div id="chart-container" class="chart-container"></div>
        </div>
      </ha-card>
    `;
  }

  static styles = css`
    :host {
      display: block;
    }

    ha-card {
      overflow: hidden;
    }

    .card-shell {
      padding: 16px;
    }

    .header {
      display: flex;
      flex-wrap: wrap;
      align-items: flex-start;
      justify-content: space-between;
      gap: 12px;
      margin-bottom: 12px;
    }

    .titles h2 {
      margin: 0;
      font-size: 1.1rem;
      font-weight: 700;
      color: var(--primary-text-color);
    }

    .subtitle {
      margin: 4px 0 0;
      font-size: 0.9rem;
      color: var(--secondary-text-color);
    }

    .insight {
      margin: 6px 0 0;
      font-size: 0.85rem;
      color: var(--secondary-text-color);
    }

    .period-toggle {
      display: grid;
      grid-template-columns: repeat(3, minmax(0, 1fr));
      gap: 2px;
      padding: 2px;
      border: 1px solid var(--divider-color, #cbd5e1);
      border-radius: 8px;
      min-width: 220px;
    }

    .period-toggle button {
      border: 0;
      border-radius: 6px;
      padding: 6px 12px;
      background: transparent;
      color: var(--secondary-text-color);
      font-size: 0.875rem;
      font-weight: 500;
      cursor: pointer;
    }

    .period-toggle button.active {
      background: #0ea5e9;
      color: #ffffff;
    }

    .period-toggle button:hover:not(.active) {
      background: var(--secondary-background-color, #f1f5f9);
    }

    .chart-container {
      min-height: 280px;
      overflow-x: auto;
    }

    .status,
    .error {
      margin: 0 0 8px;
      font-size: 0.9rem;
      color: var(--secondary-text-color);
    }

    .error {
      color: var(--error-color, #dc2626);
    }
  `;
}

declare global {
  interface HTMLElementTagNameMap {
    "latvia-weather-chart-card": LatviaWeatherChartCard;
  }

  interface Window {
    customCards?: Array<{
      type: string;
      name: string;
      description?: string;
      preview?: boolean;
    }>;
  }
}

const CARD_ELEMENT = "latvia-weather-chart-card";

if (!customElements.get(CARD_ELEMENT)) {
  customElements.define(CARD_ELEMENT, LatviaWeatherChartCard);
}

if (!window.customCards?.some((card) => card.type === CARD_ELEMENT)) {
  window.customCards = window.customCards ?? [];
  window.customCards.push({
    type: CARD_ELEMENT,
    name: "Latvia Weather Chart",
    description: "Temperature, precipitation, and wind forecast chart for Latvia Weather",
    preview: false,
  });
}

console.info(
  "%c LATVIA-WEATHER-CHART-CARD %c v0.3.0 ",
  "color: white; background: #0ea5e9; font-weight: bold;",
  "color: #0ea5e9; background: white; font-weight: bold;",
);
