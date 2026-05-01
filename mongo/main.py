import multiprocessing
import sys
import os

# Ensure the root mongo directory is in the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import the entry points from each service
from services.inbound.app import main as run_inbound
from services.outbound.app import main as run_outbound

def main():
    print("==========================================")
    print("   MAZERUN MONGO MULTI-PROCESS ORCHESTRATOR")
    print("==========================================")

    # Define the processes
    # We call the main() functions of each service directly in a new process
    p1 = multiprocessing.Process(target=run_inbound, name="InboundService")
    p2 = multiprocessing.Process(target=run_outbound, name="OutboundService")

    # Start both processes
    p1.start()
    p2.start()

    print(f"[Orchestrator] Services started. Inbound (PID: {p1.pid}), Outbound (PID: {p2.pid})")

    try:
        # Keep the main process alive while children are running
        p1.join()
        p2.join()
    except KeyboardInterrupt:
        print("\n[Orchestrator] KeyboardInterrupt detected, shutting down services...")
        p1.terminate()
        p2.terminate()
        p1.join()
        p2.join()
        print("[Orchestrator] Shutdown complete.")

if __name__ == "__main__":
    main()
