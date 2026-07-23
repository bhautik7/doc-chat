from passlib.context import CryptContext

pwd_context=CryptContext(schemes=["bcrypt"],deprecated="auto")

def hash_password(password:str)->str:
    return pwd_context.hash(password)

def verify_password(plain_password:str,hashed_password:str)->bool:
    return pwd_context.verify(plain_password,hashed_password)



# Why bcrypt specifically, not SHA-256 or MD5? . SHA-256/MD5 are fast hash functions — designed for speed, which is exactly wrong for passwords. If an attacker steals your password hashes, a fast hash lets them try billions of guesses per second on commodity hardware. Bcrypt is deliberately slow and has a work factor (cost parameter) you can tune upward as hardware gets faster, so it stays expensive to brute-force even years later. It also automatically salts each hash, which prevents rainbow-table attacks (precomputed hash lookup tables).

# Why never store the plaintext password anywhere, even temporarily in logs? Because your logging system, your DB backups, your error-tracking tool (Sentry, etc.) all become attack surfaces the moment plaintext passwords touch them. Hash immediately at the boundary.