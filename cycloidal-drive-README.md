# High-Torque Two-Stage Cycloidal Drive for Robotic Arm

A custom-designed, 3D-printed two-stage cycloidal drive developed as the transmission for a high-torque robotic arm joint.

The project explores the design, manufacturing, and control of a high-ratio transmission capable of converting the high-speed, relatively low-torque output of a BLDC motor into the high-torque, low-speed motion required for a robotic arm.

<!-- PHOTO: Hero shot — full assembled gearbox, clean background, this is the first thing a viewer sees -->
<img src="images/hero.jpg" alt="Assembled two-stage cycloidal drive" width="700">

> **Current status:** Mechanical assembly completed and connected to the BLDC motor. The theoretical reduction ratio is **121:1**, although the actual reduction ratio has not yet been experimentally verified. It is currently mounted to a bracket that will serve as the base joint of a robotic arm.

---

## Project Overview

The transmission is a custom **two-stage cycloidal drive** designed to serve as a high-torque joint actuator for a robotic arm.

The original design target was a **121:1 overall reduction ratio**, allowing a relatively compact BLDC motor to produce substantially higher torque at the output.

The gearbox was designed, parametrically modeled, 3D printed, assembled, and connected to the motor. Future testing will characterize its actual reduction ratio, torque capacity, backlash, friction, and efficiency.

### Target Specifications

| Specification              |                    Design Target |
| --------------------------- | -------------------------------: |
| Application                 |                Robotic arm joint |
| Motor                       |                Flipsky 6374 BLDC |
| Theoretical reduction       |                        **121:1** |
| Experimental reduction      |             **Not yet measured** |
| Target payload              |                            25 kg |
| Maximum lever arm           |                              1 m |
| Static payload torque       |                         ~245 N·m |
| Target output torque        |                         ~490 N·m |
| Drive type                  |              Two-stage cycloidal |
| Manufacturing                | FDM 3D printing + metal hardware |
| Primary prototype material   |                             PETG |
| Bearings                     |                    Ball bearings |
| Fasteners                    |  M3-M6 screws + heat-set inserts |

<!-- PHOTO: Side-by-side or annotated shot of the gearbox next to the BLDC motor for scale -->
<img src="images/overview-scale.jpg" alt="Gearbox mounted to BLDC motor, scale reference" width="700">

---

# Design Philosophy

The project was designed around several goals:

### High torque density

The robotic arm requires substantially more torque than the BLDC motor can provide directly. The gearbox therefore uses a high reduction ratio to trade rotational speed for output torque.

### Compact transmission

Cycloidal drives can achieve very high reduction ratios within a relatively compact package, making them attractive for robotic joints where gearbox size and weight are important.

### Manufacturability

Rather than designing around specialized industrial manufacturing processes, the gearbox was designed to be manufacturable using accessible tools and FDM 3D printing.

### Modular design

The transmission is divided into stages and assemblies so that individual components can be redesigned or replaced without completely rebuilding the mechanism.

### Iterative development

The design was developed through repeated cycles of:

**CAD → 3D print → assembly → testing → identify problems → redesign**

This resulted in several design changes involving bearing placement, tolerances, support structures, surface flatness, and component alignment.

---

# Transmission Architecture

The gearbox consists of **two cycloidal reduction stages**.

The first stage receives the high-speed input from the BLDC motor and produces a reduced-speed intermediate motion.

The second stage further reduces this motion and produces the final output.

The drive uses a nontraditional architecture in which the **outer ring assembly of the second stage acts as the final output**, rather than using the central cycloidal disc as the conventional output member.

This allows the second stage to act as a coupler between the first stage and the final output, but also creates additional requirements for maintaining concentricity and structural stability.

<!-- PHOTO: Exploded CAD render of the full two-stage architecture, labeled stage 1 / stage 2 / output ring -->
<img src="images/architecture-exploded.jpg" alt="Exploded view of two-stage cycloidal architecture" width="700">

---

# Reduction Ratio

The target reduction ratio was designed to be 121:1

The two-stage configuration was selected to achieve this ratio while keeping the number of rollers and individual components manageable.

Each stage follows the cycloidal relationship in which the number of lobes is one less than the number of rollers.

Thus, the first stage contains 11 lobes on the cycloidal disc and 12 rollers, while the second stage contains 10 lobes on the cycloidal disc and 11 rollers.

The first-stage transmission ratio is calculated based on the following expression:

$$
u_1 = -\frac{Z_{11}}{Z_{12} - Z_{11}}
$$

where $Z_{11}$ is the number of teeth of the first-stage cycloidal disc (11) and $Z_{12}$ is the number of rollers of the stationary ring gear of the first stage (12).

The second-stage transmission ratio is calculated based on the following expression:

$$
u_2 = -\frac{Z_{21}}{Z_{22} - Z_{21}}
$$

where $Z_{21}$ is the number of teeth of the second-stage cycloidal disc (10) and $Z_{22}$ is the number of rollers of the rotatable ring gear of the second stage (11).

In the case of a "one tooth difference" cycloidal drive,

$$
Z_{12} - Z_{11} = 1, \qquad Z_{22} - Z_{21} = 1,
$$

as is the case here, the final expression for the speed reducer ratio $u_{\mathrm{CR}}$ is

$$
u_{\mathrm{CR}} = Z_{11} \cdot Z_{22} = 11 \cdot 12 = 121
$$

### Important distinction

**121:1 is the theoretical/design ratio, not a verified experimental measurement.**

Because the complete gearbox has now been assembled and connected to the motor, the next step is to measure the actual input-to-output angular displacement directly.

The measured ratio may differ from the theoretical value due to:

* Manufacturing tolerances
* Assembly errors
* Backlash
* Elastic deformation
* Slippage
* Incorrect assumptions in the theoretical model

<!-- PHOTO: Close-up of a single cycloidal disc showing the lobe profile -->
<img src="images/cycloidal-disc-closeup.jpg" alt="Cycloidal disc lobe profile close-up" width="700">

---

# Cycloidal Geometry

The cycloidal discs were generated parametrically using the primary design parameters:

* Ring roller PCD: **176 mm**
* Roller radius: **11 mm**
* Eccentricity: **3 mm**
* Stage 1 rollers: **12**
* Stage 1 lobes: **11**

The parametric approach allows the cycloidal profile to be regenerated when changing:

* Number of rollers
* PCD
* Roller diameter
* Eccentricity
* Reduction ratio
* Manufacturing tolerances

This was particularly useful during the iterative development process because changes to the gearbox geometry could be propagated without manually rebuilding the cycloidal profile.

<!-- PHOTO: Screenshot of the parametric CAD (Onshape) showing the driving dimensions/variables table -->
<img src="images/parametric-cad.jpg" alt="Parametric CAD model of cycloidal profile" width="700">

---

# Bearing System

The gearbox uses multiple ball bearings to support and guide the rotating assemblies.

A major design challenge was supporting the large second-stage output.

A single large bearing would have provided a simple solution, but its cost was undesirable for the prototype.

Instead, the design uses **multiple smaller bearings distributed around the circumference** to approximate the support provided by a larger bearing.

This distributes the radial load around the gearbox while keeping the components relatively inexpensive and accessible.

<!-- PHOTO: Bearing ring layout — components before assembly, or CAD cross-section showing bearing placement -->
<img src="images/bearing-layout.jpg" alt="Distributed bearing layout around gearbox circumference" width="700">

---

# Mechanical Components

### Motor

**Flipsky 6374 BLDC**

Specifications:

* Maximum power: 3250 W
* Maximum current: 85 A
* Maximum voltage: 12S
* Maximum torque: 8 N·m
* Motor resistance: 0.05 Ω
* Diameter: 63 mm
* Length: 74 mm
* Weight: 0.86 kg
* 14 poles
* Integrated Hall-effect sensors

### Motor Controller

**ODESC v4.2**

Specifications:

* Working Voltage: 8V–56V (56V model)
* Continuous Current: 70A
* Peak Current: 120A
* Microprocessor: STM32F405RGT6
* Supported Motor Type: Brushless DC motor (BLDC) / FOC
* Braking Methods: Power resistors and battery energy recycling
* Physical Dimensions: 63mm × 58mm × 30mm
* Weight: 70g

### Encoder

**AS5047P**

Specifications:

* Type: 14-bit magnetic rotary position sensor
* Resolution: 16,384 positions per rotation
* Speed: Operates up to 28,000 RPM
* Accuracy: Max 0.34-degree error
* Voltage: 3.3V or 5V operation
* Outputs: SPI, ABI, UVW, and PWM
* Package: 14-pin TSSOP

<!-- PHOTO: Motor + controller + encoder laid out together, or wired/mounted on the bench -->
<img src="images/electronics-layout.jpg" alt="BLDC motor, ODESC controller, and AS5047P encoder" width="700">

### Shaft

A segmented shaft printed out of PETG is used to transmit torque between the motor and gearbox. The segmented pieces snap-fit to each other and are further reinforced via screws.

A keyed connection was selected to provide positive mechanical torque transmission rather than relying solely on friction, and to assemble easily with the motor's shaft.

### Fasteners

* M2-M6 screws
* M2-M6 heat-set threaded inserts
* M3-M6 nuts and washers
* M3 and M6 Nylon Locknuts

Heat-set inserts provide reusable threaded connections in the 3D-printed components.

---

# Manufacturing

The prototype was primarily manufactured using **FDM 3D printing**.

PETG was used for the initial prototype because of its accessibility and relatively good mechanical properties.

Carbon-fiber reinforced nylon and PETG was also investigated as a potential material for higher-performance components, specifically for the cycloidal discs and shaft components.

The printed components required significant post-processing, including:

* Support removal
* Bearing installation
* Heat-set insert installation
* Surface sanding
* Dimensional adjustment
* Assembly and alignment

<!-- PHOTO: Printed parts fresh off the printer / mid post-processing (support removal, sanding, etc.) -->
<img src="images/manufacturing-postprocess.jpg" alt="3D printed components during post-processing" width="700">

---

# Engineering Challenges

Several problems were encountered during development.

### Surface flatness

Large surfaces printed over support material were not perfectly flat, causing the two halves of the first-stage ring gear to sit unevenly.

This introduced alignment issues with the base piece alignment.

The problem was partially corrected through sanding, but it also demonstrated the limitations of relying on large FDM surfaces for precision alignment when printing with supports.

<!-- PHOTO: The flatness issue itself — e.g. a gap/light-gap photo between the two ring gear halves, or a warped part -->
<img src="images/flatness-issue.jpg" alt="Ring gear surface flatness issue" width="700">

### Bearing installation

Support material remaining inside bearing pockets interfered with installation.

This led to changes in support geometry and highlighted the importance of designing parts around post-processing requirements, rather than only considering the final CAD geometry.

### Component tolerances

The gearbox contains many interacting components, so relatively small dimensional errors can accumulate.

The physical prototype was therefore used to determine which tolerances needed to be modified for future iterations.

### Structural considerations

The gearbox is intended to produce very high output torque, meaning that printed components cannot simply be evaluated based on their nominal material strength.

Print orientation, layer adhesion, fastener locations, bearing loads, and stress concentrations all need to be considered.

---

# Development Timeline

## 1. Concept & Design

**Date:** May 2025

Inspired by ["A New Design of a Two-Stage Cycloidal Speed Reducer"](https://www.researchgate.net/publication/235992854_A_New_Design_of_a_Two-Stage_Cycloidal_Speed_Reducer), I decided to develop this nontraditional cycloidal drive for a robotic arm.

---

## 2. Initial CAD Development

**Date:** June - July 2025

* Developed parametric cycloidal geometry
* Designed ring gears and cycloidal discs
* Determined eccentricity and PCD
* Developed the two-stage architecture

<!-- PHOTO: Early CAD screenshots from this phase, if you have version history / earlier iterations saved -->
<img src="images/early-cad.jpg" alt="Early CAD development of cycloidal geometry" width="700">

---

## 3. 3D-Printing and Assembly

**Date:** July 2025 - July 2026

* Oriented pieces in specific printing orientations to maximize part durability
* Redesigned and modified CAD to compensate for printing tolerances or printing orientation
* Re-printed pieces in varying materials (PETG to Nylon, for example) to better suit the piece's function
* Assembled pieces together with M2-M6 screws and nuts
* Heat-set inserts into parts
* Iterated parts many times, especially when integrating the motor into the build

<!-- PHOTO: Print-in-progress shot, and/or a "part iteration" comparison photo (v1 vs v2 vs final) -->
<img src="images/print-iterations.jpg" alt="3D printing and part iteration comparison" width="700">

---

## 4. Wiring and Running the BLDC Motor

**Date:** May - July 2026

* Soldered wires and connectors together
* Set up ODESC and calibrated motor
* Ran motor with closed-loop PID

<!-- PHOTO: Soldering/wiring in progress, or the motor spinning under control on the bench -->
<img src="images/wiring-motor-bench.jpg" alt="Wiring and bench testing the BLDC motor" width="700">

---

## 5. Current Prototype

**Date:** May - July 2026

The complete mechanical gearbox has been assembled and connected to the BLDC motor.

The cycloidal drive itself has been mounted onto a bracket that will be used for the robotic arm.

The theoretical reduction ratio is **121:1**, but the actual ratio has not yet been experimentally characterized.

<!-- PHOTO: Final assembled prototype mounted on the robotic arm base bracket — this is likely your best "money shot" -->
<img src="images/final-prototype-mounted.jpg" alt="Completed gearbox mounted on robotic arm base bracket" width="700">

### Remaining characterization

* [ ] Measure actual reduction ratio
* [ ] Measure output RPM
* [ ] Measure unloaded current
* [ ] Measure loaded current
* [ ] Measure output torque
* [ ] Measure backlash
* [ ] Measure gearbox efficiency
* [ ] Determine maximum safe operating load
* [ ] Evaluate structural deformation
* [ ] Identify components requiring redesign

---

# Future Development

The next iteration will focus on experimentally characterizing the transmission rather than simply determining whether it rotates.

Planned improvements include:

* More accurate alignment features
* Improved bearing interfaces
* Optimized print orientation
* Stronger structural materials
* Reduced friction
* Reduced backlash
* Improved shaft interfaces
* Closed-loop position sensing
* Motor controller integration
* Robotic arm integration

Ultimately, the goal is to determine how closely the physical gearbox performs to its theoretical design and identify the limiting components of the transmission.

---

# Project Skills Demonstrated

This project combines several areas of engineering:

### Mechanical Engineering

* Parametric CAD
* Transmission design
* Torque calculations
* Shaft design
* Bearing selection
* Tolerance analysis
* Structural considerations

### Manufacturing

* FDM additive manufacturing
* Engineering polymers
* Heat-set inserts
* Mechanical post-processing
* Prototype iteration

### Electrical / Controls

* BLDC motor control
* Motor controller integration
* Hall sensors
* Encoder feedback
* Power electronics

### Robotics

* High-torque actuator design
* Joint transmission
* Closed-loop control
* Robotic arm integration

---

# Project Status

**Mechanical prototype: COMPLETE**

**Motor integration: COMPLETE**

**Theoretical reduction: 121:1**

**Experimental characterization: IN PROGRESS**

**Integration into robotic arm: IN PROGRESS**
