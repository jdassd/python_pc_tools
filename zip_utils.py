import zipfile
from tqdm import tqdm

def crack_zip_password(zip_file_path, password_list_path):
    """
    Attempts to crack a ZIP file password using a password list.
    """
    try:
        with open(password_list_path, "r", errors="ignore") as password_list:
            passwords = password_list.read().splitlines()
    except FileNotFoundError:
        return f"Error: Password list not found at {password_list_path}"

    zip_file = zipfile.ZipFile(zip_file_path)
    
    for password in tqdm(passwords, desc="Cracking Password"):
        try:
            zip_file.extractall(pwd=password.encode())
            return f"Success! Password found: {password}"
        except (RuntimeError, zipfile.BadZipFile):
            continue
    return "Password not found in the list."
