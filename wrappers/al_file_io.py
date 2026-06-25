import struct

class ALFileIO:
    @staticmethod
    def save(filename: str, was_compressed: bool, tokens_with_widths: list[tuple[int, int]], max_bits: int):
        if not filename.endswith('.alc'):
            filename += '.alc'
            
        with open(filename, 'wb') as f:
            # Rigid Head
            header = (1 << 7 if was_compressed else 0) | (max_bits & 0x7F)
            f.write(struct.pack('B', header))
            
            bit_buffer = 0
            bit_count = 0
            
            for token, width in tokens_with_widths:
                bit_buffer = (bit_buffer << width) | token
                bit_count += width
                
                while bit_count >= 8:
                    bit_count -= 8
                    byte_to_write = (bit_buffer >> bit_count) & 0xFF
                    f.write(struct.pack('B', byte_to_write))
            
            if bit_count > 0:
                byte_to_write = (bit_buffer << (8 - bit_count)) & 0xFF
                f.write(struct.pack('B', byte_to_write))

    @staticmethod
    def load(filename: str) -> tuple[bool, list[tuple[int, int]], int]:
        with open(filename, 'rb') as f:
            header_byte = struct.unpack('B', f.read(1))[0]
            was_compressed = bool(header_byte & (1 << 7))
            max_bits = header_byte & 0x7F
            
            tokens_with_widths = []
            bit_buffer = 0
            bit_count = 0
            
            # Reconstruct the dynamic bit-width state on-the-fly during read
            dict_size = 256
            max_dict_size = 1 << max_bits
            
            while True:
                byte_data = f.read(1)
                if not byte_data:
                    break
                    
                byte_val = struct.unpack('B', byte_data)[0]
                bit_buffer = (bit_buffer << 8) | byte_val
                bit_count += 8
                
                while True:
                    # Determine how many bits the NEXT token was encoded with
                    current_width = max(8, (dict_size - 1).bit_length()) if was_compressed else 8
                    
                    if bit_count < current_width:
                        break # Need more bytes from disk
                        
                    bit_count -= current_width
                    token = (bit_buffer >> bit_count) & ((1 << current_width) - 1)
                    tokens_with_widths.append((token, current_width))
                    
                    if was_compressed and dict_size < max_dict_size:
                        dict_size += 1
                        
            return was_compressed, tokens_with_widths, max_bits