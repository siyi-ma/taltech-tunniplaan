# TalTech Course Schedule System

## Project Overview
This is a TalTech course schedule viewer that displays course sessions with filtering and search capabilities. The system was originally designed for course catalogs but has been adapted to work with schedule data.

## Data Structure
The application expects course session data in `courses.json` with the following structure:
```json
{
  "keel": "Eesti keel",
  "tyyp": "loeng+harjutus", 
  "oppejoud": "Viktor Rjabtšikov(lektor)",
  "oppenadalad": "1",
  "ryhmad": "EDJR54_V,EDJR55_V",
  "ainekavaurl": "https://ois2.taltech.ee/uusois/aine/EVR0230",
  "tpg": "EDJR55_V",
  "date": "06.09.2025",
  "ainekood": "EVR0230", 
  "aine": "MATLAB ja numbrilised meetodid",
  "start": "13:00",
  "end": "16:15",
  "ruum": "VK1-25" // optional
}
```

## Key Features
- **Bilingual Support**: Estonian and English interface
- **Course Session Cards**: Display course name, code, instructor, time, location
- **Search Functionality**: Search by course name, code, instructor, room, or groups
- **Filtering Options**: 
  - Course type (lecture, practice, etc.)
  - Study week number
  - Instructor
  - Teaching language
- **Responsive Design**: Works on desktop and mobile devices
- **Semi-transparent UI Elements**: Modern glassmorphism design

## File Structure
- `index.html` - Main application file containing HTML, CSS, and JavaScript
- `courses.json` - Course session data
- Image files for design reference

## Customization Notes
- The filter system has been adapted from course catalog filters to schedule-specific filters
- Course type filter uses the original "school" filter dropdown
- Week number filter uses the original "institute" filter dropdown  
- Instructor filter uses the original "assessment form" filter dropdown
- EAP filtering has been removed as it doesn't apply to schedule data

## UI Components
- **Header**: Title and language toggle
- **Search Area**: Semi-transparent search box and field selector
- **Filter Panel**: Collapsible sidebar with filtering options
- **Course Cards**: Individual session information with expand/collapse details
- **Results Counter**: Shows number of matching sessions

## JavaScript Architecture
- Event-driven filtering and search
- Debounced search input for performance
- Dynamic filter population based on data
- Responsive expand/collapse functionality for course details

## Styling
- Uses TalTech brand colors (dark blue, magenta, light blue)
- Proxima Nova font family
- Tailwind CSS for layout and responsive design
- Custom CSS for brand-specific styling and transparency effects