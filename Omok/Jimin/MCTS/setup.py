from setuptools import setup
from torch.utils.cpp_extension import CppExtension, BuildExtension

setup(
    name='MCTS_cpp',
    ext_modules=[
        CppExtension(
            name='MCTS_cpp',
            sources=['mcts.cpp', 'binding.cpp'],
            extra_compile_args=["-mmacosx-version-min=11.0"],
            libraries=["torch"]
        )
    ],
    cmdclass={
        'build_ext': BuildExtension
    }
)