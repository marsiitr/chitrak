from setuptools import find_packages, setup
from glob import glob

package_name = 'chitrak_bringup'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),

        # Install launch files
        ('share/' + package_name + '/launch', glob('launch/*.launch.py')),
        # Install config files
        ('share/' + package_name + '/config', glob('config/*.rviz')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='shravan',
    maintainer_email='devashravan7@gmail.com',
    description='Bringup package for Chitrak robot',
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
