import time
import binascii
from boofuzz import *

HOST = '192.168.1.17'
PORT = 2045
BUFSIZ = 1024
ADDR = (HOST, PORT)
FUNCTION = "\x2f"


def login(target, fuzz_data_logger, session, sock):
    payload = "bbbb000000890100000004000000060000000000000c060700000004" \
              "00000000060c000000040000000009250000000400000000092600000004" \
              "000000000927000000040000000009280000000400000000092e00000004" \
              "0000000005dc000000040000000004770000000400000000047800000004" \
              "00000000270f0000000402030922270e0000000402030921cd"
    sock.send(binascii.a2b_hex(payload))
    time.sleep(0.1)


def main():
    session = Session(
        target=Target(
            connection=SocketConnection(HOST, PORT, proto='tcp')),
        pre_send_callbacks=[login])

    s_initialize("codesys")
    with s_block("header"):
        s_static("\xbb\xbb")
        s_size("command", length=4, fuzzable=False, endian=BIG_ENDIAN)
    with s_block("command"):
        s_static(FUNCTION)

        if FUNCTION == "\x1c":
            # s_SRV:_RTS_DEFINE_TRACE
            s_byte(0x0)
            s_byte(0x1)
            s_word(0x0, endian=BIG_ENDIAN)
            s_word(0x0, endian=BIG_ENDIAN)
            s_word(0x0, endian=BIG_ENDIAN)
            s_word(0x0, endian=BIG_ENDIAN)
            s_dword(0xffffffff, endian=BIG_ENDIAN)
            s_dword(0x0, endian=BIG_ENDIAN)

        if FUNCTION == "\x2d":
            # s_SRV:_RTS_DEFINE_CONFIG
            '''
            s_byte(0x436f6d6d, endian=BIG_ENDIAN)
            s_byte(0x0)
            for _ in range(8):
                s_byte(0x0, fuzzable=False)
            s_word(0x0000, endian=BIG_ENDIAN)
            '''

            s_byte(0x0)
            for _ in range(11):
                s_byte(0x0, fuzzable=False)
            s_word(0x0)
            for _ in range(10):
                s_byte(0x0, fuzzable=False)
            s_byte(0x43)
            s_byte(0x41)
            s_byte(0x4e)
            s_byte(0x0)
            for _ in range(8):
                s_byte(0x0, fuzzable=False)
            s_word(0x0)

        if FUNCTION == "\x31":
            # s_SRV:_RTS_FILE_READ_START
            # s_byte(0x0)                         # vul 1
            s_word(0x0, endian=BIG_ENDIAN)
            s_byte(0x2)                         # vul 2
            s_word(0x3100, endian=BIG_ENDIAN)

        if FUNCTION == "\x37":
            # s_SRV:_RTS_DOWNLOAD_TASKCFG
            s_byte(0x0)     # vul
            s_byte(0x0)
            s_byte(0x0)

        if FUNCTION == "\x3e":
            # s_SRV:_RTS_DOWNLOAD_IODESC
            s_byte(0x0)     # vul
            s_byte(0x0)
            s_byte(0x0)

        if FUNCTION == "\x40":
            # s_SRV:_RTS_DOWNLOAD_PRJINFO
            s_byte(0x0)
            s_dword(0x1, endian=BIG_ENDIAN)
            s_byte(0x0)
            s_byte(0x0)

        if FUNCTION == "\x41":
            # s_SRV:_RTS_CHECKBOOTPRJ       # only err led
            s_byte(0x0)
            s_word(0x0, endian=BIG_ENDIAN)
            s_word(0x0, endian=BIG_ENDIAN)
            s_byte(0x0)

        if FUNCTION == "\x42":
            # s_SRV:_RTS_CHECKTARGETID
            s_byte(0x0)
            s_dword(0x1, endian=BIG_ENDIAN)
            s_byte(0x0)
            s_byte(0x0)

        if FUNCTION == "\x43":
            # s_***_RtsSrv::RTS_FILE_TRANSFER_DO_00218ca0
            s_static("\x44\x4f\x57\x4e\x4c\x4f\x41\x44\x2e\x53\x44\x42")
            s_dword(0x0, endian=BIG_ENDIAN)
            s_byte(0x4)
            s_word(0x0, endian=BIG_ENDIAN)
            s_word(0xd8, endian=BIG_ENDIAN)

        if FUNCTION == "\x4b":
            # s_SRV:_RTS_CHECKTARGETID
            s_byte(0x0)
            s_word(0x0)
            s_word(0x0)

        if FUNCTION == "\x50":
            sub_function = "\x20"
            s_static(sub_function)

            # s_SRVSub:_RTS_READ_VAR
            # s_SRVSub:_RTS_DEFINE_VARLIST
            if sub_function == "\x05" or sub_function == "\x14":
                s_dword(0x1, endian=BIG_ENDIAN, fuzzable=False)
                s_word(0x0, endian=BIG_ENDIAN)
                s_word(0x0, endian=BIG_ENDIAN)
                s_word(0x7d01, endian=BIG_ENDIAN)
                s_word(0x0, endian=BIG_ENDIAN)
                s_word(0x0, endian=BIG_ENDIAN)

            # s_SRVSub:_RTS_FORCE_VARIABLES
            # s_SRVSub:_RTS_WRITE_VAR
            if sub_function == "\x06" or sub_function == "\x20":
                s_dword(0x1, endian=BIG_ENDIAN, fuzzable=False)
                s_word(0x0, endian=BIG_ENDIAN)
                s_word(0x0, endian=BIG_ENDIAN)
                s_word(0x7d08, endian=BIG_ENDIAN)
                s_word(0x0, endian=BIG_ENDIAN)
                s_word(0x0, endian=BIG_ENDIAN)
                s_byte(0x1)

        if FUNCTION == "\x51":
            sub_function = "\x0b"
            s_static(sub_function)

            # s_SRVSub:_RTS_STEP_OUT_002188e8
            if sub_function == "\x0b":
                s_word(0x0001, endian=BIG_ENDIAN)
                s_word(0x0000, endian=BIG_ENDIAN)
                s_dword(0x0040ffff, endian=BIG_ENDIAN)
                s_word(0xffff, endian=BIG_ENDIAN)
                s_dword(0x1ed800bf, endian=BIG_ENDIAN)

            # s_SRVSub:_RTS_BP_SET
            if sub_function == "\x0c":              # only err led
                s_word(0x00fd, endian=BIG_ENDIAN)
                s_word(0x0000, endian=BIG_ENDIAN)
                s_dword(0x0040ffff, endian=BIG_ENDIAN)
                s_dword(0xffffffff, endian=BIG_ENDIAN, fuzzable=False)
                s_word(0x1ed8, endian=BIG_ENDIAN)
                s_word(0x00bf, endian=BIG_ENDIAN)

        if FUNCTION == "\x53":
            s_byte(0x0)
            s_byte(0x25)
            s_byte(0x49)
            s_byte(0x57)
            s_byte(0x0)
            s_dword(0x0)

        if FUNCTION == "\x9c":
            sub_function = "\x02"
            s_static(sub_function)

            if sub_function == "\x00" or sub_function == "\x03":
                s_word(0x0)
                s_word(0x0)

            elif sub_function == "\x01":
                s_byte(0x0)
                s_byte(0x0)
                s_word(0x0)

            else:
                s_byte(0x0)
                s_byte(0x0)
                s_word(0x0)
                s_word(0x0)
                for i in range(10):
                    s_dword(0x0)

    session.connect(s_get("codesys"))
    session.fuzz()


if __name__ == "__main__":
    main()
