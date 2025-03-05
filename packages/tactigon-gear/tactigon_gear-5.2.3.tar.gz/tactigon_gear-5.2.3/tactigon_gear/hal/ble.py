import logging
import struct
import math
import asyncio
import time

from bleak import BleakClient
from threading import Thread, Event, Lock
from queue import Queue
from multiprocessing.connection import _ConnectionBase
from datetime import datetime

from typing import Optional, Tuple

from ..models import  TBleSelector, Hand, Angle, Acceleration, Touch, Gyro, OneFingerGesture, TwoFingerGesture, TouchConfig, BLECommands, BLECommand
from ..utils import AdvancedQueue
from ..middleware.Tactigon_Audio import ADPCMEngine

class Ble(Thread):
    TICK: float = 0.02
    _RECONNECT_TIMEOUT: float = 0.1
    SENSORS_UUID: str = "bea5760d-503d-4920-b000-101e7306b005"
    TOUCHPAD_UUID: str = "bea5760d-503d-4920-b000-101e7306b009"
    TOUCH_CONFIG_UUID: str = "bea5760d-503d-4920-b000-101e7306b011"

    AUDIO_DATA_UUID: str = "08000000-0001-11e1-ac36-0002a5d5c51b"
    AUDIO_SYNC_UUID: str = "40000000-0001-11e1-ac36-0002a5d5c51b"

    address: str
    hand: Hand
    touch_config: TouchConfig
    debug: bool

    _stop_event: Event
    client: Optional[BleakClient]
    selector: TBleSelector
    _sensor_tx: Optional[_ConnectionBase] = None
    _angle_tx: Optional[_ConnectionBase] = None
    _audio_tx: Optional[_ConnectionBase] = None
    _update: Lock
    _update_touch: Lock
    _update_selector: Lock
    _sleep: Event
    _update_time_s: float
    _last_update: datetime

    _angle: Optional[Angle] = None
    _acceleration: Optional[Acceleration] = None
    _gyro: Optional[Gyro] = None
    _battery: float = 0
    _touch: Optional[Touch] = None

    _writes: AdvancedQueue
    _reads: Queue

    adpcm_engine: ADPCMEngine

    def __init__(self, address: str, hand: Hand, touch_config: Optional[TouchConfig] = None, sleep_timeout_s: float = 5, debug: bool = False):
        Thread.__init__(self, daemon=True)
        self.address = address
        self.hand = hand
        self._update_time_s = sleep_timeout_s
        
        if touch_config:
            self.touch_config = touch_config
        else:
            self.touch_config = TouchConfig.Default()
        self.debug = debug

        self._sleep = Event()
        self._stop_event = Event()
        self._update = Lock()
        self._update_touch = Lock()
        self._update_selector = Lock()
        self.client = None
        self.selector = TBleSelector.SENSORS
        self.adpcm_engine = ADPCMEngine()

        self._writes = AdvancedQueue()
        self._reads = Queue()

        self.update_touch(self.touch_config)

    @staticmethod
    def gravity_comp(hand: Hand, accX: float, accY: float, accZ: float, gyroX: float, gyroY: float, gyroZ: float, roll: float, pitch: float, yaw: float):
        """gravity compensation"""
        G_CONST = 9.81
        ANG_TO_RAD = math.pi / 180
        ACC_RATIO = 1000
        VEL_RATIO = 30

        if hand == Hand.LEFT:
            accX = -accX / ACC_RATIO
            accY = -accY / ACC_RATIO
            accZ = -accZ / ACC_RATIO

            gyroX = -gyroX / VEL_RATIO
            gyroY = -gyroY / VEL_RATIO
            gyroZ = -gyroZ / VEL_RATIO

            _pitch = roll * ANG_TO_RAD
            _roll = pitch * ANG_TO_RAD

        else:
            accX = accX / ACC_RATIO
            accY = accY / ACC_RATIO
            accZ = -accZ / ACC_RATIO

            gyroX = gyroX / VEL_RATIO
            gyroY = gyroY / VEL_RATIO
            gyroZ = -gyroZ / VEL_RATIO

            _pitch = -roll * ANG_TO_RAD
            _roll = -pitch * ANG_TO_RAD

        if accZ == 0:
            beta = math.pi / 2
        else:
            beta = math.atan(
                math.sqrt(math.pow(accX, 2) + math.pow(accY, 2)) / accZ
            )

        accX = accX - G_CONST * math.sin(_roll)
        accY = accY + G_CONST * math.sin(_pitch)
        accZ = accZ - G_CONST * math.cos(beta)

        return accX, accY, accZ, gyroX, gyroY, gyroZ, roll, pitch, yaw

    @property
    def connected(self) -> bool:
        return (True if self.client.is_connected else False) if self.client else False
    
    @property
    def angle(self) -> Optional[Angle]:
        if self.sleep:
            return None
        
        with self._update:
            angle = self._angle
        return angle
    
    @property
    def acceleration(self) -> Optional[Acceleration]:
        if self.sleep:
            return None
        
        with self._update:
            acc = self._acceleration
        return acc

    @property
    def gyro(self) -> Optional[Gyro]:
        if self.sleep:
            return None
        
        with self._update:
            gyro = self._gyro
        return gyro
    
    @property
    def touch(self) -> Optional[Touch]:
        if self.sleep:
            return None
        
        with self._update_touch:
            touch = self._touch
            self._touch = None
        return touch
    
    @property
    def sleep(self) -> bool:
        return self._sleep.is_set()
        
    @property
    def battery(self) -> Optional[float]:
        if self.sleep:
            return None
        
        return self._battery

    def handle_audio_sync(self, char, data: bytearray):
        pass

    def handle_audio(self, char, data: bytearray):
        self._last_update = datetime.now()
        if self._audio_tx:
            self._audio_tx.send_bytes(self.adpcm_engine.extract_data(data))

    def handle_sensors(self, char, data:bytearray):
        self._last_update = datetime.now()
        
        accX, accY, accZ, gyroX, gyroY, gyroZ, roll, pitch, yaw, battery = struct.unpack("hhhhhhhhhh", data)
        accX, accY, accZ, gyroX, gyroY, gyroZ, roll, pitch, yaw = self.gravity_comp(self.hand, accX, accY, accZ, gyroX, gyroY, gyroZ, roll, pitch, yaw)

        with self._update:
            self._angle = Angle(roll, pitch, yaw)
            self._acceleration = Acceleration(accX, accY, accZ)
            self._gyro = Gyro(gyroX, gyroY, gyroZ)
            self._battery = battery/1000

        if self.debug:
            logging.debug("Angle: %f,%f,%f",roll, pitch, yaw)
            logging.debug("Acceleration: %f,%f,%f",accX, accY, accZ)
            logging.debug("Gyro: %f,%f,%f",gyroX, gyroY, gyroZ)
            logging.debug("Battery: %f", battery/1000)

        if self._sensor_tx:
            self._sensor_tx.send([accX, accY, accZ, gyroX, gyroY, gyroZ])

        if self._angle_tx:
            self._angle_tx.send([roll, pitch, yaw])

    def handle_touchpad(self, char, data: bytearray):
        self._last_update = datetime.now()
        with self._update_touch:
            one_finger = OneFingerGesture(int.from_bytes(data[0:1], "big"))
            two_finger = TwoFingerGesture(int.from_bytes(data[1:2], "big"))
            if one_finger is not OneFingerGesture.NONE or two_finger is not TwoFingerGesture.NONE:
                self._touch = Touch(
                    one_finger,
                    two_finger,
                    float(struct.unpack("h", data[2:4])[0]),
                    float(struct.unpack("h", data[4:6])[0])
                )

    def start(self):
        logging.debug("[BLE] BLE starting on address %s", self.address)
        Thread.start(self)

    def join(self, timeout: Optional[float] = None):
        logging.debug("[BLE] Stopping BLE on address %s", self.address)
        self._stop_event.set()
        Thread.join(self, timeout)

    def run(self):
        asyncio.run(self.task())

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, *attr):
        self.join()

    async def task(self):
        running_selector: Optional[TBleSelector] = None
        while not self._stop_event.is_set():
            self.client = BleakClient(self.address)
            try:
                await self.client.connect()
                await self.client.start_notify(self.TOUCHPAD_UUID, self.handle_touchpad)
                running_selector = None
                self._sleep.clear()
                self._last_update = datetime.now()
            except Exception as e:
                logging.error("[BLE] Cannot connect to %s. %s", self.address, e)
                self.client = None
                await asyncio.sleep(self._RECONNECT_TIMEOUT)
                continue

            while self.connected:
                if self._stop_event.is_set():
                    await self.client.disconnect()
                    self.client = None
                    break

                while True:
                    try:
                        cmd: BLECommand = self._writes.get_nowait()
                        try:
                            if cmd.command == BLECommands.WRITE and cmd.payload:
                                await self.client.write_gatt_char(cmd.characteristic, cmd.payload)
                            elif cmd.command == BLECommands.READ:
                                self._reads.put(await self.client.read_gatt_char(cmd.characteristic))
                        except:
                            logging.error("[BLE] Cannot %s on characteristic %s. Payload %s", cmd.command.name, cmd.characteristic, str(cmd.payload))
                    except:
                        break

                if running_selector != self.selector:
                    with self._update_selector:
                        if running_selector == TBleSelector.SENSORS:
                            await self.client.stop_notify(self.SENSORS_UUID)
                            self._update.acquire()
                            self._angle = None
                            self._acceleration = None
                            self._gyro = None
                            self._update.release()
                            logging.debug("[BLE] Stopped notification on sensors (%s)", self.SENSORS_UUID)
                        elif running_selector == TBleSelector.AUDIO:
                            await self.client.stop_notify(self.AUDIO_DATA_UUID)
                            await self.client.stop_notify(self.AUDIO_SYNC_UUID)
                            logging.debug("[BLE] Stopped notification on AUDIO (%s %s)", self.AUDIO_SYNC_UUID, self.AUDIO_DATA_UUID)

                        running_selector = self.selector

                        if running_selector == TBleSelector.SENSORS:
                            await self.client.start_notify(self.SENSORS_UUID, self.handle_sensors)
                            logging.debug("[BLE] Started notification on sensors (%s)", self.SENSORS_UUID)
                        elif running_selector == TBleSelector.AUDIO:
                            await self.client.start_notify(self.AUDIO_SYNC_UUID, self.handle_audio_sync)
                            await self.client.start_notify(self.AUDIO_DATA_UUID, self.handle_audio)
                            logging.debug("[BLE] Started notification on AUDIO (%s %s)", self.AUDIO_SYNC_UUID, self.AUDIO_DATA_UUID)

                last_update_delta = (datetime.now() - self._last_update).total_seconds()
                if self._sleep.is_set():
                    
                    if last_update_delta < self._update_time_s:
                        logging.debug("[BLE] Clearing sleep")
                        self._sleep.clear()
                else:
                    if last_update_delta > self._update_time_s:
                        logging.debug("[BLE] Setting sleep after %f seconds", last_update_delta)
                        self._sleep.set()

                await asyncio.sleep(self._RECONNECT_TIMEOUT)

            await asyncio.sleep(self._RECONNECT_TIMEOUT)

    def set_touch(self, config: TouchConfig, timeout: float = 5) -> bool:
        cfg1, cfg2, save = config.toBytes()

        ref1 = self._writes.put(BLECommand(BLECommands.WRITE, self.TOUCH_CONFIG_UUID, cfg1))
        ref2 = self._writes.put(BLECommand(BLECommands.WRITE, self.TOUCH_CONFIG_UUID, cfg2))
        refsave = self._writes.put(BLECommand(BLECommands.WRITE, self.TOUCH_CONFIG_UUID, save))

        _t = 0
        while _t < timeout:
            if self._writes.check(ref1) and self._writes.check(ref2) and self._writes.check(refsave):
                return True
            
            _t += self._RECONNECT_TIMEOUT
            time.sleep(self._RECONNECT_TIMEOUT)
            
        return False

    def get_touch(self, timeout: float = 5) -> Optional[Tuple[bytes, bytes]]:
        self._writes.put(BLECommand(BLECommands.READ, self.TOUCH_CONFIG_UUID))
        self._writes.put(BLECommand(BLECommands.READ, self.TOUCH_CONFIG_UUID))

        cfg1 = None
        cfg2 = None

        _t = 0
        while _t < timeout:
            try:
                resp: bytes = self._reads.get_nowait()
                if cfg1 == None:
                    cfg1 = resp
                else:
                    cfg2 = resp
            except:
                pass

            if cfg1 and cfg2:
                return cfg1, cfg2

            _t += self._RECONNECT_TIMEOUT
            time.sleep(self._RECONNECT_TIMEOUT)
            
        return None
    
    def update_touch(self, touch_config: TouchConfig, timeout: float = 5) -> bool:
        if self.set_touch(touch_config, timeout):
            res = self.get_touch(timeout)
            return self.touch_config.update(*res) if res else False

        return False
    
    def set_touch_sensitivity(self, sensitivity: int = 2, timeout: float = 5):
        self.touch_config.set_sensitivity(sensitivity)
        return self.set_touch(self.touch_config, timeout)

    def select_sensors(self):
        self._update_selector.acquire()
        self.selector = TBleSelector.SENSORS
        self._update_selector.release()

    def select_audio(self):
        self._update_selector.acquire()
        self.selector = TBleSelector.AUDIO
        self._update_selector.release()

    def connect(self):
        self.start()

    def disconnect(self):
        self.join()

    def terminate(self):
        self.join()