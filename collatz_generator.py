import argparse
import random
import sys

def collatz_step(n):
    if n % 2 == 0:
        return n // 2
    else:
        return 3 * n + 1

def generate_password(seed, length):
    if length % 2 != 0:
        print("Error: Length must be even to ensure equal split of 0s and 1s.")
        sys.exit(1)

    required_zeros = length // 2
    required_ones = length // 2
    
    current_zeros = 0
    current_ones = 0
    
    password = []
    
    # Start sequence with seed
    current_n = seed
    
    while len(password) < length:
        # Get bit value: 0 if even, 1 if odd
        bit = '0' if current_n % 2 == 0 else '1'
        
        # Check if we can add this bit
        if bit == '0':
            if current_zeros < required_zeros:
                password.append('0')
                current_zeros += 1
        else: # bit == '1'
            if current_ones < required_ones:
                password.append('1')
                current_ones += 1
                
        # Move to next number in sequence
        # If we reach 1, Collatz sequence loops 1-4-2-1. This is fine, it still provides numbers.
        # But to avoid getting stuck in short loop with poor entropy if length is huge, 
        # we could modify, but for standard usage 4-2-1 loop still gives even/odd mix (even-even-odd).
        current_n = collatz_step(current_n)
        
    return "".join(password)

def main():
    parser = argparse.ArgumentParser(description="Collatz Password Generator")
    parser.add_argument("--length", type=int, default=16, help="Length of the password (must be even)")
    parser.add_argument("--seed", type=int, help="Initial seed for Collatz sequence (random if not provided)")
    
    args = parser.parse_args()
    
    if args.seed is None:
        args.seed = random.randint(1, 1000000000)
        
    print(f"Using seed: {args.seed}")
    print(f"Target length: {args.length}")
    
    pwd = generate_password(args.seed, args.length)
    print(f"Generated Password: {pwd}")
    
    # Verification
    zeros = pwd.count('0')
    ones = pwd.count('1')
    print(f"Verification: 0s={zeros}, 1s={ones} - {'PASS' if zeros == ones else 'FAIL'}")

if __name__ == "__main__":
    main()
