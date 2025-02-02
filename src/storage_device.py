# storage_device.py

import os

class IDEHardDisk:
    """
    간단한 ATA/IDE 디스크 에뮬레이션.
    I/O 포트 0x1F0 ~ 0x1F7 영역을 통해 접근한다고 가정.
    """

    def __init__(self, disk_image_path="disk.img", cylinders=1024, heads=16, sectors=63):
        self.disk_image_path = disk_image_path
        self.cylinders = cylinders
        self.heads = heads
        self.sectors_per_track = sectors
        self.bytes_per_sector = 512

        # 디스크 이미지 파일이 없으면 생성
        self.total_sectors = self.cylinders * self.heads * self.sectors_per_track
        expected_size = self.total_sectors * self.bytes_per_sector
        if not os.path.exists(self.disk_image_path):
            with open(self.disk_image_path, "wb") as f:
                f.seek(expected_size - 1)
                f.write(b'\x00')

        # 상태 레지스터, 데이터 레지스터, 등등
        self.data_register = 0
        self.error_register = 0
        self.sector_count_reg = 1
        self.sector_number_reg = 1
        self.cylinder_low_reg = 0
        self.cylinder_high_reg = 0
        self.drive_head_reg = 0  # 드라이브(마스터/슬레이브), 헤드 번호
        self.status_reg = 0x40  # (RDY)
        self.command_reg = 0

        # 내부 버퍼
        self.data_buffer = bytearray()
        self.buffer_index = 0

    def lba_address(self):
        """
        drive_head_reg의 0~3 bit = head,
        cylinder 레지스터 2개, sector_number_reg
        을 이용해 LBA 계산.
        (실제 ATA LBA28/CHS 혼합은 더욱 복잡하지만 단순화)
        """
        head = self.drive_head_reg & 0x0F
        cylinder = (self.cylinder_high_reg << 8) | self.cylinder_low_reg
        sector = self.sector_number_reg
        # CHS -> LBA 변환
        lba = (cylinder * self.heads + head) * self.sectors_per_track + (sector - 1)
        return lba

    def read_sector(self, lba):
        with open(self.disk_image_path, "rb") as f:
            f.seek(lba * self.bytes_per_sector)
            return f.read(self.bytes_per_sector)

    def write_sector(self, lba, data):
        assert len(data) == self.bytes_per_sector
        with open(self.disk_image_path, "r+b") as f:
            f.seek(lba * self.bytes_per_sector)
            f.write(data)

    def execute_command(self):
        cmd = self.command_reg
        if cmd == 0x20:  # READ SECTORS
            lba = self.lba_address()
            self.data_buffer = bytearray(self.read_sector(lba))
            self.buffer_index = 0
            # 상태 레지스터 업데이트
            self.status_reg = 0x58  # DRQ=1, RDY=1, BSY=0
        elif cmd == 0x30:  # WRITE SECTORS
            lba = self.lba_address()
            # 쓰기 전용 버퍼 준비
            self.data_buffer = bytearray(self.bytes_per_sector)
            self.buffer_index = 0
            self.status_reg = 0x58  # DRQ=1
        else:
            # 지원하지 않는 명령
            self.error_register = 0x04  # ABRT
            self.status_reg = 0x50  # ERR=1, RDY=1
        # 명령 처리 후 command_reg는 0으로 리셋하거나 유지
        # ATA에서는 BSY=1 동안 명령 실행...
        self.command_reg = 0

    def read_port(self, port: int) -> int:
        # 0x1F0 = 데이터 레지스터
        if port == 0x1F0:
            # data_register 16비트 접근인데, 여기서는 8비트 단위로 나눈다고 가정
            if self.buffer_index < len(self.data_buffer):
                val = self.data_buffer[self.buffer_index]
                self.buffer_index += 1
                # DRQ 상태 해제 로직은 버퍼를 다 읽으면...
                if self.buffer_index >= len(self.data_buffer):
                    self.status_reg = 0x40  # RDY=1, DRQ=0
                return val
            else:
                return 0
        elif port == 0x1F1:
            # ERROR 레지스터 (읽기)
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
        value = value & 0xFF
        if port == 0x1F0:
            # WRITE SECTORS 명령일 때 데이터 버퍼에 기록
            if self.buffer_index < len(self.data_buffer):
                self.data_buffer[self.buffer_index] = value
                self.buffer_index += 1
                if self.buffer_index >= len(self.data_buffer):
                    # 한 섹터 데이터를 모두 받았으므로 디스크에 써야 함
                    lba = self.lba_address()
                    self.write_sector(lba, self.data_buffer)
                    self.status_reg = 0x40  # RDY=1, DRQ=0
            else:
                pass
        elif port == 0x1F1:
            # Features 레지스터
            # 여기서는 사용하지 않음
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
            # 명령 레지스터
            self.command_reg = value
            self.execute_command()
