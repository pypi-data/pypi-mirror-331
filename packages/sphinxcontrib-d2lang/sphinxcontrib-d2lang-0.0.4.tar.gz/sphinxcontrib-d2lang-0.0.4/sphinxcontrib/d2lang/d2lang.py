from docutils import nodes

from docutils.parsers.rst import Directive, directives
from sphinx.util.docutils import SphinxDirective

from shutil import which
from pathlib import Path
import shlex
import subprocess
import tempfile
import uuid

class D2langDirective(SphinxDirective):
    required_arguments = 0
    has_content = True
    optional_arguments = 3
    option_spec = {
        'layout': directives.unchanged_required,
        'filename': directives.unchanged_required,
    }
    def run(self):
        d2_bin = which('d2')
        srcdir = self.state.document.settings.env.srcdir
        diag_source = self.content
        out_dir = self.state.document.current_source.rsplit("/",1)[0]
        if 'filename' in self.options:
            output_fname = out_dir + "/" + self.options.get('filename')
        else:
            output_fname = out_dir + "/" + "d2lang_svg/" + str(uuid.uuid4()) + ".svg"
        if 'layout' in self.options:
            layout = self.options.get('layout')
        else:
            layout = 'dagre'
        if self.arguments:
            path = Path(srcdir + '/' + self.arguments[0])
            if path.is_file():
                build_svg(
                    srcdir + '/' + self.arguments[0],
                    srcdir,
                    output_fname,
                    layout
                )
            else:
                raise
        else:
            with tempfile.NamedTemporaryFile(dir="./") as fp:
                for line in self.content.data:
                    fp.write(bytes(line,'utf-8'))
                    fp.write(bytes('\n','utf-8'))
                fp.seek(0)
                build_svg(fp.name, srcdir, output_fname, layout)
        image_node = nodes.image(uri=output_fname)
        return [image_node]

def build_svg(diag_src, out_dir, filename, layout):
    d2_bin = which('d2')
    cmd_line = '{bin} -l {layout} {src} {out}'.format(
        bin=d2_bin,
        layout=layout,
        src=diag_src,
        out=out_dir + "/" + filename
    )
    args = shlex.split(cmd_line)
    subprocess.run(args)
    return True
