import re

class TextCleaner:
    @staticmethod
    def clean(text: str) -> str:
        """
        Clean extracted document text.
        """
        if not text:
            return ""
        #Convert Windows line endings
        text = text.replace("\r\n","\n")
        #Convert tabs to spaces
        text = text.replace("\t", " ")
        #Remove repeated spaces
        text = re.sub(r"[ ]{2,}"," ",text)
        #Remove excessive blank lines
        text = re.sub(r"\n{3,}","\n\n", text)
        # Remove the leading /trailing whitespace
        text = text.strip()

        return text