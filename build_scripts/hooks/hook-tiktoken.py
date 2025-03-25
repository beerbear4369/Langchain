from PyInstaller.utils.hooks import collect_data_files
import os
import glob
import tiktoken
import site

# Hook for tiktoken to ensure encoding files are included
datas = collect_data_files('tiktoken')

# Add tiktoken encoding files
tiktoken_dir = os.path.dirname(tiktoken.__file__)
encodings = glob.glob(os.path.join(tiktoken_dir, "*.tiktoken"))
for encoding in encodings:
    datas.append((encoding, 'tiktoken'))

# Try to find tiktoken_ext in site-packages
site_packages = site.getsitepackages()[0]
tiktoken_ext_path = os.path.join(site_packages, "tiktoken_ext")
if os.path.exists(tiktoken_ext_path):
    ext_encodings = glob.glob(os.path.join(tiktoken_ext_path, "*.tiktoken"))
    for encoding in ext_encodings:
        datas.append((encoding, 'tiktoken_ext'))

# Try to find the cl100k_base encoding specifically
cl100k_paths = []
# Look in tiktoken directory
cl100k_paths.extend(glob.glob(os.path.join(tiktoken_dir, "cl100k_base*.tiktoken")))
# Look in tiktoken_ext directory
if os.path.exists(tiktoken_ext_path):
    cl100k_paths.extend(glob.glob(os.path.join(tiktoken_ext_path, "cl100k_base*.tiktoken")))
# Look in openai_public directory if it exists
openai_public_path = os.path.join(tiktoken_ext_path, "openai_public")
if os.path.exists(openai_public_path):
    cl100k_paths.extend(glob.glob(os.path.join(openai_public_path, "cl100k_base*.tiktoken")))

# Add all found cl100k encodings to datas
for path in cl100k_paths:
    dirname = os.path.dirname(path)
    if "tiktoken_ext" in dirname:
        if "openai_public" in dirname:
            datas.append((path, os.path.join('tiktoken_ext', 'openai_public')))
        else:
            datas.append((path, 'tiktoken_ext'))
    else:
        datas.append((path, 'tiktoken'))

# Add regex package dependencies
hiddenimports = ['regex', 'tiktoken_ext', 'tiktoken_ext.openai_public'] 