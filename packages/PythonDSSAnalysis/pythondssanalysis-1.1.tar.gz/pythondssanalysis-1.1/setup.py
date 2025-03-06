from setuptools import setup, find_packages

setup(
    name='PythonDSSAnalysis',
    version='1.1',    
    description='A python package for DSS Analysis',
    url='https://github.com/granthendrickson19/Python-DSS-Analysis',
    author='Grant Hendrickson',
    author_email='granthendrickson19@gmail.com',
    license='MIT',
    package_data={'Sample Model 1': ["samplemodel.yml"],
                  "Sample Model 2": ["samplemodelexp.yml"],
                  "Sample Data": ["sampledata.csv"],
                    "Sample Run":["sampleRun.py"]},
    install_requires=[
                      'numpy>=2.0',                     
                      ],

    classifiers=[
        'Development Status :: 1 - Planning',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',  
        'Operating System :: POSIX :: Linux',        
        'Programming Language :: Python :: 3.9',
    ],
)