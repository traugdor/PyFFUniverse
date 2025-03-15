from tkhtmlview import HTMLScrolledText as OriginalHTMLScrolledText
from PIL import Image

class HTMLScrolledText(OriginalHTMLScrolledText):
    """
    A patched version of HTMLScrolledText that works with newer Pillow versions.
    """
    def _get_image(self, url):
        try:
            image = super()._get_image(url)
            return image
        except AttributeError as e:
            if "ANTIALIAS" in str(e):
                # Patch the PIL.Image.ANTIALIAS issue
                try:
                    from urllib.request import urlopen
                    from io import BytesIO
                    
                    if url.startswith("http"):
                        with urlopen(url) as u:
                            data = u.read()
                        image = Image.open(BytesIO(data))
                    else:
                        image = Image.open(url)
                    
                    # Use Resampling.LANCZOS instead of ANTIALIAS
                    if hasattr(Image, "Resampling"):
                        resampling = Image.Resampling.LANCZOS
                    else:
                        resampling = Image.LANCZOS
                    
                    if image.size[0] > self.max_width:
                        ratio = self.max_width / image.size[0]
                        height = int(ratio * image.size[1])
                        image = image.resize((self.max_width, height), resampling)
                    return image
                except Exception as ex:
                    print(f"Error loading image: {ex}")
                    return None
            else:
                # If it's a different error, re-raise it
                raise
