"""StarLine device."""

from typing import Optional, Dict, Any, List
from .const import (
    BATTERY_LEVEL_MIN,
    BATTERY_LEVEL_MAX,
    GSM_LEVEL_MIN,
    GSM_LEVEL_MAX,
    DEVICE_FUNCTION_POSITION,
    DEVICE_FUNCTION_STATE,
)


class StarlineDevice:
    """StarLine device class."""

    def __init__(self):
        """Constructor."""
        self._alias: Optional[str] = None
        self._typename: Optional[str] = None
        self._device_id: Optional[str] = None
        self._imei: Optional[str] = None
        self._fw_version: Optional[str] = None
        self._status: Optional[int] = None
        self._phone: Optional[str] = None
        self._gsm_lvl: Optional[int] = None
        self._balance: Dict[str, Dict[str, Any]] = {}
        self._battery: Optional[int] = None
        self._ctemp: Optional[int] = None
        self._etemp: Optional[int] = None
        self._fuel: Dict[str, Any] = {}
        self._mileage: Dict[str, Any] = {}
        self._car_state: Dict[str, bool] = {}
        self._car_alr_state: Dict[str, bool] = {}

        self._ts_activity: Optional[float] = None
        self._functions: List[str] = []
        self._position: Dict[str, float] = {}
        self._errors: Dict[str, Any] = {}
        self._electric: Dict[str, Any] = {}

    def update(self, device_data):
        """Update data from server."""
        self._alias = device_data.get("alias")
        self._typename = device_data.get("typename")
        self._device_id = str(device_data.get("device_id"))
        self._imei = device_data.get("device_id")
        self._fw_version = device_data.get("firmware_version")
        self._status = device_data.get("status")
        self._phone = device_data.get("phone")
        self._gsm_lvl = device_data.get("common").get("gsm_lvl")
        self._balance = device_data.get("balance", {})
        self._battery = round(device_data.get("common").get("battery"), 2)
        self._ctemp = device_data.get("common").get(
            "ctemp", device_data.get("common").get("mayak_temp")
        )
        self._etemp = device_data.get("common").get("etemp")
        self._fuel = {
            "val": device_data.get("obd").get("fuel_litres"),
            "ts": device_data.get("activity_ts"),
            "type": "liters",
        }
        self._mileage = {
            "val": device_data.get("obd").get("mileage"),
            "ts": device_data.get("activity_ts"),
        }
        self._car_state = device_data.get("state", {})
        self._car_alr_state = device_data.get("alarm_state", {})
        self._ts_activity = device_data.get("activity_ts")
        self._functions = device_data.get("functions", [])
        self._position = device_data.get("position")
        # Косяк в АПИ Старлайна - перепутаны Х и У, удалить, когда поправят
        x = device_data.get("position").get("y")
        y = device_data.get("position").get("x")
        self._position.update({"x": x, "y": y})
        # ================================================================
        self._electric = device_data.get("electric_status", {})

    def update_obd(self, obd_info):
        """Update OBD data from server."""
        self._errors = obd_info.get("errors")

    def update_car_state(self, car_state):
        """Update car state from server."""
        for key in car_state:
            if key in self._car_state:
                self._car_state[key] = car_state[key] in ["1", "true", True]
        return

    @property
    def name(self):
        """Device name."""
        return self._alias

    @property
    def typename(self):
        """Device type name."""
        return self._typename

    @property
    def device_id(self):
        """Device ID."""
        return self._device_id

    @property
    def imei(self):
        """Device IMEI."""
        return self._imei

    @property
    def fw_version(self):
        """Firmware version."""
        return self._fw_version

    @property
    def online(self):
        """Is device online."""
        return int(self._status) == 1

    @property
    def phone(self):
        """Device phone number."""
        for slot in self._balance:
            if slot.get("key") == "active":
                return slot.get("number")
        return "Can find active slot"

    @property
    def gsm_level(self):
        """GSM signal level."""
        if self._gsm_lvl is None:
            return None
        if not self.online:
            return 0
        return self._gsm_lvl

    @property
    def gsm_level_percent(self):
        """GSM signal level percent."""
        if self.gsm_level is None:
            return None
        if self.gsm_level > GSM_LEVEL_MAX:
            return 100
        if self.gsm_level < GSM_LEVEL_MIN:
            return 0
        return round(
            (self.gsm_level - GSM_LEVEL_MIN) / (GSM_LEVEL_MAX - GSM_LEVEL_MIN) * 100
        )

    @property
    def balance(self):
        """Device balance."""
        for slot in self._balance:
            if slot.get("key") == "active":
                return slot
        return "Can find active slot"

    @property
    def battery_level(self):
        """Car battery level."""
        return self._battery

    @property
    def battery_level_percent(self):
        """Car battery level percent."""
        if self._battery is None:
            return 0
        if self._battery > BATTERY_LEVEL_MAX:
            return 100
        if self._battery < BATTERY_LEVEL_MIN:
            return 0
        return round(
            (self._battery - BATTERY_LEVEL_MIN)
            / (BATTERY_LEVEL_MAX - BATTERY_LEVEL_MIN)
            * 100
        )

    @property
    def temp_inner(self):
        """Car inner temperature."""
        return self._ctemp

    @property
    def temp_engine(self):
        """Engine temperarure."""
        return self._etemp

    @property
    def fuel(self):
        """Device fuel count."""
        return self._fuel

    @property
    def mileage(self):
        """Device mileage count."""
        return self._mileage

    @property
    def car_state(self):
        """Car state."""
        return self._car_state

    @property
    def alarm_state(self):
        """Car alarm level."""
        return self._car_alr_state

    @property
    def support_position(self):
        """Is position supported by this device."""
        return DEVICE_FUNCTION_POSITION in self._functions and self._position

    @property
    def support_state(self):
        """Is state supported by this device."""
        return DEVICE_FUNCTION_STATE in self._functions and self._car_state

    @property
    def position(self):
        """Car position."""
        return self._position

    @property
    def errors(self):
        """Device errors info."""
        return self._errors

    @property
    def electric(self):
        """Device errors info."""
        return self._electric
