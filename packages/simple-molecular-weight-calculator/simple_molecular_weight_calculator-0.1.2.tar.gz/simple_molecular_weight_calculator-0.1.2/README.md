# Simple Molecular Weight Calculator

Simple & Fast Molecular Weight Calculator Written in Rust

## Installation

### Cargo
```bash
cargo clean && cargo build --release
```

### Pip
```bash
git clone https://github.com/zxzimeng/cli-molecular-weight-calculator
cd cli-molecular-weight-calculator
pip install .
```

### PyPi
```bash
pip install simple-molecular-weight-calculator
```

### Homebrew
```bash
brew tap zxzimeng/mm
brew install mm
```

## Usage
H2O:
```bash
❯ mm H2O          
18.015000
```

(H2O)2:
```bash
❯ mm "(H2O)2"
36.030000
```

((H2O)2CH4):
```bash
❯ mm "((H2O)2CH4)"
52.073000
```

## Libraries
Uses the **periodic_table_rs** library for molar mass lookup.

