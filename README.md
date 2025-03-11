# Typhoon parser
Parsing typhoon TAC message.

## Usage
```python
python3 parser.py --code tac.txt --output json
```

Output option:
- `json`: a json containing field and raw code/translated meaning.
- `txt`: a text explaining the message. 

## Supported message
- TC
- WT
- WS

## Reference
韩瑞[等]. 全球台风报文TAC格式的编码规则解析[M]. B1. 气象出版社, 2024.