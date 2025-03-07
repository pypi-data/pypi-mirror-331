#!/usr/bin/env python3
"""
Script to log all API request bodies from the utec_py library.
This will show the raw request bodies sent to the U-Tec API.
"""

import asyncio
import json
import logging
import os

import aiohttp

from utec_py.api import UHomeApi
from utec_py.auth import AbstractAuth
from utec_py.devices.device_const import DeviceCapability, DeviceCommand


# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("utec-api-logger")


class SimpleAuth(AbstractAuth):
    """Simple authentication implementation for testing."""

    def __init__(self, websession: aiohttp.ClientSession, access_token: str):
        super().__init__(websession)
        self._access_token = access_token

    async def async_get_access_token(self) -> str:
        """Return the access token."""
        return self._access_token

    async def close(self):
        """Close the session."""
        pass

    async def async_make_auth_request(self, method, host: str, **kwargs):
        """Override to log request bodies."""
        if "json" in kwargs:
            logger.info(f"Request Body: {json.dumps(kwargs['json'], indent=2)}")

        response = await super().async_make_auth_request(method, host, **kwargs)

        # Log response if it's JSON
        try:
            if response.status in (200, 201, 202):
                response_json = await response.json()
                logger.info(f"Response: {json.dumps(response_json, indent=2)}")
        except:
            pass

        return response


async def main():
    """Main function to demonstrate API requests."""
    # Get access token from environment or prompt user
    access_token = os.environ.get("UTEC_ACCESS_TOKEN")
    if not access_token:
        access_token = input("Enter your U-Tec API access token: ")

    # Optional device ID for testing specific device commands
    device_id = os.environ.get("UTEC_DEVICE_ID")
    if not device_id:
        device_id = input("Enter a device ID (optional, press Enter to skip): ")

    async with aiohttp.ClientSession() as session:
        # Initialize auth and API
        auth = SimpleAuth(session, access_token)
        api = UHomeApi(auth)

        try:
            # Test 1: Device Discovery
            logger.info("=== Testing Device Discovery ===")
            await api.discover_devices()

            if device_id:
                # Test 2: Query Device State
                logger.info(f"\n=== Testing Query Device State for {device_id} ===")
                await api.query_device(device_id)

                # Test 3: Example Commands (if device ID is provided)
                # These may fail depending on device type, but will show request format

                # Example: Switch command
                logger.info("\n=== Testing Switch Command ===")
                try:
                    await api.send_command(
                        device_id,
                        DeviceCapability.SWITCH,
                        "switch",
                        {"value": 1}  # ON
                    )
                except Exception as e:
                    logger.warning(f"Switch command failed: {e}")

                # Example: Lock command
                logger.info("\n=== Testing Lock Command ===")
                try:
                    await api.send_command(
                        device_id,
                        DeviceCapability.LOCK,
                        "lock",
                        None
                    )
                except Exception as e:
                    logger.warning(f"Lock command failed: {e}")

                # Example: Brightness command (for lights)
                logger.info("\n=== Testing Brightness Command ===")
                try:
                    await api.send_command(
                        device_id,
                        DeviceCapability.BRIGHTNESS,
                        "level",
                        {"value": 50}
                    )
                except Exception as e:
                    logger.warning(f"Brightness command failed: {e}")

        finally:
            # Close the API client
            await api.close()


if __name__ == "__main__":
    asyncio.run(main())