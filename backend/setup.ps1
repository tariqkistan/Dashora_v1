# Check if Python is installed
$pythonCommand = $null
$commands = @("python", "python3", "py")

foreach ($cmd in $commands) {
    try {
        $version = & $cmd --version 2>&1
        if ($version -match "Python 3") {
            $pythonCommand = $cmd
            break
        }
    } catch {
        # Command not found or other error
        continue
    }
}

if ($null -eq $pythonCommand) {
    Write-Host "Python 3 not found. Please install Python 3 from https://www.python.org/downloads/"
    Write-Host "Make sure to check 'Add Python to PATH' during installation."
    exit 1
}

Write-Host "Using $pythonCommand with version: $($version)"

# Create virtual environment
Write-Host "Creating virtual environment..."
& $pythonCommand -m venv venv

# Activate virtual environment
Write-Host "Activating virtual environment..."
. .\venv\Scripts\Activate.ps1

# Install dependencies
Write-Host "Installing dependencies..."
pip install -r requirements.txt

Write-Host "Setup complete! The virtual environment is now activated."
Write-Host "To activate the environment in the future, run: .\venv\Scripts\Activate.ps1" 