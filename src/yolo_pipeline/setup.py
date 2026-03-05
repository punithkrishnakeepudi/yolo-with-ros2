from setuptools import find_packages, setup

package_name = 'yolo_pipeline'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='punith',
    maintainer_email='punithkrishna147@gmail.com',
    description='Real-time YOLOv8 object detection pipeline for ROS2 Jazzy',
    license='MIT',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            'camera_publisher = yolo_pipeline.camera_publisher:main',
            'yolo_processor = yolo_pipeline.yolo_processor:main',
            'ui_node = yolo_pipeline.ui_node:main',
        ],
    },
)
