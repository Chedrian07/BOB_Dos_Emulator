# storage_device.py

import os

class IDEHardDisk:
    """
    간단한 ATA/IDE 디스크 에뮬레이션 (I/O 포트 0x1F0 ~ 0x1F7)
    """

    def __init__(self, disk_image_path="disk.img", cylinders=16, heads=16, sectors=63):
        self.disk_image_path = disk_image_path
        self.cylinders = cylinders
        self.heads = heads
        self.sectors_per_track = sectors
        self.bytes_per_sector = 512

        # 디스크 크기
        self.total_sectors = self.cylinders * self.heads * self.sectors_per_track
        expected_size = self.total_sectors * self.bytes_per_sector

        if not os.path.exists(self.disk_image_path):
            # 생성
            with open(self.disk_image_path, "wb") as f:
                # 최소한 expected_size 만큼 0으로
                f.seek(expected_size - 1)
                f.write(b'\x00')

                # 간단한 부트섹터 코드(512바이트)
                boot_code = bytearray([ 
                    0xB8, 0x12, 0x34,  # MOV AX,0x3412
                    0x05, 0x01, 0x00,  # ADD AX,0x0001
                    0xEA, 0x06, 0x7C, 0x00, 0x00,  # JMP 0x0000:0x7C06
                ])
                boot_code += b'\x00'*(512-len(boot_code))
                f.seek(0)
                f.write(boot_code)

        # 레지스터
        self.data_buffer = bytearray()
        self.buffer_index = 0

        self.data_register = 0
        self.error_register = 0
        self.sector_count_reg = 1
        self.sector_number_reg = 1
        self.cylinder_low_reg = 0
        self.cylinder_high_reg = 0
        self.drive_head_reg = 0
        self.status_reg = 0x40
        self.command_reg = 0

    def lba_address(self):
        head = self.drive_head_reg & 0x0F
        cylinder = (self.cylinder_high_reg << 8) | self.cylinder_low_reg
        sector = self.sector_number_reg
        lba = (cylinder * self.heads + head)*self.sectors_per_track + (sector - 1)
        return lba

    def read_sector(self, lba):
        with open(self.disk_image_path, "rb") as f:
            f.seek(lba*self.bytes_per_sector)
            return f.read(self.bytes_per_sector)

    def write_sector(self, lba, data):
        assert len(data) == self.bytes_per_sector
        with open(self.disk_image_path, "r+b") as f:
            f.seek(lba*self.bytes_per_sector)
            f.write(data)

    def execute_command(self):
        cmd = self.command_reg
        if cmd == 0x20:  # READ SECTORS
            lba = self.lba_address()
            self.data_buffer = bytearray(self.read_sector(lba))
            self.buffer_index = 0
            self.status_reg = 0x58
        elif cmd == 0x30:  # WRITE SECTORS
            lba = self.lba_address()
            self.data_buffer = bytearray(self.bytes_per_sector)
            self.buffer_index = 0
            self.status_reg = 0x58
        else:
            self.error_register = 0x04  # ABRT
            self.status_reg = 0x50
        self.command_reg = 0

    def read_port(self, port: int) -> int:
        if port == 0x1F0:
            if self.buffer_index < len(self.data_buffer):
                val = self.data_buffer[self.buffer_index]
                self.buffer_index += 1
                if self.buffer_index >= len(self.data_buffer):
                    self.status_reg = 0x40
                return val
            else:
                return 0
        elif port == 0x1F1:
            return self.error_register
        elif port == 0x1F2:
            return self.sector_count_reg
        elif port == 0x1F3:
            return self.sector_number_reg
        elif port == 0x1F4:
            return self.cylinder_low_reg
        elif port == 0x1F5:
            return self.cylinder_high_reg
        elif port == 0x1F6:
            return self.drive_head_reg
        elif port == 0x1F7:
            return self.status_reg
        return 0

    def write_port(self, port: int, value: int):
        value &= 0xFF
        if port == 0x1F0:
            if self.buffer_index < len(self.data_buffer):
                self.data_buffer[self.buffer_index] = value
                self.buffer_index += 1
                if self.buffer_index >= len(self.data_buffer):
                    lba = self.lba_address()
                    self.write_sector(lba, self.data_buffer)
                    self.status_reg = 0x40
        elif port == 0x1F1:
            # Features
            pass
        elif port == 0x1F2:
            self.sector_count_reg = value
        elif port == 0x1F3:
            self.sector_number_reg = value
        elif port == 0x1F4:
            self.cylinder_low_reg = value
        elif port == 0x1F5:
            self.cylinder_high_reg = value
        elif port == 0x1F6:
            self.drive_head_reg = value
        elif port == 0x1F7:
            self.command_reg = value
            self.execute_command()