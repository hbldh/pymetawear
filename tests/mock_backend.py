#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
mock_backend
-----------

:copyright: 2016-11-25 by hbldh <henrik.blidh@nedomkull.com>

"""

from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import absolute_import

import unittest
from ctypes import create_string_buffer

from pymetawear import libmetawear
from pymetawear.specs import _high_low_2_uuid
from pymetawear.backends import BLECommunicationBackend


class MockBackend(BLECommunicationBackend):

    METAWEAR_R_BOARD= 0
    METAWEAR_RG_BOARD= 1
    METAWEAR_RPRO_BOARD= 2
    METAWEAR_CPRO_BOARD= 3
    METAWEAR_ENV_BOARD= 4
    METAWEAR_DETECT_BOARD= 5

    def __init__(self, address, interface=None, async=True, timeout=None, debug=False, board_type=None):
        super(MockBackend, self).__init__(address, interface, async, timeout, debug)

        self.responses = []
        self.written_data = {}
        self.full_history = []

        self.boardType = board_type if board_type else self.METAWEAR_R_BOARD
        self.eventId= 0
        self.timerId= 0
        self.dataprocId= 0
        self.loggerId= 0
        self.timerSignals= []

        self.metawear_rg_services = {
            0x01: create_string_buffer(b'\x01\x80\x00\x00', 4),
            0x02: create_string_buffer(b'\x02\x80\x00\x00', 4),
            0x03: create_string_buffer(b'\x03\x80\x01\x01', 4),
            0x04: create_string_buffer(b'\x04\x80\x01\x00\x00\x03\x01\x02', 8),
            0x05: create_string_buffer(b'\x05\x80\x00\x00', 4),
            0x06: create_string_buffer(b'\x06\x80\x00\x00', 4),
            0x07: create_string_buffer(b'\x07\x80\x00\x00', 4),
            0x08: create_string_buffer(b'\x08\x80\x00\x00', 4),
            0x09: create_string_buffer(b'\x09\x80\x00\x00\x1c', 5),
            0x0a: create_string_buffer(b'\x0a\x80\x00\x00\x1c', 5),
            0x0b: create_string_buffer(b'\x0b\x80\x00\x02\x08\x80\x2D\x00\x00',
                                       9),
            0x0c: create_string_buffer(b'\x0c\x80\x00\x00\x08', 5),
            0x0d: create_string_buffer(b'\x0d\x80\x00\x00', 4),
            0x0f: create_string_buffer(b'\x0f\x80\x00\x00', 4),
            0x10: create_string_buffer(b'\x10\x80', 2),
            0x11: create_string_buffer(b'\x11\x80\x00\x00', 4),
            0x12: create_string_buffer(b'\x12\x80', 2),
            0x13: create_string_buffer(b'\x13\x80\x00\x01', 4),
            0x14: create_string_buffer(b'\x14\x80', 2),
            0x15: create_string_buffer(b'\x15\x80', 2),
            0x16: create_string_buffer(b'\x16\x80', 2),
            0x17: create_string_buffer(b'\x17\x80', 2),
            0x18: create_string_buffer(b'\x18\x80', 2),
            0xfe: create_string_buffer(b'\xfe\x80\x00\x00', 4)
        }

        self.metawear_r_services = {
            0x01: create_string_buffer(b'\x01\x80\x00\x00', 4),
            0x02: create_string_buffer(b'\x02\x80\x00\x00', 4),
            0x03: create_string_buffer(b'\x03\x80\x00\x01', 4),
            0x04: create_string_buffer(b'\x04\x80\x01\x00\x00\x01', 6),
            0x05: create_string_buffer(b'\x05\x80\x00\x00', 4),
            0x06: create_string_buffer(b'\x06\x80\x00\x00', 4),
            0x07: create_string_buffer(b'\x07\x80\x00\x00', 4),
            0x08: create_string_buffer(b'\x08\x80\x00\x00', 4),
            0x09: create_string_buffer(b'\x09\x80\x00\x00\x1C', 5),
            0x0a: create_string_buffer(b'\x0A\x80\x00\x00\x1C', 5),
            0x0b: create_string_buffer(b'\x0B\x80\x00\x02\x08\x80\x31\x00\x00',
                                       9),
            0x0c: create_string_buffer(b'\x0C\x80\x00\x00\x08', 5),
            0x0d: create_string_buffer(b'\x0D\x80\x00\x00', 4),
            0x0f: create_string_buffer(b'\x0F\x80\x00\x00', 4),
            0x10: create_string_buffer(b'\x10\x80', 2),
            0x11: create_string_buffer(b'\x11\x80\x00\x00', 4),
            0x12: create_string_buffer(b'\x12\x80', 2),
            0x13: create_string_buffer(b'\x13\x80', 2),
            0x14: create_string_buffer(b'\x14\x80', 2),
            0x15: create_string_buffer(b'\x15\x80', 2),
            0x16: create_string_buffer(b'\x16\x80', 2),
            0x17: create_string_buffer(b'\x17\x80', 2),
            0x18: create_string_buffer(b'\x18\x80', 2),
            0xfe: create_string_buffer(b'\xFE\x80\x00\x00', 4)
        }

        self.metawear_rpro_services = {
            0x01: create_string_buffer(b'\x01\x80\x00\x00', 4),
            0x02: create_string_buffer(b'\x02\x80\x00\x00', 4),
            0x03: create_string_buffer(b'\x03\x80\x01\x01', 4),
            0x04: create_string_buffer(b'\x04\x80\x01\x00\x00\x03\x01\x02', 8),
            0x05: create_string_buffer(b'\x05\x80\x00\x00', 4),
            0x06: create_string_buffer(b'\x06\x80\x00\x00', 4),
            0x07: create_string_buffer(b'\x07\x80\x00\x00', 4),
            0x08: create_string_buffer(b'\x08\x80\x00\x00', 4),
            0x09: create_string_buffer(b'\x09\x80\x00\x00\x1C', 5),
            0x0a: create_string_buffer(b'\x0A\x80\x00\x00\x1C', 5),
            0x0b: create_string_buffer(b'\x0B\x80\x00\x02\x08\x80\x2D\x00\x00',
                                       9),
            0x0c: create_string_buffer(b'\x0C\x80\x00\x00\x08', 5),
            0x0d: create_string_buffer(b'\x0D\x80\x00\x00', 4),
            0x0f: create_string_buffer(b'\x0F\x80\x00\x00', 4),
            0x10: create_string_buffer(b'\x10\x80', 2),
            0x11: create_string_buffer(b'\x11\x80\x00\x00', 4),
            0x12: create_string_buffer(b'\x12\x80\x00\x00', 4),
            0x13: create_string_buffer(b'\x13\x80\x00\x01', 4),
            0x14: create_string_buffer(b'\x14\x80\x00\x00', 4),
            0x15: create_string_buffer(b'\x15\x80', 2),
            0x16: create_string_buffer(b'\x16\x80', 2),
            0x17: create_string_buffer(b'\x17\x80', 2),
            0x18: create_string_buffer(b'\x18\x80', 2),
            0xfe: create_string_buffer(b'\xFE\x80\x00\x00', 4)
        }

        self.metawear_cpro_services = {
            0x01: create_string_buffer(b'\x01\x80\x00\x00', 4),
            0x02: create_string_buffer(b'\x02\x80\x00\x00', 4),
            0x03: create_string_buffer(b'\x03\x80\x01\x01', 4),
            0x04: create_string_buffer(b'\x04\x80\x01\x00\x00\x03\x01\x02', 8),
            0x05: create_string_buffer(b'\x05\x80\x00\x00', 4),
            0x06: create_string_buffer(b'\x06\x80\x00\x00', 4),
            0x07: create_string_buffer(b'\x07\x80\x00\x00', 4),
            0x08: create_string_buffer(b'\x08\x80\x00\x00', 4),
            0x09: create_string_buffer(b'\x09\x80\x00\x00\x1C', 5),
            0x0a: create_string_buffer(b'\x0A\x80\x00\x00\x1C', 5),
            0x0b: create_string_buffer(b'\x0B\x80\x00\x02\x08\x80\x2B\x00\x00',
                                       9),
            0x0c: create_string_buffer(b'\x0C\x80\x00\x00\x08', 5),
            0x0d: create_string_buffer(b'\x0D\x80\x00\x00', 4),
            0x0f: create_string_buffer(b'\x0F\x80\x00\x00', 4),
            0x10: create_string_buffer(b'\x10\x80', 2),
            0x11: create_string_buffer(b'\x11\x80\x00\x00', 4),
            0x12: create_string_buffer(b'\x12\x80\x00\x00', 4),
            0x13: create_string_buffer(b'\x13\x80\x00\x01', 4),
            0x14: create_string_buffer(b'\x14\x80\x00\x00', 4),
            0x15: create_string_buffer(b'\x15\x80\x00\x00', 4),
            0x16: create_string_buffer(b'\x16\x80', 2),
            0x17: create_string_buffer(b'\x17\x80', 2),
            0x18: create_string_buffer(b'\x18\x80', 2),
            0xfe: create_string_buffer(b'\xFE\x80\x00\x00', 4)
        }

        self.metawear_detector_services = {
            0x01: create_string_buffer(b'\x01\x80\x00\x00', 4),
            0x02: create_string_buffer(b'\x02\x80\x00\x00', 4),
            0x03: create_string_buffer(b'\x03\x80\x03\x01', 4),
            0x04: create_string_buffer(b'\x04\x80\x01\x00\x00\x03\x01\x02', 8),
            0x05: create_string_buffer(b'\x05\x80\x00\x01\x03\x03\x03\x03\x01',
                                       9),
            0x06: create_string_buffer(b'\x06\x80\x00\x00', 4),
            0x07: create_string_buffer(b'\x07\x80\x00\x00', 4),
            0x08: create_string_buffer(b'\x08\x80\x00\x00', 4),
            0x09: create_string_buffer(b'\x09\x80\x00\x00\x1c', 5),
            0x0a: create_string_buffer(b'\x0a\x80\x00\x00\x1c', 5),
            0x0b: create_string_buffer(b'\x0b\x80\x00\x02\x08\x80\x2b\x00\x00',
                                       9),
            0x0c: create_string_buffer(b'\x0c\x80\x00\x00\x08', 5),
            0x0d: create_string_buffer(b'\x0d\x80\x00\x00', 4),
            0x0f: create_string_buffer(b'\x0f\x80\x00\x01\x08', 5),
            0x10: create_string_buffer(b'\x10\x80', 2),
            0x11: create_string_buffer(b'\x11\x80\x00\x03', 4),
            0x12: create_string_buffer(b'\x12\x80', 2),
            0x13: create_string_buffer(b'\x13\x80', 2),
            0x14: create_string_buffer(b'\x14\x80\x00\x00', 4),
            0x15: create_string_buffer(b'\x15\x80', 2),
            0x16: create_string_buffer(b'\x16\x80', 2),
            0x17: create_string_buffer(b'\x17\x80', 2),
            0x18: create_string_buffer(b'\x18\x80\x00\x00', 4),
            0xfe: create_string_buffer(b'\xfe\x80\x00\x00', 4),
        }

        self.metawear_environment_services = {
            0x01: create_string_buffer(b'\x01\x80\x00\x00', 4),
            0x02: create_string_buffer(b'\x02\x80\x00\x00', 4),
            0x03: create_string_buffer(b'\x03\x80\x03\x01', 4),
            0x04: create_string_buffer(b'\x04\x80\x01\x00\x00\x03\x01\x02', 8),
            0x05: create_string_buffer(b'\x05\x80\x00\x01\x03\x03\x03\x03\x01',
                                       9),
            0x06: create_string_buffer(b'\x06\x80\x00\x00', 4),
            0x07: create_string_buffer(b'\x07\x80\x00\x00', 4),
            0x08: create_string_buffer(b'\x08\x80\x00\x00', 4),
            0x09: create_string_buffer(b'\x09\x80\x00\x00\x1c', 5),
            0x0a: create_string_buffer(b'\x0a\x80\x00\x00\x1c', 5),
            0x0b: create_string_buffer(b'\x0b\x80\x00\x02\x08\x80\x2b\x00\x00',
                                       9),
            0x0c: create_string_buffer(b'\x0c\x80\x00\x00\x08', 5),
            0x0d: create_string_buffer(b'\x0d\x80\x00\x00', 4),
            0x0f: create_string_buffer(b'\x0f\x80\x00\x01\x08', 5),
            0x10: create_string_buffer(b'\x10\x80', 2),
            0x11: create_string_buffer(b'\x11\x80\x00\x03', 4),
            0x12: create_string_buffer(b'\x12\x80\x01\x00', 4),
            0x13: create_string_buffer(b'\x13\x80', 2),
            0x14: create_string_buffer(b'\x14\x80', 2),
            0x15: create_string_buffer(b'\x15\x80', 2),
            0x16: create_string_buffer(b'\x16\x80\x00\x00', 4),
            0x17: create_string_buffer(b'\x17\x80\x00\x00', 4),
            0x18: create_string_buffer(b'\x18\x80', 4),
            0xfe: create_string_buffer(b'\xfe\x80\x00\x00', 4),
        }

        self.firmware_revision = create_string_buffer(b'1.1.3', 5)

    def read_gatt_char_by_uuid(self, characteristic_uuid):
        if characteristic_uuid == _high_low_2_uuid(0x00002a2400001000, 0x800000805f9b34fb):
            if self.boardType == self.METAWEAR_RG_BOARD:
                model_number = create_string_buffer(b'1', 1)
            elif self.boardType == self.METAWEAR_R_BOARD:
                model_number = create_string_buffer(b'0', 1)
            elif self.boardType == self.METAWEAR_RPRO_BOARD:
                model_number = create_string_buffer(b'1', 1)
            elif self.boardType == self.METAWEAR_CPRO_BOARD or self.boardType == self.METAWEAR_DETECT_BOARD or self.boardType == self.METAWEAR_ENV_BOARD:
                model_number = create_string_buffer(b'2', 1)

            libmetawear.mbl_mw_connection_char_read(self.board, characteristic_uuid, model_number.raw, len(model_number.raw))
        elif characteristic_uuid == _high_low_2_uuid(0x00002a2600001000, 0x800000805f9b34fb):
            libmetawear.mbl_mw_connection_char_read(self.board, characteristic_uuid, self.firmware_revision.raw, len(self.firmware_revision.raw))
        
        
        raise NotImplementedError("Use backend-specific classes instead!")

    def write_gatt_char_by_uuid(self, characteristic_uuid, data_to_send):
        if characteristic_uuid not in self.written_data:
            self.written_data[characteristic_uuid] = []
        self.written_data[characteristic_uuid].append(data_to_send)

        self.command = []
        for i in range(0, len(data_to_send)):
            self.command.append(data_to_send[i])

        self.full_history.append(self.command)
        
        d0 = ord(data_to_send[0])
        d1 = ord(data_to_send[1])

        if (d1 == 0x80):
            if (self.boardType == self.METAWEAR_RG_BOARD and d0 in self.metawear_rg_services):
                service_response= self.metawear_rg_services[d0]
            elif (self.boardType == self.METAWEAR_R_BOARD and d0 in self.metawear_r_services):
                service_response= self.metawear_r_services[d0]
            elif (self.boardType == self.METAWEAR_RPRO_BOARD and d0 in self.metawear_rpro_services):
                service_response= self.metawear_rpro_services[d0]
            elif (self.boardType == self.METAWEAR_CPRO_BOARD and d0 in self.metawear_cpro_services):
                service_response= self.metawear_cpro_services[d0]
            elif (self.boardType == self.METAWEAR_DETECT_BOARD and d0 in self.metawear_detector_services):
                service_response= self.metawear_detector_services[d0]
            elif (self.boardType == self.METAWEAR_ENV_BOARD and d0 in self.metawear_environment_services):
                service_response= self.metawear_environment_services[d0]

            libmetawear.mbl_mw_connection_notify_char_changed(self.board, service_response.raw, len(service_response))
        elif (d0 == 0xb and d1 == 0x84):
            reference_tick= create_string_buffer(b'\x0b\x84\x15\x04\x00\x00\x05', 7)
            libmetawear.mbl_mw_connection_notify_char_changed(self.board, reference_tick.raw, len(reference_tick))
        else:
            # ignore module discovey commands
            self.command_history.append(self.command)
            if (d0 == 0xc and d1 == 0x2):
                response= create_string_buffer(b'\x0c\x02', 3)
                response[2]= self.timerId
                self.timerId+= 1
                libmetawear.mbl_mw_connection_notify_char_changed(self.board, response.raw, len(response.raw))
            elif (d0 == 0xa and d1 == 0x3):
                response= create_string_buffer(b'\x0a\x02', 3)
                response[2]= self.eventId
                self.eventId+= 1
                libmetawear.mbl_mw_connection_notify_char_changed(self.board, response.raw, len(response.raw))
            elif (d0 == 0x9 and d1 == 0x2):
                response= create_string_buffer(b'\x09\x02', 3)
                response[2]= self.dataprocId
                self.dataprocId+= 1
                libmetawear.mbl_mw_connection_notify_char_changed(self.board, response.raw, len(response.raw))
            elif (d0 == 0xb and d1 == 0x2):
                response= create_string_buffer(b'\x0b\x02', 3)
                response[2]= self.loggerId
                self.loggerId+= 1
                libmetawear.mbl_mw_connection_notify_char_changed(self.board, response.raw, len(response.raw))
            elif (d0 == 0xb and d1 == 0x85):
                response= create_string_buffer(b'\x0b\x85\x9e\x01\x00\x00', 6)
                libmetawear.mbl_mw_connection_notify_char_changed(self.board, response.raw, len(response.raw))

