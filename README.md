# Space Vape Application

The **Space Vape Application** is a Python-based desktop application built using `Tkinter`. It allows users to calculate the cost, profits, and other metrics for vape liquid production. The app features a calculator interface, history management, and data visualization.

## Features

- **Calculator**: Input key parameters (aroma cost, base cost, aroma percentage, etc.) to compute results such as:
  - Base added
  - Total liquid quantity
  - Number of bottles produced
  - Liquid charges
  - Total profits
- **History Management**:
  - Saves calculation history in a JSON file.
  - Displays history in a table with sortable columns.
  - Ability to clear saved history.
- **User Interface**:
  - Tabbed interface with sections for calculator and history.
  - Interactive widgets like buttons, tables, and inputs.

## Requirements

The following Python packages are required to run the application:
- `Pillow` (for handling the logo image)

Install the dependencies using:
```bash
pip install -r requirements.txt
