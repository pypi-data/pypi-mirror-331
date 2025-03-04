from setuptools import setup, find_packages
import sys

# Define required packages
required_packages = [
    "numpy",
    "scipy",
    "librosa",
    "h5py",
    "soundfile",
    "matplotlib",
    "pyyaml"
]

# Chainer and CuPy requirements
# Note: Chainer is no longer maintained but required for this codebase
if sys.version_info < (3, 9):
    # For older Python versions where original Chainer is compatible
    required_packages.append("chainer")
    # CuPy note - we leave it as an optional dependency
else:
    # For newer Python versions, note that Chainer support is limited
    print("NOTE: You're using Python 3.9+ - Chainer has limited support for this version.")
    print("      You may need to install Chainer manually if you encounter issues.")
    # Add chainer anyway, but it might not work perfectly
    required_packages.append("chainer")

# Note: CuPy is intentionally left out as it requires specific CUDA versions
# Users should install the appropriate CuPy version manually based on their CUDA setup

setup(
    name="eend",
    version="0.1.0",
    description="End-to-End Neural Diarization",
    author="Original: Hitachi, Ltd. (Yusuke Fujita); Module adaptation by Claude",
    packages=find_packages(),
    install_requires=required_packages,
    extras_require={
        # For users who want to use GPU, they need to install CuPy manually
        # based on their CUDA version
        'gpu': [],  # This is intentionally empty as it's just a reminder
    },
    entry_points={
        "console_scripts": [
            "eend=eend:cli",
            "eend-train=eend.bin.train:main",
            "eend-infer=eend.bin.infer:main",
            "eend-make-rttm=eend.bin.make_rttm:main",
            "eend-make-mixture=eend.bin.make_mixture:main",
            "eend-random-mixture=eend.bin.random_mixture:main",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
)