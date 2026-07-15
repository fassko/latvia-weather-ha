# Latvia Weather

Home Assistant custom integration for hourly and daily weather forecasts in Latvia, powered by the public [LVĢMC](https://videscentrs.lvgmc.lv/) (Latvian Environment, Geology and Meteorology Centre) API.

Related web app: [latvia-weather.vercel.app](https://latvia-weather.vercel.app)

## Features

- One `weather` entity per configured location
- Current conditions: temperature, feels-like, precipitation, humidity, wind, pressure, cloud cover, UV index
- Hourly and daily forecasts via `weather.get_forecasts`
- Companion sensors: precipitation, snow, UV index, thunder probability, precipitation probability
- Thunder alert binary sensor for the next 24 hours
- 24-hour weather insights on the weather entity (warmest hour, rain/snow periods, windiest hour)
- Stale data fallback when the LVĢMC API is temporarily unavailable (up to 6 hours)
- All LVĢMC forecast locations across Latvia (loaded from the API)
- No API key required
- Data refreshed every 15 minutes

## Installation

### HACS (recommended)

1. Open **HACS** → **Integrations** → **⋮** → **Custom repositories**
2. Add this repository URL and category **Integration**
3. Search for **Latvia Weather**, install, and restart Home Assistant
4. Go to **Settings** → **Devices & Services** → **Add Integration**
5. Search for **Latvia Weather** and select a location

### Manual install

1. Copy the `custom_components/latvia_weather/` folder into your Home Assistant `config/custom_components/` directory
2. Restart Home Assistant
3. Add the integration via **Settings** → **Devices & Services**

## Configuration

During setup, pick a location from the list provided by the LVĢMC API. Each location creates a separate config entry, one LVĢMC device, and these entities:

| Entity | Description |
|--------|-------------|
| `weather.*` | Current conditions and forecasts |
| `sensor.*_precipitation` | Current hour precipitation (mm) |
| `sensor.*_snow` | Current hour snow (cm) |
| `sensor.*_uv_index` | Current UV index (hidden when unavailable) |
| `sensor.*_thunder_probability` | Current thunder probability (%) |
| `sensor.*_precipitation_probability` | Current precipitation probability (%) |
| `binary_sensor.*_thunder_alert` | On when thunder probability ≥ 20% in the next 24h |

To change the location later, open the integration entry and choose **Reconfigure**.

## Weather attributes

The `weather.*` entity exposes extra attributes for automations:

- `precipitation_probability`, `snow`, `thunder_probability`
- `is_stale` — `true` when showing cached data after an API failure
- `fetched_at` — ISO timestamp of the last successful fetch
- Insight attributes: `warmest_time`, `warmest_temperature`, `rain_period_start`, `rain_period_end`, `rain_total_mm`, `windiest_time`, `windiest_gust_ms`, `thunder_alert`, `snow_total_cm`, and more

Example automation trigger when data goes stale:

```yaml
trigger:
  - platform: state
    entity_id: weather.riga
    attribute: is_stale
    to: "true"
```

## Dashboard chart card

A custom Lovelace card is included for the multi-series forecast chart (temperature, precipitation, and wind) with 24h / 3 days / 7 days toggles, matching the [latvia-weather web app](https://latvia-weather.vercel.app) chart.

### Install the card

1. Copy [`custom_cards/latvia-weather-chart-card/dist/latvia-weather-chart-card.js`](custom_cards/latvia-weather-chart-card/dist/latvia-weather-chart-card.js) into your Home Assistant `config/www/` directory
2. Add a Lovelace resource (**Settings** → **Dashboards** → **Resources**):

```yaml
resources:
  - url: /local/latvia-weather-chart-card.js
    type: module
```

3. Add the card to a dashboard:

```yaml
type: custom:latvia-weather-chart-card
entity: weather.riga
default_period: 7
show_rain_insight: true
```

### Card options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `entity` | string | required | Your Latvia Weather `weather.*` entity |
| `default_period` | `1`, `3`, or `7` | `1` | Initial period: 24h, 3 days, or 7 days |
| `show_rain_insight` | boolean | `true` | Show rain hint below title in 24h mode |

The card calls `weather.get_forecasts` (hourly) and refreshes every 15 minutes. Period and legend visibility preferences are saved in browser `localStorage`.

### Build the card from source

```bash
cd custom_cards/latvia-weather-chart-card
npm install
npm run build
npm test
```

## Data attribution

Weather data is provided by the Latvian Environment, Geology and Meteorology Centre (LVĢMC).

## Development

Run unit tests locally:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements_test.txt
pytest
```

## Manual testing

Use these steps to verify the integration in a development Home Assistant instance:

1. Copy `custom_components/latvia_weather/` into your HA `config/custom_components/` directory
2. Restart Home Assistant
3. Add the integration and select a location (default web app location is `P269`)
4. Confirm a `weather.*` entity appears with temperature, humidity, and wind values
5. Confirm sensor and binary_sensor entities appear under the same device
6. Open **Developer Tools** → **Actions**
7. Run `weather.get_forecasts` with:
   - **Target:** your `weather.*` entity
   - **Forecast type:** `hourly`
8. Run `weather.get_forecasts` again with **Forecast type:** `daily`
9. Check **Settings** → **System** → **Logs** for errors after 15+ minutes to confirm polling works

## Requirements

- Home Assistant 2024.1.0 or newer

## License

MIT
