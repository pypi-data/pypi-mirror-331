from solidipes.utils import solidipes_logging as logging

from .code_snippet import CodeSnippet

logger = logging.getLogger()


class TIKZ(CodeSnippet):
    supported_mime_types = {"latex/tikz": "tikz", "text/x-tex": "tikz"}

    def __init__(self, **kwargs):
        from ..viewers.image import Image
        from ..viewers.image_source import ImageSource as ImageSourceViewer
        from ..viewers.pdf import PDF as PDFViewer

        super().__init__(**kwargs)
        self.compatible_viewers[:0] = [ImageSourceViewer, Image, PDFViewer]

    @CodeSnippet.loadable
    def image(self):
        import base64
        import os
        import subprocess
        import tempfile

        with tempfile.NamedTemporaryFile(delete=False) as fp:
            fp.write(base64.b64decode(self.pdf))
            png_fname = os.path.splitext(fp.name)[0] + ".png"
            p = subprocess.Popen(f"pdftoppm -png {fp.name} > {png_fname}", shell=True)
            p.wait()
            if p.returncode:
                error = p.stderr.read().decode()
                logger.debug(error)
                raise RuntimeError(error)

            from PIL import Image as PILImage

            return PILImage.open(png_fname)

    @CodeSnippet.loadable
    def pdf(self):
        text = self.text
        if r"\begin{document}" not in text:
            header = r"""
            \documentclass[tikz,convert={outfile=\jobname.svg}]{standalone}
\usetikzlibrary{calc,patterns,snakes}
% \usetikzlibrary{...}% tikz package already loaded by 'tikz' option
            """
            if "gnuplot" in text:
                header += r"""
                \usepackage{gnuplot-lua-tikz}
                """
            header += r"""
            \begin{document}
            """

            text = header + text + r"\end{document}"

        import tempfile

        with tempfile.NamedTemporaryFile(delete=False) as fp:
            fp.write(text.encode())
            fp.close()
            import os
            import subprocess

            tmp_dir = os.path.dirname(fp.name)
            try:
                p = subprocess.Popen(f"rubber -d {fp.name}", shell=True, cwd=tmp_dir, stderr=subprocess.PIPE)
                p.wait()
                if p.returncode:
                    error = p.stderr.read().decode()
                    logger.debug(error)
                    raise RuntimeError(error)

                import os

                from .pdf import PDF

                pdf_file = os.path.split(fp.name)[-1]
                pdf_file = os.path.join(tmp_dir, pdf_file)
                pdf = PDF(path=pdf_file + ".pdf").pdf

                for ext in ["pdf", "aux", "log", "rubbercache"]:
                    os.remove(pdf_file + "." + ext)
                return pdf
            except Exception as e:
                logger.debug(e)
                raise RuntimeError(str(e))
