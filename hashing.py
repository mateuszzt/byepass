import hashlib
import bcrypt
import os


def generate_salt():
    return os.urandom(16)


def hash_sha256(password, salt):
    return hashlib.sha256(salt + password.encode()).hexdigest()


def hash_sha1(password, salt):
    return hashlib.sha1(salt + password.encode()).hexdigest()


def hash_bcrypt(password):
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt())


def verify_sha256(password, salt, hashed):
    return hash_sha256(password, salt) == hashed


def verify_sha1(password, salt, hashed):
    return hash_sha1(password, salt) == hashed


def verify_bcrypt(password, hashed):
    return bcrypt.checkpw(password.encode(), hashed.encode())