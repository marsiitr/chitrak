from pynput import keyboard
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist


class KeyboardTeleop(Node):
    def __init__(self):
        super().__init__('keyboard_teleop')
        self.publisher_ = self.create_publisher(Twist, '/chitrak/cmd_vel', 10)

        # Velocity state
        self.vx = 0.0
        self.vy = 0.0
        self.wz = 0.0

        # Step sizes
        self.linear_step = 1 # cm/s
        self.angular_step = 5 # degrees/s

        # Start keyboard listener
        self.listener = keyboard.Listener(on_press=self.on_press)
        self.listener.start()

        self.timer = self.create_timer(0.1, self.publish_velocity) # 10 Hz

        self.get_logger().info("Keyboard teleop node started.")
        self.get_logger().info("Use WASD for linear, QE for rotation, X to stop")
    
    def on_press(self, key):
        try:
            self.update_velocity(key.char)
        except AttributeError:
            pass

    def publish_velocity(self):
        msg = Twist()
        msg.linear.x = self.vx
        msg.linear.y = self.vy
        msg.angular.z = self.wz

        self.publisher_.publish(msg)

    def update_velocity(self, key):
        if key == 'w':
            self.vx += self.linear_step
        elif key == 's':
            self.vx -= self.linear_step
        elif key == 'a':
            self.vy += self.linear_step
        elif key == 'd':
            self.vy -= self.linear_step
        elif key == 'q':
            self.wz += self.angular_step
        elif key == 'e':
            self.wz -= self.angular_step
        elif key == 'x':
            self.vx = 0.0
            self.vy = 0.0
            self.wz = 0.0

        # Round to avoid floating point accumulation errors
        self.vx = round(self.vx, 2)
        self.vy = round(self.vy, 2)
        self.wz = round(self.wz, 2)

        self.get_logger().info(f"vx: {self.vx:.2f}, vy: {self.vy:.2f}, wz: {self.wz:.2f}")

def main(args=None):
    rclpy.init(args=args)
    keyboard_teleop = KeyboardTeleop()

    try:
        rclpy.spin(keyboard_teleop)
    finally:
        keyboard_teleop.listener.stop()
        keyboard_teleop.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()    
