from html.parser import HTMLParser
import html as ihtml
import re

TG_TAGS = {"b","strong","i","em","u","ins","s","strike","del","a","code","pre","blockquote","br","span"}
BLOCKY = {"p","div","section","article","header","footer","h1","h2","h3","h4","h5","h6","ul","ol","li"}
SPAN_ALLOWED_CLASSES = {"tg-spoiler"}  # единственный разрешённый класс у <span> в TG

class TelegramHTMLSanitizer(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=False)
        self.out = []
        self.stack = []
        self.in_pre = False

    def _push(self, s): self.out.append(s)

    def handle_starttag(self, tag, attrs):
        tag = tag.lower()
        attrs = dict(attrs or [])

        # блочные теги → перенос строки, без самого тега
        if tag in BLOCKY:
            self._push("\n")
            return

        if tag not in TG_TAGS:
            return

        if tag == "a":
            href = (attrs.get("href") or "").strip()
            # Telegram принимает только http/https/mailto/tg
            if not re.match(r"^(https?://|mailto:|tg://)", href):
                return
            self._push(f'<a href="{ihtml.escape(href, quote=True)}">')
            self.stack.append(tag)
            return

        if tag == "span":
            cls = attrs.get("class", "")
            if cls not in SPAN_ALLOWED_CLASSES:
                # обычный span Telegram не понимает → игнор
                return
            self._push(f'<span class="tg-spoiler">')
            self.stack.append(tag)
            return

        if tag == "pre":
            self._push("<pre>")
            self.stack.append(tag)
            self.in_pre = True
            return

        if tag == "code":
            # в Telegram нельзя вкладывать <code> внутри <pre>
            if self.in_pre:
                return
            self._push("<code>")
            self.stack.append(tag)
            return

        if tag == "blockquote":
            self._push("<blockquote>")
            self.stack.append(tag)
            return

        if tag == "br":
            self._push("<br>")
            return

        # простые инлайны
        self._push(f"<{tag}>")
        self.stack.append(tag)

    def handle_endtag(self, tag):
        tag = tag.lower()
        if tag in BLOCKY:
            self._push("\n")
            return
        if not self.stack:
            return
        # закроем только если верх стека совпадает
        if self.stack and self.stack[-1] == tag:
            self.stack.pop()
            if tag == "pre":
                self.in_pre = False
            self._push(f"</{tag}>")
        else:
            # рассинхрон — просто игнор
            if tag == "pre":
                self.in_pre = False

    def handle_startendtag(self, tag, attrs):
        tag = tag.lower()
        if tag in {"br"}:
            self._push("<br>")
        elif tag in BLOCKY:
            self._push("\n")

    def handle_data(self, data):
        self._push(ihtml.escape(data))

    def handle_entityref(self, name):
        self._push(f"&{name};")

    def handle_charref(self, name):
        self._push(f"&#{name};")

    def get_sanitized(self):
        # закрываем незакрытые теги безопасно в обратном порядке
        while self.stack:
            t = self.stack.pop()
            if t == "pre":
                self.in_pre = False
            self._push(f"</{t}>")
        # нормализуем пустые строки
        text = "".join(self.out)
        text = re.sub(r"\n{3,}", "\n\n", text).strip()
        return text

def sanitize_to_telegram_html(s: str) -> str:
    p = TelegramHTMLSanitizer()
    p.feed(s)
    p.close()
    return p.get_sanitized()
