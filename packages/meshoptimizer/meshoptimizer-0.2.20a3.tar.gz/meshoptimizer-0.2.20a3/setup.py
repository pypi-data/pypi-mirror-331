from setuptools import setup, Extension, find_packages
import os
import platform

# Get the directory containing this file (setup.py)
SETUP_DIR = os.path.dirname(os.path.abspath(__file__))

# Get long description from README
def get_long_description():
    try:
        readme_path = os.path.join(SETUP_DIR, 'README.md')
        if os.path.exists(readme_path):
            with open(readme_path, 'r', encoding='utf-8') as f:
                return f.read()
    except Exception as e:
        print(f"Warning: Could not read README.md: {e}")
    return 'Python wrapper for meshoptimizer library'

# Determine source files and generate module file
def generate_module_file():
    src_path = os.path.join('..', 'src')
    
    # Get all .cpp files from the src directory
    source_files = []
    if os.path.exists(src_path):
        source_files = [f"../../src/{f}" for f in os.listdir(src_path) if f.endswith('.cpp')]
    
    # Create the module.cpp file from template
    module_template_path = os.path.join(SETUP_DIR, 'bindings', 'module.template.cpp')
    # Create directory if it doesn't exist
    
    output_module_path = os.path.join(SETUP_DIR, 'bindings', 'module.cpp')
    
    # Read template and insert source imports
    with open(module_template_path, 'r') as template_file:
        template_content = template_file.read()
    
    source_imports = '\n'.join([f'#include "{src}"' for src in source_files])
    module_content = template_content.replace('{{SOURCE_IMPORTS}}', source_imports)
    
    # Write the resulting module file
    with open(output_module_path, 'w') as module_file:
        module_file.write(module_content)
        
    return source_files

# Platform-specific compile and link arguments
def get_build_args():
    is_windows = platform.system() == 'Windows'
    is_macos = platform.system() == 'Darwin'
    
    extra_compile_args = []
    extra_link_args = []
    define_macros = []
    
    # Define macros for all platforms
    define_macros = [
        ('MESHOPTIMIZER_IMPLEMENTATION', '1')  # Include implementation in the build
    ]
    
    if is_windows:
        # Windows-specific flags (MSVC)
        extra_compile_args = ['/std:c++14', '/O2', '/EHsc']
        # Export functions for DLL
        define_macros.extend([
            ('MESHOPTIMIZER_API', '__declspec(dllexport)'),
            ('MESHOPTIMIZER_EXPERIMENTAL', '__declspec(dllexport)')
        ])
        extra_link_args = ['/DLL']
    else:
        # Unix-like systems (Linux/Mac)
        extra_compile_args = ['-std=c++11', '-O3', '-fPIC']
        if is_macos:
            extra_compile_args.extend(['-stdlib=libc++', '-mmacosx-version-min=10.9'])
    
    return extra_compile_args, extra_link_args, define_macros

# Get the source files and build arguments
include_dirs = [os.path.join('..', 'src')]
extra_compile_args, extra_link_args, define_macros = get_build_args()

# Define the extension module
meshoptimizer_module = Extension(
    'meshoptimizer._meshoptimizer',
    sources= ["bindings/module.cpp"],
    include_dirs=include_dirs,
    extra_compile_args=extra_compile_args,
    extra_link_args=extra_link_args,
    define_macros=define_macros,
    language='c++',
)

generate_module_file()

setup(
    name='meshoptimizer',
    version="0.2.20a3",
    description='Python wrapper for meshoptimizer library',
    long_description=get_long_description(),
    long_description_content_type='text/markdown',
    url='https://github.com/zeux/meshoptimizer',
    packages=find_packages(),
    ext_modules=[meshoptimizer_module],
    install_requires=[
        'numpy>=1.19.0',
    ],
    setup_requires=[
        'setuptools>=42',
        'wheel',
        'numpy>=1.19.0',
    ],
    python_requires='>=3.6',
    package_data={
        '': ['src/*.cpp', 'src/*.h', 'python/src/*.cpp', 'python/src/*.h'],
    },
    include_package_data=True,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Multimedia :: Graphics :: 3D Modeling',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
    ],
    keywords='mesh optimization graphics 3d',
)