#!/usr/bin/env python3
"""
Main script to run training with live analysis
"""

import threading
import time
from training.train import train_model
from training.analyze import LiveAnalysisDashboard

def run_training():
    """Run the training process"""
    print("Starting AI Fight Club Training")
    print("=" * 50)
    
    # Start training in a separate thread
    def train_thread():
        model, callback = train_model(total_timesteps=100000)
    
    # Start training thread
    training_thread = threading.Thread(target=train_thread)
    training_thread.daemon = True
    training_thread.start()
    
    # Start live analysis dashboard
    dashboard = LiveAnalysisDashboard()
    
    try:
        # Show dashboard (this will block until closed)
        dashboard.show()
    except KeyboardInterrupt:
        print("Training interrupted by user")
    
    # Wait for training thread to finish
    training_thread.join(timeout=1.0)
    
    print("Training completed!")

if __name__ == "__main__":
    run_training()