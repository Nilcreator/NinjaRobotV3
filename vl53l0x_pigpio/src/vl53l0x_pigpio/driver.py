#
# (c) 2025 Yoichi Tanibayashi
#
"""Python driver for the VL53L0X distance sensor."""

import time
import pigpio
import numpy as np
from pathlib import Path

from .my_logger import get_logger
from .config_manager import load_config


# レジスタアドレス
SYSRANGE_START = 0x00
SYSTEM_SEQUENCE_CONFIG = 0x01
SYS_INTERMEASUREMENT_PERIOD = 0x04
SYSTEM_RANGE_CONFIG = 0x09
SYSTEM_INTERRUPT_CONFIG_GPIO = 0x0A
SYSTEM_INTERRUPT_CLEAR = 0x0B
SYSTEM_THRESH_HIGH = 0x0C
SYSTEM_THRESH_LOW = 0x0E
RESULT_INTERRUPT_STATUS = 0x13
RESULT_RANGE_STATUS = 0x14
CROSSTALK_COMPENSATION_PEAK_RATE_MCPS = 0x20
PRE_RANGE_CONFIG_MIN_SNR = 0x27
ALGO_PART_TO_PART_RANGE_OFFSET = 0x28
ALGO_PHASECAL_LIM = 0x30
GLOBAL_CONFIG_VCSEL_WIDTH = 0x32
HISTOGRAM_CONFIG_INITIAL_PHASE_SELECT = 0x33
FINAL_RANGE_CFG_MIN_COUNT_RATE_RTN_LIMIT = 0x44
MSRC_CONFIG_TIMEOUT_MACROP = 0x46
FINAL_RANGE_CONFIG_VALID_PHASE_LOW = 0x47
FINAL_RANGE_CONFIG_VALID_PHASE_HIGH = 0x48
DYN_SPAD_NUM_REQUESTED_REF_SPAD = 0x4E
DYN_SPAD_REF_EN_START_OFFSET = 0x4F
PRE_RANGE_CONFIG_VCSEL_PERIOD = 0x50
PRE_RANGE_CONFIG_TIMEOUT_MACROP_HI = 0x51
PRE_RANGE_CONFIG_TIMEOUT_MACROP_LO = 0x52
HISTOGRAM_CONFIG_READOUT_CTRL = 0x55
PRE_RANGE_CONFIG_VALID_PHASE_LOW = 0x56
PRE_RANGE_CONFIG_VALID_PHASE_HIGH = 0x57
MSRC_CONFIG_CONTROL = 0x60
PRE_RANGE_CONFIG_SIGMA_THRESH_HI = 0x61
PRE_RANGE_CONFIG_SIGMA_THRESH_LO = 0x62
PRE_RANGE_CFG_MIN_COUNT_RATE_RTN_LIMIT = 0x64
FINAL_RANGE_CONFIG_MIN_SNR = 0x67
FINAL_RANGE_CONFIG_VCSEL_PERIOD = 0x70
FINAL_RANGE_CONFIG_TIMEOUT_MACROP_HI = 0x71
FINAL_RANGE_CONFIG_TIMEOUT_MACROP_LO = 0x72
POWER_MGMT_GO1_POWER_FORCE = 0x80
SYSTEM_HISTOGRAM_BIN = 0x81
GPIO_HV_MUX_ACTIVE_HIGH = 0x84
VHV_CFG_PAD_SCL_SDA_EXTSUP_HV = 0x89
I2C_SLAVE_DEVICE_ADDRESS = 0x8A
GLOBAL_CFG_SPAD_ENABLES_REF_0 = 0xB0
GLOBAL_CFG_SPAD_ENABLES_REF_1 = 0xB1
GLOBAL_CFG_SPAD_ENABLES_REF_2 = 0xB2
GLOBAL_CFG_SPAD_ENABLES_REF_3 = 0xB3
GLOBAL_CFG_SPAD_ENABLES_REF_4 = 0xB4
GLOBAL_CFG_SPAD_ENABLES_REF_5 = 0xB5
RES_PEAK_SIGNAL_RATE_REF = 0xB6
GLOBAL_CFG_REF_EN_START_SELECT = 0xB6
RES_CORE_AMBIENT_WINDOW_EVENTS_RTN = 0xBC
SOFT_RESET_GO2_SOFT_RESET_N = 0xBF
IDENTIFICATION_MODEL_ID = 0xC0
IDENTIFICATION_REVISION_ID = 0xC2
RES_CORE_AMBIENT_WINDOW_EVENTS_REF = 0xD0
RES_CORE_RANGING_TOTAL_EVENTS_REF = 0xD4
OSC_CALIBRATE_VAL = 0xF8

# 共通値
VALUE_00 = 0x00
VALUE_01 = 0x01
VALUE_02 = 0x02
VALUE_03 = 0x03
VALUE_04 = 0x04
VALUE_05 = 0x05
VALUE_06 = 0x06
VALUE_07 = 0x07
VALUE_08 = 0x08
VALUE_09 = 0x09
VALUE_0A = 0x0A
VALUE_10 = 0x10
VALUE_12 = 0x12
VALUE_14 = 0x14
VALUE_1A = 0x1A
VALUE_20 = 0x20
VALUE_21 = 0x21
VALUE_25 = 0x25
VALUE_26 = 0x26
VALUE_28 = 0x28
VALUE_30 = 0x30
VALUE_32 = 32
VALUE_34 = 0x34
VALUE_40 = 0x40
VALUE_44 = 0x44
VALUE_6B = 0x6B
VALUE_80 = 0x80
VALUE_83 = 0x83
VALUE_96 = 0x96
VALUE_A0 = 0xA0
VALUE_B4 = 0xB4
VALUE_E8 = 0xE8
VALUE_FE = 0xFE
VALUE_FF = 0xFF
VALUE_F8 = 0xF8

# レジスタ値
REG_00 = 0x00
REG_01 = 0x01
REG_0D = 0x0D
REG_0E = 0x0E
REG_09 = 0x09
REG_10 = 0x10
REG_11 = 0x11
REG_20 = 0x20
REG_22 = 0x22
REG_23 = 0x23
REG_24 = 0x24
REG_25 = 0x25
REG_27 = 0x27
REG_30 = 0x30
REG_31 = 0x31
REG_32 = 0x32
REG_34 = 0x34
REG_35 = 0x35
REG_40 = 0x40
REG_42 = 0x42
REG_43 = 0x43
REG_44 = 0x44
REG_45 = 0x45
REG_46 = 0x46
REG_47 = 0x47
REG_48 = 0x48
REG_49 = 0x49
REG_4A = 0x4A
REG_4B = 0x4B
REG_4C = 0x4C
REG_4D = 0x4D
REG_4E = 0x4E
REG_50 = 0x50
REG_51 = 0x51
REG_52 = 0x52
REG_54 = 0x54
REG_56 = 0x56
REG_57 = 0x57
REG_60 = 0x60
REG_61 = 0x61
REG_62 = 0x62
REG_64 = 0x64
REG_65 = 0x65
REG_66 = 0x66
REG_67 = 0x67
REG_70 = 0x70
REG_71 = 0x71
REG_72 = 0x72
REG_75 = 0x75
REG_76 = 0x76
REG_77 = 0x77
REG_78 = 0x78
REG_7A = 0x7A
REG_7B = 0x7B
REG_80 = 0x80
REG_81 = 0x81
REG_8E = 0x8E
REG_91 = 0x91
REG_92 = 0x92
REG_94 = 0x94
REG_FF = 0xFF

# その他の定数
I2C_STANDARD_MODE = 0x88
SPAD_NUM_REQUESTED_REF = 0x2C
GPIO_INTERRUPT_CONFIG = 0x04
CALIBRATION_VALUE_40 = 0x40
TIMEOUT_LIMIT = 1  # タイムアウト時間 (秒)
SPAD_COUNT_MASK = 0x7F
SPAD_APERTURE_BIT = 0x80
INTERRUPT_STATUS_MASK = 0x07
SPAD_START_INDEX_APERTURE = 12
SPAD_TOTAL_COUNT = 48
SPAD_MAP_BITS_PER_BYTE = 8


class VL53L0X:
    """
    VL53L0X driver.
    """

    def __init__(self, pi: pigpio.pi, i2c_bus: int = 1, i2c_address: int = 0x29, debug: bool = False, config_file_path: Path | None = None):
        """
        Initialize the VL53L0X sensor.
        """
        self.pi = pi
        self.i2c_bus = i2c_bus
        self.i2c_address = i2c_address
        self.__log = get_logger(self.__class__.__name__, debug)
        self.__log.debug(
            "Open VL53L0X at i2c_bus=%s, i2c_address=%s",
            self.i2c_bus,
            hex(self.i2c_address),
        )
        self.handle = self.pi.i2c_open(self.i2c_bus, self.i2c_address)
        self.__log.debug("handle=%s", self.handle)
        self.offset_mm = 0

        # Load offset from config file if provided
        if config_file_path:
            config = load_config(config_file_path)
            if "offset_mm" in config:
                self.set_offset(config["offset_mm"])
                self.__log.debug("Loaded offset_mm=%s from %s", self.offset_mm, config_file_path)

        self.initialize()

    def __enter__(self) -> "VL53L0X":
        """
        コンテキストマネージャーとして使用する際のエントリポイント。
        """
        return self

    def __exit__(
        self, exc_type: type | None, exc_val: Exception | None, exc_tb: type | None
    ) -> None:
        """
        コンテキストマネージャーとして使用する際の終了ポイント。
        I2C接続を閉じます。
        """
        self.__log.debug(
            "exc_type=%s, exc_val=%s, exc_tb=%s",
            exc_type, exc_val, exc_tb
        )
        self.close()

    def _set_i2c_registers_initial_values(self) -> None:
        """
        I2Cレジスタの初期値を設定します。
        """
        # I2C標準モードを設定
        self.write_byte(I2C_STANDARD_MODE, VALUE_00)

        # VL53L0Xデータシートに従って各種レジスタを初期化
        self.write_byte(REG_80, VALUE_01)
        self.write_byte(REG_FF, VALUE_01)
        self.write_byte(REG_00, VALUE_00)

        # REG_91からストップ変数を読み取る
        self.stop_variable = self.read_byte(REG_91)

        # レジスタをデフォルトの電源投入時の値に復元
        self.write_byte(REG_00, VALUE_01)
        self.write_byte(REG_FF, VALUE_00)
        self.write_byte(REG_80, VALUE_00)

        # I/O 2.8V エクスパンダ（推奨：一度だけ）
        try:
            self.write_byte(VHV_CFG_PAD_SCL_SDA_EXTSUP_HV, (self.read_byte(VHV_CFG_PAD_SCL_SDA_EXTSUP_HV) | 0x01))
        except Exception:
            pass

    def _configure_signal_rate_limit(self) -> None:
        """
        信号レート制限を設定します。
        """
        # MSRC_CONFIG_CONTROLレジスタのSIGNAL_RATE_MSRC (ビット1) と
        # SIGNAL_RATE_PRE_RANGE (ビット4) の制限チェックを無効にする。
        current_msrc_config = self.read_byte(MSRC_CONFIG_CONTROL)
        self.write_byte(MSRC_CONFIG_CONTROL, (current_msrc_config | VALUE_12))

        # 最終レンジ信号レート制限を0.25 MCPS (百万カウント/秒) に設定する。
        # この値は0.25 * 128 = 32。
        self.write_word(FINAL_RANGE_CFG_MIN_COUNT_RATE_RTN_LIMIT, VALUE_32)

        # SYSTEM_SEQUENCE_CONFIGを設定して、構成のためにすべてのシーケンスを有効にする。
        self.write_byte(SYSTEM_SEQUENCE_CONFIG, VALUE_FF)

    def _setup_spad_info(self) -> None:
        """
        SPAD情報を設定します。
        """
        spad_count, spad_is_aperture = self._get_spad_info()

        # The SPAD map (RefGoodSpadMap) is read by VL53L0X_get_info_from_device()
        # in the API, but the same data seems to be written to
        # GLOBAL_CONFIG_SPAD_ENABLES_REF_0 through GLOBAL_CONFIG_SPAD_ENABLES_REF_5,
        # so read it from there.
        ref_spad_map = self.read_block(GLOBAL_CFG_SPAD_ENABLES_REF_0, 6)

        # Configure dynamic SPAD settings
        self.write_byte(REG_FF, VALUE_01)
        self.write_byte(DYN_SPAD_REF_EN_START_OFFSET, VALUE_00)
        self.write_byte(
            DYN_SPAD_NUM_REQUESTED_REF_SPAD, SPAD_NUM_REQUESTED_REF
        )
        self.write_byte(REG_FF, VALUE_00)
        self.write_byte(GLOBAL_CFG_REF_EN_START_SELECT, VALUE_B4)

        first_spad_to_enable = SPAD_START_INDEX_APERTURE if spad_is_aperture else 0
        spads_enabled = 0

        # Enable SPADs based on count and aperture information
        for i in range(SPAD_TOTAL_COUNT):
            if i < first_spad_to_enable or spads_enabled == spad_count:
                # This bit is lower than the first one to enable, or
                # (spad_count) bits have already been enabled, so zero this bit
                ref_spad_map[i // SPAD_MAP_BITS_PER_BYTE] &= ~(1 << (i % SPAD_MAP_BITS_PER_BYTE))
            elif (ref_spad_map[i // SPAD_MAP_BITS_PER_BYTE] >> (i % SPAD_MAP_BITS_PER_BYTE)) & 0x1:
                spads_enabled += 1

        self.write_block(GLOBAL_CFG_SPAD_ENABLES_REF_0, ref_spad_map)

        # Further SPAD configuration registers
        self.write_byte(REG_FF, VALUE_01)
        self.write_byte(REG_00, VALUE_00)

        self.write_byte(REG_FF, VALUE_00)
        self.write_byte(REG_09, VALUE_00)
        self.write_byte(REG_10, VALUE_00)
        self.write_byte(REG_11, VALUE_00)

        self.write_byte(REG_24, VALUE_01)
        self.write_byte(REG_25, VALUE_FF)
        self.write_byte(REG_75, VALUE_00)

        self.write_byte(REG_FF, VALUE_01)
        self.write_byte(REG_4E, SPAD_NUM_REQUESTED_REF)
        self.write_byte(REG_48, VALUE_00)
        self.write_byte(REG_30, VALUE_20)

        self.write_byte(REG_FF, VALUE_00)
        self.write_byte(REG_30, VALUE_09)
        self.write_byte(REG_54, VALUE_00)
        self.write_byte(REG_31, VALUE_04)
        self.write_byte(REG_32, VALUE_03)
        self.write_byte(REG_40, VALUE_83)
        self.write_byte(REG_46, VALUE_25)
        self.write_byte(REG_60, VALUE_00)
        self.write_byte(REG_27, VALUE_00)
        self.write_byte(REG_50, VALUE_06)
        self.write_byte(REG_51, VALUE_00)
        self.write_byte(REG_52, VALUE_96)
        self.write_byte(REG_56, VALUE_08)
        self.write_byte(REG_57, VALUE_30)
        self.write_byte(REG_61, VALUE_00)
        self.write_byte(REG_62, VALUE_00)
        self.write_byte(REG_64, VALUE_00)
        self.write_byte(REG_65, VALUE_00)
        self.write_byte(REG_66, VALUE_A0)

        self.write_byte(REG_FF, VALUE_01)
        self.write_byte(REG_22, VALUE_32)
        self.write_byte(REG_47, VALUE_14)
        self.write_byte(REG_49, VALUE_FF)
        self.write_byte(REG_4A, VALUE_00)

        self.write_byte(REG_FF, VALUE_00)
        self.write_byte(REG_7A, VALUE_0A)
        self.write_byte(REG_7B, VALUE_00)
        self.write_byte(REG_78, VALUE_21)

        self.write_byte(REG_FF, VALUE_01)
        self.write_byte(REG_23, VALUE_34)
        self.write_byte(REG_42, VALUE_00)
        self.write_byte(REG_44, VALUE_FF)
        self.write_byte(REG_45, VALUE_26)
        self.write_byte(REG_46, VALUE_05)
        self.write_byte(REG_40, VALUE_40)
        self.write_byte(REG_0E, VALUE_06)
        self.write_byte(REG_20, VALUE_1A)
        self.write_byte(REG_43, VALUE_40)

        self.write_byte(REG_FF, VALUE_00)
        self.write_byte(REG_34, VALUE_03)
        self.write_byte(REG_35, VALUE_44)

        self.write_byte(REG_FF, VALUE_01)
        self.write_byte(REG_31, VALUE_04)
        self.write_byte(REG_4B, VALUE_09)
        self.write_byte(REG_4C, VALUE_05)
        self.write_byte(REG_4D, VALUE_04)

        self.write_byte(REG_FF, VALUE_00)
        self.write_byte(REG_44, VALUE_00)
        self.write_byte(REG_45, VALUE_20)
        self.write_byte(REG_47, VALUE_08)
        self.write_byte(REG_48, VALUE_28)
        self.write_byte(REG_67, VALUE_00)
        self.write_byte(REG_70, VALUE_04)
        self.write_byte(REG_71, VALUE_01)
        self.write_byte(REG_72, VALUE_FE)
        self.write_byte(REG_76, VALUE_00)
        self.write_byte(REG_77, VALUE_00)

        self.write_byte(REG_FF, VALUE_01)
        self.write_byte(REG_0D, VALUE_01)

        self.write_byte(REG_FF, VALUE_00)
        self.write_byte(REG_80, VALUE_01)
        self.write_byte(REG_01, VALUE_F8)

        self.write_byte(REG_FF, VALUE_01)
        self.write_byte(REG_8E, VALUE_01)
        self.write_byte(REG_00, VALUE_01)
        self.write_byte(REG_FF, VALUE_00)
        self.write_byte(REG_80, VALUE_00)

    def _configure_interrupt_gpio(self) -> None:
        """
        割り込みGPIOを設定します。
        """
        # 割り込み出力のためにGPIOを設定
        self.write_byte(SYSTEM_INTERRUPT_CONFIG_GPIO, GPIO_INTERRUPT_CONFIG)

        # GPIO_HV_MUX_ACTIVE_HIGHレジスタをアクティブローに設定
        current_gpio_hv_mux = self.read_byte(GPIO_HV_MUX_ACTIVE_HIGH)
        self.write_byte(GPIO_HV_MUX_ACTIVE_HIGH, (current_gpio_hv_mux & ~VALUE_10))

        # 割り込みをクリア
        self.write_byte(SYSTEM_INTERRUPT_CLEAR, VALUE_01)

    def _set_timing_budget_and_calibrations(self) -> None:
        """
        タイミングバジェットを設定し、キャリブレーションを実行します。
        """
        # 測定タイミングバジェットを取得して設定
        self.measurement_timing_budget_us = self.get_measurement_timing_budget()
        self.__log.debug(
            "measurement_timing_budget_us=%s",
            self.measurement_timing_budget_us
        )
        self.set_measurement_timing_budget(self.measurement_timing_budget_us)

        # 以前のシーケンス設定を復元し、再度タイミングバジェットを設定
        self.write_byte(SYSTEM_SEQUENCE_CONFIG, VALUE_E8)
        self.set_measurement_timing_budget(self.measurement_timing_budget_us)

        # 単一のリファレンスキャリブレーションを実行
        self.write_byte(SYSTEM_SEQUENCE_CONFIG, VALUE_01)
        self.perform_single_ref_calibration(CALIBRATION_VALUE_40)

        self.write_byte(SYSTEM_SEQUENCE_CONFIG, VALUE_02)
        self.perform_single_ref_calibration(VALUE_00)

        # キャリブレーション後に以前のシーケンス設定を復元
        self.write_byte(SYSTEM_SEQUENCE_CONFIG, VALUE_E8)

    def initialize(self) -> None:
        """
        センサーを初期化します。
        """
        # I2Cレジスタの初期値を設定
        self._set_i2c_registers_initial_values()

        # 信号レート制限を設定
        self._configure_signal_rate_limit()

        # SPAD情報を設定
        self._setup_spad_info()

        # 割り込みGPIOを設定
        self._configure_interrupt_gpio()

        # タイミングバジェットを設定し、キャリブレーションを実行
        self._set_timing_budget_and_calibrations()

    def _get_spad_info(self) -> tuple[int, bool]:
        """
        SPAD情報を取得します。
        """
        # SPAD情報取得のための初期レジスタ設定
        self.write_byte(REG_80, VALUE_01)
        self.write_byte(REG_FF, VALUE_01)
        self.write_byte(REG_00, VALUE_00)

        self.write_byte(REG_FF, VALUE_06)
        self.write_byte(VALUE_83, (self.read_byte(VALUE_83) | VALUE_04))
        self.write_byte(REG_FF, VALUE_07)
        self.write_byte(REG_81, VALUE_01)

        self.write_byte(REG_80, VALUE_01)

        # SPADキャリブレーションをトリガーし、完了を待つ
        self.write_byte(REG_94, VALUE_6B)
        self.write_byte(VALUE_83, VALUE_00)
        start = time.time()
        while self.read_byte(VALUE_83) == VALUE_00:
            if time.time() - start > TIMEOUT_LIMIT:
                raise Exception("Timeout")
        self.write_byte(VALUE_83, VALUE_01)

        # SPADカウントとアパーチャ情報を読み取る
        tmp = self.read_byte(REG_92)
        count = tmp & SPAD_COUNT_MASK
        is_aperture = ((tmp & SPAD_APERTURE_BIT) != 0)

        # レジスタをデフォルト値に復元
        self.write_byte(REG_81, VALUE_00)
        self.write_byte(REG_FF, VALUE_06)
        self.write_byte(VALUE_83, (self.read_byte(VALUE_83) & ~VALUE_04))
        self.write_byte(REG_FF, VALUE_01)
        self.write_byte(REG_00, VALUE_01)

        self.write_byte(REG_FF, VALUE_00)
        self.write_byte(REG_80, VALUE_00)

        return count, is_aperture

    # 内部ヘルパー関数 (C++版 calcMacroPeriod の移植)
    def _calc_macro_period(self, vcsel_period_pclks: int) -> int:
        return ((2304 * vcsel_period_pclks * 1655) + 500) // 1000  # [ns]

    def _timeout_microseconds_to_mclks(
            self, timeout_us: int, vcsel_period_pclks: int
    ) -> int:
        # C++版 VL53L0X_calc_timeout_mclks 相当
        macro_period_ns = self._calc_macro_period(vcsel_period_pclks)
        # round up
        return (timeout_us * 1000 + (macro_period_ns // 2)) // macro_period_ns

    def _timeout_mclks_to_microseconds(self, timeout_mclks: int, vcsel_period_pclks: int) -> int:
        macro_period_ns = self._calc_macro_period(vcsel_period_pclks)
        return ((timeout_mclks * macro_period_ns) + 500) // 1000

    def _decode_timeout(self, reg_val: int) -> int:
        # C++: VL53L0X_decode_timeout()
        ls_byte = reg_val & 0xFF
        ms_byte = (reg_val >> 8) & 0xFF
        return ((ls_byte << ms_byte) + 1)

    def _encode_timeout(self, timeout_mclks: int) -> int:
        # C++: VL53L0X_encode_timeout()
        ls_byte = 0
        ms_byte = 0
        if timeout_mclks > 0:
            timeout_mclks -= 1
            while (timeout_mclks & 0xFFFFFF00) > 0:
                timeout_mclks >>= 1
                ms_byte += 1
            ls_byte = timeout_mclks & 0xFF
            return (ms_byte << 8) | ls_byte
        return 0

    def get_measurement_timing_budget(self) -> int:
        """
        現在の測定タイミングバジェットをマイクロ秒単位で返す
        """
        budget_us = 1910  # Start overhead
        enables = self.read_byte(SYSTEM_SEQUENCE_CONFIG)

        pre_range_us: int = 0
        pre_range_mclks: int | None = None

        # pre-range
        if (enables >> 6) & 0x01:
            pre_range_vcsel_period_pclks = self.read_byte(PRE_RANGE_CONFIG_VCSEL_PERIOD)
            pre_range_mclks = self._decode_timeout(
                self.read_word(PRE_RANGE_CONFIG_TIMEOUT_MACROP_HI)
            )
            pre_range_us = self._timeout_mclks_to_microseconds(
                pre_range_mclks, pre_range_vcsel_period_pclks
            )
            budget_us += pre_range_us + 660  # overhead

        # final-range
        if (enables >> 7) & 0x01:
            final_range_vcsel_period_pclks = self.read_byte(FINAL_RANGE_CONFIG_VCSEL_PERIOD)
            final_range_mclks = self._decode_timeout(
                self.read_word(FINAL_RANGE_CONFIG_TIMEOUT_MACROP_HI)
            )

            if (enables >> 6) & 0x01:  # if pre-range enabled, subtract it
                if pre_range_mclks is not None:
                    final_range_mclks -= pre_range_mclks

            final_range_us = self._timeout_mclks_to_microseconds(
                final_range_mclks, final_range_vcsel_period_pclks
            )
            budget_us += final_range_us + 550  # overhead

        return budget_us

    def set_measurement_timing_budget(self, budget_us: int) -> bool:
        """
        測定タイミングバジェットを設定する
        """
        used_budget_us = 1320  # Start overhead
        enables = self.read_byte(SYSTEM_SEQUENCE_CONFIG)

        pre_range_us = 0
        pre_range_mclks = 0
        if (enables >> 6) & 0x01:
            pre_range_vcsel_period_pclks = self.read_byte(PRE_RANGE_CONFIG_VCSEL_PERIOD)
            pre_range_mclks = self._decode_timeout(
                self.read_word(PRE_RANGE_CONFIG_TIMEOUT_MACROP_HI)
            )
            pre_range_us = self._timeout_mclks_to_microseconds(
                pre_range_mclks, pre_range_vcsel_period_pclks
            )
            used_budget_us += pre_range_us + 660

        if (enables >> 7) & 0x01:
            final_range_us = budget_us - used_budget_us - 550
            if final_range_us <= 0:
                raise ValueError("Requested timing budget too small")

            final_range_vcsel_period_pclks = self.read_byte(FINAL_RANGE_CONFIG_VCSEL_PERIOD)
            # ★ ここを μs→mclks に修正
            final_range_mclks = self._timeout_microseconds_to_mclks(
                final_range_us, final_range_vcsel_period_pclks
            )

            if (enables >> 6) & 0x01:
                final_range_mclks += pre_range_mclks

            self.write_word(
                FINAL_RANGE_CONFIG_TIMEOUT_MACROP_HI,
                self._encode_timeout(final_range_mclks),
            )
            return True
        return False

    def perform_single_ref_calibration(self, vhv_init_byte: int) -> None:
        self.write_byte(SYSRANGE_START, VALUE_01 | vhv_init_byte)
        start = time.time()
        # 2秒上限で待つ（環境により1秒だと落ちる場合がある）
        while (self.read_byte(RESULT_INTERRUPT_STATUS) & INTERRUPT_STATUS_MASK) == VALUE_00:
            if time.time() - start > 2.0:
                raise Exception("Timeout during ref calibration")
        self.write_byte(SYSTEM_INTERRUPT_CLEAR, VALUE_01)
        self.write_byte(SYSRANGE_START, VALUE_00)

    def get_range(self) -> int:
        """
        単一の測距測定を実行し、結果をmm単位で返します。
        """
        # stop_variable の復元シーケンス
        self.write_byte(REG_80, VALUE_01)
        self.write_byte(REG_FF, VALUE_01)
        self.write_byte(REG_00, VALUE_00)
        self.write_byte(REG_91, self.stop_variable)
        self.write_byte(REG_00, VALUE_01)
        self.write_byte(REG_FF, VALUE_00)
        self.write_byte(REG_80, VALUE_00)

        # 測定開始（シングルショット）
        self.write_byte(SYSRANGE_START, VALUE_01)

        # 予算に応じた実時間で待つ（最低1.0s）
        budget_s = getattr(self, "measurement_timing_budget_us", 33000) / 1_000_000.0
        timeout_s = max(1.0, budget_s + 0.1)

        # 割り込みステータス待ち（データ準備完了）
        start = time.time()
        while (self.read_byte(RESULT_INTERRUPT_STATUS) & INTERRUPT_STATUS_MASK) == VALUE_00:
            if time.time() - start > timeout_s:
                raise Exception("Timeout waiting for measurement ready")

        # 結果読み出し
        range_mm = self.read_word(RESULT_RANGE_STATUS + VALUE_0A)  # 0x14 + 0x0A

        # 割り込みクリア
        self.write_byte(SYSTEM_INTERRUPT_CLEAR, VALUE_01)

        return range_mm - self.offset_mm

    def set_offset(self, offset_mm: int) -> None:
        """
        測定値のオフセット(mm)を設定します。

        Args:
            offset_mm (int): オフセット値 (mm)
        """
        self.offset_mm = offset_mm

    def get_ranges(self, num_samples: int) -> np.ndarray:
        """
        指定されたサンプル数の連続測距を実行し、結果をNumPy配列で返します。
        """
        samples = np.empty(num_samples, dtype=np.uint16)
        for i in range(num_samples):
            samples[i] = self.get_range()
        return samples

    def calibrate(self, target_distance_mm: int, num_samples: int) -> int:
        """
        指定されたターゲット距離でキャリブレーションを行い、オフセット値を計算します。

        Args:
            target_distance_mm (int): ターゲットまでの実際の距離 (mm)
            num_samples (int): 測定回数

        Returns:
            int: 計算されたオフセット値 (mm)
        """
        self.__log.debug(
            "Calibrating with target_distance_mm=%s, num_samples=%s",
            target_distance_mm, num_samples
        )

        # オフセットを一時的に0にして測定
        current_offset = self.offset_mm
        self.set_offset(0)

        samples = self.get_ranges(num_samples)
        measured_distance = int(np.mean(samples))

        # オフセットを元に戻す
        self.set_offset(current_offset)

        offset = measured_distance - target_distance_mm
        self.__log.debug("measured_distance=%s, offset=%s", measured_distance, offset)

        return offset

    def close(self) -> None:
        """
        I2C接続を閉じます。
        """
        self.pi.i2c_close(self.handle)

    def read_byte(self, register: int) -> int:
        """
        レジスタから1バイト読み取ります。
        """
        value = self.pi.i2c_read_byte_data(self.handle, register)
        # self.__log.debug("レジスタ %s からバイトを読み取り: %s", hex(register), hex(value))
        return int(value)

    def write_byte(self, register: int, value: int) -> None:
        """
        レジスタに1バイト書き込みます。
        """
        # self.__log.debug("レジスタ %s にバイトを書き込み: %s", hex(register), hex(value))
        self.pi.i2c_write_byte_data(self.handle, register, value)

    def read_word(self, register: int) -> int:
        """
        レジスタから1ワード読み取ります。
        """
        val = self.pi.i2c_read_word_data(self.handle, register)
        # pigpioはリトルエンディアンで読み取りますが、VL53L0Xはビッグエンディアンです。
        value = ((val & 0xFF) << 8) | (val >> 8)
        # self.__log.debug("レジスタ %s からワードを読み取り: %s", hex(register), hex(value))
        return int(value)

    def write_word(self, register: int, value: int) -> None:
        """
        レジスタに1ワード書き込みます。
        """
        # pigpioはリトルエンディアンで書き込みますが、VL53L0Xはビッグエンディアンです。
        value = ((value & 0xFF) << 8) | (value >> 8)
        self.pi.i2c_write_word_data(self.handle, register, value)

    def read_block(self, register: int, count: int) -> list[int]:
        """
        レジスタからデータのブロックを読み取ります。
        """
        _, data = self.pi.i2c_read_i2c_block_data(
            self.handle, register, count
        )
        if isinstance(data, bytearray):
            return list(data)
        return []

    def write_block(self, register: int, data: list[int]) -> None:
        """
        レジスタにデータのブロックを書き込みます。
        """
        self.pi.i2c_write_i2c_block_data(self.handle, register, data)
