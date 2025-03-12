# Typhoon parser
Parsing typhoon TAC message.

## Usage
```python
python3 parser.py --code examples/TCPQ_BABJ.txt --output print
```

Output option:
- `json`: a json containing field and raw code/translated meaning.
- `txt`: a text explaining the message. 
- `print`: print to stdout.

## Supported message
- TCPQ BABJ
- WTPQ BABJ
- WSCI BABJ

## Reference
- 韩瑞[等]. 全球台风报文TAC格式的编码规则解析[M]. B1. 气象出版社, 2024.
- [【教程向】从零开始看懂台风报文！](https://www.bilibili.com/video/BV1Fa411J7G3)
- [Original telecode dict](https://github.com/mkyung/chinese-telecode/blob/master/data/dict.json) and [it's translated version](https://github.com/KnugiHK/chinese-telecode/blob/main/data.json)
