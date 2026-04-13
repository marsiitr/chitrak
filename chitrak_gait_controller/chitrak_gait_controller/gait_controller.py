import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from chitrak_msgs.msg import LegGaitParams
from chitrak_msgs.msg import LegGaitParamsArray
import math

class GaitController(Node):
    def __init__(self):
        super().__init__('gait_controller')
        
        # Geometry parameters
        self.declare_parameter('geometry.length', 30.0)
        self.declare_parameter('geometry.width', 20.0)
        self.L = self.get_parameter('geometry.length').value
        self.W = self.get_parameter('geometry.width').value

        # Gait parameters
        self.declare_parameter('gait.step_height', 2.0)
        self.declare_parameter('gait.min_step_frequency', 0.25)
        self.declare_parameter('gait.max_step_frequency', 1.0)
        self.declare_parameter('gait.max_step_length', 5.0)
        self.declare_parameter('gait.type', 'walk')

        self.step_height = self.get_parameter('gait.step_height').value
        self.min_step_frequency = self.get_parameter('gait.min_step_frequency').value
        self.max_step_frequency = self.get_parameter('gait.max_step_frequency').value
        self.max_step_length = self.get_parameter('gait.max_step_length').value
        self.gait_type = self.get_parameter('gait.type').value

        self.last_cmd_vel = Twist()
        self.subscription = self.create_subscription(Twist, '/chitrak/cmd_vel', self.cmd_vel_callback, 10)

        self.publisher_ = self.create_publisher(LegGaitParamsArray, '/chitrak/leg_gait_params', 10)
        self.timer = self.create_timer(0.1, self.publish_gait_params) # 10 Hz

    def cmd_vel_callback(self, msg):
        self.last_cmd_vel = msg

    def compute_step_params(self, speed):
        if speed < 0.1:
            return 0.0, 0.0

        # try max frequency first
        f = self.max_step_frequency
        d = speed / f

        if d > self.max_step_length:
            d = self.max_step_length
            f = speed / d

            # clamp frequency also
            f = min(max(f, self.min_step_frequency), self.max_step_frequency)

        return d, f
    
    def publish_gait_params(self):
        vx = self.last_cmd_vel.linear.x
        vy = self.last_cmd_vel.linear.y
        omega = self.last_cmd_vel.angular.z

        # Inverse differential kinematics
        vr = vx + (self.W / 2.0) * omega
        vl = vx - (self.W / 2.0) * omega
        vf = vy + (self.L / 2.0) * omega
        vb = vy - (self.L / 2.0) * omega

        # Leg speeds and angles
        v_fr = math.hypot(vr, vf)
        v_bl = math.hypot(vl, vb)
        v_fl = math.hypot(vl, vf)
        v_br = math.hypot(vr, vb)

        theta_fr = math.degrees(math.atan2(vf, vr)) if v_fr > 0 else 0.0
        theta_bl = math.degrees(math.atan2(vb, vl)) if v_bl > 0 else 0.0
        theta_fl = math.degrees(math.atan2(vf, vl)) if v_fl > 0 else 0.0
        theta_br = math.degrees(math.atan2(vb, vr)) if v_br > 0 else 0.0

        msg = LegGaitParamsArray()
        msg.leg_gait_params = []

        leg_velocities = [
            (v_fr, theta_fr),
            (v_bl, theta_bl),
            (v_fl, theta_fl),
            (v_br, theta_br)
        ]

        for i, (v, theta) in enumerate(leg_velocities):
            leg_gait_params = LegGaitParams()

            step_length, frequency = self.compute_step_params(v)
            leg_gait_params.step_length = step_length
            leg_gait_params.step_direction = theta
            leg_gait_params.step_height = self.step_height

            leg_gait_params.frequency = frequency
            if self.gait_type == 'walk':
                # FR=0, BL=0.25, FL=0.5, BR=0.75
                leg_gait_params.phase = 0.25 * i
            elif self.gait_type == 'trot':
                # FR and BL in phase, FL and BR in phase
                leg_gait_params.phase = 0.5 * (i % 2)

            msg.leg_gait_params.append(leg_gait_params)
        
        self.get_logger().debug(f"{'leg':<3} {'step_length':>10} {'step_direction':>10} {'step_height':>10} {'frequency':>8} {'phase':>8}")
        for i, leg in enumerate(['FR', 'BL', 'FL', 'BR']):
            lgp = msg.leg_gait_params[i]
            self.get_logger().debug(
                f"{leg:<3} "
                f"{lgp.step_length:>10.2f} "
                f"{lgp.step_direction:>10.2f} "
                f"{lgp.step_height:>10.2f} "
                f"{lgp.frequency:>8.2f} "
                f"{lgp.phase:>8.2f}"
            )
        self.publisher_.publish(msg)

def main(args=None):
    rclpy.init(args=args)
    gait_controller = GaitController()
    
    try:
        rclpy.spin(gait_controller)
    finally:
        gait_controller.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
