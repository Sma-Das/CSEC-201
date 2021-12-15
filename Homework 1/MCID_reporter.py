#!/usr/bin/env python3

'''
Analyzes Mobile-Camera Intrusion Detection Tool log files to find abnormal and normal usage
Log files are stored in the format: "cust[ID]-[day].txt"
And reports are generated in the format: "[ID] [DURATION in minutes] [START TIME] [END TIME]"
'''

import os
import threading
from glob import iglob
from time import sleep


class InvalidLogFile(Exception):
    """
    This exception should be raised when a given log file is not in the proper format of:
    [ID] [DURATION in minutes] [START TIME] [END TIME]
    """

    def __init__(self, log_file, message="Invalid data found in log file"):
        self.log_file = log_file
        self.message = message
        super().__init__(message)

    def __str__(self) -> str:
        return f"[!] Invalid data found in file {self.log_file}"


class generate_report:
    def __init__(self, ID: int, CAMERA_LOGS: str = "./customer_usage", pretty: bool = True, quiet=False, write=False):
        """
        ID: int
            The customer ID you want to parse through
        CAMERA_LOGS: str
            The directory wherein the log files are
        pretty: bool
            Make terminal output pretty!
        quiet: bool
            Print to terminal or note
        write: bool
            Write to a file with format 'client-[ID]_result.log'
        """
        if not isinstance(ID, int):
            raise ValueError("ID must be an integer")
        self.ID = ID

        if not os.path.isdir(CAMERA_LOGS):
            raise NotADirectoryError("Log file directory does not exist")
        self.CAMERA_LOGS, self.pretty, self.quiet, self.write = CAMERA_LOGS, pretty, quiet, write

    def find_log_files(self) -> None:
        print(f"[*] Finding log files for customer ID {self.ID}") if not self.quiet else None
        self.log_files = [
            log_file for log_file in iglob(f"{self.CAMERA_LOGS}/cust{self.ID}-[0-9]*.txt")
        ]
        print(
            f"{'[+]' if len(self.log_files) else '[-]'} Found {len(self.log_files)}") if not self.quiet else None

    def parse_usage(self, log_file_name: str, log_file_contents: list[str]) -> list[int]:
        """
        Parse log files in the format "[SEQ] [DUR] [START] [END]"
        """
        usage = []
        for line, seq in enumerate(log_file_contents, start=1):
            if seq:
                try:
                    usage.append(int(seq.split()[1]))
                except ValueError:
                    raise InvalidLogFile(log_file_name)
        return usage

    def find_usage(self) -> dict[int: int]:
        '''
        Return the camera usage of each day as a dictionary in the format[day: usage]
        '''

        get_day: int = lambda name: int(name.split("-")[1].rstrip(".txt"))

        complete_usage = {}
        if not hasattr(self, "log_files"):  # Simple cache check system
            self.find_log_files()
        for log_file in self.log_files:
            with open(log_file, "r") as logfile:
                logfile.seek(0)
                print(f"\r[*] Parsing {log_file}...", end="") if not self.quiet else None
                complete_usage[get_day(log_file)] = self.parse_usage(
                    log_file, logfile.read().split("\n"))
                sleep(0.05) if self.pretty else None
                # Clearing the screen buffer
                print("\r" + " "*60, end="") if not self.quiet else None

        if not len(complete_usage):
            print("\r[-] No files were passed") if not self.quiet else None
        else:
            print(f"\r[+] All log files parsed") if not self.quiet else None

        # Repeatedly referencing a class object will result in poor performance
        self.complete_usage = complete_usage
        return complete_usage

    def total_mean_usage(self) -> dict[int: float]:
        if not hasattr(self, "complete_usage"):  # Simple cache check system
            self.find_usage()
        mean: float = lambda values: sum(values) / len(values) if values else 0
        self.mean_usage = {day: mean(values) if values else 0 for day,
                           values in self.complete_usage.items()}
        return self.mean_usage

    def report(self) -> None:

        if not hasattr(self, "mean_usage"):  # Simple cache check system
            self.total_mean_usage()

        mean_usage = self.total_mean_usage()
        if not len(self.complete_usage):
            exit(1)

        print("[*] Calculating Mean...") if not self.quiet else None
        total_mean = sum(mean_usage.values()) / len(mean_usage) if len(mean_usage) else 0

        abnormalities, abnormal_days = 0, {}
        for day, mean in sorted(mean_usage.items()):
            if mean > total_mean:
                print(f"[!] Day {day} had above average camera usage") if not self.quiet else None
                abnormalities += 1
                abnormal_days[day] = mean
        else:
            if not abnormalities:
                print("[i] No Days were found to be abnormal") if not self.quiet else None
            else:
                print(f"[!] {abnormalities} abnormalities were found") if not self.quiet else None

        if self.write:
            self.write_results(abnormalities, total_mean, abnormal_days)

    def write_results(self, abnormalities: int, total_mean: int, abnormal_days: dict[int: float]) -> None:
        print(f"[*] Writing files to client-{self.ID}_results.log") if not self.quiet else None
        try:
            with open(f"client-{self.ID}_results.log", "w") as output_file:
                output_file.write(f"[!] {abnormalities} abnormalities were found\n")
                output_file.write(f"[i] Daily average of: {round(total_mean, 2)}\n")
                output_file.write("Day \tMean\n")
                output_file.write(
                    "\n".join([f"{d}:\t{round(m, 2)}" for d, m in abnormal_days.items()]) + "\n")
        except PermissionError or FileExistsError as write_error:
            print(f"[-] Unable to write to client-{self.ID}_results.log with error: {write_error}")
        else:
            print(f"[+] File: 'client-{self.ID}_results.log' Written!")


def main(clients: list[int] = range(1, 9+1)):
    threads = []
    for client_id in clients:
        client_report = generate_report(ID=client_id, pretty=False, quiet=True, write=True)
        threads.append(threading.Thread(target=client_report.report, name=str(client_id)))
        threads[-1].start()

    while any(map(lambda t: t.is_alive(), threads)): pass


if __name__ == '__main__':
    main()

    client_1 = generate_report(ID=1, pretty=True, write=False)
    # client_1.report()
