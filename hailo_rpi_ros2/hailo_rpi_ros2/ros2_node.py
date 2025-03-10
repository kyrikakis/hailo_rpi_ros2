# Copyright 2025 Stefanos Kyrikakis
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# !/usr/bin/env python3

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image, CompressedImage
from hailo_rpi_ros2_interfaces.srv import AddPerson
from hailo_rpi_ros2 import face_detection
import cv2


class HailoDetection(Node):
    def __init__(self):
        Node.__init__(self, 'hailo_detection')

        self.image_publisher_compressed = self.create_publisher(
            CompressedImage, '/camera/image_raw/compressed', 10)
        self.image_publisher_ = self.create_publisher(Image, '/camera/image_raw', 10)

        self.srv = self.create_service(AddPerson, '~/add_person', self.add_person_callback)

        self.face_detection = face_detection.FaceDetection(self.frame_callback)

    def add_person_callback(self, request: AddPerson.Request, response: AddPerson.Response):
        self.get_logger().info(f'Incoming request: Add person {request.name}')
        response.success = True
        response.message = "Person added"
        return response

    def frame_callback(self, frame: cv2.UMat):
        ret, buffer = cv2.imencode('.jpg', frame)
        msg = CompressedImage()
        msg.header.frame_id = 'camera_frame'
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.format = "jpeg"
        msg.data = buffer.tobytes()

        self.image_publisher_compressed.publish(msg)


def main(args=None):
    rclpy.init(args=args)

    detection = HailoDetection()

    rclpy.spin(detection)
    # Destroy the node explicitly
    # (optional - otherwise it will be done automatically
    # when the garbage collector destroys the node object)
    detection.detection_thread.join()
    detection.destroy_node()
    rclpy.shutdown()


# Main program logic follows:
if __name__ == '__main__':
    main()
