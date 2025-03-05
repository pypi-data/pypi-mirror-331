"""Эмулятор Bluetooth дисплея потребителя для счётчика МИР."""

import asyncio
import logging
import struct
import re

from bleak import BleakScanner, BleakClient
from bleak.exc import BleakDBusError
from bleak.backends.device import BLEDevice

SPP_SERVICE_UUID = "4880C12C-FDCB-4077-8920-A450D7F9B907"
PROTO_SELECTOR_CHARACTERISTIC_UUID = "B3F7E595-2951-42FA-879E-0D9DFA5E846E"

PIN_CODE_SERVICE_UUID = "53367898-FDD5-46CC-81E6-B79A008CE1AD"
ENTER_PIN_CODE_CHARACTERISTIC_UUID = "D24A5138-1448-48EA-A983-F7DF274C6D89"

SPP_CHARACTERISTIC_UUID = "FEC26EC4-6D71-4442-9F81-55BC21D658D6"

_LOGGER = logging.getLogger(__name__)


class MIRMeter:

    def __init__(self, scanner: BleakScanner, device_id: str, pin: str) -> None:
        self._scanner = scanner
        self._device_id = device_id
        self._device = device_id if type(device_id) is BLEDevice else None
        self._pin = struct.pack("<I", pin)
        self._queue = asyncio.Queue()

    def calc_crc16(self, data, length):
        crc = 0xFFFF
        for i in range(length):
            crc ^= data[i] << 8
            for j in range(8):
                crc = (crc << 1) ^ 0x1021 if (crc & 0x8000) else crc << 1
        return crc & 0xFFFF

    def wrap_to_proto(self, source):
        dest = [0] * (len(source) + 4)
        dest[1] = len(source)
        for i in range(len(source)):
            dest[i + 2] = source[i]
        crc = self.calc_crc16(dest, len(source) + 2)
        dest[len(source) + 2] = crc >> 8
        dest[len(source) + 3] = crc & 0xFF
        return dest

    def is_valid(self, data):
        try:
            length, crc = int.from_bytes(data[:2]), int.from_bytes(data[-2:])
            if len(data) == length + 4 and self.calc_crc16(data, length + 2) == crc:
                return True
            _LOGGER.error("Неправильный пакет данных")
            return False
        except:
            _LOGGER.error("Сбой при разборе пакета данных")
            return False

    def get_str(self, data, begin):
        if data[begin] != 0x09:
            _LOGGER.error("Тип данных - не строка")
            raise TypeError
        end = begin + data[begin + 1] + 1
        return (" ".join(data[begin + 2 : end].decode("cp1251").split()).replace(". ", "."), end + 1)

    def get_obis(self, data, begin):
        if data[begin] != 0x07:
            _LOGGER.error("Тип данных - не OBIS")
            raise TypeError
        end = begin + 8
        return (".".join([str(a) for a in data[end - 2 : begin : -1]]), end + 1)

    def get_byte(self, data, begin):
        if data[begin] != 0x11:
            _LOGGER.error("Тип данных - не байт")
            raise TypeError
        end = begin + 1
        return (int.from_bytes(data[begin + 1 : end + 1]), end + 1)

    async def find_device(self):
        if self._device is None:
            _LOGGER.debug("Поиск устройства %s", self._device_id)
            devices = await self._scanner.discover()
            if re.match("([0-9A-Fa-f]{2}:){5}([0-9A-Fa-f]){2}$", self._device_id):
                self._device = next((dev for dev in devices if dev.address == self._device_id), None)
            else:
                self._device = next((dev for dev in devices if dev.name == self._device_id), None)
        return self._device

    async def _setup_connection(self, client):
        try:
            spp_svc = client.services.get_service(SPP_SERVICE_UUID)
            ps_char = spp_svc.get_characteristic(PROTO_SELECTOR_CHARACTERISTIC_UUID)
            await client.write_gatt_char(ps_char, b"\x01", response=True)

            pin_svc = client.services.get_service(PIN_CODE_SERVICE_UUID)
            pin_char = pin_svc.get_characteristic(ENTER_PIN_CODE_CHARACTERISTIC_UUID)
            await client.write_gatt_char(pin_char, self._pin, response=True)
        except BleakDBusError as ex:
            _LOGGER.error(ex)
            return False
        return True

    async def check_pin(self):
        async with BleakClient(self._device) as client:
            res = await self._setup_connection(client)
            if client.is_connected:
                await client.disconnect()
            return res

    async def _notification_handler(self, handle, data):
        await self._queue.put(data)

    async def get_data(self, full_poll=True):
        _LOGGER.debug("Подключение к устройству %s", self._device.name)
        async with BleakClient(self._device) as client:
            client._mtu_size = 247

            if not await self._setup_connection(client):
                raise ConnectionError
            _LOGGER.debug("Настройка связи с устройством завершена")

            spp_svc = client.services.get_service(SPP_SERVICE_UUID)
            spp_char = spp_svc.get_characteristic(SPP_CHARACTERISTIC_UUID)
            await client.start_notify(spp_char, self._notification_handler)

            state = 0
            command = b"\xEE"
            obis_codes = dict()
            group_name = "Параметры автопрокрутки"
            while True:
                await client.write_gatt_char(spp_char, self.wrap_to_proto(command), response=False)
                data = await asyncio.wait_for(self._queue.get(), timeout=1.0)
                if not self.is_valid(data):
                    break
                data = data[2:-2]
                match state:
                    case 0:
                        if data[0] != 0x03:
                            break
                        name, position = self.get_str(data, 3)
                        obis, position = self.get_obis(data, position)
                        value, position = self.get_str(data, position)
                        unit, position = self.get_str(data, position)
                        if obis not in obis_codes:
                            obis_codes[obis] = (group_name, name, value, unit)
                            _LOGGER.debug("Параметр автопрокрутки %s '%s': %s %s", obis, name, value, unit)
                            command = b"\x08"
                        else:
                            state = 1
                            command = b"\x02"
                    case 1:
                        if data[0] != 0x01:
                            break
                        current_group, position = self.get_byte(data, 1)
                        total_groups, position = self.get_byte(data, position)
                        _, position = self.get_byte(data, position)
                        name, position = self.get_str(data, position)
                        group_name = name
                        _LOGGER.debug("Вход в группу меню %s из %s, '%s'", current_group, total_groups, group_name)
                        if current_group <= total_groups:
                            state = 2
                            command = b"\x08"
                    case 2:
                        if data[0] == 0x02:
                            current_parameter, position = self.get_byte(data, 1)
                            total_parameters, position = self.get_byte(data, position)
                            current_group, position = self.get_byte(data, position)
                            total_groups, position = self.get_byte(data, position)
                            obis, position = self.get_obis(data, position)
                            name, position = self.get_str(data, position)
                            value, position = self.get_str(data, position)
                            unit, position = self.get_str(data, position)
                            if obis == "0.0.128.5.10.255":
                                value, unit = value.split()
                            if obis not in obis_codes:
                                obis_codes[obis] = (group_name, name, value, unit)
                            _LOGGER.debug(
                                "Параметр группы меню %s из %s, %s '%s': %s %s",
                                current_parameter,
                                total_parameters,
                                obis,
                                name,
                                value,
                                unit,
                            )
                            if current_parameter == total_parameters:
                                state = 3
                                command = b"\x01"
                        elif data[0] == 0x05:
                            state = 3
                            command = b"\x01"
                        elif data[0] == 0x07:
                            state = 3
                            command = b"\x01"
                        else:
                            break
                    case 3:
                        if data[0] != 0x01:
                            break
                        current_group, position = self.get_byte(data, 1)
                        total_groups, position = self.get_byte(data, position)
                        _, position = self.get_byte(data, position)
                        name, position = self.get_str(data, position)
                        _LOGGER.debug("Выход из группы меню %s из %s, '%s'", current_group, total_groups, name)
                        if (full_poll and current_group < total_groups) or (not full_poll and current_group < 1):
                            state = 1
                            command = b"\x01"
                        else:
                            state = 4
                            break

            await client.stop_notify(spp_char)
            _LOGGER.debug("Опрос устройства завершен")
            if client.is_connected:
                await client.disconnect()
            _LOGGER.debug("Отключение от устройства завершено")

            if state == 4:
                return obis_codes
            else:
                raise InterruptedError
