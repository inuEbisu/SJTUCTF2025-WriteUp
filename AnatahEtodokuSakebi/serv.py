from Crypto.Cipher import AES
import copy

key = b"UZhyYC6oiNH2IDZE"
iv = b"sjtuctf20250oops"

class AESCryptService:
    key = b"UZhyYC6oiNH2IDZE"
    iv = b"sjtuctf20250oops"
    BLOC = 16

    def getw(self, remained: bytes, last_enc_tail: bytes, data_blocks: list[bytes]):
        assert len(last_enc_tail) + len(remained) == self.BLOC

        original_block = remained.ljust(16, b"\x00") # I don't know why. I just brute force it
        cbc = AES.new(self.key, AES.MODE_CBC, self.iv)
        for block in data_blocks:
            cbc.encrypt(block) # Recover the state
        return cbc.encrypt(original_block)

    def decrypt(self, data: str):
        data = bytes.fromhex(data)
        pad = 0
        key = self.key
        iv = self.iv
        BLOC = self.BLOC
        if (len(data) % BLOC) > 0:
            pad = BLOC - (len(data) % BLOC)
            # Step 1: ECB Decrypt & Append
            secondToLast = data[len(data) - 2 * BLOC + pad : len(data) - BLOC + pad]
            dec = AES.new(key, AES.MODE_ECB).decrypt(secondToLast)
            data += bytes(dec[len(dec) - pad : len(dec)])
            # Step 2: Swap
            data = (
                data[: len(data) - 2 * BLOC]
                + data[len(data) - BLOC :]
                + data[len(data) - 2 * BLOC : len(data) - BLOC]
            )

        # Step 3: CBC Decrypt
        index = 0
        decd = b""
        cipher = AES.new(key, AES.MODE_CBC, iv)
        while index < len(data):
            decd += cipher.decrypt(data[index : index + BLOC])
            index += BLOC

        # Step 4: Trash
        if pad != 0:
            decd = decd[: len(decd) - pad]
        return decd.decode("utf-8")
    
    def encrypt(self, data: str):
        # Prologue
        data = data.encode('utf-8')
        key = self.key
        iv = self.iv
        BLOC = self.BLOC

        # Step 1: Calc Padding
        pad = 0
        if len(data) % self.BLOC > 0:
            pad = self.BLOC - (len(data) % self.BLOC)
            remained = data[len(data) - BLOC + pad:]
            
        # Step 2: CBC For complete BLOC
        index = 0
        enc = b""
        blocks = []
        cipher = AES.new(key, AES.MODE_CBC, iv)
        while index + BLOC <= len(data):
            t_block = data[index : index + BLOC]
            block = cipher.encrypt(data[index : index + BLOC])
            enc += block
            blocks.append(t_block)
            index += BLOC
     
        # Step 3: ECB
        if pad != 0:
            last_enc_tail = enc[len(enc) - pad:]
            w = self.getw(remained, last_enc_tail, blocks)
            enc = (
                enc[: len(enc) - BLOC]
                + w
                + enc[len(enc) - BLOC : len(enc) - pad]
            )

        # Finale
        return enc.hex()


if __name__ == "__main__":
    aes = AESCryptService()
    text = "0123456789ABCDEF0123456789ABCDEF0123456789ABCDEF01234567"
    print(text)
    cipher = aes.encrypt(text)
    print(cipher)
    text = aes.decrypt(cipher)
    print(text)