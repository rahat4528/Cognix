import asyncio
import os
import sys
import random
import time
import pandas as pd

# Setup import path
project_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if project_dir not in sys.path:
    sys.path.insert(0, project_dir)

from backend.core.database import AsyncSessionLocal, engine, Base
from backend.core.security import get_password_hash
from backend.models.models import User, Item, Interaction, UserPreference
from model_training.train import train_and_evaluate_all


# 100 realistic e-commerce products across 6 tech categories
CATEGORIES_CATALOG = {
    "Audio": [
        ("aud-01", "Aura Pro Wireless Noise-Cancelling Headphones", 349.99, 4.8, 1420, "wireless noise-cancelling bluetooth audiophile anc hi-res", "Flagship active noise-cancelling over-ear headphones with custom 40mm beryllium drivers."),
        ("aud-02", "StudioMaster Open-Back Reference Monitors", 499.00, 4.9, 860, "open-back studio mastering wired planar audiophile", "Open-back planar magnetic headphones tuned for critical acoustic mixing and mastering."),
        ("aud-03", "WaveBuds ANC True Wireless In-Ear Earbuds", 179.99, 4.6, 2150, "earbuds wireless bluetooth anc waterproof spatial", "Compact wireless earbuds with adaptive transparency mode and IPX5 moisture resistance."),
        ("aud-04", "PulseDAC High-Resolution USB Audio Converter", 199.50, 4.7, 540, "dac amp usb-c mqa 32-bit dsd desktop", "Ultra-low distortion desktop DAC and headphone amplifier with balanced 4.4mm output."),
        ("aud-05", "StreamMic Pro Cardioid Condenser Microphone", 129.99, 4.7, 3100, "microphone usb condenser podcast streaming xlr", "Broadcast-grade condenser microphone with built-in pop filter and zero-latency monitoring."),
        ("aud-06", "AcousticCore Soundbar with Dolby Atmos", 399.00, 4.5, 920, "soundbar atmos hdmi earc bluetooth home-theater", "Immersive 5.1.2 soundbar with upward-firing height drivers and wireless subwoofer."),
        ("aud-07", "BassWave Portable Bluetooth Speaker", 89.99, 4.4, 1840, "speaker bluetooth waterproof outdoor battery", "Rugged 30W portable speaker with 24-hour battery and dual passive radiators."),
        ("aud-08", "VocalShield Acoustic Isolation Booth", 79.99, 4.3, 410, "studio foam isolation shield vocal recording", "High-density acoustic foam reflection filter for crystal clear vocal recording."),
        ("aud-09", "LinearAmp Balanced Headphone Preamplifier", 279.00, 4.8, 330, "amplifier balanced analog audiophile desktop", "Class-A balanced headphone amplifier with discrete transistor architecture."),
        ("aud-10", "SpatialStage Studio Desktop Nearfield Monitors", 320.00, 4.7, 780, "speakers monitors nearfield powered studio", "Bi-amplified powered studio monitors delivering flat frequency response from 45Hz to 22kHz."),
        ("aud-11", "EchoBuds Sport Hook Wireless Earphones", 99.99, 4.3, 1120, "sports earhooks bluetooth sweatproof running", "Secure-fit earhook wireless earphones engineered for intense workouts."),
        ("aud-12", "TubeWarmth Hybrid Vacuum Tube Headphone Amp", 229.00, 4.6, 620, "vacuum-tube analog vintage preamp audiophile", "Hybrid vacuum tube preamplifier adding rich analog warmth to digital audio."),
        ("aud-13", "OmniLapel Wireless Lavalier Microphone Kit", 149.00, 4.7, 1340, "lavalier wireless mic interview video 2.4ghz", "Dual-transmitter 2.4GHz wireless lapel microphone system with active noise suppression."),
        ("aud-14", "SonicCable 8-Core Silver Plated Audio Cable", 49.99, 4.5, 490, "cable 3.5mm balanced silver audiophile iem", "Hand-braided 8-core silver-plated copper headphone cable with MMCX connectors."),
        ("aud-15", "StudioArm Heavy Duty Articulating Mic Boom", 69.99, 4.8, 2210, "boom-arm desk-mount studio cable-management", "Internal spring microphone boom arm with 360-degree rotation and integrated cable channel."),
        ("aud-16", "HiResStreamer Network Audio Receiver", 249.99, 4.6, 380, "streamer airplay2 roon dsd dlna wi-fi", "Lossless network audio bridge streaming FLAC and DSD over dual-band Wi-Fi and Ethernet."),
    ],
    "Computing": [
        ("cmp-01", "TitanBook Pro 16 M-Core Developer Laptop", 2499.00, 4.9, 1250, "laptop workstation 32gb 1tb mini-led developer", "Ultra-fast 16-core laptop featuring 32GB unified RAM and 120Hz Liquid Retina display."),
        ("cmp-02", "UltraWide Curve 34-Inch 144Hz Monitor", 649.99, 4.7, 1980, "monitor ultrawide 144hz 1440p ips usb-c", "Curved 21:9 WQHD productivity monitor with 90W USB-C power delivery."),
        ("cmp-03", "ApexMech Pro Wireless Mechanical Keyboard", 169.99, 4.8, 3420, "keyboard mechanical hot-swap rgb wireless gateron", "75% wireless mechanical keyboard with hot-swappable tactile switches and sound-dampening foam."),
        ("cmp-04", "PrecisionMaster 3S Ergonomic Wireless Mouse", 99.99, 4.9, 4890, "mouse ergonomic bluetooth multi-device scroll", "Ergonomic productivity mouse with electromagnetic MagSpeed wheel and silent click switches."),
        ("cmp-05", "CoreStation Thunderbolt 4 Docking Station", 229.00, 4.6, 1140, "dock thunderbolt4 dual-4k usb-c 100w ethernet", "12-in-1 high-bandwidth Thunderbolt 4 dock supporting dual 4K displays and 100W PD charging."),
        ("cmp-06", "VelocityDrive Gen4 2TB NVMe SSD", 149.99, 4.8, 3820, "ssd nvme pcie4 2tb 7000mbps storage m2", "Blazing fast PCIe 4.0 NVMe M.2 internal solid-state drive with graphene heatsink."),
        ("cmp-07", "VortexMini Aluminum ITX Desktop Chassis", 189.00, 4.7, 610, "case itx sff aluminum mini-pc gaming", "Precision CNC-milled small form factor ITX chassis with sandwich layout."),
        ("cmp-08", "AirStream Magnetic Laptop Cooling Stand", 49.99, 4.5, 1430, "stand aluminum ergonomic cooling portable", "Foldable aircraft-grade aluminum laptop riser with twin silent brushless fans."),
        ("cmp-09", "HyperScreen 27-Inch 4K OLED Pro Display", 899.00, 4.9, 720, "monitor oled 4k hdr color-grading creator", "Reference-grade 4K OLED display with 99% DCI-P3 color gamut and factory calibration."),
        ("cmp-10", "ClickPad Custom Macropad with Rotary Dial", 59.99, 4.6, 950, "macropad rotary-knob programmable qmk artisan", "Programmable 9-key QMK/VIA macropad with knurled aluminum rotary encoder."),
        ("cmp-11", "EtherSpeed 10GbE PCIe Network Card", 79.99, 4.7, 430, "networking 10gbe pcie rj45 low-latency", "Single-port 10 Gigabit Ethernet PCI Express network interface card."),
        ("cmp-12", "KeyCraft PBT Dye-Sub Minimalist Keycaps", 39.99, 4.6, 1890, "keycaps pbt cherry-profile mechanical keyboard", "Thick 1.5mm PBT keycap set with crisp dye-sublimated alphanumeric legends."),
        ("cmp-13", "DeskMatrix Felt Desk Mat Pad XL", 29.99, 4.7, 2410, "desk-pad felt wool minimalist surface mousepad", "Premium 900x400mm water-resistant wool felt desk mat with anti-slip silicone backing."),
        ("cmp-14", "SecureVault Hardware Encrypted 1TB SSD", 179.99, 4.8, 310, "portable-ssd hardware-encryption biometric security", "Rugged portable SSD with AES-XTS 256-bit hardware encryption and fingerprint unlock."),
        ("cmp-15", "SilentFan PWM High Static Pressure Fan Pack", 34.99, 4.6, 1540, "fan cooling pwm radiator silent pc-build", "Triple pack of 120mm fluid dynamic bearing case fans optimized for radiator airflow."),
        ("cmp-16", "CableFlex Custom Braided USB-C Coiled Cable", 24.99, 4.5, 1280, "cable coiled aviator usb-c mechanical-keyboard", "Double-sleeved coiled keyboard cable with detachable 4-pin aviator connector."),
    ],
    "Wearables": [
        ("wer-01", "Aegis Horizon Titanium GPS Smartwatch", 449.00, 4.8, 1680, "smartwatch titanium sapphire gps ecg battery", "Titanium adventure smartwatch with dual-frequency GPS, sapphire glass, and 14-day battery life."),
        ("wer-02", "BioRing Gen3 Smart Sleep & Recovery Ring", 299.00, 4.6, 920, "smart-ring sleep hrv temperature titanium", "Ultralight titanium health tracking ring monitoring sleep stages, HRV, and body temperature."),
        ("wer-03", "FitPulse Active Waterproof Fitness Tracker", 79.99, 4.4, 3140, "fitness-band tracker heart-rate spo2 waterproof", "Slim lightweight fitness tracker with continuous heart rate, SpO2 monitoring, and 50m water resistance."),
        ("wer-04", "VeloSpeed Cycling GPS Computer with HRM", 249.99, 4.7, 750, "cycling gps bike-computer cadence navigation", "Aerodynamic bike computer with turn-by-turn navigation, climb dynamics, and ANT+ sensor support."),
        ("wer-05", "PulseBand Medical Grade ECG Heart Monitor", 119.99, 4.8, 480, "ecg chest-strap hrm bluetooth ant medical", "Accurate chest strap heart rate monitor with continuous RR interval data transmission."),
        ("wer-06", "SmartLens Pro Audio AR Sunglasses", 189.00, 4.3, 830, "audio-glasses polarized bluetooth speakers uv", "Polarized UV400 sunglasses with open-ear directional audio speakers and voice control."),
        ("wer-07", "StrapPro FKM Waterproof Quick-Release Band", 34.99, 4.7, 1260, "watch-band fkm-rubber waterproof quick-release", "Fluoroelastomer waterproof sport watch strap with titanium buckle for 22mm lugs."),
        ("wer-08", "AirGrip Magnetic Wireless Power Charger for Watches", 29.99, 4.5, 980, "charger magnetic wireless portable usb-c", "Fast magnetic wireless charging puck compatible with flagship smartwatches."),
        ("wer-09", "AuraStrap Biomarker Body Composition Band", 89.99, 4.2, 340, "strap bioimpedance body-fat hydration sensor", "Smart apple-watch compatible strap measuring body fat percentage and hydration levels."),
        ("wer-10", "AltitudeAltimeter Barometric Climbing Compass", 139.00, 4.6, 510, "altimeter barometer compass outdoor survival", "Rugged outdoor instrument with barometric storm alarm and digital 3D compass."),
        ("wer-11", "RecoveryBoots Pneumatic Compression Sleeves", 499.00, 4.8, 410, "recovery compression lymphatic circulation athletes", "Sequential pneumatic compression recovery boots with 4 overlapping air chambers."),
        ("wer-12", "SoleSensor Smart Foot Pod Running Meter", 129.99, 4.6, 360, "running footpod cadence stride-length power-meter", "High-precision shoe-mounted sensor measuring running power, ground contact time, and cadence."),
        ("wer-13", "BreatheSense Sleep Apnea Monitoring Patch", 159.00, 4.5, 290, "sleep-apnea pulse-oximeter medical health", "Wearable continuous pulse oximeter monitoring overnight blood oxygen desaturation events."),
        ("wer-14", "GlowBand High-Visibility LED Running Belt", 19.99, 4.6, 2180, "safety led reflective night-running rechargeable", "Rechargeable 360-degree reflective LED waist belt for nighttime road safety."),
        ("wer-15", "ThermoBand Continuous Core Temperature Sensor", 199.99, 4.4, 210, "temperature heat-strain endurance clinical", "Non-invasive thermal sensor tracking core body temperature during endurance exertion."),
        ("wer-16", "HydroWatch Water Resistant Charging Case", 39.99, 4.4, 620, "travel-case powerbank waterproof smartwatch", "Hard EVA travel pouch with integrated 2000mAh battery for wireless watch top-ups."),
    ],
    "Smart Office": [
        ("off-01", "ErgoLift Pro Dual-Motor Standing Desk Frame", 429.00, 4.8, 1890, "standing-desk dual-motor motorized ergonomic sit-stand", "Heavy-duty steel dual-motor adjustable desk frame with 4 programmable memory presets."),
        ("off-02", "SpineSupport Breathable Mesh Ergonomic Chair", 549.00, 4.9, 2120, "ergonomic-chair mesh lumbar 3d-armrests executive", "Full ergonomic task chair with auto-tuning dynamic lumbar support and 4D armrests."),
        ("off-03", "LuminaGlow ScreenBar Auto-Dimming Desk Lamp", 79.99, 4.8, 4310, "monitor-lightbar desk-lamp led glare-free usb", "Space-saving asymmetrical LED light bar clamping directly to monitor bezel."),
        ("off-04", "CableHide Under-Desk Steel Cable Tray", 32.99, 4.7, 2840, "cable-management under-desk steel tray organizer", "Ventilated steel cable channel concealing power bricks and cable clutter."),
        ("off-05", "PureAir HEPA H13 Silent Room Air Purifier", 139.99, 4.7, 1920, "air-purifier hepa silent allergies odor sensor", "Medical-grade H13 True HEPA filter capturing 99.97% of airborne particles and dust."),
        ("off-06", "AromaMist Ultrasonic Essential Oil Diffuser", 39.99, 4.5, 3100, "diffuser aromatherapy ultrasonic ambient-light", "Whisper-quiet 500ml ultrasonic humidifier and aromatherapy diffuser."),
        ("off-07", "BalanceBoard Ergonomic Anti-Fatigue Rocker", 59.99, 4.6, 820, "balance-board standing-desk active-standing anti-fatigue", "Engineered wood active wobble balance board with non-slip PU traction surface."),
        ("off-08", "DualMonitor Gas Spring Articulated Arm", 89.99, 4.7, 1750, "monitor-mount dual-arm vesa gas-spring heavy-duty", "Gas-spring counterbalanced dual monitor arm holding screens up to 32 inches."),
        ("off-09", "TimeCube Smart Productivity Pomodoro Timer", 24.99, 4.5, 2390, "pomodoro timer productivity focus desk-clock", "Gravity-sensor visual countdown timer designed for deep focus work sessions."),
        ("off-10", "ThermalMug Temperature Controlled Smart Mug", 109.00, 4.6, 1450, "smart-mug heated coffee app-controlled charging-coaster", "Ceramic coated stainless steel travel mug maintaining drinks at selected temperature."),
        ("off-11", "PowerTower 12-in-1 Surge Protector Station", 42.99, 4.7, 3620, "power-strip surge-protector usb-c desktop tower", "Vertical power strip tower with 8 AC outlets and 4 high-speed USB charging ports."),
        ("off-12", "FootRest Ergonomic Memory Foam Cushion", 29.99, 4.6, 2890, "footrest ergonomic memory-foam posture washable", "High-density curved teardrop memory foam foot cushion with washable velour cover."),
        ("off-13", "Whiteboard Glass Magnetic Desktop Pad", 49.99, 4.7, 1180, "whiteboard glass desktop dry-erase drawer-storage", "Tempered glass desktop dry-erase notepad with built-in hidden storage drawer."),
        ("off-14", "PrivacyShield Magnetic Screen Filter for 27-Inch", 44.99, 4.4, 690, "privacy-screen anti-glare blue-light magnetic", "Snap-on micro-louver privacy filter blocking lateral viewing angles beyond 30 degrees."),
        ("off-15", "NoiseMask White Noise Sound Machine", 39.99, 4.6, 1760, "sound-machine white-noise sleep office-privacy", "Compact acoustic sound conditioner with 24 non-looping natural and ambient tracks."),
        ("off-16", "DeskDrawer Under-Desk Slide-Out Organizer", 27.99, 4.5, 940, "drawer under-desk organizer storage stationery", "Self-adhesive concealed pull-out under-desk pencil drawer and accessory tray."),
    ],
    "Photography": [
        ("pht-01", "AlphaFrame Full-Frame 33MP Mirrorless Camera", 1999.00, 4.9, 940, "camera full-frame 4k60p mirrorless bsi ibis", "Flagship 33MP full-frame mirrorless camera with 4K60p 10-bit video and 5-axis IBIS."),
        ("pht-02", "PrimeLux 50mm f/1.2 Art Portrait Lens", 1299.00, 4.9, 610, "lens prime 50mm f1.2 portrait bokeh sharp", "Ultra-fast prime portrait lens delivering exceptional resolving power and circular bokeh."),
        ("pht-03", "GimbalGlide 3-Axis Motorized Camera Stabilizer", 379.00, 4.8, 1420, "gimbal stabilizer motorized 3-axis payload carbon", "Carbon fiber 3-axis camera gimbal stabilizer with 4.5kg payload and OLED touch screen."),
        ("pht-04", "SunLite 100W Daylight Balanced COB LED Light", 189.99, 4.7, 1180, "lighting cob-led bowens-mount cri96 video-light", "Continuous Bowens-mount 100W COB video light with 96+ CRI and silent fan mode."),
        ("pht-05", "TripodPro Lightweight Carbon Fiber Travel Tripod", 199.00, 4.8, 1650, "tripod carbon-fiber ball-head lightweight compact", "Compact 4-section carbon fiber camera tripod with Arca-Swiss compatible ball head."),
        ("pht-06", "NDVariable True Color 82mm Fader Filter", 79.99, 4.6, 890, "filter variable-nd 82mm optics anti-reflective", "Multi-coated 1-to-5 stop variable neutral density filter with zero cross-polarization."),
        ("pht-07", "SoftBox 90cm Quick-Collapse Parabolic Softbox", 69.99, 4.7, 1340, "softbox parabolic bowens studio modifier diffusion", "16-rib quick-release parabolic softbox modifier producing soft wrap-around lighting."),
        ("pht-08", "V-Mount Lithium Cine Battery 99Wh 14.8V", 149.00, 4.7, 720, "battery v-mount d-tap usb-c cinema-camera", "Airline-safe 99Wh mini V-Mount battery with D-Tap and 65W bidirectional USB-C."),
        ("pht-09", "FieldMonitor 7-Inch 2200-Nit Daylight Viewable", 279.00, 4.6, 810, "monitor field-monitor 4k hdmi daylight false-color", "Ultra-bright 2200-nit touchscreen camera monitor with waveforms, scopes, and 3D LUT support."),
        ("pht-10", "MatteBox Carbon Fiber Swing-Away Clamp", 89.99, 4.5, 480, "matte-box carbon clamp-on filter-tray cinema", "Lightweight clamp-on matte box accommodating two 4x5.65-inch square cinema filters."),
        ("pht-11", "CamBackpack 30L Weatherproof Camera Bag", 169.00, 4.8, 1890, "backpack camera-bag waterproof modular dividers", "Modular 30L camera backpack with side quick-draw access and magnetic tripod straps."),
        ("pht-12", "WirelessTrans Video Transmitter & Receiver Set", 399.00, 4.7, 390, "wireless-video hdmi low-latency 1080p transmitter", "Zero-latency 5GHz wireless HD video transmission system with 400ft line-of-sight range."),
        ("pht-13", "SensorClean Full-Frame Sensor Cleaning Kit", 19.99, 4.8, 2810, "sensor-swab cleaning optics lint-free safe", "Vacuum-sealed 24mm full-frame sensor swabs with specialized non-abrasive liquid cleaner."),
        ("pht-14", "MacroFocus Bellows Extension Ring Set", 49.99, 4.4, 430, "macro extension-tubes autofocus close-up", "Electronic autofocus macro extension tube set enabling extreme close-up magnification."),
        ("pht-15", "SlideMotor Ultra-Quiet Automated Camera Slider", 299.00, 4.6, 320, "slider motorized timelapse smooth motion-control", "Bluetooth controlled carbon fiber motorized camera slider for silky timelapses and tracking shots."),
        ("pht-16", "ColorChecker Passport Photo Calibration Target", 99.00, 4.9, 1420, "color-checker calibration dng-profile accurate-color", "Industry-standard 24-patch color calibration chart in durable pocket-sized case."),
    ],
    "Smart Home": [
        ("hom-01", "MeshWiFi 6E Tri-Band Whole Home System (3-Pack)", 379.00, 4.7, 1840, "mesh-wifi router tri-band wifi6e gigabit roaming", "High-capacity AX5400 tri-band mesh system blanketing up to 6,000 sq ft in gigabit Wi-Fi."),
        ("hom-02", "AuraHub Smart Zigbee & Thread Border Gateway", 99.99, 4.6, 910, "hub zigbee thread matter smart-home gateway", "Universal Matter and Thread border router connecting local smart sensors with zero cloud latency."),
        ("hom-03", "NeoLight Smart Color Gradient Lightstrip 5m", 69.99, 4.7, 3120, "lightstrip rgbw addressable ambient matter wifi", "Individually addressable RGBIC gradient LED lightstrip with music sync and Matter compatibility."),
        ("hom-04", "SafeGuard 2K Battery Wire-Free Video Doorbell", 149.99, 4.6, 2480, "doorbell video 2k battery ai-detection two-way", "2K HDR wire-free video doorbell with local on-device person and package detection."),
        ("hom-05", "SmartPlug Mini Energy Monitoring Outlet (4-Pack)", 39.99, 4.8, 4520, "smart-plug energy-meter timer voice-control compact", "Compact 15A Wi-Fi smart plugs with real-time power consumption telemetry."),
        ("hom-06", "ThermoSmart Learning Programmable Thermostat", 179.00, 4.7, 2190, "thermostat smart hvac energy-saving geofencing", "Intuitive color touch display thermostat with auto-scheduling and remote humidity regulation."),
        ("hom-07", "SecureLock Smart Fingerprint Keyless Deadbolt", 189.99, 4.6, 1340, "smart-lock deadbolt fingerprint keypad keyless", "Weatherproof biometric deadbolt lock with 0.3s fingerprint scanner and anti-peep keypad."),
        ("hom-08", "WaterGuard Smart Leak Detector with Siren (3-Pack)", 59.99, 4.8, 1120, "leak-detector water-sensor alarm flood prevention", "Ultra-sensitive gold-plated probe water leak sensors alerting via loud 100dB buzzer and push notification."),
        ("hom-09", "AirQuality Smart Indoor Radon & TVOC Monitor", 159.00, 4.5, 670, "air-quality sensor co2 radon tvoc humidity", "Multi-parameter indoor air sensor measuring carbon dioxide, airborne chemicals, and humidity."),
        ("hom-10", "MotionBeam PIR Outdoor Solar Security Floodlight", 49.99, 4.6, 2810, "security-light solar motion-sensor floodlight outdoor", "Solar-powered 1500-lumen dual-head LED floodlight with 180-degree wide-angle motion detection."),
        ("hom-11", "SmartBlind Motorized Retrofit Roller Shutter", 119.00, 4.4, 760, "motorized-blinds smart-shutter solar-panel automation", "Rechargeable retrofit blind motor opening and closing shades on schedules or sunrise/sunset triggers."),
        ("hom-12", "CleanBot Laser Navigation Robot Vacuum & Mop", 499.00, 4.7, 1680, "robot-vacuum lidar auto-empty mop smart-mapping", "LiDAR navigation robotic vacuum with 4000Pa suction and auto-lifting sonic mop."),
        ("hom-13", "PlantSense Wireless Soil Moisture Sensor (4-Pack)", 34.99, 4.5, 930, "garden soil-moisture plant-care wireless-sensor", "Corrosion-resistant soil probes monitoring plant hydration and ambient sunlight intensity."),
        ("hom-14", "NightGlow Motion-Activated LED Underbed Lighting", 24.99, 4.7, 1940, "underbed-light motion-sensor warm-white nightlight", "Gentle 2700K warm ambient under-bed LED strip turning on automatically upon stepping onto floor."),
        ("hom-15", "SmartFeeder Automatic Pet Food Dispenser with HD Cam", 109.99, 4.6, 1270, "pet-feeder automatic camera voice-recording portion-control", "Portion-controlled smart cat/dog feeder with wide-angle camera and scheduled dispensing."),
        ("hom-16", "NanoSwitch In-Wall Smart Relay Module", 19.99, 4.6, 850, "relay in-wall smart-switch zigbee retrofit", "Miniature hidden relay transforming standard mechanical wall switches into smart switches."),
    ]
}


async def seed():
    print("Initializing Cognix Recommendation System database schema...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as session:
        # Check if already seeded
        from sqlalchemy.future import select
        existing_items = (await session.execute(select(Item))).scalars().all()

        if len(existing_items) == 0:
            print("Seeding 100 authentic catalog items across 6 tech categories...")
            all_items_list = []
            for category, items in CATEGORIES_CATALOG.items():
                for item_id, title, price, rating, reviews, tags, desc in items:
                    it = Item(
                        id=item_id,
                        title=title,
                        category=category,
                        price=price,
                        rating=rating,
                        review_count=reviews,
                        tags=tags,
                        description=desc,
                        image_url=f"/images/products/{item_id}.jpg"
                    )
                    session.add(it)
                    all_items_list.append(it)
            await session.commit()
            print(f"Successfully seeded {len(all_items_list)} items.")

        # Seed standard users
        existing_users = (await session.execute(select(User))).scalars().all()
        user_ids = []

        if len(existing_users) == 0:
            print("Seeding demo accounts and synthetic user community (50 users)...")
            # Demo accounts
            shopper = User(
                email="shopper@cognix.local",
                hashed_password=get_password_hash("ShopperPass123!"),
                role="customer"
            )
            admin = User(
                email="admin@cognix.local",
                hashed_password=get_password_hash("AdminPass123!"),
                role="admin"
            )
            analyst = User(
                email="analyst@cognix.local",
                hashed_password=get_password_hash("AnalystPass123!"),
                role="analyst"
            )
            session.add_all([shopper, admin, analyst])
            await session.flush()
            user_ids.extend([shopper.id, admin.id, analyst.id])

            # Generate remaining users
            for u_idx in range(4, 51):
                u = User(
                    email=f"user_{u_idx:02d}@cognix.local",
                    hashed_password=get_password_hash(f"PassWord_{u_idx}!"),
                    role="customer"
                )
                session.add(u)
                await session.flush()
                user_ids.append(u.id)
            await session.commit()
            print("Successfully seeded 50 user profiles.")
        else:
            user_ids = [u.id for u in existing_users]

        # Seed 2,500+ realistic temporal interaction events
        existing_interactions = (await session.execute(select(Interaction))).scalars().all()
        if len(existing_interactions) == 0:
            print("Generating 2,500 authentic temporal interaction events over 90 simulated days...")
            # Fetch all item objects
            all_items = (await session.execute(select(Item))).scalars().all()
            category_item_map = {}
            for it in all_items:
                category_item_map.setdefault(it.category, []).append(it.id)

            # Assign primary interest affinities to users (coherent clusters)
            categories = list(category_item_map.keys())
            user_affinities = {}
            for uid in user_ids:
                # Pick 2 primary categories per user
                user_affinities[uid] = random.sample(categories, 2)

            now = time.time()
            ninety_days_sec = 90 * 86400
            start_timestamp = now - ninety_days_sec

            interactions_to_insert = []
            interaction_weights = {"click": 1.0, "favorite": 2.0, "add_to_cart": 3.0, "purchase": 5.0}
            types_pool = ["click"] * 12 + ["favorite"] * 4 + ["add_to_cart"] * 3 + ["purchase"] * 1

            total_events_target = 2500
            for ev_idx in range(total_events_target):
                uid = random.choice(user_ids)
                user_cats = user_affinities[uid]

                # 75% chance of picking from preferred categories, 25% random exploration
                if random.random() < 0.75:
                    chosen_cat = random.choice(user_cats)
                else:
                    chosen_cat = random.choice(categories)

                chosen_item = random.choice(category_item_map[chosen_cat])
                itype = random.choice(types_pool)
                w = interaction_weights[itype]

                # Progressing timestamp with slight jitter
                prog = ev_idx / total_events_target
                ev_time = start_timestamp + (prog * ninety_days_sec) + random.uniform(-3600, 3600)

                inter = Interaction(
                    user_id=uid,
                    item_id=chosen_item,
                    interaction_type=itype,
                    weight=w,
                    session_id=f"sess_{uid}_{int(ev_time // 86400)}",
                    timestamp=ev_time
                )
                interactions_to_insert.append(inter)

            session.add_all(interactions_to_insert)
            await session.commit()
            print(f"Successfully generated and committed {len(interactions_to_insert)} temporal interaction events.")

        # Train and evaluate models offline
        print("Executing offline model training & temporal evaluation suite...")
        all_items_df = pd.DataFrame([{
            'id': it.id, 'title': it.title, 'category': it.category,
            'tags': it.tags, 'description': it.description
        } for it in (await session.execute(select(Item))).scalars().all()])

        all_inter_df = pd.DataFrame([{
            'user_id': it.user_id, 'item_id': it.item_id, 'weight': it.weight,
            'session_id': it.session_id or it.user_id, 'timestamp': it.timestamp
        } for it in (await session.execute(select(Interaction))).scalars().all()])

        eval_dir = os.path.join(project_dir, "model_evaluation")
        summary = train_and_evaluate_all(all_items_df, all_inter_df, output_dir=eval_dir)
        print("Offline evaluation complete. Summary:")
        print(f"Train/Val/Test Splits: {summary['temporal_split']['train_ratio']*100:.0f}% / {summary['temporal_split']['val_ratio']*100:.0f}% / {summary['temporal_split']['test_ratio']*100:.0f}%")
        for model_name, metrics in summary['benchmarks'].items():
            print(f" -> {model_name}: NDCG@10={metrics['ndcg@10']}, Recall@10={metrics['recall@10']}, Coverage={metrics['catalog_coverage']}")


if __name__ == "__main__":
    asyncio.run(seed())
