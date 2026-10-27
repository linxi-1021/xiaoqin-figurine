from pathlib import Path
r=Path(__file__).resolve().parent
exec(compile((r/'verify_print.py').read_text(encoding='utf-8').replace("r/'finished/","r/'bag-v7/"),str(r/'verify_print.py'),'exec'))
