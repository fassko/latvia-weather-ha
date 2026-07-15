"""JavaScript module registration for the Latvia Weather chart card."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

from homeassistant.components.frontend import add_extra_js_url
from homeassistant.components.http import StaticPathConfig
from homeassistant.core import HomeAssistant
from homeassistant.helpers.event import async_call_later

from ..const import DOMAIN, JSMODULES, URL_BASE

_LOGGER = logging.getLogger(__name__)

_CARD_REGISTERED_KEY = f"{DOMAIN}_card_registered"


class JSModuleRegistration:
    """Register the Latvia Weather chart card with Home Assistant."""

    def __init__(self, hass: HomeAssistant) -> None:
        """Initialize the registrar."""
        self.hass = hass
        self.lovelace = self.hass.data.get("lovelace")

    async def async_register(self) -> None:
        """Register frontend resources."""
        if self.hass.data.get(_CARD_REGISTERED_KEY):
            return

        frontend_dir = Path(__file__).parent
        if not any((frontend_dir / module["filename"]).is_file() for module in JSMODULES):
            _LOGGER.warning(
                "Latvia Weather chart card files not found in %s — skipping registration",
                frontend_dir,
            )
            return

        await self._async_register_path(frontend_dir)

        for module in JSMODULES:
            add_extra_js_url(self.hass, self._versioned_url(module))

        if self.lovelace and self.lovelace.mode == "storage":
            await self._async_wait_for_lovelace_resources()

        self.hass.data[_CARD_REGISTERED_KEY] = True

    async def _async_register_path(self, frontend_dir: Path) -> None:
        """Register the static HTTP path for bundled card assets."""
        try:
            await self.hass.http.async_register_static_paths(
                [StaticPathConfig(URL_BASE, frontend_dir, False)]
            )
            _LOGGER.debug("Registered frontend path: %s -> %s", URL_BASE, frontend_dir)
        except RuntimeError:
            _LOGGER.debug("Frontend path already registered: %s", URL_BASE)

    async def _async_wait_for_lovelace_resources(self) -> None:
        """Wait for Lovelace resources to load before registering modules."""

        async def _check_loaded(_now: Any) -> None:
            if self.lovelace.resources.loaded:
                await self._async_register_modules()
            else:
                _LOGGER.debug("Lovelace resources not loaded, retrying in 5s")
                async_call_later(self.hass, 5, _check_loaded)

        await _check_loaded(0)

    async def _async_register_modules(self) -> None:
        """Register or update JavaScript modules in Lovelace resources."""
        existing_resources = [
            resource
            for resource in self.lovelace.resources.async_items()
            if resource["url"].startswith(URL_BASE)
        ]

        for module in JSMODULES:
            url = self._module_url(module)
            versioned_url = self._versioned_url(module)
            registered = False

            for resource in existing_resources:
                if self._get_path(resource["url"]) == url:
                    registered = True
                    if self._get_version(resource["url"]) != module["version"]:
                        _LOGGER.info(
                            "Updating %s to version %s",
                            module["name"],
                            module["version"],
                        )
                        await self.lovelace.resources.async_update_item(
                            resource["id"],
                            {"res_type": "module", "url": versioned_url},
                        )
                    break

            if not registered:
                _LOGGER.info(
                    "Registering %s version %s",
                    module["name"],
                    module["version"],
                )
                await self.lovelace.resources.async_create_item(
                    {"res_type": "module", "url": versioned_url}
                )

    @staticmethod
    def _module_url(module: dict[str, str]) -> str:
        """Return the unversioned module URL."""
        return f"{URL_BASE}/{module['filename']}"

    @staticmethod
    def _versioned_url(module: dict[str, str]) -> str:
        """Return the cache-busted module URL."""
        return f"{URL_BASE}/{module['filename']}?v={module['version']}"

    @staticmethod
    def _get_path(url: str) -> str:
        """Extract the path without query parameters."""
        return url.split("?")[0]

    @staticmethod
    def _get_version(url: str) -> str:
        """Extract the version query parameter from a resource URL."""
        parts = url.split("?")
        if len(parts) > 1 and parts[1].startswith("v="):
            return parts[1].replace("v=", "")
        return "0"
