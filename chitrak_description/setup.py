from setuptools import find_packages, setup
from glob import glob

package_name = 'chitrak_description'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),

        # Install URDF files
        ('share/' + package_name + '/urdf', glob('urdf/*.urdf')),
        # Install Mesh files
        ('share/' + package_name + '/meshes', glob('meshes/*.STL')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Shravan Deva',
    maintainer_email='devashravan7@gmail.com',
    description='URDF description for the Chitrak robot',
    license='MIT',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
        ],
    },
)
