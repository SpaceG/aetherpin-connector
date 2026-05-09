"""PyInstaller entry point — uses absolute imports for bundled .exe/.app."""
from agent.cli import main

if __name__ == '__main__':
    main()
