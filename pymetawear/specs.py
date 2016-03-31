import uuid


def _high_low_2_uuid(uuid_high, uuid_low):
    return uuid.UUID(int=(uuid_high << 64) + uuid_low)


# Service specs obtained from conection.h
METAWEAR_SERVICE_NOTIFY_CHAR = _high_low_2_uuid(0x326a900085cb9195, 0xd9dd464cfbbae75a), \
                               _high_low_2_uuid(0x326a900685cb9195, 0xd9dd464cfbbae75a)


# Service & char specs obtained from metawearboard.cpp

_DEVICE_INFO_SERVICE = _high_low_2_uuid(0x0000180a00001000, 0x800000805f9b34fb)

METAWEAR_COMMAND_CHAR = METAWEAR_SERVICE_NOTIFY_CHAR, \
                        _high_low_2_uuid(0x326a900185cb9195, 0xd9dd464cfbbae75a)
DEV_INFO_FIRMWARE_CHAR = _DEVICE_INFO_SERVICE, \
                         _high_low_2_uuid(0x00002a2600001000, 0x800000805f9b34fb)
DEV_INFO_MODEL_CHAR = _DEVICE_INFO_SERVICE, \
                      _high_low_2_uuid(0x00002a2400001000, 0x800000805f9b34fb)

