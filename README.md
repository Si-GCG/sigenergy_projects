# Sigenergy Projects for Home Assistant

Welcome to the **sigenergy_projects** repo! This is my home for all things Sigenergy + Home Assistant. Here you'll find cards, templates, and a healthy dose of creative workarounds—because sometimes the best solutions are the ones you hack together at 2 AM.

## What’s Inside?

- **Custom Cards:** Visualize your Sigenergy data like a pro.
- **Templates:** Automate all the things (or at least the Sigenergy bits).
- **Workarounds:** Because not everything works out-of-the-box (yet).

## Who’s This For?

Anyone looking to supercharge their Home Assistant setup with Sigenergy integrations, or just someone who enjoys a good workaround.

## How to Use
First and foremost this makes use of the amazing local modbus Sigenergy integration by Andrei Ignat: https://github.com/TypQxQ/Sigenergy-Local-Modbus/tree/main
I would recommend that you just go for it and do the full install with control not just monitoring as it opens up a lot more entities.

1. Ensure that you have file editor installed so you can upload the images. I have uploaded a few but the ultimate source for the images is: https://github.com/vdvmichel/sigen-app-images
2. In File Editor navigate to www and then create a new folder called "Sigenergy".
3. Go into the new folder and upload the images you want to use.
4. Browse the folders for cards, templates, or hacks you need.
5. Copy, tweak, and enjoy.
6. Got improvements? PRs welcome!
7. Double check the names of your entities and edit as required.

## Why Sigenergy?

Because your smart home deserves a smarter energy system—and because Home Assistant users never settle for default.

# Dependencies and Installation

## Required Custom Components

The dashboards and cards require several custom components to be installed via HACS (Home Assistant Community Store). If you don't have HACS installed, please follow the [HACS installation guide](https://hacs.xyz/docs/setup/download) first.

### 1. HACS Frontend Components

Install these components through HACS > Frontend:

#### Button Card
- **Name**: `button-card`
- **Repository**: [custom-cards/button-card](https://github.com/custom-cards/button-card)
- **Installation**: HACS > Frontend > Explore & Download Repositories > Search "Button Card"
- **Purpose**: Creates the custom energy flow visualisation cards with positioned elements

#### Mushroom Cards
- **Name**: `lovelace-mushroom`
- **Repository**: [piitaya/lovelace-mushroom](https://github.com/piitaya/lovelace-mushroom)
- **Installation**: HACS > Frontend > Explore & Download Repositories > Search "Mushroom"
- **Purpose**: Provides the template cards used for displaying power values and status information

#### Card Mod
- **Name**: `lovelace-card-mod`
- **Repository**: [thomasloven/lovelace-card-mod](https://github.com/thomasloven/lovelace-card-mod)
- **Installation**: HACS > Frontend > Explore & Download Repositories > Search "Card Mod"
- **Purpose**: Enables custom CSS styling for card positioning and appearance

### 2. Required Images

The dashboard uses custom system diagrams. Create the following directory structure in your Home Assistant configuration:

```
config/
└── www/
    └── Sigenergy/
        ├── sys_type_resd.png
        └── 1inverter1dcCharger2battery.png
```

You'll need to source or create these images:
- `sys_type_resd.png` - System overview diagram showing solar, battery, grid, and home connections
- `1inverter1dcCharger2battery.png` - Detailed system diagram showing inverter, DC charger, and battery layout

The images should be approximately 395px wide to fit the card layout properly.

### 3. Installation Steps

1. **Install HACS** (if not already installed):
   - Follow the [official HACS documentation](https://hacs.xyz/docs/setup/download)

2. **Install Custom Cards**:
   - Navigate to HACS in your Home Assistant sidebar
   - Click "Frontend"
   - Click "Explore & Download Repositories"
   - Search for and install each component listed above
   - Restart Home Assistant after installing all components

3. **Add Images**:
   - Create the `www/Sigenergy/` directory in your Home Assistant config folder
   - Add your system diagram images to this directory
   - Images will be accessible at `/local/Sigenergy/filename.png` in your dashboard

4. **Configure Dashboard**:
   - Copy the provided YAML configuration to your dashboard
   - Ensure all your Sigen entity names match those used in the configuration
   - Adjust entity names in the YAML if your integration uses different naming

### 4. Entity Requirements

This dashboard expects entities from the Sigenergy integration with names like:
- `sensor.sigen_plant_*`
- `sensor.sigen_inverter_*`
- `binary_sensor.sigen_plant_*`
- `number.sigen_plant_*`
- `select.sigen_plant_*`
- `switch.sigen_plant_*`

If your entity names differ, you'll need to update the YAML configuration accordingly.

### 5. Optional Configuration

#### Custom Height Control
The dashboard includes a height control entity:
- `input_number.sigen_home_card_height`

Create this helper in Home Assistant:
1. Settings > Devices & Services > Helpers
2. Create a "Number" helper
3. Name: "Sigen Home Card Height"
4. Entity ID: `input_number.sigen_home_card_height`
5. Min: 300, Max: 600, Step: 10, Initial: 400
6. Unit: pixels

This allows you to adjust the card height dynamically without editing YAML.

## Troubleshooting

**Cards not displaying correctly?**
- Ensure all custom components are installed and Home Assistant has been restarted
- Check that images are in the correct `/config/www/Sigenergy/` directory
- Verify entity names match your actual Sigenergy integration entities

**CSS styling not working?**
- Confirm Card Mod is installed and enabled
- Clear your browser cache
- Check browser developer tools for CSS errors

**Missing power flow animations?**
- Ensure all required sensors are available and providing data
- Check that binary sensors for power flow states are working correctly
---

*Got questions, ideas, or want to share your own Sigenergy wizardry? Open an issue or start a discussion!*
