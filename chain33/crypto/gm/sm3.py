from gmssl import sm3


class SM3Util(object):
    # SM3哈希函数
    def hash(self, msg):
        if isinstance(msg, (bytes, bytearray)):
            in_msg = list(msg)

        msg = in_msg[0:]
        return sm3.sm3_hash(msg)
