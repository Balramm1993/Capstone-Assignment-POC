from flask import Flask, render_template
import re

app = Flask(__name__, template_folder='templates')

with app.app_context():
    html = render_template('index.html')
    print("First 1000 chars:")
    print(html[:1000])
    print("\nTitle found:")
    title = re.search(r'<title>(.*?)</title>', html)
    if title:
        print(f"  '{title.group(1)}'")
    
    print(f"\nTotal length: {len(html)}")
