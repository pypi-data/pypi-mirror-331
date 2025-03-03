from setuptools import setup

setup(
  name = 'DPConCFil',
  packages = ['DPConCFil'],
  version = '0.0.4',
  description = 'A collection of filament identification and analysis algorithms',
  author = ['Jiang Yu'],
  author_email = 'yujiang@pmo.ac.cn',
  url = 'https://github.com/JiangYuTS/DPConCFil',
#   download_url = '',
  keywords = ['astrophysics', 'DPConCFil', 'filaments'],
  classifiers = [],
  install_requires=[
      'numpy',
      'scipy',
      'matplotlib',
      'astropy',
      'scikit-learn',
      'scikit-image',
      'networkx',
      'pandas',
      'tqdm',
      'FacetClumps',
      'radfil',
      
  ]
)
