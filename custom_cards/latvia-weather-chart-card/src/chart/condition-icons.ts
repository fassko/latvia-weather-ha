const CONDITION_LABELS: Record<string, string> = {
  "101_day": "Sunny",
  "101_night": "Clear night",
  "102": "Partly cloudy",
  "103": "Mostly cloudy",
  "104": "Cloudy",
  "201": "Fog",
  "202": "Fog",
  "203": "Fog",
  "204": "Overcast",
  "301": "Rain",
  "302": "Rain",
  "303": "Heavy rain",
  "304": "Thunderstorm",
  "305": "Thunderstorm with rain",
  "306": "Hail",
  "401": "Snow",
  "402": "Snow",
  "403": "Heavy snow",
  "404": "Sleet",
  "501": "Rain",
  "502": "Rain",
  "503": "Sleet",
  "504": "Sleet",
  "505": "Rain",
  "506": "Rain",
  fallback_day: "Variable",
  fallback_night: "Variable",
};

export function getConditionKey(iconCode: string): string {
  const code = iconCode.slice(1);
  const isNight = iconCode.startsWith("2");

  const conditions: Record<string, string> = {
    "101": isNight ? "101_night" : "101_day",
    "102": "102",
    "103": "103",
    "104": "104",
    "201": "201",
    "202": "202",
    "203": "203",
    "204": "204",
    "301": "301",
    "302": "302",
    "303": "303",
    "304": "304",
    "305": "305",
    "306": "306",
    "401": "401",
    "402": "402",
    "403": "403",
    "404": "404",
    "501": "501",
    "502": "502",
    "503": "503",
    "504": "504",
    "505": "505",
    "506": "506",
  };

  return conditions[code] ?? (isNight ? "fallback_night" : "fallback_day");
}

export function getConditionLabel(iconCode: string): string {
  return CONDITION_LABELS[getConditionKey(iconCode)] ?? "Variable";
}

export function getConditionEmoji(iconCode: string): string {
  const code = iconCode.slice(1);
  const isNight = iconCode.startsWith("2");

  if (code.startsWith("50") || code.startsWith("30")) return "🌧️";
  if (code.startsWith("40")) return "❄️";
  if (code === "104" || code === "204") return "☁️";
  if (code === "103" || code === "203") return "🌥️";
  if (code === "102" || code === "202") return isNight ? "🌙" : "⛅";
  if (code === "101" || code === "201") return isNight ? "🌙" : "☀️";
  if (code.startsWith("30")) return "⛈️";

  return isNight ? "🌙" : "🌤️";
}
