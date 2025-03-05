#!/usr/bin/env python3
from extension_audit.analysis import NetworkAnalyzer
from extension_audit.flow_processor import FlowProcessor
import pandas as pd
import argparse
import os
import subprocess
from mitmproxy.io import FlowReader
from mitmproxy.http import HTTPFlow
import time
import json
import tempfile

class GenAIAudit:
    def __init__(self, extension) -> None:
        self.extension = extension
        self.processor = FlowProcessor(self.extension)
        self.flow_path = os.path.join(tempfile.gettempdir(), "working.flow")
        self.network_interface = 'Wi-Fi'
        self.proxy_port = 8080

    def enable_proxy(self):
        """Set the macOS proxy settings for Wi-Fi."""
        try:
            print("Enabling Wi-Fi proxy settings...")
            subprocess.run(
                [
                    "networksetup", "-setwebproxy", self.network_interface, "127.0.0.1", str(self.proxy_port)
                ],
                check=True
            )
            subprocess.run(
                [
                    "networksetup", "-setsecurewebproxy", self.network_interface, "127.0.0.1", str(self.proxy_port)
                ],
                check=True
            )
        except subprocess.CalledProcessError as e:
            print(f"Failed to enable proxy: {e}")

    def disable_proxy(self):
        """Reset the macOS proxy settings after mitmproxy stops."""
        try:
            print("Disabling Wi-Fi proxy settings...")
            subprocess.run(
                ["networksetup", "-setwebproxystate", self.network_interface, "off"], check=True
            )
            subprocess.run(
                ["networksetup", "-setsecurewebproxystate", self.network_interface, "off"], check=True
            )
        except subprocess.CalledProcessError as e:
            print(f"Failed to disable proxy: {e}")

    def start_proxy(self):
        flow_path = self.flow_path
        self.enable_proxy()
        time.sleep(3)

        try:
            
            proxy_process = subprocess.Popen(
            ["mitmweb", "-w", flow_path],
            stdout=subprocess.DEVNULL,       
            stderr=subprocess.DEVNULL
            )


            while proxy_process.poll() is None:
                time.sleep(1)

        except KeyboardInterrupt:
            print("\nCtrl + C detected. Stopping mitmproxy...")
            proxy_process.terminate()
            proxy_process.wait()
        except subprocess.CalledProcessError as e:
            print(f"Error running mitmproxy: {e}")
        finally:
            self.disable_proxy()
            
    def run(self):
        self.start_proxy()
        try:
            df = self.processor.process_flows(self.flow_path)
            analyzer = NetworkAnalyzer(df, self.flow_path, self.extension)
            fp, tp = analyzer.run()

            json_args = json.dumps({"fp": fp, "tp": tp})
            subprocess.Popen(["streamlit", "run", "extension_audit/app.py", "--", json_args], start_new_session=True)

        finally:
            if os.path.exists(self.flow_path):
                print(f"Deleting flow file: {self.flow_path}")
                os.remove(self.flow_path)

def main():
    parser = argparse.ArgumentParser(description="Run GenAIAudit with network traffic analysis.")

    parser.add_argument(
        "extension_name",
        type=str,
        help="Name of the browser extension being analyzed (e.g., maxai)."
    )
    
    args = parser.parse_args()
    audit = GenAIAudit(extension=args.extension_name)
    audit.run()

if __name__ == "__main__":
    main()
