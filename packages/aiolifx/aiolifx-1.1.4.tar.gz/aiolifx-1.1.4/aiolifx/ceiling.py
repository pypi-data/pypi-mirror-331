"""Ceiling-specific compound operations."""

from __future__ import annotations

import asyncio

from aiolifx.aiolifx import DEFAULT_TIMEOUT, Light


class CeilingException(Exception):
    """Ceiling specific exception."""


class Ceiling:
    """LIFX Ceiling."""

    def __init__(self, light: Light) -> None:
        """Initialize the Ceiling extras."""
        self._light: Light = light
        self._populated: bool = False

    async def _wait_for_replies(self, timeout: float = DEFAULT_TIMEOUT) -> None:
        """Wait for device replies."""

        async def empty_queue():
            """Sleep until queue is empty."""
            while len(self._light.message) > 0:
                await asyncio.sleep(0)

        await asyncio.wait_for(empty_queue(), timeout=timeout)

    async def async_get64(self) -> None:
        """Populate the required metadata."""

        if self._populated is False:
            if self._light.product is None:
                self._light.get_version()
            if self._light.host_firmware_version is None:
                self._light.get_hostfirmware()
            if self._light.color is None:
                self._light.get_color()
            await self._wait_for_replies()

            # Needs product and firmware
            if len(self._light.tile_devices) == 0:
                self._light.get_device_chain()
            await self._wait_for_replies()

            if (
                self._light.product is not None
                and self._light.host_firmware_version is not None
                and self._light.color is not None
                and self._light.tile_devices is not None
            ):
                self._populated = True
        else:
            await self._wait_for_replies()

        # Needs tile_width
        if len(self._light.tile_devices) > 0:
            self._light.get64()
        await self._wait_for_replies()

    @property
    def uplight_color(self) -> tuple[int, int, int, int]:
        """Return the HSBK for the uplight."""
        if not self._populated:
            raise CeilingException(
                "Call async_get64() before trying to retrieve property values."
            )

        hue, saturation, brightness, kelvin = self._light.chain[0][63]
        return hue, saturation, brightness, kelvin

    @property
    def uplight_on(self) -> bool:
        """Return true if the device is on and the uplight brightness > 0."""
        if not self._populated:
            raise CeilingException(
                "Call async_get64() before trying to retrieve property values."
            )

        return bool(self._light.power_level > 0 and self.uplight_color[2] > 0)

    @property
    def downlight_on(self) -> bool:
        """Return true if the device is on and at least one of the downlight zones brightness > 0."""
        if not self._populated:
            raise CeilingException(
                "Call async_get64() before trying to retrieve property values."
            )

        brightness = max(
            brightness for _, _, brightness, _ in self._light.chain[0][:63]
        )
        return bool(self._light.power_level > 0 and brightness > 0)

    def turn_uplight_on(
        self, color: tuple[int, int, int, int], duration: int = 0
    ) -> None:
        """Turn the uplight on using color provided."""
        if self._light.power_level > 0:
            self._light.set64(
                tile_index=0, x=7, y=7, width=8, duration=duration, colors=[color]
            )
        else:
            zones = [(h, s, 0, k) for h, s, _, k in self._light.chain[0][:63]]
            zones.append(color)
            self._light.set64(tile_index=0, x=0, y=0, width=8, duration=0, colors=zones)
            self._light.set_power(value=True, duration=duration)

    async def async_turn_uplight_on(
        self,
        color: tuple[int, int, int, int],
        duration: int = 0,
        timeout: float = DEFAULT_TIMEOUT,
    ) -> None:
        """Asynchronously turn the uplight on using the color and duration provided."""
        self.turn_uplight_on(color, duration)
        await self.async_get64()

    def turn_uplight_off(self, duration: int = 0) -> None:
        """Turn uplight off.

        If the downlight is on, lower brightness to zero.
        If the downlight is off, lower brightness to zero then turn the device off.
        """
        h, s, _, k = self.uplight_color
        self._light.set64(
            tile_index=0, x=7, y=7, width=8, duration=duration, colors=[(h, s, 0, k)]
        )
        if self.downlight_on is False:
            self._light.set_power(value=False, duration=duration)

    async def async_turn_uplight_off(
        self, duration: int = 0, timeout: float = DEFAULT_TIMEOUT
    ) -> None:
        """Asynchronously turn the uplight off."""
        self.turn_uplight_off(duration)
        await self.async_get64()

    def turn_downlight_on(
        self, color: tuple[int, int, int, int], duration: int = 0
    ) -> None:
        """Turn downlight on using color provided."""
        zones = [color for _ in range(63)]
        if self._light.power_level > 0:
            zones.append(self.uplight_color)
            self._light.set64(
                tile_index=0, x=0, y=0, width=8, duration=duration, colors=zones
            )
        else:
            uplight = self.uplight_color
            zones.append((uplight[0], uplight[1], 0, uplight[2]))
            self._light.set64(tile_index=0, x=0, y=0, width=8, duration=0, colors=zones)
            self._light.set_power(value=True, duration=duration)

    async def async_turn_downlight_on(
        self,
        color: tuple[int, int, int, int],
        duration: int = 0,
        timeout: float = DEFAULT_TIMEOUT,
    ) -> None:
        """Asynchronously turn the downlight on."""
        self.turn_downlight_on(color, duration=duration)
        await self.async_get64()

    def turn_downlight_off(self, duration: int = 0) -> None:
        """Turn downlight off.

        If the uplight is on, lower brightness to zero.
        If the uplight is off, turn the device off.
        """
        zones = [(h, s, 0, k) for h, s, _, k in self._light.chain[0][:63]]
        zones.append(self.uplight_color)
        self._light.set64(
            tile_index=0, x=0, y=0, width=8, duration=duration, colors=zones
        )
        if self.uplight_on is False:
            self._light.set_power(value=False, duration=duration)

    async def async_turn_downlight_off(
        self, duration: int = 0, timeout: float = DEFAULT_TIMEOUT
    ) -> None:
        """Asynchronously turn the downlight off."""
        self.turn_downlight_off(duration)
        await self.async_get64()
