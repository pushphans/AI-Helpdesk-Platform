from pwdlib import PasswordHash

password_hasher = PasswordHash.recommended()


def hash_passwrord(password : str):
    return password_hasher.hash(password=password)



def verify_hashed_password(hashed_password : str, password : str):
    return password_hasher.verify(password=password, hash=hashed_password)