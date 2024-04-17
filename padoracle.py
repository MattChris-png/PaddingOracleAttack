import socket
import re

# create a socket object
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

#type connection information.
#s.connect(("ip", port))

decryption = []
block_size = 16


def discover_message_len(initial_message="-e "):
    s.send(initial_message.encode())
    base_response = s.recv(1024).decode()
    initial_enc_data = base_response.split('\\n')[1].replace(' ', '')
    initial_enc_len = len(initial_enc_data)/2

    message_blocks = int((initial_enc_len/16)-2)
    

    i = 0  
    message = initial_message
    
    while True:
        message += '11'
        s.send(message.encode())
        response = s.recv(1024).decode()
        current_enc_data = response.split('\\n')[1].replace(' ', '')
        current_enc_len = len(current_enc_data)/2
        if current_enc_len != initial_enc_len:
        
            if(i+1 == 16):
                return (message_blocks)*16, message_blocks
            return (block_size-(i+1))+(message_blocks*16), message_blocks
        i += 1


# Call the function
message_len, num_blocks = discover_message_len()
print(f"message length = {message_len}")
num_blocks = int(message_len /16)
if(num_blocks == 0):
    num_blocks+=1
print(num_blocks)

if not (message_len % 16 == 0):
    prefix = '00' * (block_size-message_len)
i= 2
if(num_blocks == 1):
    i=1
j = 0
num_prefix = 0
true_message=[]
message_string = ''
for block in range(3):
    prefix = ''    
    for position in range(15, -1, -1):   
        
        message = '-e ' + prefix
        s.send(message.encode())
        response = s.recv(1024).decode('utf-8')
        #print(response)
        cipher = response.split("\\n")[1]
        cipher = cipher.replace(' ', '')
        iv = response.split('\'')[3]



        for random_bytes in range(256):
            random_block = '0'*30 + format(random_bytes, '02x')
            cipher_blocks = [cipher[i:i+32] for i in range(0, len(cipher), 32)]
            
            new_cipher = random_block + cipher_blocks[i]
            message = '-v ' + new_cipher +' '+  iv 
            s.send(message.encode())
            response = s.recv(1024).decode()

            if "Tag" in response:

                #print(random_bytes)
                if(i == 0):
                    last_byte = int(iv[-2] + iv[-1], 16)
                else:
                    orig_cipher_block = cipher_blocks[i-1]
                    #print(orig_cipher_block)
                    last_byte = int(orig_cipher_block[-2] + orig_cipher_block[-1], 16)
                true_message.append(random_bytes ^ last_byte)
                #message_string = chr(random_bytes) + message_string
                break
        prefix+='00'
    i-=1
true_message.reverse()
message = bytes(true_message)
print(message)
print(num_blocks)
