# aim2numpy/extract.py
# Import necessary modules
import numpy as np
import struct
import matplotlib.pyplot as plt


class AimFile:
    def __init__(self, filename):
        self.filename = filename
        self.block_list = []
        self.dimensions = []
        self.buffer_type = None
        self.aim_type = None
        self.offset = None
        self.version = None

    def read_image_info(self):
        with open(self.filename, 'rb') as f:
            self.read_block_list(f)
            self.read_header(f)
            self.read_processing_log(f)            

    def read_block_list(self, f):
        # Read in pre-header
        buffer = f.read(24)

        # Check if the first 2 bytes = version030_string
        version030_string = b'Version030'
        file_64bit_flag = False
        head_mb_size = 0
        memory_offset = 0

        if buffer[:len(version030_string)] == version030_string:
            file_64bit_flag = True
            head_mb_size = struct.unpack('<Q', buffer[16:24])[0]
            memory_offset = 16
        else:
            head_mb_size = struct.unpack('<I', buffer[:4])[0]
            if head_mb_size > 20:
                raise Exception("File neither 32bit version nor AIM_V030.")
            memory_offset = 0

        memory_offset += head_mb_size

        # Number of blocks
        if file_64bit_flag:
            nr_mb = head_mb_size // 8 - 1  # First entry was pre-header size.
        else:
            nr_mb = head_mb_size // 4 - 1

        self.block_list = [{'offset': 0, 'size': 0} for _ in range(nr_mb)]

        # Read memory block list
        if file_64bit_flag:
            f.seek(16)
            buffer = f.read(head_mb_size)

        for i in range(nr_mb):
            self.block_list[i]['offset'] = memory_offset
            if file_64bit_flag:
                self.block_list[i]['size'] = struct.unpack('<Q', buffer[(i + 1) * 8:(i + 2) * 8])[0]
            else:
                self.block_list[i]['size'] = struct.unpack('<I', buffer[(i + 1) * 4:(i + 2) * 4])[0]
            memory_offset += self.block_list[i]['size']

    def read_header(self, f):
        if not self.block_list:
            raise ValueError("Block list is empty")

        block_size = self.block_list[0]['size']
        block_offset = self.block_list[0]['offset']

        if block_size == 140:
            f.seek(block_offset)
            header_data = f.read(140)
            fd = struct.unpack('<15i 20f', header_data)

            self.version = 'AIMFILE_VERSION_140'
            self.id = fd[0]
            self.reference = fd[1]
            self.aim_type = fd[0]
            if self.aim_type == 16:
                self.aim_type='AIMFILE_TYPE_D1Tshort'
            self.position = fd[6:9]
            self.dimensions = fd[9:12]
            self.offset = fd[12:15]
            self.supdim = fd[12:15]
            self.suppos = fd[15:18]
            self.subdim = fd[18:21]
            self.testoff = fd[21:24]
            
            # Extract element size using VMS conversion
            element_size_x = self.vms_to_native(header_data[108:112])
            element_size_y = self.vms_to_native(header_data[112:116])
            element_size_z = self.vms_to_native(header_data[116:120])
            self.element_size = np.array([element_size_x, element_size_y, element_size_z])
            
            self.assoc_id = fd[27]
            self.assoc_nr = fd[28]
            self.assoc_size = fd[29]
            self.assoc_type = fd[30]
            self.byte_offset = self.block_list[2]['offset']

        # Additional conditions for other header types (e.g., Version 30, 20, 11, 10)

        self.buffer_type = self.get_transfer_buffer_type(self.aim_type)

    def read_processing_log(self, f):
        if len(self.block_list) > 1 and self.block_list[1]['size'] >= 2:
            f.seek(self.block_list[1]['offset'])
            buffer = f.read(self.block_list[1]['size'])
            self.processing_log = buffer.decode('utf-8')

    def get_transfer_buffer_type(self, storage_type):
        if storage_type in ['AIMFILE_TYPE_D1Tchar', 'AIMFILE_TYPE_D1TbinCmp', 'AIMFILE_TYPE_D1TcharCmp', 'AIMFILE_TYPE_D3Tbit8']:
            return 'AIMFILE_TYPE_CHAR'
        elif storage_type == 'AIMFILE_TYPE_D1Tshort':
            return 'AIMFILE_TYPE_SHORT'
        elif storage_type == 'AIMFILE_TYPE_D1Tfloat':
            return 'AIMFILE_TYPE_FLOAT'
        else:
            raise ValueError("Unsupported AIM data type.")

    def read_any_data(self, buffer_number, dtype):
        with open(self.filename, 'rb') as f:
            block = self.block_list[buffer_number]
            f.seek(block['offset'])
            buffer = f.read(block['size'])
            #print(f"Raw data (first 100 bytes): {buffer[:100]}")  # Debugging line
            data = self.decompress(buffer, dtype)
            return data

    def decompress(self, buffer, dtype):
        if self.aim_type in ['AIMFILE_TYPE_D1TcharCmp', 'AIMFILE_TYPE_D1TbinCmp']:
            dim_no_off = np.array(self.dimensions) - np.array(self.offset) * 2
            temp = np.zeros(np.prod(dim_no_off), dtype=np.uint8)
            self.decompress_no_offset(temp, buffer, self.aim_type, dim_no_off)
            return self.restore_offset(temp, self.dimensions, self.offset)
        else:
            return self.decompress_no_offset(buffer, dtype)

    def decompress_no_offset(self, buffer, dtype):
        #print(f"aim_type: {self.aim_type}")  # Debugging line
        if self.aim_type == 'AIMFILE_TYPE_D3Tbit8':
            # Implement the decompression logic for AIMFILE_TYPE_D3Tbit8
            pass
        elif self.aim_type == 'AIMFILE_TYPE_D1TcharCmp':
            # Implement the decompression logic for AIMFILE_TYPE_D1TcharCmp
            pass
        elif self.aim_type == 'AIMFILE_TYPE_D1TbinCmp':
            # Implement the decompression logic for AIMFILE_TYPE_D1TbinCmp
            pass
        elif self.aim_type == 'AIMFILE_TYPE_D1Tchar':
            return np.frombuffer(buffer, dtype=np.uint8)
        elif self.aim_type == 'AIMFILE_TYPE_D1Tshort':
            return np.frombuffer(buffer, dtype=np.int16)
        elif self.aim_type == 'AIMFILE_TYPE_D1Tfloat':
            return np.frombuffer(buffer, dtype=np.float32)
        else:
            raise ValueError("Unrecognized AIM data type.")

    def restore_offset(self, temp, dim, off):
        out = np.zeros(np.prod(dim), dtype=np.uint8)
        idx = 0
        for k in range(off[2], dim[2] - off[2]):
            for j in range(off[1], dim[1] - off[1]):
                for i in range(off[0], dim[0] - off[0]):
                    out[(k * dim[1] + j) * dim[0] + i] = temp[idx]
                    idx += 1
        return out

    def read_image_data(self, dtype):
        assert len(self.block_list) >= 3
        size = np.prod(self.dimensions)
        data = self.read_any_data(2, dtype)
        #print(f"Read data shape (before reshape): {data.shape}")  # Debugging line
        return data.reshape(self.dimensions[::-1])

    def vms_to_native(self, float_bytes):
        """
        Convert VMS floating-point format to native floating-point format.
        
        Parameters:
        float_bytes (bytes): 4 bytes representing a VMS float
        
        Returns:
        float: The converted native float value
        """
        # Swap byte pairs as in the C++ code
        swapped_bytes = bytes([
            float_bytes[2],  # byte 0 becomes byte 2
            float_bytes[3],  # byte 1 becomes byte 3
            float_bytes[0],  # byte 2 becomes byte 0
            float_bytes[1]   # byte 3 becomes byte 1
        ])
        
        # Convert the swapped bytes to a float
        value = struct.unpack('<f', swapped_bytes)[0]
        
        # Divide by 4.0 as in the C++ code
        return value / 4.0


def extract(filename):
    """
    Extracts data from an AIM file and returns it as a numpy array.

    Parameters:
    filename (str): The path to the AIM file.

    Returns:
    np.ndarray: The extracted data as a numpy array.
    """
    aim_file = AimFile(filename)
    aim_file.read_image_info()
    image_data = aim_file.read_image_data(np.int16)  # Change dtype as needed
    #print(f"Image data shape (after reshape): {image_data.shape}")

    return image_data
    


    """
    # Initial slice index
    slice_index = 400

    # Function to update the plot
    def update_plot():
        plt.imshow(image_data[:, :, slice_index], cmap='gray')
        plt.title(f'Slice at index {slice_index}')
        plt.draw()

    # Function to handle key press events
    def on_key(event):
        global slice_index
        if event.key == 'up':
            slice_index = min(slice_index + 1, image_data.shape[2] - 1)
        elif event.key == 'down':
            slice_index = max(slice_index - 1, 0)
        update_plot()

    # Create the initial plot
    fig, ax = plt.subplots()
    update_plot()

    # Connect the key press event to the handler
    fig.canvas.mpl_connect('key_press_event', on_key)

    plt.show()
    """
    

