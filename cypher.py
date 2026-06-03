import string

digits = "0123456789"
ru_lower = "абвгдежзийклмнопрстуфхцчшщъыьэюя"
ru_upper = "АБВГДЕЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ"
en_lower = string.ascii_lowercase
en_upper = string.ascii_uppercase
punct = string.punctuation
space = " "

CIRCLE = digits + ru_lower + ru_upper + en_lower + en_upper + punct + space

def encrypt(text, sid=70225220):
    shift = sid % 11
    result = ""
    for char in text:
        if char in CIRCLE:
            idx = CIRCLE.find(char)
            new_idx = (idx + shift) % len(CIRCLE)
            result += CIRCLE[new_idx]
        else:
            result += char
    return result

def decrypt(text, sid=70225220):
    shift = sid % 11
    result = ""
    for char in text:
        if char in CIRCLE:
            idx = CIRCLE.find(char)
            new_idx = (idx - shift) % len(CIRCLE)
            result += CIRCLE[new_idx]
        else:
            result += char
    return result

if __name__ == "__main__":
    # Тестирование модуля
    test_cases = ["Привет!", "Test 123", "Secret-Message."]
    for case in test_cases:
        enc = encrypt(case)
        dec = decrypt(enc)
        print(f"Orig: {case} -> Enc: {enc} -> Dec: {dec}")
