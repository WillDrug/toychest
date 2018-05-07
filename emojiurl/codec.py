import pickle
import sys
pickle.dump('test', open('test.pcl', 'wb+'))
emojis = pickle.load(open('emojis.pcl', 'rb+'))

def base_encode(dec, base=512):
    if base <= 1:
        raise Exception('no.')
    starting_register = 0
    while dec - base**starting_register >= 0:
        starting_register += 1
    # got starting register
    encoded = list()
    decode = dec
    for register in range(0, starting_register)[::-1]:
        chunk = 0
        while decode - base**register >= 0:
            decode = decode - base**register
            chunk += 1
        encoded.append(chunk)
    if encoded.__len__()==0:
        encoded.append(0)
    return encoded

def base_decode(based, base=512):
    result = 0
    register = 0
    for a in based[::-1]:
        result += a*(base**register)
        register += 1
    return result

base = 512
padding_character = emojis[512]
padding_code = 512
code_lengths = emojis[840:851]

def to_emoji(input_string):
    return_list = list()
    maxlen = 0
    for ch in input_string:
        encoded = base_encode(ord(ch), base=base)
        return_list.append(encoded)
        if encoded.__len__() > maxlen:
            maxlen = encoded.__len__()
    #print('to:', return_list)
    return_st = list()
    return_st.append(code_lengths[maxlen-1])
    for codes in return_list:
        strcodes = [emojis[q] for q in codes]
        return_st.append(''.join(strcodes).rjust(maxlen, padding_character))
    return ''.join(return_st)

def from_emoji(input_emoji):
    padlen = code_lengths.index(input_emoji[0])+1
    input_emoji = input_emoji[1:]
    if divmod(input_emoji.__len__(), padlen)[1] != 0:
        raise Exception('Invalid code length character provided') # TODO: specific
    it = input_emoji.__iter__()
    decoded = list()
    for code in range(int(input_emoji.__len__()/padlen)):
        decode_point = list()
        for iter_num in range(padlen):
            code = it.__next__()
            if code != padding_character:
                decode_point.append(emojis.index(code))
        #print('from:', decode_point)
        decoded.append(base_decode(decode_point, base=base))
    decoded = [chr(q) for q in decoded]
    return ''.join(decoded)

if __name__ == '__main__':
    input_string = ' '.join(sys.argv[1:])  # [ord(str(q)) for q in ' '.join(sys.argv[1:])]
    encoded = to_emoji(input_string)
    print(encoded)
    decoded = from_emoji(encoded)
    print(decoded)
