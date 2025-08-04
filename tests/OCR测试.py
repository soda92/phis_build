import ddddocr
from pathlib import Path

ocr = ddddocr.DdddOcr(show_ad=False)
result = ocr.classification(Path('captcha.png').read_bytes())
print(result)
