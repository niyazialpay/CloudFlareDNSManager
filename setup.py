from cx_Freeze import setup, Executable

buildOptions = dict(packages=[], excludes=[])

import sys

base = 'Win32GUI' if sys.platform == 'win32' else None

executables = [
    Executable('main.py',  # py uzantılı dosyamızın adını yazıyoruz.
               base=base,
               icon='Templates/img/icon.ico')  # ikon dosyamızın adını yazıyoruz.
]

setup(  # py'den exe'ye dönüştürülmüş dosyanın ayrıntılarında
    name='CloudFlare DNS Manager',  # gözükecek olan adı(name),
    version='0.1',  # versiyonu(version) ve
    description='You can manage your DNS settings on CloudFlare, add a new domain, or remove domain. Add, delete or '
                'edit DNS records. Most importantly, you can change the IP addresses of all domains at once.',
    # açıklamasını(description) yazıyoruz.
    options=dict(build_exe=buildOptions),
    executables=executables
)
