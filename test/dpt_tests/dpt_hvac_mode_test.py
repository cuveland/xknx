"""Unit test for KNX DPT HVAC Operation modes."""

import pytest

from xknx.dpt import DPTArray, DPTHVACMode, DPTHVACStatus
from xknx.dpt.dpt_20 import HVACControllerMode, HVACOperationMode, HVACStatus
from xknx.exceptions import ConversionError, CouldNotParseTelegram


class TestDPTHVACMode:
    """Test class for KNX DPT HVAC Operation modes."""

    def test_mode_to_knx(self):
        """Test parsing DPTHVACMode to KNX."""
        assert DPTHVACMode.to_knx(HVACOperationMode.AUTO) == DPTArray((0x00,))
        assert DPTHVACMode.to_knx(HVACOperationMode.COMFORT) == DPTArray((0x01,))
        assert DPTHVACMode.to_knx(HVACOperationMode.STANDBY) == DPTArray((0x02,))
        assert DPTHVACMode.to_knx(HVACOperationMode.NIGHT) == DPTArray((0x03,))
        assert DPTHVACMode.to_knx(HVACOperationMode.FROST_PROTECTION) == DPTArray(
            (0x04,)
        )

    def test_mode_to_knx_by_string(self):
        """Test parsing DPTHVACMode string values to KNX."""
        assert DPTHVACMode.to_knx("auto") == DPTArray((0x00,))
        assert DPTHVACMode.to_knx("Comfort") == DPTArray((0x01,))
        assert DPTHVACMode.to_knx("standby") == DPTArray((0x02,))
        assert DPTHVACMode.to_knx("NIGHT") == DPTArray((0x03,))
        assert DPTHVACMode.to_knx(
            "Frost Protection"  # Enum value, not name
        ) == DPTArray((0x04,))

    def test_mode_to_knx_wrong_value(self):
        """Test serializing DPTHVACMode to KNX with wrong value."""
        with pytest.raises(ConversionError):
            DPTHVACMode.to_knx(5)

    def test_mode_from_knx(self):
        """Test parsing DPTHVACMode from KNX."""
        assert DPTHVACMode.from_knx(DPTArray((0x00,))) == HVACOperationMode.AUTO
        assert DPTHVACMode.from_knx(DPTArray((0x01,))) == HVACOperationMode.COMFORT
        assert DPTHVACMode.from_knx(DPTArray((0x02,))) == HVACOperationMode.STANDBY
        assert DPTHVACMode.from_knx(DPTArray((0x03,))) == HVACOperationMode.NIGHT
        assert (
            DPTHVACMode.from_knx(DPTArray((0x04,)))
            == HVACOperationMode.FROST_PROTECTION
        )

    def test_mode_from_knx_wrong_value(self):
        """Test parsing of DPTHVACMode with wrong value)."""
        with pytest.raises(CouldNotParseTelegram):
            DPTHVACMode.from_knx(DPTArray((1, 2)))
        with pytest.raises(ConversionError):
            DPTHVACMode.from_knx(DPTArray((0x05,)))


class TestHVACStatus:
    """Test HVACStatus class."""

    @pytest.mark.parametrize(
        ("data", "value"),
        [
            (
                {
                    "mode": "comfort",
                    "dew_point": False,
                    "heat_cool": "heat",
                    "inactive": False,
                    "frost_alarm": False,
                },
                HVACStatus(
                    mode=HVACOperationMode.COMFORT,
                    dew_point=False,
                    heat_cool=HVACControllerMode.HEAT,
                    inactive=False,
                    frost_alarm=False,
                ),
            ),
            (
                {
                    "mode": "standby",
                    "dew_point": False,
                    "heat_cool": "cool",
                    "inactive": True,
                    "frost_alarm": False,
                },
                HVACStatus(
                    mode=HVACOperationMode.STANDBY,
                    dew_point=False,
                    heat_cool=HVACControllerMode.COOL,
                    inactive=True,
                    frost_alarm=False,
                ),
            ),
        ],
    )
    def test_dict(self, data, value):
        """Test from_dict and as_dict methods."""
        test_value = HVACStatus.from_dict(data)
        assert test_value == value
        assert value.as_dict() == data

    @pytest.mark.parametrize(
        "data",
        [
            {
                "mode": 1,  # invalid
                "dew_point": False,
                "heat_cool": "heat",
                "inactive": False,
                "frost_alarm": False,
            },
            {
                "mode": "comfort",
                "dew_point": False,
                "heat_cool": "invalid",  # invalid
                "inactive": False,
                "frost_alarm": False,
            },
            {
                "mode": "comfort",
                "dew_point": False,
                "heat_cool": "nodem",  # invalid for HVACStatus
                "inactive": False,
                "frost_alarm": False,
            },
            {
                "mode": "comfort",
                "dew_point": 20,  # invalid
                "heat_cool": "heat",
                "inactive": False,
                "frost_alarm": False,
            },
        ],
    )
    def test_dict_invalid(self, data):
        """Test from_dict and as_dict methods."""
        with pytest.raises(ValueError):
            HVACStatus.from_dict(data)


class TestDPTHVACStatus:
    """Test class for KNX DPTHVACStatus objects."""

    @pytest.mark.parametrize(
        ("value", "raw"),
        [
            (
                HVACStatus(
                    mode=HVACOperationMode.COMFORT,
                    dew_point=False,
                    heat_cool=HVACControllerMode.HEAT,
                    inactive=False,
                    frost_alarm=False,
                ),
                (0b10000100,),
            ),
            (
                HVACStatus(
                    mode=HVACOperationMode.COMFORT,
                    dew_point=False,
                    heat_cool=HVACControllerMode.COOL,
                    inactive=False,
                    frost_alarm=False,
                ),
                (0b10000000,),
            ),  # min values
            (
                HVACStatus(
                    mode=HVACOperationMode.NIGHT,
                    dew_point=True,
                    heat_cool=HVACControllerMode.COOL,
                    inactive=False,
                    frost_alarm=True,
                ),
                (0b00101001,),
            ),
        ],
    )
    def test_dpt_encoding_decoding(self, value, raw):
        """Test DPTHVACStatus parsing and streaming."""
        knx_value = DPTHVACStatus.to_knx(value)
        assert knx_value == DPTArray(raw)
        assert DPTHVACStatus.from_knx(knx_value) == value

    @pytest.mark.parametrize(
        ("value", "raw"),
        [
            (
                {
                    "mode": "comfort",
                    "dew_point": False,
                    "heat_cool": "heat",
                    "inactive": False,
                    "frost_alarm": False,
                },
                (0b10000100,),
            ),
            (
                {
                    "mode": "standby",
                    "dew_point": False,
                    "heat_cool": "cool",
                    "inactive": True,
                    "frost_alarm": False,
                },
                (0b01000010,),
            ),
        ],
    )
    def test_dpt_to_knx_from_dict(self, value, raw):
        """Test DPTHVACStatus parsing from a dict."""
        knx_value = DPTHVACStatus.to_knx(value)
        assert knx_value == DPTArray(raw)

    @pytest.mark.parametrize(
        "value",
        [
            {"mode": "comfort", "dew_point": False, "heat_cool": "heat"},
            1,
            "cool",
        ],
    )
    def test_dpt_wrong_value_to_knx(self, value):
        """Test DPTHVACStatus parsing with wrong value."""
        with pytest.raises(ConversionError):
            DPTHVACStatus.to_knx(value)

    def test_dpt_wrong_value_from_knx(self):
        """Test DPTHVACStatus parsing with wrong value."""
        with pytest.raises(CouldNotParseTelegram):
            DPTHVACStatus.from_knx(DPTArray((0xFF, 0x4E)))
