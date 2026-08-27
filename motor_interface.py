"""
Simple interface for controlling a BLDC motor via an ODESC v4.2 (ODrive v3.6-compatible)
motor controller board.

Assumes:
  - Firmware is already flashed (v0.5.x line, standard for ODrive v3.x hardware)
  - Motor + encoder calibration has already been completed and saved
    (odrv0.axis0.motor.config.pre_calibrated = True,
     odrv0.axis0.encoder.config.pre_calibrated = True)
    If that's not saved yet, this script will still work, it'll just re-run
    calibration each time you call activate().
"""

import sys
import time
import odrive
from odrive.enums import (
    AXIS_STATE_IDLE,
    AXIS_STATE_FULL_CALIBRATION_SEQUENCE,
    AXIS_STATE_CLOSED_LOOP_CONTROL,
    CONTROL_MODE_POSITION_CONTROL,
    CONTROL_MODE_VELOCITY_CONTROL,
    CONTROL_MODE_TORQUE_CONTROL,
)


class MotorController:
    def __init__(self):
        self.odrv = None
        self.axis = None

    # ---------- Connection ----------

    def connect(self, timeout=15):
        """Find and connect to the ODESC board over USB."""
        print("Looking for ODESC board...")
        self.odrv = odrive.find_any(timeout=timeout)
        self.axis = self.odrv.axis0
        print(f"Connected. Bus voltage: {self.odrv.vbus_voltage:.2f} V")
        return self

    def _require_connection(self):
        if self.odrv is None:
            raise RuntimeError("Not connected yet — call connect() first.")

    def _check_errors(self, context=""):
        """
        Check for any latched fault and, if one is found, print a diagnostic
        snapshot (velocity, measured current, bus voltage) to help figure out
        what was happening at the time. Returns True if an error was found.
        """
        if self.axis.error != 0 or self.axis.motor.error != 0 or self.axis.encoder.error != 0:
            where = f" during {context}" if context else ""
            print(f"Fault detected{where}:")
            print(f"  Axis error: {self.axis.error}, Motor error: {self.axis.motor.error}, "
                  f"Encoder error: {self.axis.encoder.error}")
            print(f"  Velocity at detection: {self.axis.encoder.vel_estimate:.3f} turns/s")
            print(f"  Measured current (Iq): {self.axis.motor.current_control.Iq_measured:.2f} A")
            print(f"  Bus voltage: {self.odrv.vbus_voltage:.2f} V")
            return True
        return False

    # ---------- Activate / Deactivate ----------

    def activate(self, calibrate_if_needed=True):
        """
        Bring the motor into closed-loop control so it can hold position
        and respond to move commands.
        """
        self._require_connection()

        # Error flags latch (stay set) even after the root cause is gone.
        # Clear them here so a past fault doesn't silently block this
        # activation attempt.
        if self.axis.error != 0 or self.axis.motor.error != 0 or self.axis.encoder.error != 0:
            print(
                f"Clearing previous errors before activating "
                f"(axis: {self.axis.error}, motor: {self.axis.motor.error}, "
                f"encoder: {self.axis.encoder.error})..."
            )
            self.axis.error = 0
            self.axis.motor.error = 0
            self.axis.encoder.error = 0

        already_calibrated = (
            self.axis.motor.config.pre_calibrated
            and self.axis.encoder.config.pre_calibrated
        )

        if calibrate_if_needed and not already_calibrated:
            print("Motor/encoder not marked as pre-calibrated — running calibration sequence...")
            self.axis.requested_state = AXIS_STATE_FULL_CALIBRATION_SEQUENCE
            time.sleep(1)
            while self.axis.current_state != AXIS_STATE_IDLE:
                time.sleep(0.1)
            if self.axis.error != 0:
                raise RuntimeError(f"Calibration failed, axis error code: {self.axis.error}")

        # Make sure we're in position control mode for the move() method below
        self.axis.controller.config.control_mode = CONTROL_MODE_POSITION_CONTROL

        self.axis.requested_state = AXIS_STATE_CLOSED_LOOP_CONTROL
        time.sleep(0.2)

        if self.axis.current_state != AXIS_STATE_CLOSED_LOOP_CONTROL:
            self._check_errors(context="activation")
            raise RuntimeError("Failed to enter closed-loop control.")

        # Motor holds its current position as soon as it goes active, so set
        # the setpoint to wherever it already is to avoid a surprise jump.
        self.axis.controller.input_pos = self.axis.encoder.pos_estimate
        print("Motor active and holding position.")

    def deactivate(self):
        """Turn off closed-loop control. Motor goes limp (idle)."""
        self._require_connection()
        self.axis.requested_state = AXIS_STATE_IDLE
        print("Motor deactivated (idle).")

    # ---------- Movement ----------

    def move_to(self, turns):
        """
        Command the motor to a target position, given in encoder 'turns'
        (e.g. 1.0 = one full revolution from the calibration zero-point).
        """
        self._require_connection()
        if self.axis.current_state != AXIS_STATE_CLOSED_LOOP_CONTROL:
            raise RuntimeError("Motor isn't active — call activate() first.")

        # Ensure we're in position mode (spin() below switches to velocity
        # mode, so a move_to() command should always bring it back).
        self.axis.controller.config.control_mode = CONTROL_MODE_POSITION_CONTROL
        self.axis.controller.input_pos = turns
        print(f"Moving to {turns} turns...")

        time.sleep(0.1)
        if self._check_errors(context="move_to"):
            raise RuntimeError("Fault occurred while moving — see diagnostic above.")

    def nudge(self, delta_turns):
        """Move relative to the current setpoint, e.g. nudge(0.25) = quarter turn forward."""
        self._require_connection()
        current_target = self.axis.controller.input_pos
        self.move_to(current_target + delta_turns)

    def current_position(self):
        """Read the motor's current estimated position, in turns."""
        self._require_connection()
        return self.axis.encoder.pos_estimate

    # ---------- Continuous velocity spin ----------

    def spin(self, turns_per_sec):
        """
        Continuously spin at a target speed (in turns/second) until told
        otherwise. The board holds this speed on its own — this method just
        sets the target once and returns immediately.
        """
        self._require_connection()
        if self.axis.current_state != AXIS_STATE_CLOSED_LOOP_CONTROL:
            raise RuntimeError("Motor isn't active — call activate() first.")

        self.axis.controller.config.control_mode = CONTROL_MODE_VELOCITY_CONTROL
        self.axis.controller.input_vel = turns_per_sec
        print(f"Spinning at {turns_per_sec} turns/s until told otherwise...")

        time.sleep(0.1)
        if self._check_errors(context="spin"):
            raise RuntimeError("Fault occurred while spinning — see diagnostic above.")

    def stop_spin(self):
        """
        Stop a continuous spin and return to holding whatever position the
        motor happens to be at right now (switches back to position mode,
        same idea as the position-hold behavior in activate()).
        """
        self._require_connection()
        current_pos = self.axis.encoder.pos_estimate
        self.axis.controller.config.control_mode = CONTROL_MODE_POSITION_CONTROL
        self.axis.controller.input_pos = current_pos
        print(f"Stopped spinning. Holding position at {current_pos:.3f} turns.")

    def spin_with_kick(self, turns_per_sec, kick_torque=None, kick_duration=0.15):
        """
        Break static friction with a brief, bounded torque pulse (in Nm) using
        torque-control mode, then hand off to the normal velocity controller
        once the shaft is already moving. This avoids relying on the velocity
        integrator alone to slowly climb toward breakaway torque, which has
        no built-in ceiling and can run away before it succeeds (see our
        current-instability faults from testing high integrator gains).
        """
        self._require_connection()
        if self.axis.current_state != AXIS_STATE_CLOSED_LOOP_CONTROL:
            raise RuntimeError("Motor isn't active — call activate() first.")

        if kick_torque is None:
            # Conservative default: torque equivalent to 15% of current_lim.
            kick_torque = (
                self.axis.motor.config.current_lim
                * 0.15
                * self.axis.motor.config.torque_constant
            )

        direction = 1 if turns_per_sec >= 0 else -1

        print(f"Applying breakaway kick: {direction * kick_torque:.3f} Nm for {kick_duration:.2f}s...")

        # The torque-mode velocity limiter (a newer-firmware safety feature)
        # isn't present on every firmware version — your board's 0.5.1
        # doesn't have it, confirmed by the AttributeError this raised
        # before this fix. Check for it rather than assume it exists, so
        # this works whether or not a given board has it.
        has_vel_limiter_toggle = hasattr(
            self.axis.controller.config, "enable_torque_mode_vel_limit"
        )
        if has_vel_limiter_toggle:
            prior_limiter_setting = self.axis.controller.config.enable_torque_mode_vel_limit
            self.axis.controller.config.enable_torque_mode_vel_limit = False

        self.axis.controller.config.control_mode = CONTROL_MODE_TORQUE_CONTROL
        self.axis.controller.input_torque = direction * kick_torque

        # Confirm the command actually took effect, rather than assuming it
        # did — a silently-rejected write would look identical to "nothing
        # happened" in every reading we've taken so far.
        actual_mode = self.axis.controller.config.control_mode
        actual_input_torque = self.axis.controller.input_torque
        torque_lim = self.axis.motor.config.torque_lim
        print(f"    confirming: control_mode={actual_mode} (torque mode is "
              f"{int(CONTROL_MODE_TORQUE_CONTROL)}), input_torque={actual_input_torque:.3f} Nm, "
              f"torque_lim={torque_lim}")

        # Sample repeatedly *during* the kick itself, rather than sleeping
        # blindly and only checking afterward — a 0.15s pulse is too short to
        # observe by manually calling watch() after the fact. Iq_setpoint
        # (what the controller is trying to achieve) is included alongside
        # Iq_measured (what actually happened), so we can tell whether a
        # failed command or a failed delivery is the issue.
        sample_interval = 0.02
        samples = max(1, int(kick_duration / sample_interval))
        for _ in range(samples):
            pos = self.axis.encoder.pos_estimate
            vel = self.axis.encoder.vel_estimate
            iq_setpoint = self.axis.motor.current_control.Iq_setpoint
            iq_measured = self.axis.motor.current_control.Iq_measured
            print(f"    kick sample: pos={pos:7.3f} turns | vel={vel:7.3f} turns/s | "
                  f"Iq_setpoint={iq_setpoint:6.2f} A | Iq_measured={iq_measured:6.2f} A")
            time.sleep(sample_interval)

        # Restore the limiter now that the kick is over, if it exists here.
        if has_vel_limiter_toggle:
            self.axis.controller.config.enable_torque_mode_vel_limit = prior_limiter_setting

        if self._check_errors(context="breakaway kick"):
            self.deactivate()
            raise RuntimeError("Fault occurred during breakaway kick — see diagnostic above.")

        print(f"Handing off to velocity control at {turns_per_sec} turns/s...")
        self.axis.controller.config.control_mode = CONTROL_MODE_VELOCITY_CONTROL
        self.axis.controller.input_vel = turns_per_sec

        time.sleep(0.1)
        if self._check_errors(context="spin_with_kick handoff"):
            raise RuntimeError("Fault occurred after handoff to velocity control — see diagnostic above.")

    # ---------- Velocity controller tuning ----------

    def get_velocity_gains(self):
        """Read and print the current velocity-loop gains."""
        self._require_connection()
        vg = self.axis.controller.config.vel_gain
        vig = self.axis.controller.config.vel_integrator_gain
        print(f"vel_gain: {vg:.6f}   vel_integrator_gain: {vig:.6f}   "
              f"(ratio integrator/proportional: {vig / vg:.2f}x)")
        return vg, vig

    def set_velocity_integrator_gain(self, value):
        """Set and persist a new vel_integrator_gain."""
        self._require_connection()
        self.axis.controller.config.vel_integrator_gain = value
        self.odrv.save_configuration()
        print(f"vel_integrator_gain set to {value} and saved.")

    def set_torque_constant_from_kv(self, kv):
        """
        Set motor.config.torque_constant correctly for a motor with the given
        KV rating (Nm/A = 8.27 / KV). The stock default (0.04) is very likely
        wrong for your specific motor, which would make input_torque values
        in spin_with_kick() inaccurate.
        """
        self._require_connection()
        constant = 8.27 / kv
        self.axis.motor.config.torque_constant = constant
        self.odrv.save_configuration()
        print(f"torque_constant set to {constant:.5f} Nm/A (for {kv} KV) and saved.")

    def status(self):
        self._require_connection()
        print(f"State: {self.axis.current_state}")
        print(f"Position: {self.axis.encoder.pos_estimate:.3f} turns")
        print(f"Velocity: {self.axis.encoder.vel_estimate:.3f} turns/s")
        print(f"Measured current (Iq): {self.axis.motor.current_control.Iq_measured:.2f} A "
              f"(limit: {self.axis.motor.config.current_lim:.1f} A)")
        print(f"Axis error: {self.axis.error}, Motor error: {self.axis.motor.error}, "
              f"Encoder error: {self.axis.encoder.error}")

    def watch(self, duration=5.0, interval=0.2):
        """
        Repeatedly print position, velocity, and current for `duration`
        seconds (sampled every `interval` seconds). Useful for watching how
        the motor responds right after a spin()/move_to() command — e.g.
        seeing current build up over time, or spotting overshoot/oscillation
        that a single status() snapshot would miss. Stops early if a fault
        is detected, if velocity overshoots far beyond a commanded spin()
        target (a sign of too-aggressive integrator tuning), or if you press
        Ctrl+C.
        """
        self._require_connection()
        target = None
        if self.axis.controller.config.control_mode == CONTROL_MODE_VELOCITY_CONTROL:
            target = self.axis.controller.input_vel

        steps = max(1, int(duration / interval))
        print(f"Watching for {duration:.1f}s (every {interval:.1f}s)... Ctrl+C to stop early.")
        try:
            for _ in range(steps):
                pos = self.axis.encoder.pos_estimate
                vel = self.axis.encoder.vel_estimate
                iq = self.axis.motor.current_control.Iq_measured
                print(f"  pos={pos:7.3f} turns | vel={vel:7.3f} turns/s | Iq={iq:6.2f} A")

                if self._check_errors(context="watch"):
                    self.deactivate()
                    print("Fault detected — motor deactivated automatically.")
                    break

                if target is not None and abs(vel) > abs(target) * 3 + 0.05:
                    print("Velocity overshooting far beyond the commanded target — "
                          "stopping automatically (possible unstable tuning).")
                    self.stop_spin()
                    break

                time.sleep(interval)
        except KeyboardInterrupt:
            print("Watch stopped early.")


# ---------------------------------------------------------------------------
# Simple interactive menu on top of the class above
# ---------------------------------------------------------------------------

def print_menu():
    menu = """
    Motor control:
      [a] Activate
      [m] Move to position (turns)
      [n] Nudge by relative amount
      [v] Spin continuously at a speed (turns/s)
      [k] Spin with breakaway kick (for stiction)
      [x] Stop spinning (hold position)
      [g] Show velocity-loop gains
      [i] Set vel_integrator_gain
      [t] Set torque_constant from motor KV (one-time setup)
      [s] Show status
      [w] Watch live readings for a few seconds
      [d] Deactivate
      [q] Quit (deactivates first)
    """
    print(menu)


def run_menu():
    motor = MotorController()
    motor.connect()

    try:
        while True:
            print_menu()
            choice = input("> ").strip().lower()
            if choice == "a":
                motor.activate()
            elif choice == "m":
                turns = float(input("Target position (turns): "))
                motor.move_to(turns)
            elif choice == "n":
                delta = float(input("Relative move (turns): "))
                motor.nudge(delta)
            elif choice == "v":
                speed = float(input("Speed to spin at (turns/s): "))
                motor.spin(speed)
            elif choice == "k":
                speed = float(input("Speed to spin at once moving (turns/s): "))
                motor.spin_with_kick(speed)
            elif choice == "x":
                motor.stop_spin()
            elif choice == "g":
                motor.get_velocity_gains()
            elif choice == "i":
                value = float(input("New vel_integrator_gain: "))
                motor.set_velocity_integrator_gain(value)
            elif choice == "t":
                kv = float(input("Motor KV rating: "))
                motor.set_torque_constant_from_kv(kv)
            elif choice == "s":
                motor.status()
            elif choice == "w":
                secs = float(input("Watch for how many seconds? "))
                motor.watch(duration=secs)
            elif choice == "d":
                motor.deactivate()
            elif choice == "q":
                motor.deactivate()
                break
            else:
                print(f"'{choice}' isn't a valid option.")
    except KeyboardInterrupt:
        pass
    finally:
        # Safety net: no matter how the program exits, don't leave the motor
        # energized and unattended.
        try:
            motor.deactivate()
        except Exception:
            pass
        print("Exited safely.")


if __name__ == "__main__":
    run_menu()