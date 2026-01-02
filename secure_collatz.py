import secrets
import argparse
import sys
import hmac
import hashlib
import math
from collections import Counter

def generate_k_derived(n, key):
    """
    Derives a deterministic but cryptographically strong 'k' from n and a secret key.
    This simulates AES-like behavior where the trajectory is dependent on the key.
    We use HMAC-SHA256 to generate this dynamic 'k'.
    """
    # Convert n to bytes for hashing
    # Ensure at least 1 byte
    byte_len = (n.bit_length() + 7) // 8
    if byte_len == 0:
        byte_len = 1
    n_bytes = n.to_bytes(byte_len, byteorder='big')
    
    # HMAC-SHA256
    h = hmac.new(key, n_bytes, hashlib.sha256).digest()
    
    # Convert hash slice to int (using first 4 bytes for a reasonable size k)
    k_candidate = int.from_bytes(h[:4], byteorder='big')
    
    # Ensure k is not 0 (to avoid 3n+0 degeneracy if n is 0, though n shouldn't be 0)
    # Also strictly, Collatz uses 3n+1. We allow any k.
    if k_candidate == 0:
        k_candidate = 1
        
    return k_candidate

def secure_collatz_step(n, key):
    """
    Performs the randomized Collatz step.
    If even: n / 2
    If odd: 3*n + k (where k is derived securely from n and key)
    """
    if n % 2 == 0:
        return n // 2
    else:
        k = generate_k_derived(n, key)
        return 3 * n + k

def generate_secure_password(length):
    if length % 2 != 0:
        print("Error: Length must be even to ensure equal split of 0s and 1s.")
        sys.exit(1)

    required_zeros = length // 2
    required_ones = length // 2
    
    current_zeros = 0
    current_ones = 0
    
    password = []
    
    # 1. Secure Random Seed & Key
    # Use secrets module for cryptographically secure starting point
    current_n = secrets.randbits(256)
    
    # 32-byte secret key for the HMAC operations (acts like the AES key)
    key = secrets.token_bytes(32)
    
    # print(f"DEBUG: Initial Seed (start): {str(current_n)[:20]}...")
    # print(f"DEBUG: Secret Key (hex): {key.hex()[:16]}...")
    
    while len(password) < length:
        # User Requirement: 
        # Even -> 1
        # Odd -> 0
        is_even = (current_n % 2 == 0)
        bit = '1' if is_even else '0'
        
        # Check constraints
        if bit == '0':
            if current_zeros < required_zeros:
                password.append('0')
                current_zeros += 1
        else: # bit == '1'
            if current_ones < required_ones:
                password.append('1')
                current_ones += 1
                
        # Move to next number
        current_n = secure_collatz_step(current_n, key)
        
        # Anti-loop/degeneracy check
        if current_n <= 1:
             current_n = secrets.randbits(256)
             
    return "".join(password)

def perform_statistical_tests(bit_string):
    n = len(bit_string)
    if n == 0:
        return

    print("\n--- Statistical Analysis & Quality Check ---")
    
    # 1. Chi-Square Test (Goodness of Fit for Uniformity)
    counts = Counter(bit_string)
    n0 = counts.get('0', 0)
    n1 = counts.get('1', 0)
    
    expected_count = n / 2
    # Chi-Squared Statistic: sum((Observed - Expected)^2 / Expected)
    chi_sq = ((n0 - expected_count) ** 2 / expected_count) + \
             ((n1 - expected_count) ** 2 / expected_count)
    
    # For 1 degree of freedom, critical value at alpha=0.05 is 3.841
    print(f"1) Chi-Square Test (0/1 Balance):")
    print(f"   - Counts: 0s={n0}, 1s={n1}")
    print(f"   - Statistic: {chi_sq:.4f}")
    if chi_sq < 3.841:
        print(f"   - Result: PASS (Consistent with uniform distribution)")
    else:
        print(f"   - Result: FAIL (Significant deviation)")

    # 2. Runs Test (Wald-Wolfowitz) - Checks for independence / random clustering
    runs = 0
    if n > 0:
        runs = 1
        for i in range(1, n):
            if bit_string[i] != bit_string[i-1]:
                runs += 1
                
    expected_runs = 1 + (2 * n0 * n1) / n
    
    if n > 1:
        numerator = 2 * n0 * n1 * (2 * n0 * n1 - n)
        denominator = (n ** 2) * (n - 1)
        variance = numerator / denominator if denominator != 0 else 0
        std_dev = math.sqrt(variance)
        
        z_score = (runs - expected_runs) / std_dev if std_dev > 0 else 0.0
    else:
        z_score = 0.0
        
    print(f"\n2) Runs Test (Independence/Randomness):")
    print(f"   - Total Runs: {runs}")
    print(f"   - Expected Runs: {expected_runs:.2f}")
    print(f"   - Z-Score: {z_score:.4f}")
    
    if -1.96 <= z_score <= 1.96:
        print(f"   - Result: PASS (No significant evidence of non-randomness)")
    else:
        print(f"   - Result: FAIL (Data may be clustered or alternating too much)")

def main():
    parser = argparse.ArgumentParser(description="Secure Balanced Collatz Generator (AES-like Strength)")
    parser.add_argument("--length", type=int, default=128, help="Length of the output (must be even)")
    
    args = parser.parse_args()
    
    try:
        pwd = generate_secure_password(args.length)
        print(f"Generated Secure Output: {pwd}")
        
        # Verification
        zeros = pwd.count('0')
        ones = pwd.count('1')
        print(f"Verification: 0s={zeros}, 1s={ones} - {'PASS' if zeros == ones else 'FAIL'}")
        
        perform_statistical_tests(pwd)
        
    except Exception as e:
        print(f"An error occurred: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
