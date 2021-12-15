#!/usr/bin/env python3

'''
Enumerate given directories for potential password files and crack a given zip

Using generator techniques to mitigate the amount of IO Wrappers and Memory Usage of the program when dealing with large password banks
'''

import re
import sys
import zipfile
from glob import iglob
from os import path


class crack_zip:
    def __init__(self, zip_name: str, pretty=True):
        '''
        zip_name: str
            Name of the zip that needs to be cracked

        pretty: bool
            Pretty output to the terminal
        '''
        self.zip_name = zip_name
        self.pretty = pretty

    def find_txt_files(self, directory: str = "./") -> list[str]:
        """
        Searches for valid txt files in a given directory

        :rtype: generator[str]
            List of valid text files
        """
        yield from (txt_file for txt_file in iglob(f"{directory}/*.txt") if path.isfile(txt_file))

    def search_file(self, txt_file_contents: list[str]) -> list[str]:
        """
        Find passwords from a given text file's contents

        :rtype: generator[str]
            returns a `str` instance of a potential password
        """
        pattern = "^password_[0-9]*:[0-9]{7}$"  # pattern of the potential password in the file
        yield from (password.split(":")[1] for password in txt_file_contents if re.search(pattern, password))

    def find_passwords(self, search_dirs: list[str] = ["./"]) -> list[str]:
        """
        Yield passwords from a given search directory

        search_dirs: list
            List of directories you want to search
            default: current directory

        :rtype: list[str]
            List of strings containing the passwords to search from.
        """
        print(f"[i] Searching {len(search_dirs)} directories for passwords") if self.pretty else None
        for directory in search_dirs:
            for txt_file in self.find_txt_files(directory.rstrip("/")):
                try:
                    with open(txt_file, "r") as t_file:
                        yield from self.search_file(t_file.read().split("\n"))
                except PermissionError or FileNotFoundError as err:
                    print(f"\n[-] Failed to read from {txt_file} with error {err}")

    def extract_zip(self, password: bytes = None, extract_dir: str = "./") -> bool:
        """
        Extract a zip file given a password in bytes into an optional directory

        password: bytes
            The byte representation of the potential password to unzip the file with
        extract_dir: str
            The str representation of the output directory

        :rtype: bool
            A boolean representing if the zip file was cracked or not
        """
        try:
            with zipfile.ZipFile(self.zip_name, "r") as zip_file:
                zip_file.extractall(path=extract_dir, pwd=password)
        except RuntimeError:
            return False
        except zipfile.BadZipFile:
            return False
        return True

    def crack(self, password_folders: list[str], extract_dir: str = "./") -> str:
        """
        Attempts to crack the given zip file with the found passwords

        password_folders: list[str]
            The list of directories in str format to enumerate for passwords
        extract_dir: str
            The directory to extract to
            default: current directory

        :rtype: str
            The str representation of the password. If none is found, it will return "" after checking for empty password zip files
        """
        if not isinstance(password_folders, list):
            print("[!] Please enter a list of str values for password folder")
            sys.exit(1)

        print(f"[*] Analyzing zip file {self.zip_name}")
        try:
            if self.extract_zip(extract_dir=extract_dir):
                print("[i] Zip file has no password, exiting...")
                return
        except RuntimeError:
            print("[!] This is not a zip file!, aborting...")
            return

        for count, password in enumerate(self.find_passwords(password_folders), start=1):
            print(f"\r[*] Passwords attempted: {count}", end="") if self.pretty else None
            if self.extract_zip(password=bytes(password, 'utf-8'), extract_dir=extract_dir):
                print(f"\n[+] Found the password: {password}")
                return password
        else:
            print("[-] No password found")
        return ""


def demo():
    """
    Crack secret.zip with passwords supplied from ./password_folder
    """
    crack_zip(
        "./password_folder/secret.zip").crack(["./password_folder"], extract_dir="./cracked_zips")


if __name__ == '__main__':
    demo()
