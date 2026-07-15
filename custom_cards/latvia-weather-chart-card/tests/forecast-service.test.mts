import assert from "node:assert/strict";
import { describe, it } from "node:test";

import { fetchHourlyForecasts } from "../src/forecast-service.ts";
import type { HomeAssistant } from "../src/types.ts";

describe("fetchHourlyForecasts", () => {
  it("requests forecast data with return_response enabled", async () => {
    const calls: unknown[] = [];
    const hass = {
      callService: async (
        domain: string,
        service: string,
        serviceData?: Record<string, unknown>,
        target?: Record<string, unknown>,
        notifyOnError?: boolean,
        returnResponse?: boolean,
      ) => {
        calls.push([domain, service, serviceData, target, notifyOnError, returnResponse]);
        return {
          response: {
            "weather.garupe": {
              forecast: [
                {
                  datetime: "2026-07-15T12:00:00+03:00",
                  temperature: 21,
                  precipitation: 0.2,
                  wind_speed: 4.5,
                },
              ],
            },
          },
        };
      },
    } as HomeAssistant;

    const forecasts = await fetchHourlyForecasts(hass, "weather.garupe");

    assert.deepEqual(calls, [
      [
        "weather",
        "get_forecasts",
        { type: "hourly" },
        { entity_id: "weather.garupe" },
        true,
        true,
      ],
    ]);
    assert.equal(forecasts.length, 1);
    assert.equal(forecasts[0]?.temperature, 21);
    assert.equal(forecasts[0]?.precipitation, 0.2);
    assert.equal(forecasts[0]?.windSpeed, 4.5);
  });

  it("returns an empty list when the service response is missing", async () => {
    const hass = {
      callService: async () => ({ response: undefined }),
    } as HomeAssistant;

    const forecasts = await fetchHourlyForecasts(hass, "weather.garupe");

    assert.deepEqual(forecasts, []);
  });
});
