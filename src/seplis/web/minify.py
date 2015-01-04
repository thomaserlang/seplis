import os, os.path
import logging
import subprocess
from seplis import utils

def minify_files(files, out_path, minify_method):
    print('Start minifying to {}'.format(out_path))
    with open(out_path, 'w') as fout:
        for file_ in files:
            print('Minifying {}'.format(
                file_,
            ))

            fout.write(
                minify_method(
                    file_
                ).decode('utf-8')
            )

def js_minify(file_):
    args = [
        'uglifyjs',
        file_,
    ]
    try:
        return subprocess.check_output(args)
    except subprocess.CalledProcessError:
        return

def css_minify(file_):
    args = [
        'yui-compressor',
        file_,
    ]
    try:
        return subprocess.check_output(args)
    except subprocess.CalledProcessError:
        return

def main():
    skip = ('vendor.min.js', 'seplis.min.js')
    js_path = os.path.join(os.path.dirname(__file__), 'static/js')
    js_vendor_files = utils.get_files(
        os.path.join(js_path, 'vendor'),
        '.js',
        skip=skip,
    )
    to_top = []
    for f in js_vendor_files:
        if 'jquery-' in f:
            to_top.append(f)
    for f in to_top:
        js_vendor_files.remove(f)
        js_vendor_files.insert(0, f)
    js_source_files = utils.get_files(
        js_path, 
        '.js',        
        skip=skip,
    )
    for file_ in js_vendor_files:
        js_source_files.remove(file_)
    # vendor.min.js
    minify_files(
        js_vendor_files,
        out_path=os.path.join(os.path.dirname(__file__), 'static/js/vendor/vendor.min.js'),
        minify_method=js_minify,
    )
    # seplis.min.js
    minify_files(
        js_source_files,
        out_path=os.path.join(os.path.dirname(__file__), 'static/js/seplis.min.js'),
        minify_method=js_minify,
    )

    css_path = os.path.join(os.path.dirname(__file__), 'static/css')
    css_vendor_files = utils.get_files(os.path.join(css_path, 'vendor'), '.css')
    css_source_files = utils.get_files(css_path, '.css')
    for file_ in css_vendor_files:
        css_source_files.remove(file_)
    # vendor.min.css
    minify_files(
        css_vendor_files,
        out_path=os.path.join(os.path.dirname(__file__), 'static/css/vendor/vendor.min.css'),
        minify_method=css_minify,
    )
    # seplis.min.css
    minify_files(
        css_source_files,
        out_path=os.path.join(os.path.dirname(__file__), 'static/css/seplis.min.css'),
        minify_method=css_minify,
    )

if __name__ == '__main__':
    main()