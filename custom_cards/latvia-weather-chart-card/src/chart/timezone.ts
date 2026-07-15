export const LATVIA_TIME_ZONE = "Europe/Riga";

function zonedTimeToUtc(
  year: number,
  month: number,
  day: number,
  hour: number,
  minute: number,
  timeZone = LATVIA_TIME_ZONE,
): Date {
  const utcDate = new Date(Date.UTC(year, month - 1, day, hour, minute));
  const formatter = new Intl.DateTimeFormat("en-US", {
    timeZone,
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
    hourCycle: "h23",
  });

  const parts = formatter.formatToParts(utcDate);
  const values = Object.fromEntries(
    parts
      .filter((part) => part.type !== "literal")
      .map((part) => [part.type, part.value]),
  );

  const asUtc = Date.UTC(
    Number(values.year),
    Number(values.month) - 1,
    Number(values.day),
    Number(values.hour),
    Number(values.minute),
  );

  return new Date(utcDate.getTime() + (utcDate.getTime() - asUtc));
}

export function parseIsoAsLatviaWall(iso: string): Date {
  return new Date(iso);
}

export function getLatviaWallClock(date: Date): Date {
  const formatter = new Intl.DateTimeFormat("en-CA", {
    timeZone: LATVIA_TIME_ZONE,
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
    hour12: false,
  });

  const parts = Object.fromEntries(
    formatter
      .formatToParts(date)
      .filter((part) => part.type !== "literal")
      .map((part) => [part.type, part.value]),
  );

  const hour = parts.hour === "24" ? "00" : parts.hour;

  return new Date(
    Number(parts.year),
    Number(parts.month) - 1,
    Number(parts.day),
    Number(hour),
    Number(parts.minute),
  );
}

export function getLatviaStartOfHour(date: Date): Date {
  const wall = getLatviaWallClock(date);
  wall.setMinutes(0, 0, 0);
  return wall;
}

export function getLatviaDayKey(date: Date): string {
  const wall = getLatviaWallClock(date);
  const year = wall.getFullYear();
  const month = String(wall.getMonth() + 1).padStart(2, "0");
  const day = String(wall.getDate()).padStart(2, "0");
  return `${year}-${month}-${day}`;
}

export function formatLatviaTime(date: Date, pattern: "time" | "chartDay" | "chartTooltip"): string {
  const wall = getLatviaWallClock(date);

  if (pattern === "time") {
    const hours = String(wall.getHours()).padStart(2, "0");
    const minutes = String(wall.getMinutes()).padStart(2, "0");
    return `${hours}:${minutes}`;
  }

  if (pattern === "chartDay") {
    const weekday = new Intl.DateTimeFormat("en-US", {
      timeZone: LATVIA_TIME_ZONE,
      weekday: "short",
    }).format(date);
    const day = wall.getDate();
    return `${weekday} ${day}`;
  }

  const weekday = new Intl.DateTimeFormat("en-US", {
    timeZone: LATVIA_TIME_ZONE,
    weekday: "short",
  }).format(date);
  const month = new Intl.DateTimeFormat("en-US", {
    timeZone: LATVIA_TIME_ZONE,
    month: "short",
  }).format(date);
  const day = wall.getDate();
  const hours = String(wall.getHours()).padStart(2, "0");
  const minutes = String(wall.getMinutes()).padStart(2, "0");
  return `${weekday}, ${month} ${day} - ${hours}:${minutes}`;
}

export function addHours(date: Date, hours: number): Date {
  return new Date(date.getTime() + hours * 60 * 60 * 1000);
}

export function addDays(date: Date, days: number): Date {
  return new Date(date.getTime() + days * 24 * 60 * 60 * 1000);
}

export function isWeekendDay(dayKey: string): boolean {
  const date = new Date(`${dayKey}T12:00:00`);
  const day = date.getDay();
  return day === 0 || day === 6;
}

export function formatLaiks(date: Date): string {
  const wall = getLatviaWallClock(date);
  const year = wall.getFullYear();
  const month = String(wall.getMonth() + 1).padStart(2, "0");
  const day = String(wall.getDate()).padStart(2, "0");
  const hour = String(wall.getHours()).padStart(2, "0");
  const minute = String(wall.getMinutes()).padStart(2, "0");
  return `${year}${month}${day}${hour}${minute}`;
}

export { zonedTimeToUtc };
