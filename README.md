# FortiPass

A professional-grade password strength visualizer optimized for cybersecurity professionals and secure system integration.

## Features

- **Real-Time Password Analysis**
  - Shannon entropy calculation
  - Character diversity assessment
  - Pattern detection (dates, keyboard sequences, repeated characters)
  - Dictionary-based weakness checks

- **Visual Feedback System**
  - Dynamic strength meter with color gradients
  - Real-time feedback messages with actionable tips
  - Character-level heatmap visualization

- **Professional Guidance**
  - NIST SP 800-63B compliant recommendations
  - Estimated crack time based on modern hardware capabilities
  - Actionable improvement suggestions

- **Advanced Features**
  - Strong password generation with customizable settings
  - Export analysis reports in PDF/JSON formats
  - Modular design for easy integration with other systems

## Installation

### Requirements

- Python 3.7+
- PyQt5
- ReportLab (for PDF export)

### Install from source

```bash
# Clone the repository
git clone https://github.com/fortipass/fortipass.git
cd fortipass

# Install the package
pip install -e .
```

## Usage

### Running the application

```bash
# Run directly
python -m fortipass.main

# Or if installed via pip
fortipass
```

### Using as a library

```python
from fortipass.core.password_analyzer import PasswordAnalyzer

# Initialize analyzer with optional wordlist
analyzer = PasswordAnalyzer(wordlist_path="path/to/wordlist.txt")

# Analyze a password
results = analyzer.analyze("MyP@ssw0rd")

# Generate a strong password
strong_password = analyzer.generate_strong_password(
    length=16,
    include_uppercase=True,
    include_digits=True,
    include_symbols=True
)
```

## Security Considerations

- FortiPass is designed for local analysis only and does not transmit passwords over networks
- Password data is never stored persistently
- All analysis is performed in memory and cleared after use
- Report exports do not include the actual password

## License

This project is licensed under the MIT License - see the LICENSE file for details.
