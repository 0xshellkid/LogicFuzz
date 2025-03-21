
## ⚙️ Installation

> Requires Python 3.8+

```bash
pip install boofuzz snap7 pycomm3 openai
```


---

## 🚀 Usage

### Command‑Line (LogicFuzz)

Display help and all available options:

```bash
python LogicFuzz/run.py --help
```

Generate a test program for a single logic instruction:

```bash
python LogicFuzz/run.py \
  --mode generate \
  --instruction SysSockConnect \
  --model gpt-4 \
  --output ./results/
```

Fuzzing a logic instruction:

```bash
python LogicFuzz/run.py --mode fuzzing --target <PLC_IP_ADDRESS:PORT>  --RoundTime T --pollTime t --bugNum 1000 --instruction SysMemCpy
```

---

## 📖 Documentation

- CLI usage reference: `python LogicFuzz/run.py --help`  
- Report issues or request features: https://github.com/YourOrg/LogicFuzz/issues
---

## 🤝 Contributing

1. Fork the repository  
2. Create a feature branch  
3. Submit a pull request  



